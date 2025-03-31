from django.urls import path
from .views import *

urlpatterns = [
    # ------------------------------------------------ ADMINISTRATIVE 
    path('v1/administrative/product_receipt/detail/', ProductReceiptDetailView.as_view(), name='product-receipt-detail'),
    path('v1/administrative/purchase_order/create/', PurchaseOrderCreateView.as_view(), name='purchase-order-create'),
    path('v1/warehouse/products/', WarehouseProductsView.as_view(), name='warehouse-products'),
    path('v1/administrative/home/', WarehouseHomeDisplayView.as_view(), name='home-display'),
    # ------------------------------------------------ CAPTAN / WAREHOUSE
    path('v1/warehouse/fill_capacity/', WarehouseFillCapacityView.as_view(), name='warehouse-fill-capacity'),
    path('v1/warehouse/transfer/', ProductTransferView.as_view(), name='product-transfer'),
    # ------------------------------------------------ WAREHOUSE
    path('v1/warehouse/product_receipt/create/', ProductReceiptCreateView.as_view(), name='product-receipt-create'),
    # ------------------------------------------------ CAPTAN
    path('v1/warehouse/consume_products/', ProductConsumptionReportView.as_view(), name='report-consume-products')
]