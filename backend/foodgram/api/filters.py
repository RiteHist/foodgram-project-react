from django_filters import FilterSet, NumberFilter
from django_filters.rest_framework import BooleanFilter
from django_filters.rest_framework import ModelMultipleChoiceFilter
from foods.models import Recipe, Tag


class RecipeFilter(FilterSet):
    author__id = NumberFilter()
    is_favorited = BooleanFilter()
    is_in_shopping_cart = BooleanFilter()
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
