
from django.contrib import admin

from .models import Component, Category


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "quantity", "price", "image")
    search_fields = ("name",)
    list_filter = ("quantity",)
    ordering = ("id",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "component")
    search_fields = ("user__username", "component__name")
    list_filter = ("user",)
    ordering = ("id",)
