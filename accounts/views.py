import random
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CreateUserSerializer, LoginUserSerializer
from .models import User, PhoneOTP
from rest_framework import permissions
from knox.views import LoginView as KnoxLoginView
from django.contrib.auth import login


class ValidatePhone(APIView):
    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({
                    'status': False,
                    'message': 'Phone Number already exists'
                })
            else:
                code = send_otp(phone)
                print(phone, code)
                if code:
                    code = str(code)
                    print(code)
                    count = 0
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        count = old.first().count
                        old.first().count = count + 1
                        old.first().save()

                    else:
                        count = count + 1

                        PhoneOTP.objects.create(
                            phone=phone,
                            code=code,
                            count=count

                        )
                    if count > 7:
                        return Response({
                            'status': False,
                            'message': 'The maximum code limits have been reached. Please support our customer service or try another number'
                        })
                else:
                    return Response({
                        'status': 'False', 'message': "Code sending error. Please try after some time."
                    })

                return Response({
                    'status': True, 'message': 'Code has been sent successfully.'
                })
        else:
            return Response({
                'status': 'False', 'message': "I haven't received any phone number. Please do a POST request."
            })


def send_otp(phone):
    if phone:
        key = random.randint(999, 9999)
        return key
    else:
        return False


class ValidateCode(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        otp_sent = request.data.get('code', False)

        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                code = old.code
                if str(code) == str(otp_sent):
                    old.logged = True
                    old.save()

                    return Response({
                        'status': True,
                        'message': 'The code matches, please save the password'
                    })
                else:
                    return Response({
                        'status': False,
                        'message': 'Invalid code, please try again'
                    })
            else:
                return Response({
                    'status': False,
                    'message': 'The phone is not recognized. Please request a new code with this number'
                })
        else:
            return Response({
                'status': 'False',
                'message': 'Phone or Code was not recieved'
            })


class Register(APIView):
    def post(self, request, *args, **kwargs):
        phone = request.data.get('phone', False)
        password = request.data.get('password', False)

        if phone and password:
            phone = str(phone)
            user = User.objects.filter(phone__iexact=phone)
            if user.exists():
                return Response({'status': False,
                                 'message': 'The phone number is already associated with the account. Please try to forget your password'})
            else:
                old = PhoneOTP.objects.filter(phone__iexact=phone)
                if old.exists():
                    old = old.first()
                    if old.logged:
                        Temp_data = {'phone': phone, 'password': password}

                        serializer = CreateUserSerializer(data=Temp_data)
                        serializer.is_valid(raise_exception=True)
                        user = serializer.save()
                        user.save()

                        old.delete()
                        return Response({
                            'status': True,
                            'message': 'Congrts, user has been created successfully'
                        })

                    else:
                        return Response({
                            'status': False,
                            'message': 'Your code was not verified earlier. Please go back and verify code'
                        })
                else:
                    return Response({
                        'status': False,
                        'message': 'Phone number not recognised. Kindly request a new code with this number'
                    })
        else:
            return Response({
                'status': 'False',
                'message': 'Phone or password was not recieved'
            })

class Login(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        if user.last_login is None:
            user.first_login = True
            user.save()

        elif user.first_login:
            user.first_login = False
            user.save()

        login(request, user)
        return super().post(request, format=None)