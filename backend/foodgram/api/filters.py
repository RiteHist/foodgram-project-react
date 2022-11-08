from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import BooleanFilter
from django_filters.rest_framework import ModelMultipleChoiceFilter
from foods.models import Recipe, Tag, Favorite, Cart


class RecipeFilter(FilterSet):
    author__id = NumberFilter()
    is_favorited = BooleanFilter(field_name='is_favorited',
                                 method='filter_is_favorited')
    is_in_shopping_cart = BooleanFilter(field_name='is_in_shopping_cart',
                                        method='filter_is_in_shopping_cart')
    tags = ModelMultipleChoiceFilter(field_name='tags__slug',
                                     to_field_name='slug',
                                     queryset=Tag.objects.all())

    class Meta:
        model = Recipe
        fields = ['author',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'tags'
                  ]

    def filter_is_favorited(self, queryset, name, tags):
        user = self.request.user
        fav_recipes = Favorite.objects.filter(user=user).values('recipe')
        return queryset.filter(id__in=fav_recipes)

    def filter_is_in_shopping_cart(self, queryset, name, tags):
        user = self.request.user
        recipes = Cart.objects.filter(user=user).values('recipe')
        return queryset.filter(id__in=recipes)
