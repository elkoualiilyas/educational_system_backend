from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bawabati_app.models import UserProfile

class Command(BaseCommand):
    help = 'Sets up the admin user profile with admin role'

    def handle(self, *args, **kwargs):
        try:
            admin_user = User.objects.get(username='admin')
            admin_profile = UserProfile.objects.get(user=admin_user)
            admin_profile.role = 'admin'
            admin_profile.save()
            self.stdout.write(self.style.SUCCESS('Successfully set up admin profile'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user does not exist'))
        except UserProfile.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin profile does not exist')) 