from django.contrib import admin

from .models import User, Recipe, Ingredient, Tag

admin.site.register(User)
admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(Tag)
