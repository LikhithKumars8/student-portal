# Import any package related classes and functions
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
import json
import datetime
from django.views.decorators.csrf import csrf_protect
from django.db.models import F

# Import models
from .models import Student, Subject

# Import custom functions
from core.api_logger import api_logging

# app/views.py
from core.response_format import message_response
from core.constants import LINE_BREAK, ERROR_MESSAGE, INVALID_HTTP_REQUEST
from .validations import StudentValidator
from core.response_messages import deleted_successfully, an_error_occurred
from django.http import JsonResponse
from .helpers import admin_verification
from core.api_permissions import has_permission
from django.urls import reverse

# Views
@csrf_protect
def login_view(request):
    from core.encryption import jwt_admin_payload_handler, jwt_encode_handler
    log_data = [f"info|| {datetime.datetime.now()}: Login view"]

    try:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = admin_verification(password, username)
            if user:
                login(request, user)
                jwt_payload = jwt_admin_payload_handler(user)
                token = jwt_encode_handler(jwt_payload)
                response = redirect('home')
                response.set_cookie('authToken', token, httponly=True, secure=True)
                return response
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        return render(request, 'login.html')

    except Exception as e:
        log_data.append(f"error|| {datetime.datetime.now()}: {str(e)}")
        log_data.append(f"info || {LINE_BREAK}")
        api_logging(log_data)
        return JsonResponse({
            'message': an_error_occurred,
            'error_code': 'stp_400',
            'details': str(e)
        }, status=500)

@csrf_protect
def home_view(request):
    if not has_permission(request):
        return redirect(reverse('login'))
    
    log_data = [f"info|| {datetime.datetime.now()}: Home view"]

    try:
        students = Student.objects.filter(is_active=True)
        return render(request, 'home.html', {'students': students})
    except Exception as e:
        log_data.append(f"error|| {datetime.datetime.now()}: {str(e)}")
        log_data.append(f"info || {LINE_BREAK}")
        api_logging(log_data)
        return JsonResponse({
            'message': an_error_occurred,
            'error_code': 'stp_01',
            'details': str(e)
        }, status=500)

@csrf_protect
def get_subjects(request):
    if not has_permission(request):
        return redirect(reverse('login'))
    if request.method == "GET":
        subjects = Subject.objects.values('id', 'name')
        return JsonResponse(list(subjects), safe=False)

@csrf_protect
def add_student(request):
    if not has_permission(request):
        return redirect(reverse('login'))
    log_data = [f"info|| {datetime.datetime.now()}: add student"]

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Validate the incoming data
            student_data = StudentValidator().validate(data)
            student_data['subject'] = Subject.objects.filter(id=student_data.get('subject'), is_active=True).first()
            if not student_data['subject']:
                raise ValueError("The Subject id passed is wrong!, please check the code")
            student_instance= Student.objects.filter(
                name=student_data['name'], subject_id=student_data['subject'], is_active=True
            ).first()
            if student_instance:
                student_instance.marks += student_data['marks']
                student_instance.save()
            else:
                Student.objects.create(**student_data)
            return JsonResponse({'message': 'Student added successfully'}, status=200)
        except Exception as e:
            log_data.append(f"info || {LINE_BREAK}")
            api_logging(log_data)
            return JsonResponse({
                'message': an_error_occurred,
                'error_code': 'stp_01',
                'details': str(e)
            }, status=500)
    else:
        return JsonResponse(message_response(ERROR_MESSAGE, "stp_400", INVALID_HTTP_REQUEST), status=500)

@csrf_protect
def edit_student(request):
    if not has_permission(request):
        return redirect(reverse('login'))
    log_data = [f"info|| {datetime.datetime.now()}: edit student"]

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Check the id is valid
            student_instance = Student.objects.filter(
                id=data.get('id'), is_active=True).first()
            if not student_instance:
                raise ValueError("Invalid student id!")

            # Validate the incoming data
            student_data = StudentValidator().validate(data)

            # Validate the subject data
            student_data['subject'] = Subject.objects.filter(
                id=student_data.get('subject'), is_active=True).first()
            if not student_data['subject']:
                raise ValueError("The Subject id passed is wrong!, please check the code")

            # Save all the data
            student_instance.name = student_data['name']
            student_instance.subject = student_data['subject']
            student_instance.marks = student_data['marks']
            student_instance.save()
            return JsonResponse({'message': 'Student update successfully'}, status=200)
        except Exception as e:
            log_data.append(f"info || {LINE_BREAK}")
            api_logging(log_data)
            return JsonResponse({
                'message': an_error_occurred,
                'error_code': 'stp_01',
                'details': str(e)
            }, status=500)
    else:
        return JsonResponse(message_response(ERROR_MESSAGE, "stp_400", INVALID_HTTP_REQUEST), status=500)

@csrf_protect
def delete_student(request, student_id):
    if not has_permission(request):
        return redirect(reverse('login'))
    log_data = [f"info|| {datetime.datetime.now()}: delete student"]

    if request.method == 'DELETE':
        try:
            student = get_object_or_404(Student, id=student_id)
            student.is_active = False
            student.save()
            return JsonResponse(message_response(deleted_successfully,"stp_200", {'status': 'success'}))
        except Exception as e:
            log_data.append(f"info || {LINE_BREAK}")
            api_logging(log_data)
            return JsonResponse(message_response(ERROR_MESSAGE, "stp_400", e), status=500)
    else:
        return JsonResponse(message_response(ERROR_MESSAGE, "stp_400", INVALID_HTTP_REQUEST), status=500)

@csrf_protect
def get_student_data(request):
    log_data = [f"info|| {datetime.datetime.now()}: student detail"]

    if request.method == 'GET':
        try:
            student_id = request.GET.get('id')

            # Check the id is valid
            student_queryset = Student.objects.filter(
                id=student_id, is_active=True)
            if not student_queryset:
                raise ValueError("Invalid student id!")
            student_data = student_queryset.values('name', 'marks').annotate(
                subject_name=F('subject__name'),
                subject_id=F('subject_id')
            )
            return JsonResponse(message_response(student_data[0],"stp_200", {'status': 'success'}))
        except Exception as e:
            log_data.append(f"info || {LINE_BREAK}")
            api_logging(log_data)
            return JsonResponse(message_response(ERROR_MESSAGE, "stp_400", e), status=500)
    else:
        return JsonResponse(message_response(ERROR_MESSAGE, "stp_400", INVALID_HTTP_REQUEST), status=500)
    
@csrf_protect
def logout_user(request):
    # Check if user has permission
    if not has_permission(request):
        return redirect(reverse('login'))  # Redirect if permission is denied
    
    if request.method == 'POST':
        # Create the response object
        response = JsonResponse(
            message_response("Logged out successfully", "stp_200", "User logged out."),
            status=200
        )
        
        response.delete_cookie('authToken', path='/')
        response.delete_cookie('csrftoken', path='/')

        # Clear server-side session data
        request.session.flush()

        return response
    else:
        # Handle invalid HTTP methods
        return JsonResponse(
            message_response(ERROR_MESSAGE, "stp_400", INVALID_HTTP_REQUEST),
            status=400
        )