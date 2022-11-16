from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters import rest_framework
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse

from foods.models import Ingredient, Tag, Recipe, Favorite
from foods.models import Cart, RecipeIngredients
from .serializers import IngredientSerializer, TagSerializer
from .serializers import RecipeGetSerializer, RecipeWriteSerializer
from .serializers import RecipeShortSerialzier
from .filters import RecipeFilter
from .permissions import AnonReadOnlyOrOwnerOrAdmin


class CustomSearchFilter(filters.SearchFilter):
    search_param = 'name'


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


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

    def post_or_delete(self, request, pk, model, to_fav: bool):
        """
        Вспомогательный метод для создания либо
        удаления избранного/элементов списка покупок.
        """
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object_exists = model.objects.filter(recipe=recipe, user=user).exists()
        if request.method == 'POST':
            if to_fav:
                same_user = recipe.author == user
                if same_user:
                    return Response({'errors': 'Нельзя добавлять'
                                     ' свои рецепты в избранное'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if object_exists:
                return Response({'errors': 'Этот рецепт уже добавлен'},
                                status=status.HTTP_400_BAD_REQUEST)

            model.objects.create(recipe=recipe, user=user)
            serializer = RecipeShortSerialzier(recipe)
            return Response(serializer.data)

        if not object_exists:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        model.objects.filter(recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        return self.post_or_delete(request, pk, Favorite, True)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return self.post_or_delete(request, pk, Cart, False)

    @action(detail=False)
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        text = 'Спиосок покупок:'
        current_user = request.user
        ingredients = RecipeIngredients.objects.filter(
            recipe_id__cart__user=current_user
            ).values('ingredient_id__name',
                     'ingredient_id__measurement_unit'
                     ).annotate(amount=Sum('amount'))
        for i in ingredients:
            text += (
                f"\n{i['ingredient_id__name']} - "
                f"{i['amount']} {i['ingredient_id__measurement_unit']}"
            )

        file_name = 'shopping_list.txt'
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        response.writelines(text)
        return response
