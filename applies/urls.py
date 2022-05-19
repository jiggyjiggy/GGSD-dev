from django.urls import path

from applies.views import UserApplyView

urlpatterns = [
    path('/<int:project_id>', UserApplyView.as_view()),
    path('/apply', UserApplyView.as_view())
]