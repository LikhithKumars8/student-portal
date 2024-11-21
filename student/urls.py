from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('subjects/', views.get_subjects, name='subjects'),
    path('add-student/', views.add_student, name='add_student'),
    path('edit-student/', views.edit_student, name='edit_student'),
    path('get-student-detail/', views.get_student_data, name='get-student-detail'),
    path('delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('logout/', views.logout_user, name='logout'),
]
