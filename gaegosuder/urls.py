from django.urls import path, include

urlpatterns = [
    path("projects", include("projects.urls")),
    path("commons", include("commons.urls"))
]
