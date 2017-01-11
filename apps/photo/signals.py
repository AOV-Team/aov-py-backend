from apps.photo import models as photo_models
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=photo_models.Photo)
def save_photo_image_caches(sender, instance, **kwargs):
    """
    This signal is basically a hack. After an image is saved, we need to generate different image sizes using Image Kit.
    The problem is that the .generate() function throws a ValueError. So this is meant to ensure that cached images
    are available for the app to call up.

    :param sender:
    :param instance: instance of Photo that was just saved
    :param kwargs:
    :return: None
    """
    image_sizes = ('image_blurred', 'image_medium', 'image_small', 'image_small_2')

    for image in image_sizes:
        try:
            img = getattr(instance, image)
            img.generate()
        except ValueError:
            pass
