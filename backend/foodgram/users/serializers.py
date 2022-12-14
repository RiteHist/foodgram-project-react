from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from djoser.serializers import UserSerializer
from rest_framework import serializers

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователя."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed'
                  )

    def get_is_subscribed(self, obj):
        request_user = self.context.get('request').user
        if type(request_user) == AnonymousUser:
            return False
        return request_user.follower.filter(author__exact=obj).exists()
