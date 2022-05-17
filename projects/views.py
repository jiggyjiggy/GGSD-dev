import json
import datetime
from datetime import timedelta
from unicodedata import category

from django.http      import JsonResponse
from django.views     import View
from django.db.models import Q, F, Case, When,ExpressionWrapper,DateTimeField, Prefetch
from django.db import transaction
from django_mysql.models import GroupConcat


from projects.models import *
from commons.models import *
from applies.models import *

from core.utils import get_client_ip
from core.utils       import UserType


from projects.models import Project, ProjectStack
from applies.models  import ProjectApply, ProjectApplyStack
from commons.models  import Image
from users.models import User


from core.storage import MyS3Client
from django.conf import settings

from core.utils import query_debugger


class ProjectsListView(View):
    @query_debugger
    def get(self, request):
        order_condition = request.GET.get("sort", "deadline")
        search          = request.GET.get("search", None)
        region_id       = request.GET.get("region_id", None)
        apply_status_id = request.GET.get("apply_status_id",None)
        start_recruit   = request.GET.get("start_recruit", None)
        end_recruit     = request.GET.get("end_recruit", None)
        category_ids_q  = request.GET.getlist("category_ids", None)
        stack_ids_q     = request.GET.getlist("stack_ids", None)
        offset          = int(request.GET.get("offset", 0))
        limit           = int(request.GET.get("limit", 10))

        THUMBNAIL="project_thumbnail"

        q = Q()

        page_title=None

        if search:
            q &= Q(title__icontains=search)\
                | Q(description__icontains=search)\
                | Q(region__district_name__icontains=search)\
                | Q(projectstack__technology_stack__title__icontains=search)
            page_title = f"{search}\"에 대한 검색결과"

        if region_id:
            q &= Q(region_id=region_id)

        if stack_ids_q:
            q &= Q(stack_ids__in=','.join(stack_ids_q))
            # q &= Q(projectstack__technology_stack_id__in=stack_ids_q)
            # for stack_id in stack_ids:
        #         q &= Q(projectstack__technology_stack_id=stack_id)
        #         print(q)

        if category_ids_q:
            q &= Q(project_categories_id__in=stack_ids_q)

        if apply_status_id:
            q &= Q(projectapply__project_apply_status_id=apply_status_id)\
                & Q(projectapply__user_id=2)
                # & Q(user_id=user_id)

        if start_recruit:
            q &= Q(start_recruit__gte=start_recruit)
        
        if end_recruit:
            q &= Q(end_recruit__lte=end_recruit)
            
        if order_condition=="deadline":
            q &= Q(end_recruit__lte=datetime.datetime.now()+datetime.timedelta(days=3))\
                & Q(end_recruit__gte=datetime.datetime.now())

        if order_condition=="recent_created":
            q &= Q(created_at__lte=datetime.datetime.now())\
                & Q(created_at__gte=datetime.datetime.now()-datetime.timedelta(days=3))

        order = {
            "recent_created": "-created_at",
            "deadline"      : "-end_recruit"
        }
        
        projects = Project.objects\
            .select_related("project_category")\
            .prefetch_related(
                Prefetch("image_set", queryset=Image.objects.filter(image_type__title=THUMBNAIL),to_attr="thumbnails"),
                Prefetch("projectstack_set", queryset=ProjectStack.objects.select_related("technology_stack"), to_attr="project_stacks"))\
            .annotate(stack_ids=GroupConcat("projectstack__technology_stack_id"))\
            .filter(q)\
            .order_by(order[order_condition])\
            [offset:offset + limit]



        print(q)



        # projects = Project.objects\
        #     .select_related("project_category")\
        #     .prefetch_related(
        #         Prefetch("image_set", queryset=Image.objects.filter(image_type__title=THUMBNAIL),to_attr="thumbnails"),
        #         Prefetch("projectstack_set", queryset=ProjectStack.objects.select_related("technology_stack"), to_attr="project_stacks"))\
        #     .filter(q)\
        #     .order_by(order[order_condition])\
        #     # [offset:offset + limit]
        # print(projects)

        results=[]

        for project in projects:
            thumbnail        = [thumbnail.image_url for thumbnail in project.thumbnails]
            project_stack_qs = [project_stack for project_stack in project.project_stacks]

            project_stacks =[{
                "id"   :project_stack.technology_stack.id,
                "title":project_stack.technology_stack.title,
                "color":project_stack.technology_stack.color
            } for project_stack in project_stack_qs]

            results.append({
                "today"      : datetime.date.today(),
                "end_recruit": project.end_recruit,
                "created_at" : project.created_at,
                "sort"       : order,
                "page_title" : page_title,
                "project_id" : project.id,
                "category"   : project.project_category.title,
                "title"      : project.title,
                "thumbnail"  : thumbnail,
                "stacks"     : project_stacks
            })
        return JsonResponse({"results": results}, status=200)


