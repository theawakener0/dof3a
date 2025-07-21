from djoser.serializers import UserCreateSerializer as BaseCreateUserSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class UserCreateSerializer(BaseCreateUserSerializer):
    class Meta(BaseCreateUserSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
