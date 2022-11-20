from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Sum

from .validators import SlugValidator, min_amount

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        models.UniqueConstraint(
            fields=['name', 'measurement_unit'],
            name='unique_ingredient_pair'
        )
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7)
    slug = models.SlugField(max_length=200, unique=True,
                            validators=[SlugValidator()])

    def __str__(self):
        return self.slug

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    name = models.CharField(max_length=200)
    text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient,
                                         through='RecipeIngredients')
    tags = models.ManyToManyField(Tag, through='RecipeTags')
    image = models.ImageField(
        upload_to='recipes/images',
        null=False,
        default=None
    )
    cooking_time = models.IntegerField(validators=[min_amount])
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta():
        models.UniqueConstraint(
            fields=['author', 'name'],
            name='unique_recipe_pair'
        )
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class RecipeIngredients(models.Model):
    """Связующая модель ингредиента и рецепта."""
    ingredient_id = models.ForeignKey(Ingredient,
                                      on_delete=models.CASCADE,
                                      related_name='recipes')
    recipe_id = models.ForeignKey(Recipe,
                                  on_delete=models.CASCADE,
                                  related_name='ingredients_num')
    amount = models.IntegerField(validators=[min_amount])

    def form_shopping_list(user):
        text = 'Список покупок:'
        ingredients = RecipeIngredients.objects.filter(
            recipe_id__cart__user=user
        ).values('ingredient_id__name',
                 'ingredient_id__measurement_unit'
                 ).annotate(amount=Sum('amount'))
        for i in ingredients:
            text += (
                f"\n{i['ingredient_id__name']} - "
                f"{i['amount']} {i['ingredient_id__measurement_unit']}"
            )
        return text

    class Meta():
        models.UniqueConstraint(
            fields=['ingredient_id', 'recipe_id'],
            name='unique_recipeingredients_pair'
        )
        verbose_name = 'Рецепты и ингредиенты'
        verbose_name_plural = verbose_name


class RecipeTags(models.Model):
    """Связующая модель рецепта и тега."""
    tag_id = models.ForeignKey(Tag,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    recipe_id = models.ForeignKey(Recipe,
                                  on_delete=models.CASCADE,
                                  related_name='tags_list')

    class Meta:
        verbose_name = 'Рецепты и теги'
        verbose_name_plural = verbose_name


class Favorite(models.Model):
    """Модель избранного."""
    user = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='favorites',
        on_delete=models.CASCADE
    )

    class Meta():
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_favorite_pair'
        )
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name


class Cart(models.Model):
    """Модель элемента списка покупок."""
    user = models.ForeignKey(
        User,
        related_name='cart',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        related_name='cart',
        on_delete=models.CASCADE
    )

    class Meta():
        models.UniqueConstraint(
            fields=['user', 'recipe'],
            name='unique_cart_pair'
        )
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
