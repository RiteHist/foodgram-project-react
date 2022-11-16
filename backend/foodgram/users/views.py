from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from api.views import CustomPaginator
from api.serializers import FollowSerializer
from .models import Follow


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User"""
    pagination_class = CustomPaginator

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        """Подписка на автора."""
        current_user = request.user
        user_to_follow = get_object_or_404(User, pk=id)
        same_user = current_user == user_to_follow
        follow_exists = (current_user.follower.
                         filter(author=user_to_follow).exists())

        if request.method == 'POST':
            if same_user or follow_exists:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=current_user,
                                  author=user_to_follow)
            seriailizer = FollowSerializer(user_to_follow,
                                           context={'request': request})
            return Response(seriailizer.data)

        if not follow_exists:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Follow.objects.filter(user=current_user,
                              author=user_to_follow).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, pagination_class=CustomPaginator)
    def subscriptions(self, request):
        """Получение списка подписок."""
        current_user = request.user
        author_ids = current_user.follower.values_list('author', flat=True)
        queryset = User.objects.filter(pk__in=author_ids)
        page = self.paginate_queryset(queryset)
        if not page:
            serializer = FollowSerializer(queryset,
                                          many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(page,
                                      many=True,
                                      context={'request': request})
        return self.get_paginated_response(serializer.data)
