from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('predict/', views.predict_manual, name='predict_manual'),
    path('upload/', views.predict_csv, name='predict_csv'),
    path('info/', views.model_info, name='model_info'),
]