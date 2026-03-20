# Database Configuration Guide

## Overview

Backend ini mendukung 3 jenis database:
- **SQLite** - Development/Testing (default)
- **MySQL** - Production
- **PostgreSQL** - Production

## Konfigurasi Database

### 1. SQLite (Development)

**Kelebihan:**
- Tidak perlu install server database
- Cocok untuk development dan testing
- Single file database

**Setup:**
```bash
# .env file
DB_TYPE=sqlite
DATABASE_URL=sqlite:///app.db
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Initialize database:**
```bash
flask init-db
```

---

### 2. MySQL (Production)

**Kelebihan:**
- Performa baik untuk read-heavy workload
- Familiar untuk kebanyakan developer
- Support dari hosting murah

**Setup:**

1. **Install MySQL Server** (jika belum ada):
```bash
# Ubuntu/Debian
sudo apt-get install mysql-server

# Windows: Download dari mysql.com
# macOS: brew install mysql
```

2. **Buat database:**
```sql
CREATE DATABASE resto_manager CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'resto_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON resto_manager.* TO 'resto_user'@'localhost';
FLUSH PRIVILEGES;
```

3. **Konfigurasi .env:**
```bash
# .env file
DB_TYPE=mysql
DATABASE_URL=mysql+pymysql://resto_user:your_password@localhost:3306/resto_manager?charset=utf8mb4
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Initialize database:**
```bash
flask init-db
```

---

### 3. PostgreSQL (Production - Recommended)

**Kelebihan:**
- Performa lebih baik untuk write-heavy dan concurrent workload
- Advanced features (JSONB, full-text search, window functions)
- MVCC untuk concurrency yang lebih baik

**Setup:**

1. **Install PostgreSQL Server:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Windows: Download dari postgresql.org
# macOS: brew install postgresql
```

2. **Buat database:**
```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE resto_manager;
CREATE USER resto_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE resto_manager TO resto_user;
\c resto_manager
GRANT ALL ON SCHEMA public TO resto_user;
\q
```

3. **Konfigurasi .env:**
```bash
# .env file
DB_TYPE=postgresql
DATABASE_URL=postgresql://resto_user:your_password@localhost:5432/resto_manager
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

5. **Initialize database:**
```bash
flask init-db
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_TYPE` | Type database (sqlite/mysql/postgresql) | `sqlite` |
| `DATABASE_URL` | Connection string | `sqlite:///app.db` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `JWT_SECRET_KEY` | JWT signing key | `dev-jwt-secret` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:5173,...` |

---

## Connection String Format

### MySQL
```
mysql+pymysql://username:password@host:port/database?charset=utf8mb4
```
Contoh:
```
mysql+pymysql://root:password123@localhost:3306/resto_manager?charset=utf8mb4
```

### PostgreSQL
```
postgresql://username:password@host:port/database
```
Contoh:
```
postgresql://postgres:password123@localhost:5432/resto_manager
```

### SQLite
```
sqlite:///relative/path/to/database.db
sqlite:////absolute/path/to/database.db
```
Contoh:
```
sqlite:///app.db
sqlite:////var/data/resto.db
```

---

## Migration antar Database

### Dari SQLite ke MySQL/PostgreSQL

1. **Export data dari SQLite:**
```bash
# Install sqlite3 jika belum
sqlite3 instance/app.db .dump > backup.sql
```

2. **Setup database baru** (MySQL/PostgreSQL)

3. **Update .env** dengan database baru

4. **Initialize schema:**
```bash
flask init-db
```

5. **Import data** (jika perlu, sesuaikan syntax SQL)

### Menggunakan Flask-Migrate

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

---

## Performance Tips

### MySQL
```env
# Optimize connection pool
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 10, "max_overflow": 20, "pool_recycle": 3600, "pool_pre_ping": true}
```

### PostgreSQL
```env
# Optimize connection pool
SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 10, "max_overflow": 20, "pool_recycle": 3600, "pool_pre_ping": true}
```

### General
- Gunakan composite index untuk query multi-tenant: `CREATE INDEX idx_orders_restaurant_created ON orders(restaurant_id, created_at);`
- Enable query logging di development untuk debugging
- Gunakan connection pooling untuk production

---

## Troubleshooting

### Error: "No module named 'pymysql'"
```bash
pip install PyMySQL==1.1.0
```

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary==2.9.9
```

### Error: "Access denied for user"
- Pastikan username dan password benar di DATABASE_URL
- Pastikan user punya akses ke database

### Error: "Database does not exist"
- Buat database manual terlebih dahulu
- Pastikan nama database benar di DATABASE_URL

### Error: "SQLite objects created in a thread can only be used in the same thread"
- Sudah dihandle di config dengan `check_same_thread: False`
- Pastikan menggunakan SQLiteConfig

---

## Production Deployment

### Environment Variables (Production)

```bash
# Production .env
DB_TYPE=mysql
DATABASE_URL=mysql+pymysql://prod_user:strong_password@prod_host:3306/resto_manager?charset=utf8mb4
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET_KEY=<generate-strong-random-key>
CORS_ORIGINS=https://your-domain.com
FLASK_ENV=production
```

### Generate Strong Secret Keys

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Using .env.production

Buat file `.env.production` untuk production settings:
```bash
DB_TYPE=mysql
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db
SECRET_KEY=prod-secret-key
JWT_SECRET_KEY=prod-jwt-secret
```

Load di production server:
```bash
export FLASK_ENV=production
python run.py
```
