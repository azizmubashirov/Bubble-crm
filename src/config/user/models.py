from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin


def default_location():
    return {
        "latitude": 0,
        "longitude": 0,
    }


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, is_staff=False, is_active=True, **extra_fields):

        user = self.model(is_active=is_active,
                          is_staff=is_staff, **extra_fields)
        if username:
            user.username = username

        if password:
            user.set_password(password)

        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        return self.create_user(username, password, is_staff=True,
                                is_superuser=True, **extra_fields)


class Access(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True, )

    def __str__(self):
        return self.name


class Role(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True, )
    status = models.BooleanField(default=False, )
    slug = models.SlugField(unique=True, max_length=355, allow_unicode=True, null=True, blank=True)

    def __str__(self):
        return self.name


class RoleAccess(BaseModel):
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    access = models.ForeignKey(Access, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.role.name}-{self.access.name}"


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    firstname = models.CharField(max_length=100, help_text="First name")
    lastname = models.CharField(max_length=100, help_text="Last name")
    phone_number = models.CharField(max_length=13, null=True, blank=True, unique=True)
    username = models.CharField(max_length=60, unique=True)
    # email = models.EmailField('email', max_length=256, null=True, blank=True)
    location = models.JSONField(blank=False, null=False, default=default_location)
    image = models.URLField(blank=True, null=True, max_length=500)
    access_time = models.DateTimeField(auto_now=True)
    status = models.BooleanField("status", default=True)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)

    is_active = models.BooleanField("active status", default=True)
    is_staff = models.BooleanField("is_staff", default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.firstname or self.lastname or self.username or "User None"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


class AgentInformation(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    passport = models.CharField(max_length=100, blank=True, null=True)
    inn = models.CharField(max_length=100, blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    is_merried = models.IntegerField(
        choices=[(1, "Not Merried"), (2, "Merried"), (3, "Divorced")],
        default=1, blank=False, null=False
    )
    dad_name = models.CharField(max_length=100, blank=True, null=True)
    dad_phone = models.CharField(max_length=100, blank=True, null=True)
    mom_name = models.CharField(max_length=100, blank=True, null=True)
    mom_phone = models.CharField(max_length=100, blank=True, null=True)
    
    
class AgentPlan(BaseModel):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agent_plan", blank=True, null=True)
    balance = models.BigIntegerField(blank=True, null=False, default=0)
    plan = models.BigIntegerField(blank=True, null=False, default=0)

class AgentBalanceToday(BaseModel):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agent_balance", blank=True, null=True)
    balance = models.BigIntegerField(blank=True, null=False, default=0)
    

class Notes(BaseModel):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agent_notes", blank=True, null=True)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)


class UserLocation(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lat = models.CharField(max_length=255, null=True, blank=True)
    lon = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class WorkerTime(BaseModel):
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    hour = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    