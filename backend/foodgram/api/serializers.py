from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from drf_extra_fields.fields import Base64ImageField
from foods.models import Ingredient, Tag, Recipe, RecipeIngredients
from users.serializers import CustomUserSerializer


User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов на модель Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit'
                  )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор модели Ingredient для GET запросов рецепта."""
    amount = serializers.SerializerMethodField()

    class Meta:
        model = Ingredient
        fields = ('id',
                  'name',
                  'measurement_unit',
                  'amount'
                  )

    def get_amount(self, obj):
        recipe = self.context.get('recipe')
        amount = (recipe.ingredients_num.
                  filter(ingredient_id__exact=obj.id).first().amount)
        return amount


class RecipeIngredientPostSerializer(serializers.ModelSerializer):
    """Вложенный сериализатор ингредиентов для POST запросов рецептов."""
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount')


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов модели Tag."""

    class Meta:
        model = Tag
        fields = ('id',
                  'name',
                  'color',
                  'slug'
                  )


class RecipeGetSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов на модель Recipe."""
    ingredients = serializers.SerializerMethodField()
    author = CustomUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id',
                  'tags',
                  'author',
                  'ingredients',
                  'is_favorited',
                  'is_in_shopping_cart',
                  'name',
                  'image',
                  'text',
                  'cooking_time'
                  )

    def get_is_favorited(self, obj):
        request_user = self.context.get('request').user
        if type(request_user) == AnonymousUser:
            return False
        is_favorited = (request_user.favorites.
                        filter(recipe__exact=obj).exists())
        return is_favorited

    def get_is_in_shopping_cart(self, obj):
        request_user = self.context.get('request').user
        if type(request_user) == AnonymousUser:
            return False
        in_shopping_cart = request_user.cart.filter(recipe__exact=obj).exists()
        return in_shopping_cart

    def get_ingredients(self, obj):
        ingredients = obj.ingredients
        """
        Добавление в контекст объекта Recipe для последующего
        получения поля amount.
        """
        serializer_context = {'request': self.context.get('request'),
                              'recipe': obj}
        serializer = RecipeIngredientSerializer(ingredients,
                                                context=serializer_context,
                                                many=True)
        return serializer.data


class RecipeWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для POST и PATCH запросов рецептов."""
    ingredients = RecipeIngredientPostSerializer(many=True, write_only=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(),
                                              many=True)

    class Meta:
        model = Recipe
        fields = ('ingredients',
                  'tags',
                  'image',
                  'name',
                  'text',
                  'cooking_time'
                  )

    def create_or_update_recipe(self, validated_data,
                                create: bool, instance=None):
        """Создание или обновление рецепта."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        if create and not instance:
            instance = Recipe.objects.create(**validated_data)
        else:
            """Обновление полей рецепта и удаление связей с ингредиентами."""
            for key, value in validated_data.items():
                setattr(instance, key, value)
            (RecipeIngredients.objects.
             filter(recipe_id__exact=instance).delete())
        instance.tags.set(tags)
        instance.save()
        for ingredient in ingredients:
            """Создание связей с ингредиентами."""
            RecipeIngredients.objects.create(
                recipe_id=instance,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount')
            )
        return instance

    def create(self, validated_data):
        return self.create_or_update_recipe(validated_data, True)

    def update(self, instance, validated_data):
        return self.create_or_update_recipe(validated_data,
                                            False, instance=instance)

    def to_representation(self, instance):
        instance = Recipe.objects.get(pk=instance.pk)
        res = RecipeGetSerializer(instance,
                                  context=self.context).data
        return res


class RecipeShortSerialzier(serializers.ModelSerializer):
    """Сериализатор для отображения краткой информации о рецепте."""

    class Meta:
        model = Recipe
        fields = ('id',
                  'name',
                  'image',
                  'cooking_time'
                  )


class FollowSerializer(CustomUserSerializer):
    """Сериализатор для подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email',
                  'id',
                  'username',
                  'first_name',
                  'last_name',
                  'is_subscribed',
                  'recipes',
                  'recipes_count'
                  )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = Recipe.objects.filter(author=obj)
        limit = request.query_params.get('recipes_limit')
        if limit:
            recipes = recipes[:int(limit)]

        serializer = RecipeShortSerialzier(recipes,
                                           many=True,
                                           context={'request': request})
        return serializer.data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj).count()
