from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User Model with roles"""
    ROLE_CHOICES = [
        ('superuser', 'Superuser'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    organization = models.ForeignKey(
        'Organization', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Organization(models.Model):
    """Organization Model"""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Project(models.Model):
    """Project Model with password protection"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    password = models.CharField(
        max_length=128, 
        help_text="Password required to unlock this project"
    )
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='projects'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_projects'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.organization.name}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['name', 'organization']


class Assignment(models.Model):
    """Assignment Model - Links Staff to Projects"""
    staff = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'staff'},
        related_name='assignments'
    )
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='assignments'
    )
    assigned_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='assigned_projects',
        limit_choices_to={'role': 'admin'}
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_unlocked = models.BooleanField(default=False)
    unlocked_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(
        blank=True, 
        help_text="Additional notes for this assignment"
    )
    
    class Meta:
        unique_together = ['staff', 'project']
        ordering = ['-assigned_at']
    
    def unlock(self):
        """Unlock the assignment"""
        self.is_unlocked = True
        self.unlocked_at = timezone.now()
        self.save()
    
    def __str__(self):
        status = "Unlocked" if self.is_unlocked else "Locked"
        return f"{self.staff.username} - {self.project.name} ({status})"