from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.hashers import make_password
from .models import User, Organization, Project, Assignment


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Custom User Admin"""
    list_display = (
        'username', 'email', 'role', 'organization', 
        'is_active', 'date_joined'
    )
    list_filter = ('role', 'organization', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'organization')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('role', 'organization')
        }),
    )


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization Admin"""
    list_display = (
        'name', 'created_at', 
        'get_projects_count', 'get_users_count'
    )
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_projects_count(self, obj):
        return obj.projects.count()
    get_projects_count.short_description = 'Projects'
    
    def get_users_count(self, obj):
        return obj.user_set.count()
    get_users_count.short_description = 'Users'


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """Project Admin with automatic password hashing"""
    list_display = (
        'name', 'organization', 'created_by', 
        'is_active', 'created_at', 'get_assignments_count'
    )
    list_filter = ('organization', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'name', 'description', 'organization', 
                'created_by', 'is_active'
            )
        }),
        ('Security', {
            'fields': ('password',),
            'description': 'Password will be automatically hashed when saved'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to hash password if it's not already hashed"""
        if 'password' in form.changed_data:
            if not obj.password.startswith('pbkdf2_'):
                obj.password = make_password(obj.password)
        
        if not change and not obj.created_by_id:
            obj.created_by = request.user
        
        super().save_model(request, obj, form, change)
    
    def get_assignments_count(self, obj):
        return obj.assignments.count()
    get_assignments_count.short_description = 'Assignments'


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    """Assignment Admin"""
    list_display = (
        'staff', 'project', 'assigned_by', 
        'is_unlocked', 'assigned_at', 'unlocked_at'
    )
    list_filter = ('is_unlocked', 'assigned_at', 'project__organization')
    search_fields = (
        'staff__username', 'project__name', 'assigned_by__username'
    )
    readonly_fields = ('assigned_at', 'unlocked_at')
    
    fieldsets = (
        ('Assignment Details', {
            'fields': ('staff', 'project', 'assigned_by', 'notes')
        }),
        ('Status', {
            'fields': ('is_unlocked', 'assigned_at', 'unlocked_at')
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'staff', 'project', 'assigned_by', 'project__organization'
        )


admin.site.site_header = "Project Management System"
admin.site.site_title = "PMS Admin"
admin.site.index_title = "Welcome to Project Management System Admin"