class ProjectEnrollmentView(View):
    def post(self, request):
        before_start=1

        # user_id = request.user
        user_id = 1

        data    = json.loads(request.body)

        title                     = data["title"]
        start_recruit             = data["start_recruit"]
        end_recruit               = data["end_recruit"]
        start_project             = data["start_project"]
        end_project               = data["end_project"]
        description               = data["description"]
        front_vacancy             = data["front_vacancy"]
        back_vacancy              = data["back_vacancy"]
        is_online                 = data.get("is_online",0)
        progress_status_id        = data.get("progress_status_id", before_start)
        project_category_id       = data["project_category_id"]
        region_id                 = data["region_id"]
        project_stacks_ids        = data["project_stacks_ids"]
        project_apply_position_id = data["project_apply_position_id"]
        apply_stacks_ids          = data.get("apply_stacks_ids",[1])
        image_url = data["image_url"]
        is_private = data["is_private"]
        # print(request.POST)
        # print(request.FILES)

        # file = request.FILES['project_thumbnail']
        # s3_client = MyS3Client(settings.AWS_S3_ACCESS_KEY_ID, settings.AWS_S3_SECRET_ACCESS_KEY, settings.AWS_STORAGE_BUCKET_NAME) 
        # uploaded_url = s3_client.upload(file)

        PROJECT_THUMBNAIL = 2
        CREATED           = 1

        with transaction.atomic():
            new_project = Project.objects.create(
                title                =title,
                start_recruit        =start_recruit,
                end_recruit          =end_recruit,
                start_project        =start_project,
                end_project          =end_project,
                description          =description,
                front_vacancy        =front_vacancy,
                back_vacancy         =back_vacancy,
                is_online            =is_online,
                project_category_id  =project_category_id,
                region_id            =region_id,
                progress_status_id   =progress_status_id,
            )

            [ProjectStack.objects.create(
                project_id         =new_project.id,
                technology_stack_id=project_stack_id
            ) for project_stack_id in project_stacks_ids]

            new_project_apply = ProjectApply.objects.create(
                project_id             =new_project.id,
                position_id            =project_apply_position_id,
                project_apply_status_id=CREATED,
                user_id                =user_id
            )

            [ProjectApplyStack.objects.create(
                project_apply_id   =new_project_apply.id,
                technology_stack_id=apply_stack_id
            ) for apply_stack_id in apply_stacks_ids]

            creator_portfolio = User.objects.get(id=user_id).portfolio
            creator_portfolio.is_private =is_private
            creator_portfolio.save()

            Image.objects.create(
                project_id   =new_project.id,
                # image_url    =uploaded_url,
                image_url = image_url,
                image_type_id=PROJECT_THUMBNAIL
            )
            results=[{
                "project" :{
                    "id": new_project.id
                }
            }]
        return JsonResponse({"MESSAGE": "PROJECT_CREATED", "results":results}, status=201)

    def get(self, request):
        user_id=1
        creator_portfolio = User.objects.get(id=user_id).portfolio

        results=[{
            "is_private": creator_portfolio.is_private
        }]
        return JsonResponse({"results": results}, status=200) 


