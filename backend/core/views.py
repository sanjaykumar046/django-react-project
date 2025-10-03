from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Project, Assignment
from .serializers import (
    UserSerializer, ProjectSerializer, ProjectDetailSerializer,
    AssignmentDetailSerializer, LoginSerializer,
    AssignProjectSerializer, UnlockProjectSerializer
)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    """API Root endpoint"""
    return Response({
        'message': 'Project Management System API',
        'version': '1.0',
        'user': request.user.username if request.user.is_authenticated else 'Anonymous',
        'endpoints': {
            'login': '/api/login/',
            'staff': '/api/staff/',
            'projects': '/api/projects/',
            'assignments': '/api/assignments/',
            'my_assignments': '/api/my-assignments/',
            'assign_project': '/api/assign-project/',
            'unlock_project': '/api/unlock-project/',
        }
    })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Login endpoint - Returns JWT tokens"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'error': 'Account is inactive'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)
    
    return Response({
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': UserSerializer(user).data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def staff_list(request):
    """Get all staff members"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can view staff'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    staff = User.objects.filter(
        role='staff',
        is_active=True
    ).order_by('username')

    return Response(UserSerializer(staff, many=True).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def projects_list(request):
    """Get all projects"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can view projects'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    projects = Project.objects.filter(
        is_active=True
    ).select_related('organization', 'created_by').order_by('-created_at')

    return Response(ProjectDetailSerializer(projects, many=True).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def assignments_list(request):
    """Get all assignments"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can view assignments'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    assignments = Assignment.objects.all().select_related(
        'staff', 'project', 'assigned_by', 'project__organization'
    ).order_by('-assigned_at')

    return Response(AssignmentDetailSerializer(assignments, many=True).data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_assignments(request):
    """Get current user's assignments (for staff)"""
    if request.user.role != 'staff':
        return Response(
            {'error': 'Only staff can view their assignments'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    assignments = Assignment.objects.filter(
        staff=request.user
    ).select_related(
        'project', 'assigned_by', 'project__organization'
    ).order_by('-assigned_at')

    return Response(AssignmentDetailSerializer(assignments, many=True).data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_project(request):
    """Assign project to staff member"""
    if request.user.role != 'admin':
        return Response(
            {'error': 'Only admins can assign projects'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = AssignProjectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    staff_id = serializer.validated_data['staff_id']
    project_id = serializer.validated_data['project_id']
    project_password = serializer.validated_data['project_password']
    notes = serializer.validated_data.get('notes', '')

    try:
        staff = User.objects.get(id=staff_id, role='staff')
        project = Project.objects.get(id=project_id, is_active=True)
    except User.DoesNotExist:
        return Response(
            {'error': 'Staff member not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Project.DoesNotExist:
        return Response(
            {'error': 'Project not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if not check_password(project_password, project.password):
        return Response(
            {'error': 'Invalid project password'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if Assignment.objects.filter(staff=staff, project=project).exists():
        return Response(
            {'error': 'Project already assigned to this staff member'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    assignment = Assignment.objects.create(
        staff=staff,
        project=project,
        assigned_by=request.user,
        notes=notes
    )

    return Response(
        {
            'message': 'Project assigned successfully',
            'assignment': AssignmentDetailSerializer(assignment).data
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlock_project(request):
    """Unlock project for staff"""
    if request.user.role != 'staff':
        return Response(
            {'error': 'Only staff can unlock projects'}, 
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = UnlockProjectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    assignment_id = serializer.validated_data['assignment_id']
    project_password = serializer.validated_data['project_password']

    try:
        assignment = Assignment.objects.select_related('project').get(
            id=assignment_id,
            staff=request.user
        )
    except Assignment.DoesNotExist:
        return Response(
            {'error': 'Assignment not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    if not check_password(project_password, assignment.project.password):
        return Response(
            {'error': 'Invalid project password'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if assignment.is_unlocked:
        return Response(
            {
                'message': 'Project is already unlocked',
                'assignment': AssignmentDetailSerializer(assignment).data
            }, 
            status=status.HTTP_200_OK
        )

    assignment.unlock()
    
    return Response(
        {
            'message': 'Project unlocked successfully',
            'assignment': AssignmentDetailSerializer(assignment).data
        },
        status=status.HTTP_200_OK
    )