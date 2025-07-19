from django.contrib import admin
from . import models

@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'grade']
    list_editable = ['grade']
    list_filter = ['grade']
    
@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['caption', 'description', 'likes']
    list_editable = ['likes']