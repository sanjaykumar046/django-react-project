# verify_setup.py - Run this to verify your Django setup
# Place this file in your backend folder and run: python verify_setup.py

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password, make_password
from core.models import User, Organization, Project

def check_database():
    print("=" * 50)
    print("DATABASE VERIFICATION")
    print("=" * 50)
    
    # Check if tables exist
    try:
        user_count = User.objects.count()
        org_count = Organization.objects.count()
        project_count = Project.objects.count()
        
        print(f"✅ Database connected successfully")
        print(f"   Users: {user_count}")
        print(f"   Organizations: {org_count}")  
        print(f"   Projects: {project_count}")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_admin_user():
    print("\n" + "=" * 50)
    print("ADMIN USER VERIFICATION")
    print("=" * 50)
    
    try:
        admin = User.objects.filter(username='admin').first()
        if not admin:
            print("❌ Admin user not found")
            print("   Run: python manage.py createsuperuser")
            return False
            
        print(f"✅ Admin user found: {admin.username}")
        print(f"   Email: {admin.email}")
        print(f"   Role: {admin.role}")
        print(f"   Organization: {admin.organization}")
        print(f"   Is Active: {admin.is_active}")
        print(f"   Is Staff: {admin.is_staff}")
        
        # Test password
        if check_password('admin123', admin.password):
            print("✅ Password 'admin123' is correct")
        else:
            print("❌ Password 'admin123' is incorrect")
            print("   Current password hash:", admin.password[:50] + "...")
        
        # Test Django authenticate
        auth_user = authenticate(username='admin', password='admin123')
        if auth_user:
            print("✅ Django authenticate() works")
        else:
            print("❌ Django authenticate() failed")
            
        return True
    except Exception as e:
        print(f"❌ Admin user error: {e}")
        return False

def create_test_data():
    print("\n" + "=" * 50)
    print("CREATING TEST DATA")
    print("=" * 50)
    
    try:
        # Create organization
        org, created = Organization.objects.get_or_create(
            name="Tech Corp",
            defaults={'description': "Test Organization"}
        )
        print(f"{'✅ Created' if created else '✅ Found'} organization: {org.name}")
        
        # Update admin user
        admin = User.objects.filter(username='admin').first()
        if admin:
            admin.role = 'admin'
            admin.organization = org
            admin.is_active = True
            admin.save()
            print(f"✅ Updated admin user with organization")
        
        # Create staff user
        staff, created = User.objects.get_or_create(
            username='staff1',
            defaults={
                'email': 'staff1@example.com',
                'password': make_password('staff123'),
                'role': 'staff',
                'organization': org,
                'is_active': True
            }
        )
        print(f"{'✅ Created' if created else '✅ Found'} staff user: {staff.username}")
        
        # Create test project
        if admin:
            project, created = Project.objects.get_or_create(
                name="Test Project",
                organization=org,
                defaults={
                    'description': "Test project for authentication",
                    'password': make_password('project123'),
                    'created_by': admin,
                    'is_active': True
                }
            )
            print(f"{'✅ Created' if created else '✅ Found'} project: {project.name}")
        
        return True
    except Exception as e:
        print(f"❌ Test data creation error: {e}")
        return False

def test_authentication():
    print("\n" + "=" * 50)
    print("AUTHENTICATION TEST")
    print("=" * 50)
    
    try:
        # Test admin login
        admin_auth = authenticate(username='admin', password='admin123')
        if admin_auth:
            print("✅ Admin authentication successful")
            print(f"   User: {admin_auth.username}")
            print(f"   Role: {admin_auth.role}")
        else:
            print("❌ Admin authentication failed")
            
        # Test staff login  
        staff_auth = authenticate(username='staff1', password='staff123')
        if staff_auth:
            print("✅ Staff authentication successful")
            print(f"   User: {staff_auth.username}")
            print(f"   Role: {staff_auth.role}")
        else:
            print("❌ Staff authentication failed")
            
        return admin_auth is not None
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

def main():
    print("🔍 Django Setup Verification")
    print("This will check your database, users, and authentication")
    
    if not check_database():
        print("\n❌ Database setup failed - run migrations first:")
        print("   python manage.py makemigrations")
        print("   python manage.py migrate")
        return
    
    if not check_admin_user():
        print("\n⚠️ Admin user issues found - creating/fixing...")
        create_test_data()
    
    create_test_data()  # Ensure test data exists
    
    if test_authentication():
        print("\n🎉 SETUP VERIFICATION COMPLETE!")
        print("\nYou can now test login with:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\nOr staff login with:")
        print("   Username: staff1") 
        print("   Password: staff123")
        print("\nNext step: Run test_login.py to test the API endpoint")
    else:
        print("\n❌ SETUP INCOMPLETE - Please check the errors above")

if __name__ == "__main__":
    main()