from core_events.registry import register
from leads.models import Lead

@register("message_received")

def upsert_lead(event):
    Lead.objects.get_or_create(phone=event['phone']
                               )