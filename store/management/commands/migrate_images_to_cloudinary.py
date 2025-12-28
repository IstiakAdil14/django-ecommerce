"""
Django management command to migrate existing media files from local storage to Cloudinary.

This script:
1. Uploads local media files to Cloudinary
2. Updates Django model fields to reference Cloudinary URLs
3. Handles: Product images, ProductGallery images, UserProfile pictures, ReviewMedia images
4. Skips files already on Cloudinary (checks if URL starts with 'http')

Usage:
    python manage.py migrate_images_to_cloudinary

Requirements:
    - Cloudinary credentials must be set in environment variables (CLOUDINARY_URL or individual vars)
    - Local media files must exist in MEDIA_ROOT
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, ProductGallery, ReviewMedia
from accounts.models import UserProfile
import os
import cloudinary.uploader
import cloudinary


class Command(BaseCommand):
    help = 'Migrate existing images from local storage to Cloudinary'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without actually uploading',
        )
        parser.add_argument(
            '--folder',
            type=str,
            default='django_ecommerce',
            help='Cloudinary folder prefix for uploaded files (default: django_ecommerce)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        folder = options['folder']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No files will be uploaded'))

        # Verify Cloudinary configuration
        try:
            cloudinary.config()
            self.stdout.write(self.style.SUCCESS('Cloudinary configuration verified'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Cloudinary configuration error: {str(e)}')
            )
            self.stdout.write(
                self.style.WARNING('Please set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET')
            )
            return

        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            self.stdout.write(
                self.style.WARNING(f'Media root {media_root} does not exist. Nothing to migrate.')
            )
            return

        migrated_count = 0
        skipped_count = 0
        error_count = 0

        # Migrate Product images
        self.stdout.write('\n=== Migrating Product Images ===')
        products = Product.objects.all()
        for product in products:
            if not product.images or not product.images.name:
                continue

            # Check if already on Cloudinary (URL starts with http)
            current_url = str(product.images.url) if hasattr(product.images, 'url') else ''
            if current_url.startswith('http') and 'cloudinary' in current_url:
                self.stdout.write(f'Skipping {product.product_name} - already on Cloudinary')
                skipped_count += 1
                continue

            # Try to get local file path
            try:
                local_path = product.images.path
                if not os.path.exists(local_path):
                    self.stdout.write(
                        self.style.WARNING(f'Local file not found for {product.product_name}: {local_path}')
                    )
                    skipped_count += 1
                    continue
            except (ValueError, AttributeError):
                # FileField doesn't have a local path (might already be on Cloudinary or remote)
                self.stdout.write(
                    self.style.WARNING(f'Cannot access local path for {product.product_name}')
                )
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f'Would migrate: {product.product_name} from {local_path}')
                continue

            try:
                # Upload to Cloudinary
                upload_result = cloudinary.uploader.upload(
                    local_path,
                    folder=f"{folder}/photos/products",
                    resource_type="image"
                )
                cloudinary_public_id = upload_result['public_id']
                
                # Update the image field with the Cloudinary public_id
                # CloudinaryStorage expects public_id format
                product.images = cloudinary_public_id
                product.save()

                migrated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Migrated: {product.product_name}')
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[FAIL] Failed {product.product_name}: {str(e)}')
                )

        # Migrate ProductGallery images
        self.stdout.write('\n=== Migrating ProductGallery Images ===')
        galleries = ProductGallery.objects.all()
        for gallery in galleries:
            if not gallery.image or not gallery.image.name:
                continue

            current_url = str(gallery.image.url) if hasattr(gallery.image, 'url') else ''
            if current_url.startswith('http') and 'cloudinary' in current_url:
                skipped_count += 1
                continue

            try:
                local_path = gallery.image.path
                if not os.path.exists(local_path):
                    skipped_count += 1
                    continue
            except (ValueError, AttributeError):
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f'Would migrate gallery image for: {gallery.product.product_name}')
                continue

            try:
                upload_result = cloudinary.uploader.upload(
                    local_path,
                    folder=f"{folder}/store/products",
                    resource_type="image"
                )
                gallery.image = upload_result['public_id']
                gallery.save()

                migrated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Migrated gallery: {gallery.product.product_name}')
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[FAIL] Failed gallery {gallery.product.product_name}: {str(e)}')
                )

        # Migrate UserProfile pictures
        self.stdout.write('\n=== Migrating UserProfile Pictures ===')
        profiles = UserProfile.objects.all()
        for profile in profiles:
            if not profile.profile_picture or not profile.profile_picture.name:
                continue

            current_url = str(profile.profile_picture.url) if hasattr(profile.profile_picture, 'url') else ''
            if current_url.startswith('http') and 'cloudinary' in current_url:
                skipped_count += 1
                continue

            try:
                local_path = profile.profile_picture.path
                if not os.path.exists(local_path):
                    skipped_count += 1
                    continue
            except (ValueError, AttributeError):
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f'Would migrate profile: {profile.user.email}')
                continue

            try:
                upload_result = cloudinary.uploader.upload(
                    local_path,
                    folder=f"{folder}/userprofile",
                    resource_type="image"
                )
                profile.profile_picture = upload_result['public_id']
                profile.save()

                migrated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Migrated profile: {profile.user.email}')
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[FAIL] Failed profile {profile.user.email}: {str(e)}')
                )

        # Migrate ReviewMedia images
        self.stdout.write('\n=== Migrating ReviewMedia Images ===')
        review_media = ReviewMedia.objects.all()
        for media in review_media:
            if not media.image or not media.image.name:
                continue

            current_url = str(media.image.url) if hasattr(media.image, 'url') else ''
            if current_url.startswith('http') and 'cloudinary' in current_url:
                skipped_count += 1
                continue

            try:
                local_path = media.image.path
                if not os.path.exists(local_path):
                    skipped_count += 1
                    continue
            except (ValueError, AttributeError):
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f'Would migrate review media: {media.review.subject}')
                continue

            try:
                upload_result = cloudinary.uploader.upload(
                    local_path,
                    folder=f"{folder}/reviews",
                    resource_type="image"
                )
                media.image = upload_result['public_id']
                media.save()

                migrated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'[OK] Migrated review media: {media.review.subject}')
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'[FAIL] Failed review media {media.review.subject}: {str(e)}')
                )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Migration Summary:'))
        self.stdout.write(f'  Migrated: {migrated_count}')
        self.stdout.write(f'  Skipped:  {skipped_count}')
        self.stdout.write(f'  Errors:   {error_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No files were actually uploaded'))
        else:
            self.stdout.write(self.style.SUCCESS('\nMigration completed!'))
