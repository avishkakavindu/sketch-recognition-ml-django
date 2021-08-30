from django.contrib import admin
from django.urls import path, include
from doodle_api.views import *
from doodle_api.api_views import *

urlpatterns = [
    path('', HomeView.as_view(), name="index"),
    path('predict/', PredictAPIView.as_view(), name='predict    '),
]
