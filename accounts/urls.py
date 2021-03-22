from django.urls import path, include, re_path
from .views import ValidatePhoneSendCode
from .views import ValidateCode
from .views import Register
app_name = 'accounts'

urlpatterns = [
    re_path(r'^validate_phone/', ValidatePhoneSendCode.as_view()),
    re_path(r'^validate_code/', ValidateCode.as_view()),
    re_path(r'^register/', Register.as_view()),
]

