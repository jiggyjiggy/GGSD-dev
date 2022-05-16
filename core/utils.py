from enum import Enum

import functools, time
from django.db   import connection, reset_queries


import jwt, json

from my_settings import SECRET_KEY, ALGORITHM
from django.http import JsonResponse

from users.models import User

def login_required(func):
    def wrapper(self, request, *args, **kwargs):
        try:
            access_token = request.headers.get('Authorization', None)
            payload      = jwt.decode(access_token, SECRET_KEY, algorithms = ALGORITHM)
            request.user = User.objects.get(id=payload['id'])
        
        except jwt.InvalidSignatureError:
            return JsonResponse({'message' : 'invalid_signature'}, status=401)
        
        except jwt.DecodeError:
            return JsonResponse({'message' : 'invalid_payload'}, status=401)
        
        except User.DoesNotExist:
            return JsonResponse({'message':'INVALID_USER'}, status = 400)
        
        return func(self, request, *args, **kwargs)
    return wrapper


def query_debugger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        number_of_start_queries = len(connection.queries)
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        number_of_end_queries = len(connection.queries)
        print(f"-------------------------------------------------------------------")
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {number_of_end_queries-number_of_start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        print(f"-------------------------------------------------------------------")
        return result
    return wrapper


class UserType(Enum):
    creator   = "생성함"
    applicant = "신청함"


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


