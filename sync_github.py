#!/usr/bin/env python3
"""
Script to sync PythonAnywhere deployment with GitHub repository.
Place this script in /home/gembonganggeredu/mysite/ and run via PythonAnywhere console.

Usage:
    python sync_github.py [--branch main] [--hard]

Options:
    --branch    Branch to pull from (default: main)
    --hard      Reset all local changes before pulling
"""

import os
import subprocess
import sys
from pathlib import Path


# Configuration
SITE_ROOT = Path("/home/gembonganggeredu/mysite")
BACKUP_DIR = SITE_ROOT / "backups"
GIT_DIR = SITE_ROOT  # Assuming the repo is cloned at mysite root


def print_header(text):
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60)


def run_command(cmd, cwd=None, check=True):
    """Run shell command and return result"""
    print(f"  → {cmd}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or GIT_DIR,
            capture_output=True,
            text=True,
            check=check
        )
        if result.stdout:
            print(result.stdout)
        if result.returncode != 0 and result.stderr:
            print(f"  ERROR: {result.stderr}", file=sys.stderr)
        return result
    except subprocess.CalledProcessError as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        if check:
            raise
        return e


def create_backup():
    """Create backup of current state"""
    print_header("Creating Backup")

    BACKUP_DIR.mkdir(exist_ok=True)

    # Backup database
    db_path = SITE_ROOT / "instance" / "app.db"
    if db_path.exists():
        backup_db = BACKUP_DIR / "app.db.backup"
        import shutil
        shutil.copy2(db_path, backup_db)
        print(f"  ✓ Database backed up to {backup_db}")

    # Backup .env
    env_path = SITE_ROOT / ".env"
    if env_path.exists():
        backup_env = BACKUP_DIR / "env.backup"
        import shutil
        shutil.copy2(env_path, backup_env)
        print(f"  ✓ .env backed up to {backup_env}")

    # Backup uploads folder (IMPORTANT: prevent image loss)
    uploads_path = SITE_ROOT / "static" / "uploads"
    if uploads_path.exists():
        backup_uploads = BACKUP_DIR / "uploads.backup"
        import shutil
        shutil.copytree(uploads_path, backup_uploads, dirs_exist_ok=True)
        print(f"  ✓ Uploads folder backed up to {backup_uploads}")

    print("  ✓ Backup completed")


def check_git_status():
    """Check if we're in a git repository"""
    print_header("Checking Git Status")

    if not (GIT_DIR / ".git").exists():
        print("  ✗ Not a git repository!")
        print(f"  Please clone the repository to {GIT_DIR}")
        print("  Run: git clone https://github.com/gembongangger/backend-resto-manager.git /home/gembonganggeredu/mysite")
        return False

    # Show current status
    run_command("git status --short")
    run_command("git log -1 --oneline")

    return True


def pull_changes(branch="main", hard_reset=False):
    """Pull latest changes from GitHub"""
    print_header(f"Pulling from GitHub (branch: {branch})")

    # Fetch latest
    run_command("git fetch origin")

    # Stash local changes to sync_github.py (this script) to avoid conflicts
    print("  → Stashing local changes to sync_github.py...")
    run_command("git stash push -m 'local sync_github.py' sync_github.py")

    if hard_reset:
        print("  → Hard resetting local changes (keeping uploads & database safe)...")
        
        # Save uploads temporarily
        uploads_path = SITE_ROOT / "static" / "uploads"
        temp_uploads = BACKUP_DIR / "temp_uploads_hard"
        if uploads_path.exists():
            import shutil
            shutil.copytree(uploads_path, temp_uploads, dirs_exist_ok=True)
            print(f"  → Uploads saved temporarily")
        
        # Save database temporarily
        db_path = SITE_ROOT / "instance" / "app.db"
        temp_db = BACKUP_DIR / "temp_app.db"
        if db_path.exists():
            import shutil
            shutil.copy2(db_path, temp_db)
            print(f"  → Database saved temporarily")
        
        run_command("git reset --hard HEAD")
        run_command("git clean -fd")
        
        # Restore uploads after hard reset
        if temp_uploads.exists():
            uploads_path.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copytree(temp_uploads, uploads_path, dirs_exist_ok=True)
            shutil.rmtree(temp_uploads)
            print(f"  → Uploads restored after hard reset")
        
        # Restore database after hard reset
        if temp_db.exists():
            db_path.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(temp_db, db_path)
            shutil.rmtree(temp_db, ignore_errors=True)
            print(f"  → Database restored after hard reset")

    # Pull changes
    result = run_command(f"git pull origin {branch}", check=False)

    if result.returncode != 0:
        print("\n  ✗ Pull failed! You may have local conflicts.")
        print("  Try running with --hard flag to reset local changes:")
        print("  python sync_github.py --hard")
        return False

    print("  ✓ Pull completed successfully")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print_header("Installing Dependencies")

    requirements = SITE_ROOT / "requirements.txt"
    if not requirements.exists():
        print("  ✗ requirements.txt not found")
        return False

    # Check if virtualenv exists
    venv = SITE_ROOT / "venv"
    if venv.exists():
        pip = venv / "bin" / "pip"
        run_command(f"{pip} install -r {requirements} --upgrade")
        print("  ✓ Dependencies installed (virtualenv)")
    else:
        # System Python
        run_command("pip3 install -r requirements.txt --upgrade --user")
        print("  ✓ Dependencies installed (system)")

    return True


