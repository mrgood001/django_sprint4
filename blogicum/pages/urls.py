from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('rules/', views.RulesPage.as_view(), name='rules'),
    path('about/', views.AboutPage.as_view(), name='about'),
]
