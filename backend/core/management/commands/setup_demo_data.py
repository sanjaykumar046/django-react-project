from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Organization, Project

User = get_user_model()

class Command(BaseCommand):
    help = 'Set up demo data for the project management system'
    
    def handle(self, *args, **options):
        # Create organizations
        tech_corp, _ = Organization.objects.get_or_create(
            name='Tech Corp',
            defaults={'description': 'Technology company focused on web solutions'}
        )
        
        startup_xyz, _ = Organization.objects.get_or_create(
            name='StartupXYZ',
            defaults={'description': 'Innovative startup creating mobile solutions'}
        )
        
        # Admin
        admin1, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@techcorp.com',
                'role': 'admin',
                'organization': tech_corp,
                'is_staff': True,
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin1.set_password('password')
            admin1.save()
            self.stdout.write(f'Created admin: admin/password')
        
        # Staff 1
        staff1, created = User.objects.get_or_create(
            username='john_doe',
            defaults={
                'email': 'john@techcorp.com',
                'role': 'staff',
                'organization': tech_corp,
                'first_name': 'John',
                'last_name': 'Doe'
            }
        )
        if created:
            staff1.set_password('password')
            staff1.save()
            self.stdout.write(f'Created staff: john_doe/password')
        
        # Staff 2
        staff2, created = User.objects.get_or_create(
            username='jane_smith',
            defaults={
                'email': 'jane@techcorp.com',
                'role': 'staff',
                'organization': tech_corp,
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
        )
        if created:
            staff2.set_password('password')
            staff2.save()
            self.stdout.write(f'Created staff: jane_smith/password')
        
        # Project 1
        project1, created = Project.objects.get_or_create(
            name='Website Redesign',
            organization=tech_corp,
            defaults={
                'description': 'Overhaul company website with modern design',
                'password': 'project123',
                'created_by': admin1
            }
        )
        if created:
            self.stdout.write(f'Created project: {project1.name} (password: project123)')
        
        # Project 2
        project2, created = Project.objects.get_or_create(
            name='Mobile App Development',
            organization=tech_corp,
            defaults={
                'description': 'Develop iOS & Android apps',
                'password': 'mobile456',
                'created_by': admin1
            }
        )
        if created:
            self.stdout.write(f'Created project: {project2.name} (password: mobile456)')
        
        self.stdout.write(self.style.SUCCESS('Demo data setup completed!'))
