from django.urls import path, include, re_path
from .views import ValidatePhone
from .views import ValidateCode
from .views import Register
from .views import Login
app_name = 'accounts'

urlpatterns = [
    re_path(r'^validate_phone/', ValidatePhone.as_view()),
    re_path(r'^validate_code/', ValidateCode.as_view()),
    re_path(r'^register/', Register.as_view()),
    re_path(r'^login/', Login.as_view()),
]

