from django.contrib import admin
from . import models

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'grade']
    list_editable = ['grade']
    list_filter = ['grade']