from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User, Organization, Project, Assignment


class UserSerializer(serializers.ModelSerializer):
    """User Serializer"""
    organization_name = serializers.CharField(
        source='organization.name', 
        read_only=True
    )
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'role', 'organization', 'organization_name', 'is_active', 
            'date_joined', 'password'
        ]
    
    def create(self, validated_data):
        """Hash password before saving"""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class OrganizationSerializer(serializers.ModelSerializer):
    """Organization Serializer"""
    projects_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'created_at', 'projects_count', 'users_count']
    
    def get_projects_count(self, obj):
        return obj.projects.count()
    
    def get_users_count(self, obj):
        return obj.user_set.count()


class ProjectSerializer(serializers.ModelSerializer):
    """Project Serializer"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    assignments_count = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'organization', 'organization_name', 
            'created_by', 'created_by_username', 'is_active', 'created_at', 
            'assignments_count', 'password'
        ]
    
    def get_assignments_count(self, obj):
        return obj.assignments.count()
    
    def create(self, validated_data):
        """Hash project password before saving"""
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class ProjectDetailSerializer(ProjectSerializer):
    """Detailed Project Serializer"""
    organization = OrganizationSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)


class AssignmentSerializer(serializers.ModelSerializer):
    """Assignment Serializer"""
    staff_username = serializers.CharField(source='staff.username', read_only=True)
    staff_email = serializers.CharField(source='staff.email', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    organization_name = serializers.CharField(source='project.organization.name', read_only=True)
    assigned_by_username = serializers.CharField(source='assigned_by.username', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'staff', 'staff_username', 'staff_email', 'project', 'project_name', 
            'organization_name', 'assigned_by', 'assigned_by_username', 'assigned_at', 
            'is_unlocked', 'unlocked_at', 'notes'
        ]
        read_only_fields = ['assigned_at', 'unlocked_at', 'is_unlocked']


class AssignmentDetailSerializer(AssignmentSerializer):
    """Detailed Assignment Serializer"""
    staff = UserSerializer(read_only=True)
    project = ProjectDetailSerializer(read_only=True)
    assigned_by = UserSerializer(read_only=True)


class LoginSerializer(serializers.Serializer):
    """Login Serializer"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class AssignProjectSerializer(serializers.Serializer):
    """Assign Project Serializer"""
    staff_id = serializers.IntegerField()
    project_id = serializers.IntegerField()
    project_password = serializers.CharField(write_only=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class UnlockProjectSerializer(serializers.Serializer):
    """Unlock Project Serializer"""
    assignment_id = serializers.IntegerField()
    project_password = serializers.CharField(write_only=True)