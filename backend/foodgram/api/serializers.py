import base64
from rest_framework import serializers
from django.core.files.base import ContentFile
from django.contrib.auth.models import AnonymousUser
from foods.models import Ingredient, Tag, Recipe, RecipeIngredients
from users.serializers import CustomUserSerializer


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            imgformat, imgstr = data.split(';base64,')
            ext = imgformat.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


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
    image = Base64ImageField(allow_null=True)

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
        serializer_context = {'request': self.context.get('request'),
                              'recipe': instance}
        res = super().to_representation(instance)
        res['ingredients'] = RecipeIngredientSerializer(
            instance.ingredients,
            context=serializer_context,
            many=True
        ).data

        return res
