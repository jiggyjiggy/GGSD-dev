import json, enum

from django.http      import JsonResponse
from django.shortcuts import render
from django.views     import View
from django.db        import transaction

from users.models    import User, Portfolio
from projects.models import Project
from applies.models  import ProjectApply,ProjectApplyStack

from core.utils import login_required

class ApplyStatusType(enum.Enum):
    APPLICANT = 1
    CREATOR   = 2

class UserApplyView(View):
    @login_required
    def post(self, request, project_id):
        data = json.loads(request.body)
        
        try:
            user_id           = request.user
            position_id       = data['position_id']
            technology_stacks = data['technology_stacks']
            github_repo_url   = data['github_repo_url']
            is_private        = data['is_private']
            
            
            with transaction.atomic():
                project_apply=ProjectApply.objects.create(
                    user_id = user_id,
                    position_id = position_id,
                    project_apply_status_id = ApplyStatusType.APPLICANT.value,
                    project_id = project_id
                )
                
                [ProjectApplyStack.objects.create(
                    project_apply_id = project_apply.id,
                    technology_stack_id = technology_stack
                ) for technology_stack in technology_stacks]
                
                user=User.objects.get(id=user_id)
                user.portfolio = Portfolio.objects.create(is_private=is_private)
                user.portfolio.is_private=is_private 
                user.portfolio.save()
                           
                user.github_repo_url=github_repo_url
                user.save()

            return JsonResponse({'MESSAGE' : 'SUCCESS'}, status=200)
        
        except KeyError:
                return JsonResponse({"message" : "KEY_ERROR"}, status = 400)      