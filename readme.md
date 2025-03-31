# Warehouse Management System (WMS)

A Flask-based REST API for managing warehouse operations, inventory tracking, and product transfers.

## Setup

### Prerequisites

- Python 3.x
- SQLite3
- pip (Python package installer)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/Alberto-CHLO/wms-chlo.git
cd WMS-CHLO/backend
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Initialize the database:

```bash
python init_db.py
```

## Database Schema

The system uses SQLite with the following main tables:

- Warehouse: Stores warehouse information
- Product: Contains product details
- Inventory: Tracks product quantities in warehouses
- WarehouseCapacity: Defines capacity limits for products
- User: Manages user authentication and roles
- ProductReceipt: Tracks product receipts
- PurchaseOrder: Manages purchase orders

## API Endpoints

### Authentication

- `POST /v1/auth/login/` - User login

### Administrative

- `GET /v1/administrative/home/` - Display warehouse overview
- `GET /v1/administrative/warehouse/products/` - List warehouse products
- `GET /v1/administrative/product_receipt/detail/` - Get receipt details
- `POST /v1/administrative/purchase_order/create/` - Create purchase order

### Warehouse Operations

- `GET /v1/warehouse/capacity_needed/` - Check capacity requirements
- `PUT /v1/warehouse/transfer/` - Transfer products between warehouses
- `GET /v1/warehouse/suppliers/` - List suppliers
- `POST /v1/warehouse/receive/` - Create product receipt

### Boatman Operations

- `PUT /v1/boatman/consume_products/` - Record product consumption

## Development

To run the development server:

```bash
python server.py
```

The server will start on `http://localhost:5000`

## User Roles

- ADMIN: Full system access
- WAREHOUSE: Manage inventory and receipts
- BOATMAN: Handle product consumption
- DRIVER: Transport-related operations

## Database Initialization

Default data includes:

- 4 warehouses
- 5 sample products
- Initial inventory levels
- 3 suppliers
- Test user accounts
