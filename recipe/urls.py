from django.urls import path
from . import views
app_name='recipe'
urlpatterns=[
    path('',views.HomePage.as_view(),name='home'),
]
