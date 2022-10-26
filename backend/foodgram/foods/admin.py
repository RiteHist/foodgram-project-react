from django.contrib import admin
from . import models


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'color',
                    'slug')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'author')
    list_filter = ('name',
                   'author',
                   'tag')
    empty_value_display = '-пусто-'


class RecipeIngredientsAdmin(admin.ModelAdmin):
    list_display = ('ingredient_id',
                    'recipe_id',
                    'amount')
    list_filter = ('recipe_id',
                   'ingredient_id')


class RecipeTagsAdmin(admin.ModelAdmin):
    list_display = ('tag_id',
                    'recipe_id')


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')


class CartAdmin(admin.ModelAdmin):
    list_display = ('user',
                    'recipe')


admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.Tag, TagAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
admin.site.register(models.RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(models.RecipeTags, RecipeTagsAdmin)
admin.site.register(models.Favorite, FavoriteAdmin)
admin.site.register(models.Cart, CartAdmin)
