from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from foods.models import Ingredient, Tag, Recipe, Favorite
from foods.models import Cart, RecipeIngredients
from .serializers import IngredientSerializer, TagSerializer
from .serializers import RecipeGetSerializer, RecipeWriteSerializer
from .serializers import FavoriteSerializer, CartSerializer
from .filters import RecipeFilter, CustomSearchFilter
from .permissions import AnonReadOnlyOrOwnerOrAdmin
from .paginator import CustomPaginator


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredient."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [CustomSearchFilter]
    search_fields = ['^name']
    permission_classes = (AnonReadOnlyOrOwnerOrAdmin,)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Tag."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AnonReadOnlyOrOwnerOrAdmin,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модеи Recipe."""
    queryset = Recipe.objects.all()
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator
    permission_classes = (AnonReadOnlyOrOwnerOrAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeGetSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def post_or_delete(self, request, pk, model):
        """
        Вспомогательный метод для создания либо
        удаления избранного/элементов списка покупок.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {'user': user.pk,
                'recipe': recipe.pk}
        context = {'request': request}
        if model == Favorite:
            serializer = FavoriteSerializer(
                data=data,
                context=context
            )
        else:
            serializer = CartSerializer(
                data=data,
                context=context
            )
        if serializer.is_valid(raise_exception=True):
            if request.method == 'DELETE':
                model.objects.filter(recipe=recipe, user=user).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        return self.post_or_delete(request, pk, Favorite)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return self.post_or_delete(request, pk, Cart)

    @action(detail=False)
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        current_user = request.user
        text = RecipeIngredients.form_shopping_list(user=current_user)
        file_name = 'shopping_list.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        response.writelines(text)
        return response
