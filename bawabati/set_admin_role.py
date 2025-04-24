import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bawabati.settings')
django.setup()

from django.contrib.auth.models import User
from bawabati_app.models import UserProfile

def set_admin_role(username):
    try:
        user = User.objects.get(username=username)
        profile = UserProfile.objects.get(user=user)
        profile.role = 'admin'
        profile.save()
        print(f"Successfully set {username}'s role to admin")
    except User.DoesNotExist:
        print(f"User {username} does not exist")
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user, role='admin')
        print(f"Created new profile for {username} with admin role")

if __name__ == '__main__':
    set_admin_role('badr1') 