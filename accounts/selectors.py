from django.contrib.auth.models import User

class AccountSelector:
    @staticmethod
    def by_username(username):
        return User.objects.filter(username=username).first()