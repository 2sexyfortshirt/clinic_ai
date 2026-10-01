from django.db import models
from django.contrib.auth.models import User

from common.models import BaseModel

class Clinic(BaseModel):
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="clinic",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
    )
    phone = models.CharField(max_length=30,blank=True,)
    email = models.EmailField(blank=True,)
    address = models.TextField(blank=True,)
    is_active = models.BooleanField(default=True,)
    def __str__(self):
        return self.name



# Create your models here.