class ProjectDetailView(View):     
    @query_debugger 
    # def get(self, request, project_id):
    #     project = Project.objects\
    #         .get(id=project_id)

    #     project_stacks = project.projectstack_set.all()

    #     creators = project.projectapply_set.filter(project_apply_status__type=UserType.creator.value)
    #     applicants = project.projectapply_set.filter(project_apply_status__type=UserType.applicant.value)

    #     # fixed_applicants = applicant.request_status_set.filter(type="수락됌") for applicant in applicants

    #     print(creators.values("position"))
    #     # print(fixed_applicants.values("position"))


        # results = [
        #     {
        #         "project": {
        #             "title"         : project.title,
        #             "front_vacancy" : project.front_vacancy,
        #             "back_vacancy"  : project.back_vacancy,
        #             # "fixed_front"   : project.fixed_front,
        #             # "fixed_back"    : project.fixed_back,
        #             "start_recruit" : project.start_recruit,
        #             "end_recruit"   : project.end_recruit,
        #             "start_project" : project.start_project,
        #             "end_project"   : project.end_project,
        #             "location"      : project.region.district_name if project.region else None,
        #             "is_online"     : project.is_online,
        #             "description"   : project.description,
        #             "project_stacks": [{
        #                     "stack_id": project_stack.technology_stack.id,
        #                     "title": project_stack.technology_stack.title,
        #                     "color": project_stack.technology_stack.color
        #                 } for project_stack in project_stacks],
        #             "creators" : [{
        #                 "name"     : creator.user.name,
        #                 "portfolio": None if creator.user.portfolio.is_private else creator.user.portfolio.file_url,
        #                 "githuburl": creator.user.github_repo_url
        #             } for creator in creators],
        #             "applicants" : [{
        #                 "name"     : applicant.user.name,
        #                 "githuburl": applicant.user.github_repo_url
        #             } for applicant in applicants]
        #         }
        #     }
        # ]
        # return JsonResponse({"results": results}, status=200)


        # class ProjectDetailView(View):
    def get(self, request, project_id):
        project = Project.objects\
            .select_related("region")\
            .prefetch_related(
                Prefetch("projectstack_set",
                        queryset=ProjectStack.objects.select_related("technology_stack"),
                        to_attr="project_stacks"),
                Prefetch("projectapply_set",
                        queryset=ProjectApply.objects.select_related("user", "user__portfolio").filter(project_apply_status__type=UserType.creator.value),
                        to_attr="creators_apply"),
                Prefetch("projectapply_set",
                        queryset=ProjectApply.objects.select_related("user").filter(project_apply_status__type=UserType.applicant.value),
                        to_attr="applicants_apply")
                )\
            .get(id=project_id)


        results = [
            {
                "project": {
                    "title"         : project.title,
                    "front_vacancy" : project.front_vacancy,
                    "back_vacancy"  : project.back_vacancy,
                    "start_recruit" : project.start_recruit,
                    "end_recruit"   : project.end_recruit,
                    "start_project" : project.start_project,
                    "end_project"   : project.end_project,
                    "region"        : project.region.district_name if project.region else None,
                    "is_online"     : project.is_online,
                    "description"   : project.description,
                    "project_stacks": [{
                        "stack_id": project_stack.technology_stack.id,
                        "title"   : project_stack.technology_stack.title,
                        "color"   : project_stack.technology_stack.color
                    } for project_stack in project.project_stacks],
                    "creators": [{
                        "id"        : creator_apply.user.id,
                        "name"      : creator_apply.user.name,
                        "github_url": creator_apply.user.github_repo_url,
                        "portfolio" : [{
                            "file_url"  : None if creator_apply.user.portfolio.is_private else creator_apply.user.portfolio.file_url,
                            "is_private": creator_apply.user.portfolio.is_private
                        }]
                    } for creator_apply in project.creators_apply],
                    "applicants": [{
                        "id"        : applicant_apply.user.id,
                        "name"      : applicant_apply.user.name,
                        "github_url": applicant_apply.user.github_repo_url
                    } for applicant_apply in project.applicants_apply]
                }
            }
        ]
        return JsonResponse({"results": results}, status=200)
