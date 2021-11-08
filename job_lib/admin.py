from django.contrib import admin

from job_lib.models import Job, RegisteredImage

admin.site.register(Job)
admin.site.register(RegisteredImage)
