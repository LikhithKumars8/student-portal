from django.contrib import admin
from .models import Student, Subject, StudentPortalAdmin

@admin.register(StudentPortalAdmin)
class StudentPortalAdminAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile_number', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'mobile_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'mobile_number', 'password', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(Subject) 
class SubjectAdmin(admin.ModelAdmin): 
    list_display = ('name', 'is_active', 'created_at', 'updated_at') 
    search_fields = ('name', 'is_active') 

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'marks')
    search_fields = ('name', 'subject')
