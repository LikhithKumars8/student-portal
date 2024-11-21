from django.db import models
from django.contrib.auth.hashers import check_password

class Subject(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subject'

    def __str__(self):
        return self.name

class Student(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks = models.IntegerField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: 
        db_table = 'studentportal_student'
        indexes = [ 
            models.Index(fields=['name', 'subject']),
        ]

    def __str__(self):
        return f"{self.name} - {self.subject}"

class StudentPortalAdmin(models.Model):
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=10, blank=True)
    password = models.CharField(max_length=200, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(blank=True, null=True)

    # Meta options
    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['email'])
        ]

        db_table = 'student_portal_admin'
        verbose_name_plural = 'admins'

    # String representation
    def __str__(self):
        return f"{self.name} - {self.email}"

    def check_password(self, raw_password):
        def setter(raw_password):
            self.set_password(raw_password)
            self._otp = None
            self.save(update_fields=["password"])
        return check_password(raw_password, self.otp, setter)
