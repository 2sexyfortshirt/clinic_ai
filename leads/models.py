from django.db import models
from common.models import BaseModel
from clinics.models import Clinic
from django.contrib.auth.models import User



class Lead(BaseModel):
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE,related_name="leads")
    user = models.OneToOneField(User,on_delete=models.SET_NULL,related_name="lead",null=True,blank=True,)
    phone = models.CharField(max_length=50)
    name = models.CharField(max_length=255,null=True,blank=True)
    status = models.CharField(max_length=20,
                              choices=[
                                  ("new","New"),
                                  ("contacted","Booked",),
                                  ("completed","Completed"),
                              ],
                              default="new",)
    def __str__(self):
        return f"{self.name}  {self.phone}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["clinic","phone"],
                name="unique_phone_per_clinic",
            )
        ]

# Create your models here.
