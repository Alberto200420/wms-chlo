from apps.users.permissions import IsAdministrator, IsWarehouse, IsBoatman
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import views, status
from django.db import transaction
from .serializers import *
from .models import *
import logging
logger = logging.getLogger(__name__)
# ------------------------------------------------ ADMINISTRATIVE

# ----------------------------------- GET
class WarehouseHomeDisplayView(views.APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        warehouses = Warehouse.objects.all()
        serializer = WarehouseSerializer(warehouses, many=True)
        return Response(serializer.data)

class WarehouseProductsView(views.APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        warehouse_id = request.query_params.get('warehouse_id')
        if not warehouse_id:
            return Response({"error": "warehouse_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        inventory_items = Inventory.objects.filter(warehouse=warehouse).select_related('product')

        serializer = WarehouseProductSerializer(inventory_items, many=True)

        return Response({
            "warehouse_name": warehouse.warehouse_name,
            "products": serializer.data
        }, status=status.HTTP_200_OK)

class ProductReceiptDetailView(views.APIView):
    permission_classes = [IsAdministrator]

    def get(self, request):
        receipt_id = request.query_params.get('receipt_id')
        if not receipt_id:
            return Response({"error": "receipt_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        product_receipt = get_object_or_404(ProductReceipt, pk=receipt_id)
        serializer = ProductReceiptSerializer(product_receipt)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ----------------------------------- POST
class PurchaseOrderCreateView(views.APIView):
    permission_classes = [IsAdministrator]

    def post(self, request):
        logger.info("Received purchase order request: %s", request.data)

        supplier_id = request.data.get('supplier_id')
        total_amount = request.data.get('total_amount')

        if not supplier_id or not total_amount:
            logger.error("Supplier ID and Total amount is required")
            return Response({'error': 'Supplier ID and Total amount is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if supplier exists
        try:
            supplier = Supplier.objects.get(supplier_id=supplier_id)
        except Supplier.DoesNotExist:
            logger.error("Supplier with ID %s not found", supplier_id)
            return Response({'error': 'Supplier not found'}, status=status.HTTP_404_NOT_FOUND)

        # Create the purchase order
        serializer = PurchaseOrderSerializer(data={'supplier': supplier.supplier_id, 'total_amount': total_amount})
        if serializer.is_valid():
            purchase_order = serializer.save()
            logger.info("Purchase order created successfully: %s", purchase_order.purchase_order_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            logger.error("Purchase order creation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ------------------------------------------------ CAPTAN / WAREHOUSE

# ----------------------------------- GET
class WarehouseFillCapacityView(views.APIView):
    permission_classes = [IsAdministrator|IsWarehouse|IsBoatman]

    def get(self, request):
        warehouse_id = request.query_params.get('warehouse_id')
        if not warehouse_id:
            return Response({"error": "warehouse_id query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
        inventory_items = Inventory.objects.filter(warehouse=warehouse).select_related('product')
        capacities = WarehouseCapacity.objects.filter(warehouse=warehouse).select_related('product')
        
        # Create a dictionary to map product to its max capacity
        capacity_map = {capacity.product_id: capacity.max_capacity for capacity in capacities}
        
        # Prepare the response data
        response_data = []
        for item in inventory_items:
            max_capacity = capacity_map.get(item.product_id, 0)
            if item.status == 'LOW_CAPACITY' and max_capacity > item.quantity:
                quantity_needed = max_capacity - item.quantity
                response_data.append({
                    'product_id': item.product.product_id,
                    'product_name': item.product.product_name,
                    'quantity_needed': quantity_needed,
                    'max_capacity': max_capacity
                })
        
        serializer = ProductFillCapacitySerializer(response_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ----------------------------------- PUT
class ProductTransferView(views.APIView):
    permission_classes = [IsAdministrator|IsWarehouse|IsBoatman]

    def put(self, request):
        logger.info("Received product transfer request: %s", request.data)

        serializer = ProductTransferSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error("Product transfer validation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        source_warehouse = validated_data['from_warehouse']
        destination_warehouse = validated_data['to_warehouse']
        products_to_transfer = validated_data['products_to_get']

        transfer_errors = []
        successful_transfers = []

        try:
            with transaction.atomic():
                for product_data in products_to_transfer:
                    product_id = product_data['product_id']
                    quantity_needed = product_data['quantity_needed']

                    logger.info("Processing transfer: Product ID %d, Quantity: %d", product_id, quantity_needed)

                    # Get inventory records
                    source_inventory = Inventory.objects.get(
                        warehouse=source_warehouse,
                        product_id=product_id
                    )
                    destination_inventory, _ = Inventory.objects.get_or_create(
                        warehouse=destination_warehouse,
                        product_id=product_id,
                        defaults={'quantity': 0, 'status': 'LOW_CAPACITY'}
                    )

                    # Ensure enough stock is available in source warehouse
                    if source_inventory.quantity < quantity_needed:
                        logger.warning("Insufficient quantity for Product ID %d: Available %d, Requested %d",
                                       product_id, source_inventory.quantity, quantity_needed)
                        transfer_errors.append({
                            'product_id': product_id,
                            'error': f'Insufficient quantity. Available: {source_inventory.quantity}, Requested: {quantity_needed}'
                        })
                        continue

                    # Update source and destination inventory
                    source_inventory.quantity -= quantity_needed
                    destination_inventory.quantity += quantity_needed

                    # Update inventory status based on warehouse capacity
                    self.update_inventory_status(source_inventory)
                    self.update_inventory_status(destination_inventory)

                    # Save inventory changes
                    source_inventory.save()
                    destination_inventory.save()

                    logger.info("Transfer successful: Product ID %d, %d units from %s to %s",
                                product_id, quantity_needed,
                                source_warehouse.warehouse_name, destination_warehouse.warehouse_name)

                    successful_transfers.append({
                        'product_id': product_id,
                        'quantity': quantity_needed,
                        'from_warehouse': source_warehouse.warehouse_name,
                        'to_warehouse': destination_warehouse.warehouse_name,
                        'source_remaining': source_inventory.quantity,
                        'destination_new_total': destination_inventory.quantity
                    })

                # Rollback if any errors occurred
                if transfer_errors:
                    logger.error("Some transfers failed: %s", transfer_errors)
                    raise ValueError("Transfer validation failed")

        except ValueError:
            return Response({
                'status': 'error',
                'message': 'Some products could not be transferred',
                'errors': transfer_errors
            }, status=status.HTTP_400_BAD_REQUEST)

        logger.info("Product transfer completed successfully.")
        return Response({
            'status': 'success',
            'message': 'Products transferred successfully',
            'transfers': successful_transfers
        }, status=status.HTTP_200_OK)

    def update_inventory_status(self, inventory):
        """ Update inventory status based on warehouse capacity """
        capacity = WarehouseCapacity.objects.get(
            warehouse=inventory.warehouse,
            product=inventory.product
        )
        capacity_percentage = (inventory.quantity / capacity.max_capacity) * 100
        inventory.status = 'GOOD_CAPACITY' if capacity_percentage > capacity.capacity_percentage else 'LOW_CAPACITY'

# ------------------------------------------------ WAREHOUSE

# ----------------------------------- POST
class ProductReceiptCreateView(views.APIView):
    permission_classes = [IsWarehouse]

    def post(self, request):
        serializer = ProductReceiptSerializer(data=request.data)
        if serializer.is_valid():
            supplier_id = serializer.validated_data['supplier_id']
            products = serializer.validated_data['products']
            
            # Get the supplier
            supplier = get_object_or_404(Supplier, supplier_id=supplier_id)
            
            # Get the PurchaseOrder in REQUESTED status for the supplier
            purchase_order = get_object_or_404(
                PurchaseOrder,
                supplier=supplier,
                status='REQUESTED'
            )
            
            # Create the ProductReceipt
            product_receipt = ProductReceipt.objects.create(
                purchase_order=purchase_order,
                received_by=request.user.username
            )
            
            # Create ProductReceiptItems and update inventory
            warehouse = get_object_or_404(Warehouse, pk=1)
            for product_data in products:
                product = get_object_or_404(Product, pk=product_data['product_id'])
                quantity = product_data['quantity']
                expiration_date = product_data.get('expiration_date')
                
                ProductReceiptItem.objects.create(
                    receipt=product_receipt,
                    warehouse=warehouse,
                    product=product,
                    quantity_received=quantity,
                    expiration_date=expiration_date
                )
                
                # Update inventory
                inventory, created = Inventory.objects.get_or_create(
                    warehouse=warehouse,
                    product=product,
                    defaults={'quantity': 0, 'status': 'GOOD_CAPACITY'}
                )
                inventory.quantity += quantity
                inventory.save()
            
            # Update the PurchaseOrder status to RECEIVED
            purchase_order.status = 'RECEIVED'
            purchase_order.save()
            
            return Response({"message": "Product receipt created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# ------------------------------------------------ CAPTAN

# ----------------------------------- POST
class ProductConsumptionReportView(views.APIView):
    permission_classes = [IsBoatman]
    
    def post(self, request):
        serializer = WarehouseProductConsumptionSerializer(data=request.data)
        if serializer.is_valid():
            warehouse_id = serializer.validated_data['warehouse_id']
            products_consumed = serializer.validated_data['products_consumed']
            
            # Get the warehouse
            warehouse = get_object_or_404(Warehouse, pk=warehouse_id)
            
            consumption_errors = []
            successful_consumptions = []

            try:
                with transaction.atomic():
                    for product_data in products_consumed:
                        product_id = product_data['product_id']
                        quantity = product_data['quantity']

                        logger.info("Processing consumption for product ID: %d, Quantity: %d", product_id, quantity)

                        # Get the objects tables
                        product = get_object_or_404(Product, pk=product_id)
                        inventory = get_object_or_404(Inventory, warehouse=warehouse, product=product)
                        warehouse_capacity = get_object_or_404(WarehouseCapacity, warehouse=warehouse, product=product)

                        # Check if warehouse has enough quantity
                        if inventory.quantity < quantity:
                            logger.warning("Insufficient quantity for %s (ID: %d). Available: %d, Requested: %d",
                                           product.product_name, product_id, inventory.quantity, quantity)
                            consumption_errors.append({
                                'product_id': product_id,
                                'product_name': product.product_name,
                                'error': f'Insufficient quantity. Available: {inventory.quantity}, Requested: {quantity}'
                            })
                            continue

                        # Update inventory
                        inventory.quantity -= quantity

                        # Calculate the remaining capacity percentage
                        remaining_capacity_percentage = (inventory.quantity / warehouse_capacity.max_capacity) * 100

                        # Update inventory status if needed
                        if remaining_capacity_percentage <= warehouse_capacity.capacity_percentage:
                            inventory.status = 'LOW_CAPACITY'
                        else:
                            inventory.status = 'GOOD_CAPACITY'

                        # Save inventory changes
                        inventory.save()

                        logger.info("Consumption successful for %s (ID: %d): %d units from %s", product.product_name, product_id, quantity, warehouse.warehouse_name)

                        successful_consumptions.append({
                            'product_id': product_id,
                            'product_name': product.product_name,
                            'quantity': quantity,
                            'warehouse': warehouse.warehouse_name,
                            'remaining_quantity': inventory.quantity
                        })

                    # If there are errors, raise an exception to rollback the transaction
                    if consumption_errors:
                        logger.error("Consumption errors occurred: %s", consumption_errors)
                        raise serializers.ValidationError(consumption_errors)

            except serializers.ValidationError as e:
                logger.error("Transaction rollback due to validation error: %s", consumption_errors)
                return Response({
                    'status': 'error',
                    'message': 'Some products could not be consumed',
                    'errors': consumption_errors
                }, status=status.HTTP_400_BAD_REQUEST)

            logger.info("Product consumption completed successfully.")
            return Response({
                'status': 'success',
                'message': 'Products consumed successfully',
                'consumptions': successful_consumptions
            }, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)