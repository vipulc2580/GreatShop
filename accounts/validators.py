from django.core.exceptions import ValidationError
import os


def validate_profile_picture(image):
    filesize = image.size
    max_size_mb = 5
    if filesize > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file too large (>{max_size_mb}MB)")

    ext = os.path.splitext(image.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(
            f"Unsupported file extension.Allowed {', '.join(valid_extensions)}.")
