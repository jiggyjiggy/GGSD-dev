# from hashlib import new
# import json, jwt, requests, enum

# from tkinter import image_types
# from commons.models import Image

# from django.http  import JsonResponse
# from django.db    import transaction
# from django.conf  import settings
# from django.views import View

# from users.models   import User
# from commons.models import Image

# from core.utils import login_required


# class ImageType(enum.Enum):
#     BANNER            = 1
#     PROJECT_THUMBNAIL = 2
#     PROJECT_DETAIL    = 3
#     STACK             = 4
#     USER_PROFILE      = 5

# class KakaoLoginView(View):        
#     def get(self, request):        
#         try:
#             kakao_token   = request.headers.get('Authorization', None)
#             requests_url  = "https://kapi.kakao.com/v2/user/me"
#             user_account  = requests.get(requests_url, headers = {'Authorization': f'Bearer {kakao_token}'}).json()
            
#             kakao_id  = user_account['id']
#             email     = user_account['kakao_account']['email']
#             name      = user_account['kakao_account']['profile']['nickname']
#             image_url = user_account['kakao_account']['profile']['profile_image_url']
            
#             if User.objects.filter(email = email):
#                 user         = User.objects.get(email = email)
#                 access_token = jwt.encode({"id" : user.id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
                
#                 return JsonResponse({'message' : 'SUCCESS', 'access_token' : access_token, 'user_id':user.id}, status=200)
            
#             with transaction.atomic():
                
#                 new_user = User.objects.create(
#                     user_id  = user.id,
#                     kakao_id = kakao_id,
#                     email    = email,
#                     name     = name
#                 )
#                 new_user_image = Image.objects.create(
#                     user_id       = new_user.id,
#                     image_url     = image_url,
#                     image_type_id = ImageType.USER_PROFILE.value
#                 )
            
#             access_token = jwt.encode({"id" : new_user.id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
            
#             result = {
#                 'user_id'      : new_user.id,
#                 'kakao_id'     : new_user.kakao_id,
#                 'name'         : new_user.name,
#                 'profile_url'  : new_user_image.image_url,
#                 'access_token' : access_token,
#                 "batch"        : new_user.batch
#             }
            
#             return JsonResponse({'message' : 'SUCCESS',
#                                  'result'  : result
#                                 }, status=200)
            
#         except KeyError:
#             return JsonResponse({"message" : "KEY_ERROR"}, status = 400)
    
#     # @login_required    
#     def patch(self, request):
#         data = json.loads(request.body)
        
#         # user_id = request.user.id
#         user_id=1
        
#         try:
#             name     = data['name']
#             batch    = data['batch']
#             position_id = data['position_id']
            
#             user = User.objects.get(id=user_id)
            
#             user.id = user_id
#             user.name        = name
#             user.batch       = batch
#             user.position_id = position_id
            
#             user.save()
            
#             result = {
#                 'name'        : user.name,
#                 'batch'       : user.batch,
#                 'position_id' : user.position_id
#             }
            
            
#             return JsonResponse({'message':'success',
#                                  'result':result},
#                                 status=200)
            
#         except KeyError:
#             return JsonResponse({"message" : "KEY_ERROR"}, status = 400)

       
# class UserDetailView(View):
#     @login_required
#     def get(self, request, user_id):
#         try:
#             # user_id =3
#             user_id = request.user.id
            
#             user = User.objects.get(id=user_id)
            
#             result = [{
#                 "batch"      : user.batch,
#                 "name"       : user.name,
#                 "email"      : user.email,
#                 "github_url" : user.github_repo_url,
#                 "profile"    : user.image_set.get(image_type_id=ImageType.USER_PROFILE.value).image_url if user.image_set.exists() else None,
#                 "stacks"     : [{
#                     "id"    : stack.id,
#                     "title" : stack.title,
#                     } for stack in user.stack.all()]
#             }]
            
#             return JsonResponse({'result' : result}, status=200)
#         except KeyError:
#             return JsonResponse({"message" : "KEY_ERROR"}, status = 400)








###

import json, jwt, requests, enum

from django.http  import JsonResponse
from django.db    import transaction
from django.conf  import settings
from django.views import View

from users.models   import Portfolio, User, UserStack
from core.utils     import login_required 
from commons.models import Image
from users.models   import User, UserStack


from core.utils import login_required


