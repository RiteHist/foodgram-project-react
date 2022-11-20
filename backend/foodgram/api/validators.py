from rest_framework import serializers
from users.models import Follow
from foods.models import Favorite


def check_unique_and_exists(context, model, data):
    request = context['request']
    curr_user = request.user
    method = request.method
    if model == Follow:
        author = data['author']
        pair = curr_user.follower.filter(author=author)
    else:
        recipe = data['recipe']
        pair = model.objects.filter(recipe=recipe, user=curr_user)

    if method == 'DELETE':
        if not pair.exists():
            if model == Follow:
                raise serializers.ValidationError(
                    {'errors': 'Такой подписки не существует.'}
                )
            elif model == Favorite:
                raise serializers.ValidationError(
                    {'errors': 'Такого избранного не существует.'}
                )
            else:
                raise serializers.ValidationError(
                    {'errors': 'Такого элемента списка покупок нет.'}
                )
        return data
    if pair.exists():
        if model == Follow:
            raise serializers.ValidationError(
                {'errors': 'Такая подписка уже существует.'}
            )
        elif model == Favorite:
            raise serializers.ValidationError(
                {'errors': 'Такое избранное уже существует.'}
            )
        else:
            raise serializers.ValidationError(
                {'errors': 'Такой элемент списка покупок уже есть.'}
            )
    if model == Follow:
        if curr_user == author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя.'}
            )
    elif model == Favorite:
        if curr_user == recipe.author:
            raise serializers.ValidationError(
                {'errors': 'Нельзя добавлять свои рецепты в ищбранное.'}
            )
    return data
