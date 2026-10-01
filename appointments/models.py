from django.db import models
from common.models import BaseModel
from clinics.models import Clinic
from leads.models import Lead

# Create your models here.


class Appointment(BaseModel):
    clinic = models.ForeignKey(Clinic,on_delete=models.CASCADE,
                               related_name="appointments",
                               )
    lead = models.ForeignKey(Lead,on_delete=models.CASCADE,related_name="apointments",
                             )
    scheduled_at = models.DateTimeField()
    STATUS_CHOICES = [
        ("pending","Pending"),
        ("confirmed","Confirmed"),
        ("completed","Completed"),
        ("cancelled","Cancelled"),
    ]
    status =models.CharField(max_length=20,
                             choices=STATUS_CHOICES,
                             default="pending",
                             )
    notes = models.TextField(blank=True,)


    def __str__(self):
        return f"{self.lead.phone} - {self.scheduled_at}"



