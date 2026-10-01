handlers = {}

def register(event_name):
    def decorator(func):
        handlers.setdefault(event_name, []).append(func)
        return func
    return decorator
def publish(event_name, payload):
    print("PUBLISH:", event_name)
    print("HANDLERS:", handlers)

    for handler in handlers.get(event_name, []):
        print("RUN:", handler)
        handler(payload)