from django.contrib import admin

# Register your models here.
from .models import *
admin.site.register(Progress)
admin.site.register(Staff)
admin.site.register(Submission)
admin.site.register(Document)
admin.site.register(Student)
admin.site.register(Project)
