# PythonAnywhere Deployment Guide

## Setup Steps for PythonAnywhere

### 1. Upload Files to PythonAnywhere

Via Git atau manual upload, pastikan file-file ini ada di `/home/gembonganggeredu/mysite/`:

```
/home/gembonganggeredu/mysite/
├── .env.production      ← Environment production
├── requirements.txt     ← Dependencies
├── wsgi.py              ← File WSGI lokal (opsional, untuk referensi)
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   ├── models.py
│   ├── routes/
│   └── ...
└── ...
```

### 2. Configure PythonAnywhere Web Dashboard

1. Login ke https://www.pythonanywhere.com
2. Klik tab **"Web"**
3. Klik **"Add a new web app"** (atau edit yang existing)

### 3. WSGI Configuration (PENTING!)

Di bagian **"Code"** pada Web dashboard:

**WSGI configuration file:**
- Klik link file WSGI (biasanya `/var/www/gembonganggeredu_pythonanywhere_com_wsgi.py`)
- **BACKUP** isi original terlebih dahulu
- Ganti dengan isi dari `wsgi.py` atau gunakan format ini:

```python
import sys
import os

project_home = '/home/gembonganggeredu/mysite'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.environ['FLASK_ENV'] = 'production'
os.environ['DB_TYPE'] = 'mysql'

from app import create_app
application = create_app()
```

- Simpan dan klik **Reload** 🔴

### 4. Python Version

Pastikan menggunakan **Python 3.10** atau yang lebih baru.

### 5. Sync dari GitHub (Opsional)

Jika project Anda di GitHub, di **Bash Console** PythonAnywhere:

```bash
cd /home/gembonganggeredu/mysite
git init  # Jika belum ada git
git remote add origin https://github.com/your-username/your-repo.git
git pull origin main
```

**Note:** WSGI file PythonAnywhere (`/var/www/...`) TIDAK akan ter-sync dari GitHub. Anda harus edit manual di dashboard.

### 6. Environment Variables

Di tab **"Web"** → **"Environment variables"**, tambahkan:

```
FLASK_ENV=production
DB_TYPE=mysql
DB_HOST=gembonganggeredu.mysql.pythonanywhere-services.com
DB_PORT=3306
DB_USER=gembonganggeredu
DB_PASSWORD=Gembongmajesa112
DB_NAME=gembonganggeredu$restaurant_db
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,https://resto-manager.netlify.app,capacitor://localhost,http://localhost,ionic://localhost
```

**Note:** Atau gunakan `.env.production` di folder project dan PythonAnywhere akan otomatis load (jika menggunakan load_dotenv).

### 7. Install Dependencies

Buka **Bash console** di PythonAnywhere dan jalankan:

```bash
cd /home/gembonganggeredu/mysite
pip3 install -r requirements.txt
```

### 8. Setup Database

Pastikan database sudah dibuat di PythonAnywhere:

1. Login ke MySQL di PythonAnywhere
2. Database: `gembonganggeredu$restaurant_db`
3. Jalankan migrations jika ada

### 9. Reload Web App

Klik tombol **"Reload"** (merah) di tab Web.

### 10. Test Backend

Buka browser dan akses:
```
https://gembonganggeredu.pythonanywhere.com/
```

Jika berhasil, seharusnya tidak ada error 500 lagi.

---

## Troubleshooting

### Error 500 masih muncul?

1. **Check Error Logs:**
   - Di PythonAnywhere dashboard, tab "Web"
   - Klik "Error log"
   - Lihat error detailnya

2. **Database Connection:**
   ```bash
   # Di Bash console
   cd /home/gembonganggeredu/mysite
   python3 -c "from app import create_app; app = create_app(); print('OK')"
   ```

3. **Verify Environment:**
   ```bash
   python3 -c "import os; print(os.getenv('DB_HOST'))"
   ```

### CORS Error di Mobile?

Pastikan `CORS_ORIGINS` include:
- `capacitor://localhost`
- `ionic://localhost`
- `http://localhost`

---

## Testing APK setelah Backend Fixed

Setelah backend berjalan, install APK di Android emulator/device:

```bash
# Via ADB
export ANDROID_HOME=/home/gembong/Android/Sdk
$ANDROID_HOME/platform-tools/adb install \
  /mnt/data/web/resto_svelte/sveltekit_capasitor/android/app/build/outputs/apk/debug/app-debug.apk
```

Aplikasi akan otomatis connect ke:
```
https://gembonganggeredu.pythonanywhere.com
```
