from django.contrib.auth import get_user_model
from .validators import SlugValidator, min_amount
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'


class Tag(models.Model):
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
    ingredient_id = models.ForeignKey(Ingredient,
                                      on_delete=models.CASCADE,
                                      related_name='recipes')
    recipe_id = models.ForeignKey(Recipe,
                                  on_delete=models.CASCADE,
                                  related_name='ingredients_num')
    amount = models.IntegerField(validators=[min_amount])

    class Meta():
        models.UniqueConstraint(
            fields=['ingredient_id', 'recipe_id'],
            name='unique_recipeingredients_pair'
        )
        verbose_name = 'Рецепты и ингредиенты'
        verbose_name_plural = verbose_name


class RecipeTags(models.Model):
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
