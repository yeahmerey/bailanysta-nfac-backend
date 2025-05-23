import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import UserProfile

class Command(BaseCommand):
    help = 'Create UserProfile for existing users who don\'t have one'

    def handle(self, *args, **options):
        os.makedirs('api/management', exist_ok=True)
        os.makedirs('api/management/commands', exist_ok=True)
        
        for path in ['api/management/__init__.py', 'api/management/commands/__init__.py']:
            if not os.path.exists(path):
                with open(path, 'w') as f:
                    f.write('')
        
        users_without_profile = User.objects.filter(profile__isnull=True)
        created_count = 0
        
        for user in users_without_profile:
            UserProfile.objects.create(user=user, bio='', avatar=None)
            created_count += 1
            self.stdout.write(f'Created profile for user: {user.username}')
        
        if created_count == 0:
            self.stdout.write(
                self.style.SUCCESS('All users already have profiles!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} profiles!')
            )