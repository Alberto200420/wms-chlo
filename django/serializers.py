from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from rest_framework import serializers
from .models import *

class WarehouseSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = ['warehouse_id', 'warehouse_name', 'current_value', 'status']
    
    def get_current_value(self, obj):
        inventory_value = Inventory.objects.filter(warehouse=obj).annotate(
            item_value=F('quantity') * F('product__unit_price')
        ).aggregate(
            total=Coalesce(Sum('item_value'), 0, output_field=DecimalField(max_digits=12, decimal_places=2))
        )['total']
        return inventory_value
    
    def get_status(self, obj):
        low_capacity_items = Inventory.objects.filter(
            warehouse=obj, status='LOW_CAPACITY'
        ).exists()
        return 'Low Capacity' if low_capacity_items else 'Good Capacity'

class WarehouseProductSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name')
    max_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Inventory
        fields = ['product_name', 'quantity', 'max_capacity']

    def get_max_capacity(self, obj):
        capacity = WarehouseCapacity.objects.filter(
            warehouse=obj.warehouse,
            product=obj.product
        ).first()
        return capacity.max_capacity if capacity else 0

class ProductFillCapacitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    quantity_needed = serializers.IntegerField()
    max_capacity = serializers.IntegerField()

class ProductTransferItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity_needed = serializers.IntegerField(min_value=1)

class ProductTransferSerializer(serializers.Serializer):
    from_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )
    to_warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all()
    )
    products_to_get = ProductTransferItemSerializer(many=True)
    
    def validate(self, data):
        # Check that source and destination warehouses are different
        if data['from_warehouse'] == data['to_warehouse']:
            raise serializers.ValidationError("Source and destination warehouses must be different")
        return data

class PurchaseOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrder
        fields = ['purchase_order_id', 'warehouse', 'supplier', 'order_date', 'total_amount', 'status']
        read_only_fields = ['purchase_order_id', 'warehouse', 'order_date', 'status']

    def create(self, validated_data):
        warehouse = Warehouse.objects.get(warehouse_id=1)  # Always warehouse ID 1
        purchase_order = PurchaseOrder.objects.create(
            warehouse=warehouse,
            **validated_data
        )
        return purchase_order

class ProductReceiptItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()
    expiration_date = serializers.DateField(required=False, allow_null=True)

class ProductReceiptSerializer(serializers.Serializer):
    supplier_id = serializers.IntegerField()
    products = ProductReceiptItemSerializer(many=True)

class ProductConsumedSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField()

class WarehouseProductConsumptionSerializer(serializers.Serializer):
    warehouse_id = serializers.IntegerField()
    products_consumed = ProductConsumedSerializer(many=True)

class ProductReceiptItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name')

    class Meta:
        model = ProductReceiptItem
        fields = ['product_name', 'quantity_received', 'expiration_date']

class ProductReceiptSerializer(serializers.ModelSerializer):
    items = ProductReceiptItemSerializer(many=True, read_only=True)

    class Meta:
        model = ProductReceipt
        fields = ['receipt_id', 'receipt_date', 'received_by', 'items']