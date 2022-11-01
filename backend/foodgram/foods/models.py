from django.contrib.auth import get_user_model
from .validators import SlugValidator, min_amount
from django.db import models


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True)
    measurement_unit = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=7, unique=True)
    slug = models.SlugField(max_length=200, unique=True,
                            validators=[SlugValidator()])

    def __str__(self):
        return self.slug


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
        upload_to='recipes/images/',
        null=False,
        default=None
    )
    cooking_time = models.IntegerField(validators=[min_amount])

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    ingredient_id = models.ForeignKey(Ingredient,
                                      on_delete=models.CASCADE,
                                      related_name='recipes')
    recipe_id = models.ForeignKey(Recipe,
                                  on_delete=models.CASCADE,
                                  related_name='ingredients_num')
    amount = models.IntegerField(validators=[min_amount])


class RecipeTags(models.Model):
    tag_id = models.ForeignKey(Tag,
                               on_delete=models.CASCADE,
                               related_name='recipes')
    recipe_id = models.ForeignKey(Recipe,
                                  on_delete=models.CASCADE,
                                  related_name='tags_list')


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
