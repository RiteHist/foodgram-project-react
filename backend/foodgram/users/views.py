from api.paginator import CustomPaginator
from api.serializers import FollowReturnSerializer, FollowSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """Вьюсет для модели User"""
    pagination_class = CustomPaginator

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        """Подписка на автора."""
        current_user = request.user
        user_follow = get_object_or_404(User, pk=id)
        seriailizer = FollowSerializer(data={'user': current_user.pk,
                                             'author': user_follow.pk},
                                       context={'request': request})
        if seriailizer.is_valid(raise_exception=True):
            if request.method == 'DELETE':
                current_user.follower.filter(author=user_follow).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            seriailizer.save()
            return Response(seriailizer.data)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, pagination_class=CustomPaginator)
    def subscriptions(self, request):
        """Получение списка подписок."""
        current_user = request.user
        author_ids = current_user.follower.values_list('author', flat=True)
        queryset = User.objects.filter(pk__in=author_ids)
        page = self.paginate_queryset(queryset)
        if not page:
            serializer = FollowReturnSerializer(queryset,
                                                many=True,
                                                context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = FollowReturnSerializer(page,
                                            many=True,
                                            context={'request': request})
        return self.get_paginated_response(serializer.data)
