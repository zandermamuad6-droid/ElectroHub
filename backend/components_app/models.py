
from django.conf import settings
from django.db import models


class Component(models.Model):
    name = models.CharField(max_length=150)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(
        upload_to="components/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="categories",
    )
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        related_name="categories",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "component"],
                name="unique_user_component",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.component.name}"