class ImageType(enum.Enum):
    BANNER            = 1
    PROJECT_THUMBNAIL = 2
    PROJECT_DETAIL    = 3
    STACK             = 4
    USER_PROFILE      = 5


class KakaoLoginView(View):        
    def get(self, request):        
        try:
            kakao_token   = request.headers.get('Authorization', None)
            requests_url  = "https://kapi.kakao.com/v2/user/me"
            user_account  = requests.get(requests_url, headers = {'Authorization': f'Bearer {kakao_token}'}).json()
            
            kakao_id  = user_account['id']
            email     = user_account['kakao_account']['email']
            name      = user_account['kakao_account']['profile']['nickname']
            image_url = user_account['kakao_account']['profile']['profile_image_url']
            
            if User.objects.filter(email = email):
                user         = User.objects.get(email = email)
                access_token = jwt.encode({"id" : user.id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
                
                return JsonResponse({'MESSAGE' : 'SUCCESS', 'access_token' : access_token}, status=200)
            
            with transaction.atomic():
                
                new_user = User.objects.create(
                    kakao_id = kakao_id,
                    email    = email,
                    name     = name
                )
                new_user_image = Image.objects.create(
                    user_id       = new_user.id,
                    image_url     = image_url,
                    image_type_id = ImageType.USER_PROFILE.value
                )
            
            access_token = jwt.encode({"id" : new_user.id}, settings.SECRET_KEY, algorithm = settings.ALGORITHM)
            
            result = {
                'name'         : new_user.name,
                "batch"        : new_user.batch,
                'kakao_id'     : new_user.kakao_id,
                'profile_url'  : new_user_image.image_url,
                'access_token' : access_token
            }
            
            return JsonResponse({"MESSAGE" : 'SUCCESS',
                                 "RESULT"  : result}, status=200)
            
        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status = 400)
        
        
    @login_required    
    def patch(self, request):
        data = json.loads(request.body)
        
        user_id = request.user.id
        
        try:
            name        = data['name']
            batch       = data['batch']
            position_id = data['position_id']
            
            user = User.objects.get(id=user_id)
            
            user.name        = name
            user.batch       = batch
            user.position_id = position_id
            
            user.save()
            
            result = {
                'name'        : user.name,
                'batch'       : user.batch,
                'position_id' : user.position_id
            }
            
            return JsonResponse({'MESSAGE':'SUCCESS',
                                 'RESULT':result}, status=200)
            
        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status = 400)

class UserDetailView(View):
    @login_required
    def get(self, request):
        try:
            user_id = request.user.id
        
            user = User.objects.get(id=user_id)
            
            result = [{
                "user_id"     : user.id,
                "batch"       : user.batch,
                "name"        : user.name,
                "email"       : user.email,
                "github_url"  : user.github_repo_url,
                "profile_url" : user.image_set.get(image_type_id=ImageType.USER_PROFILE.value).image_url if user.image_set.exists() else None,
                "portfolios": user.portfolio.file_url if user.portfolio else "",
                "stacks"     : [{
                    "id"     : stack.id,
                    "title"  : stack.title,
                    } for stack in user.stack.all()]
            }]
            return JsonResponse({'RESULT' : result}, status=200)
        
        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status = 400)
        
        
    @login_required    
    def patch(self, request):
        data = json.loads(request.body)
        
        user_id = request.user.id
        
        try:
            portfolio_file_url = data['portfolio_file_url']
            stack_ids          = data['stack']
            github_repo_url    = data['github_repo_url']
            
            user = User.objects.get(id=user_id)
            
            if not user.portfolio:
                new_portfolio=Portfolio.objects.create(
                    file_url=portfolio_file_url,
                    is_private=0
                )
                user.portfolio_id= new_portfolio.id   
                user.save()
            else:
                user.portfolio.file_url = portfolio_file_url 
                user.portfolio.is_private = 0
                user.portfolio.save()
            
            user.github_repo_url = github_repo_url
            user.save()
            
            UserStack.objects.filter(user_id=user_id).delete()
            
            [UserStack.objects.create(
                user_id=user_id,
                technology_stack_id=stack_id
            ) for stack_id in stack_ids ]
            
            
            return JsonResponse({'MESSAGE':'SUCCESS'
                                 },status=200)
            
        except KeyError:
            return JsonResponse({"MESSAGE" : "KEY_ERROR"}, status = 400)