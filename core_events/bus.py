from celery import shared_task
from core_events.registry import EVENT_HANDLERS


class EventBus:

    def emit(self,event_name,payload):
        handle_event.delay(event_name,payload)
@shared_task
def handle_event(event_name,payload):
    handlers = EVENT_HANDLERS.get(event_name, [])
    for handler in handlers:
        handler(payload)
