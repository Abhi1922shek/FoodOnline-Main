from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, UserProfile

# Receiver Function   
# Connecting receiver to sender - method1 (recommended)
@receiver(post_save, sender=User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        try:
            profile = UserProfile.objects.get(user=instance)
            profile.save()
        except:
            # Create the user profile if not exists
            UserProfile.objects.create(user=instance)

# Connecting receiver to sender - method2
# post_save.connect(post_save_create_profile_receiver, sender=User)

# # Pre Save signal
# @receiver(pre_save, sender=User)
# def pre_save_profile_receiver(sender, instance, **kwargs):
#     if instance.username == "":
#         raise ValueError("username is required")