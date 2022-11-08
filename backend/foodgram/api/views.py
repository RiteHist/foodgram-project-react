from rest_framework import viewsets, status
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django_filters import rest_framework

from foods.models import Ingredient, Tag, Recipe, Favorite, Cart
from .serializers import IngredientSerializer, TagSerializer
from .serializers import RecipeGetSerializer, RecipeWriteSerializer
from .serializers import RecipeShortSerialzier
from .filters import RecipeFilter


class CustomSearchFilter(filters.SearchFilter):
    search_param = 'name'


class CustomPaginator(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [CustomSearchFilter]
    search_fields = ['^name']


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_class = RecipeFilter
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RecipeGetSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def post_or_delete(self, request, pk, model):
        user = request.user
        recipe = Recipe.objects.get(pk=pk)
        object_exists = model.objects.filter(recipe=recipe, user=user).exists()
        if request.method == 'POST':
            same_user = recipe.author == user
            if object_exists or same_user:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            model.objects.create(recipe=recipe, user=user)
            serializer = RecipeShortSerialzier(recipe)
            return Response(serializer.data)

        if not object_exists:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        model.objects.filter(recipe=recipe, user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'])
    def favorite(self, request, pk):
        return self.post_or_delete(request, pk, Favorite)

    @action(detail=True, methods=['post', 'delete'])
    def shopping_cart(self, request, pk):
        return self.post_or_delete(request, pk, Cart)