def run_migrations():
    """Run database migrations"""
    print_header("Running Database Migrations")

    # Check if Flask app exists
    wsgi = SITE_ROOT / "wsgi.py"
    runpy = SITE_ROOT / "run.py"
    if not wsgi.exists() and not runpy.exists():
        print("  ! Flask app not found, skipping migrations")
        return False

    # Try to run migrations
    venv = SITE_ROOT / "venv"
    if venv.exists():
        python = venv / "bin" / "python"
    else:
        python = "python3"

    # Set environment
    env = os.environ.copy()
    env["FLASK_APP"] = "run.py"
    env["FLASK_ENV"] = "production"

    try:
        result = subprocess.run(
            [str(python), "-m", "flask", "db", "upgrade"],
            cwd=SITE_ROOT,
            env=env,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode == 0:
            print("  ✓ Migrations completed")
        else:
            print(f"  ! Migration output: {result.stderr}")
    except Exception as e:
        print(f"  ! Could not run migrations: {e}")

    return True


def restore_uploads():
    """Restore uploads folder from backup"""
    print_header("Restoring Uploads Folder")

    backup_uploads = BACKUP_DIR / "uploads.backup"
    uploads_path = SITE_ROOT / "static" / "uploads"

    if not backup_uploads.exists():
        print("  ! No uploads backup found, skipping restore")
        return

    try:
        import shutil
        # Ensure target directory exists
        uploads_path.mkdir(parents=True, exist_ok=True)
        # Restore files
        shutil.copytree(backup_uploads, uploads_path, dirs_exist_ok=True)
        print(f"  ✓ Uploads folder restored from backup")
    except Exception as e:
        print(f"  ! Error restoring uploads: {e}")


def collect_static():
    """Collect static files if needed"""
    print_header("Checking Static Files")

    try:
        # Ensure uploads folder exists
        uploads_dir = SITE_ROOT / "static" / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Uploads folder exists: {uploads_dir}")

        # Ensure static folder exists
        static_dir = SITE_ROOT / "static"
        static_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Static folder exists: {static_dir}")
    except PermissionError as e:
        print(f"  ! Permission error: {e}")
        print("  Try: chmod -R u+w /home/gembonganggeredu/mysite")
    except Exception as e:
        print(f"  ! Error creating directories: {e}")


def reload_app():
    """Reload PythonAnywhere app"""
    print_header("Reloading Application")

    wsgi_file = "/var/www/gembonganggeredu_pythonanywhere_com_wsgi.py"

    try:
        # Touch the WSGI file to trigger reload
        os.utime(wsgi_file, None)
        print(f"  ✓ Reload triggered: {wsgi_file}")
        print("  ! Please wait a few seconds for the app to restart")
    except PermissionError:
        print(f"  ! Permission denied: {wsgi_file}")
        print("  Manual reload needed - click 'Reload' in PythonAnywhere Dashboard")
    except Exception as e:
        print(f"  ! Error triggering reload: {e}")
        print("  Manual reload needed - run: touch /var/www/gembonganggeredu_pythonanywhere_com_wsgi.py")


def main():
    print_header("GitHub Sync Script for PythonAnywhere")
    print(f"Site Root: {SITE_ROOT}")

    # Parse arguments
    branch = "main"
    hard_reset = False

    if "--branch" in sys.argv:
        idx = sys.argv.index("--branch")
        if idx + 1 < len(sys.argv):
            branch = sys.argv[idx + 1]

    if "--hard" in sys.argv:
        hard_reset = True

    # Check git
    if not check_git_status():
        sys.exit(1)

    # Create backup
    create_backup()

    # Pull changes
    if not pull_changes(branch, hard_reset):
        print("\n Sync stopped at pull stage")
        sys.exit(1)

    # Restore uploads (IMPORTANT: prevent image loss)
    restore_uploads()

    # Install dependencies
    install_dependencies()

    # Run migrations
    run_migrations()

    # Check static
    collect_static()

    # Reload PythonAnywhere app
    reload_app()

    print_header("Sync Complete!")
    print("\n✓ All done!")
    print("\nYour app has been reloaded automatically.")
    print("If reload failed, manually run:")
    print("  touch /var/www/gembonganggeredu_pythonanywhere_com_wsgi.py")


if __name__ == "__main__":
    main()
