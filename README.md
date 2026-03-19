# Backend Resto Manager

Flask REST API untuk sistem manajemen restoran.

## Fitur

- Autentikasi user (JWT)
- Manajemen menu dan kategori
- Manajemen pesanan
- dapur
- Inventori dapur
- Laporan keuangan

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dengan konfigurasi yang sesuai

# Jalankan server
python run.py
```

## API Endpoints

### Auth
- `POST /api/auth/login` - Login user
- `POST /api/auth/register` - Registrasi user

### Menu
- `GET /api/menu` - List menu items
- `POST /api/menu` - Tambah menu item
- `PUT /api/menu/<id>` - Update menu item
- `DELETE /api/menu/<id>` - Hapus menu item

### Categories
- `GET /api/menu-categories` - List kategori
- `POST /api/menu-categories` - Tambah kategori

### Orders
- `GET /api/orders` - List pesanan
- `POST /api/orders` - Buat pesanan baru
- `PUT /api/orders/<id>` - Update pesanan

### Kitchen
- `GET /api/kitchen/orders` - Pesanan untuk dapur
- `PUT /api/kitchen/orders/<id>` - Update status pesanan
- `GET /api/kitchen/inventory` - List inventori
- `POST /api/kitchen/inventory` - Tambah inventori

### Reports
- `GET /api/reports/sales` - Laporan penjualan
- `GET /api/reports/finance` - Laporan keuangan

### Finance
- `GET /api/finance/entries` - List entri keuangan
- `POST /api/finance/entries` - Tambah entri keuangan

### Restaurants
- `GET /api/restaurants` - List restoran
- `POST /api/restaurants` - Tambah restoran

### Users
- `GET /api/users` - List user
- `POST /api/users` - Tambah user
- `PUT /api/users/<id>` - Update user
- `DELETE /api/users/<id>` - Hapus user

### Recipes
- `GET /api/recipes` - List resep
- `POST /api/recipes` - Tambah resep
- `PUT /api/recipes/<id>` - Update resep
- `DELETE /api/recipes/<id>` - Hapus resep

## Tech Stack

- Flask
- Flask-SQLAlchemy
- Flask-Migrate (Alembic)
- Flask-JWT-Extended
- PyMySQL
