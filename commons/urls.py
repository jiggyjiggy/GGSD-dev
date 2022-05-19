from django.urls import path
from commons.views import FileView, MetaDataView # ,FiledownView

urlpatterns = [
    path('/file', FileView.as_view()),
    # path('/filedown', FiledownView.as_view()),
    path('/meta', MetaDataView.as_view())
]
