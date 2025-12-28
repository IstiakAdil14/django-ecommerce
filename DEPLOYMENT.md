# Deployment Guide for PythonAnywhere

This guide explains how to deploy the GreatKart Django e-commerce project to PythonAnywhere.

## Prerequisites

- PythonAnywhere account (free tier available)
- GitHub repository with the project code
- MinIO or S3-compatible storage for media files (optional, but recommended for production)

## Step 1: Prepare Your Project

### 1.1 Update .gitignore

Ensure your `.gitignore` file excludes large directories and files:

```
media/
static/
migrations/
db.sqlite3
__pycache__/
*.pyc
.DS_Store
```

### 1.2 Push to GitHub

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

## Step 2: Set Up PythonAnywhere

### 2.1 Create a New Web App

1. Log in to PythonAnywhere
2. Go to the "Web" tab
3. Click "Add a new web app"
4. Choose "Manual configuration" and select Python 3.10 (or latest available)
5. Set the source code directory (e.g., `/home/yourusername/greatkart`)

### 2.2 Clone Your Repository

Open a Bash console in PythonAnywhere and clone your repository:

```bash
git clone https://github.com/yourusername/your-repo-name.git greatkart
cd greatkart
```

## Step 3: Configure the Environment

### 3.1 Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3.2 Install Dependencies

```bash
pip install -r requirements_clean.txt
```

### 3.3 Set Environment Variables

Create a `.env` file in your project root:

```bash
nano .env
```

Add the following content (adjust as needed):

```env
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=yourusername.pythonanywhere.com

# Database (use PostgreSQL for production)
DATABASE_URL=sqlite:///db.sqlite3  # Or PostgreSQL URL

# MinIO/S3 Configuration (if using cloud storage)
USE_MINIO=True
MINIO_ENDPOINT=your-minio-endpoint
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=your-bucket-name
MINIO_USE_HTTPS=True

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True

# Other settings
USE_TZ=True
```

### 3.4 Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3.5 Collect Static Files

```bash
python manage.py collectstatic --noinput
```

## Step 4: Configure Web App

### 4.1 Update WSGI Configuration

In PythonAnywhere's Web tab, go to the "WSGI configuration file" and update it:

```python
import os
import sys

# Add your project directory to the sys.path
project_home = '/home/yourusername/greatkart'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variable to tell django where your settings.py is
os.environ['DJANGO_SETTINGS_MODULE'] = 'ecommerce.settings'

# Activate your virtualenv
activate_this = '/home/yourusername/greatkart/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import django
import django
django.setup()

# Import the WSGI application
from ecommerce.wsgi import application
```

### 4.2 Set Static Files Directory

In the Web tab, set the static files directory to `/home/yourusername/greatkart/static/`

## Step 5: Database Setup (Optional)

If using PostgreSQL instead of SQLite:

1. In PythonAnywhere, go to the "Databases" tab
2. Create a PostgreSQL database
3. Update your `.env` file with the database URL

## Step 6: Media Storage Setup

### Option 1: MinIO (Recommended)

1. Set up MinIO server or use a cloud service
2. Configure environment variables as shown above
3. Ensure the bucket exists

### Option 2: Local Media (Not Recommended for Production)

If you must use local media:

1. Create a `media/` directory in your project
2. Upload media files manually or via admin interface
3. Note: This will count towards your PythonAnywhere storage limit

## Step 7: Reload and Test

1. In PythonAnywhere's Web tab, click "Reload"
2. Visit your site at `https://yourusername.pythonanywhere.com`
3. Test the application functionality

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed in the virtual environment
2. **Static Files Not Loading**: Check static files configuration and run `collectstatic`
3. **Database Errors**: Run migrations and check database configuration
4. **Media Upload Errors**: Verify MinIO/S3 configuration

### Logs

Check logs in PythonAnywhere:
- Web app logs: Web tab > Logs
- Error logs: `/var/log/pythonanywhere/error.log`
- Your app logs: Check Django's logging configuration

## Production Considerations

1. **Security**: Use strong SECRET_KEY, enable HTTPS, set DEBUG=False
2. **Performance**: Use PostgreSQL, enable caching, optimize static files
3. **Backup**: Regularly backup your database and media files
4. **Monitoring**: Set up error monitoring and logging
5. **Updates**: Use Git to deploy updates

## Updating Your App

To update your deployed app:

```bash
cd greatkart
git pull origin main
source venv/bin/activate
pip install -r requirements_clean.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then reload the web app in PythonAnywhere.

## Support

If you encounter issues, check:
- PythonAnywhere help pages
- Django documentation
- MinIO documentation (if using MinIO)
