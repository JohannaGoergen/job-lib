from django.urls import path, include
from rest_framework.routers import DefaultRouter

from job_lib import views


job_router = DefaultRouter(trailing_slash=False)
job_router.register("jobs", views.JobsViewSet, basename="jobs")

registered_images_router = DefaultRouter(trailing_slash=False)
registered_images_router.register(
    "registered_images", views.RegisteredImagesViewSet, basename="registered-images"
)


urlpatterns = [
    path("", include(job_router.urls)),
    path("", include(registered_images_router.urls)),
    path("job_status_updates", views.JobStatusChangesView.as_view()),
]
