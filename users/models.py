from django.db   import models
from core.models import TimeStampModel


class User(TimeStampModel):
    kakao_id        = models.BigIntegerField(unique=True)
    email           = models.EmailField(unique=True, null=True)
    name            = models.CharField(max_length=10, blank=True)
    nickname        = models.CharField(max_length=10, unique=True, null=True)
    batch           = models.PositiveSmallIntegerField(null=True)
    hit             = models.PositiveBigIntegerField(default=0)
    like            = models.PositiveBigIntegerField(default=0)
    github_repo_url = models.URLField(max_length=2000, null=True)
    region          = models.ForeignKey("commons.Region", on_delete=models.PROTECT, null=True)
    position        = models.ForeignKey("commons.Position", on_delete=models.SET_NULL, null=True)
    user_status     = models.ForeignKey("UserStatus", on_delete=models.SET_NULL, null=True)
    portfolio       = models.ForeignKey("Portfolio", on_delete=models.SET_NULL, null=True)
    follow          = models.ManyToManyField("self", symmetrical=False, through="Follow")
    stack           = models.ManyToManyField("commons.TechnologyStack", through="UserStack")
    project         = models.ManyToManyField("projects.Project", through="applies.ProjectApply")

    class Meta:
        db_table = "users"


class Follow(TimeStampModel):
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="follower")
    followee = models.ForeignKey("User", on_delete=models.CASCADE, related_name="followee")

    class Meta:
        db_table = "follows"


class UserStatus(TimeStampModel):
    recruit_status = models.CharField(max_length=50)

    class Meta:
        db_table = "user_statuses"


class Portfolio(TimeStampModel):
    file_url   = models.URLField(max_length=2000, null=True)
    is_private = models.BooleanField(default=True)

    class Meta:
        db_table = "portfolios"


class UserStack(TimeStampModel):
    user             = models.ForeignKey("User", on_delete=models.CASCADE)
    technology_stack = models.ForeignKey("commons.TechnologyStack", on_delete=models.CASCADE)

    class Meta:
        db_table = "users_stacks"