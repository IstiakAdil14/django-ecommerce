# Cloudinary Media Storage Integration

This document describes the Cloudinary integration for media storage and delivery in the django-ecommerce project.

## Overview

The project uses Cloudinary for storing and serving user-uploaded media files (product images, user profile pictures, review media, etc.). Cloudinary provides:
- CDN delivery for fast image loading
- Automatic image optimization and transformations
- Persistent storage (not ephemeral like local file storage)
- Scalable media management

## Prerequisites

- Cloudinary account (sign up at https://cloudinary.com)
- Cloudinary credentials (Cloud Name, API Key, API Secret)

## Installation

### 1. Dependencies

The required packages are already in `requirements.txt`:
```
cloudinary==1.36.0
django-cloudinary-storage==0.3.0
```

To install:
```bash
pip install -r requirements.txt
```

### 2. Environment Variables

#### Option A: Using CLOUDINARY_URL (Recommended)

Set a single environment variable with the connection string:

```bash
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

Example:
```bash
CLOUDINARY_URL=cloudinary://123456789:abcdefghijklmnop@my-cloud-name
```

#### Option B: Using Individual Variables

Set three separate environment variables:

```bash
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

### 3. Local Development Setup

For local development, create a `.env` file in the project root (if using `python-decouple`):

```env
CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME
```

Or set environment variables in your shell:
- **Windows (PowerShell):**
  ```powershell
  $env:CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
  ```

- **Linux/Mac:**
  ```bash
  export CLOUDINARY_URL="cloudinary://API_KEY:API_SECRET@CLOUD_NAME"
  ```

### 4. Render Deployment Setup

1. Go to your Render service dashboard
2. Navigate to **Environment** section
3. Add the following environment variables:

   - `CLOUDINARY_URL` (or the three individual variables):
     - `CLOUDINARY_CLOUD_NAME`
     - `CLOUDINARY_API_KEY`
     - `CLOUDINARY_API_SECRET`

4. Save and redeploy the service

## Configuration

The Cloudinary configuration is in `greatkart/settings.py`:

```python
# Uses environment variables automatically
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CLOUDINARY_STORAGE = {
    "prefix": "django_ecommerce",  # Optional: folder prefix in Cloudinary
}
```

## Migrating Existing Media

To migrate existing local media files to Cloudinary, use the management command:

### Dry Run (Preview)

First, check what will be migrated without actually uploading:

```bash
python manage.py migrate_images_to_cloudinary --dry-run
```

### Actual Migration

Run the migration command:

```bash
python manage.py migrate_images_to_cloudinary
```

With custom folder prefix:

```bash
python manage.py migrate_images_to_cloudinary --folder my_custom_folder
```

### What Gets Migrated

The script migrates:
- Product images (`store.models.Product.images`)
- Product gallery images (`store.models.ProductGallery.image`)
- User profile pictures (`accounts.models.UserProfile.profile_picture`)
- Review media images (`store.models.ReviewMedia.image`)

The script:
- Skips files already on Cloudinary (checks for `http` URLs)
- Handles missing files gracefully
- Provides detailed progress output
- Shows summary of migrated/skipped/errored files

## Verification

### 1. Check Cloudinary Dashboard

1. Log in to [Cloudinary Dashboard](https://console.cloudinary.com)
2. Navigate to **Media Library**
3. Check the `django_ecommerce` folder (or your custom prefix)
4. Verify uploaded images appear there

### 2. Test in Application

1. **Local Testing:**
   ```bash
   python manage.py runserver
   ```
   - Visit product pages
   - Check browser developer tools → Network tab
   - Verify image requests return 200 status
   - Confirm image URLs point to `res.cloudinary.com` domain

2. **Production Testing (Render):**
   - Deploy the application
   - Visit product pages
   - Inspect network requests
   - Verify images load from Cloudinary CDN

### 3. Upload New Image

1. Log in to Django admin
2. Create/edit a product and upload an image
3. Verify the image appears immediately
4. Check Cloudinary dashboard - new image should appear automatically

### 4. Debugging Checklist

If images are not loading:

- [ ] **404 Errors:**
  - Check Cloudinary console for uploaded files
  - Verify files exist in the correct folder
  - Run migration script if files haven't been uploaded

- [ ] **403 Errors:**
  - Verify API keys are correct in environment variables
  - Check Cloudinary account permissions
  - Ensure API key has upload/read permissions

- [ ] **Relative Paths in Templates:**
  - Ensure templates use `{{ product.images.url }}` or `{{ product.get_image_url }}`
  - Verify `DEFAULT_FILE_STORAGE` is set to `cloudinary_storage.storage.MediaCloudinaryStorage`
  - Check settings.py configuration

- [ ] **Environment Variables:**
  - Verify environment variables are set correctly
  - Check for typos in variable names
  - Restart the Django server after changing env vars

## Rollback Plan

If you need to revert to local file storage:

### 1. Update settings.py

Change `DEFAULT_FILE_STORAGE` back to local storage:

```python
# In greatkart/settings.py
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
# Remove or comment out Cloudinary config
# DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
```

### 2. Optional: Remove Cloudinary Packages

If you want to completely remove Cloudinary:

```bash
pip uninstall cloudinary django-cloudinary-storage
```

Then remove from `requirements.txt`:
```
# cloudinary==1.36.0
# django-cloudinary-storage==0.3.0
```

### 3. Redeploy

Redeploy the application on Render.

**Note:** This will only affect new uploads. Existing Cloudinary URLs in the database will still point to Cloudinary. To fully revert, you would need to:
- Download images from Cloudinary
- Update database fields to point to local paths
- Run database migrations

## Best Practices

1. **Backup Before Migration:**
   - Keep a backup of your local `media/` folder
   - Export database before running migration

2. **Test Locally First:**
   - Run migration script locally with `--dry-run`
   - Test image uploads locally before deploying

3. **Monitor Cloudinary Usage:**
   - Check Cloudinary dashboard regularly
   - Monitor bandwidth and storage usage
   - Cloudinary has a free tier with generous limits

4. **Environment Variables Security:**
   - Never commit credentials to version control
   - Use Render's environment variable system for production
   - Rotate API keys periodically

## Troubleshooting

### "Cloudinary configuration error"

- Verify environment variables are set correctly
- Check that `CLOUDINARY_URL` format is correct: `cloudinary://KEY:SECRET@NAME`
- Ensure no extra spaces or quotes in environment variables

### "Local file not found"

- The migration script only migrates files that exist locally
- If files are already on Cloudinary, they will be skipped
- Verify `MEDIA_ROOT` path in settings.py matches actual location

### Images work locally but not on Render

- Double-check environment variables in Render dashboard
- Ensure environment variables are set before deployment
- Check Render build logs for any configuration errors
- Verify Cloudinary account is active and not suspended

## Additional Resources

- [Cloudinary Python SDK Documentation](https://cloudinary.com/documentation/django_integration)
- [Django Cloudinary Storage Documentation](https://github.com/klis87/django-cloudinary-storage)
- [Cloudinary Console](https://console.cloudinary.com)

## Support

For issues related to:
- **Cloudinary:** Contact Cloudinary support or check their documentation
- **Django Integration:** Check Django Cloudinary Storage GitHub issues
- **Project-specific:** Check project repository issues

