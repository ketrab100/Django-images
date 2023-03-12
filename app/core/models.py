from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.contrib.postgres.fields import ArrayField


class Tier(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    resolutions = ArrayField(
        models.PositiveIntegerField(), blank=True, null=True)
    unlimited_resolution = models.BooleanField(default=False)
    active_link_share = models.BooleanField(default=False)


class UserManager(BaseUserManager):
    def create_superuser(self, email, password=None,):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()

        return user

    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    tier = models.ForeignKey(
        to=Tier, on_delete=models.CASCADE, null=False, default=1)
    object = UserManager()

    USERNAME_FIELD = 'email'
