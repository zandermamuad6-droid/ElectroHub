
from django.db import models


class Inventory(models.Model):
    component = models.ForeignKey(
        "components_app.Component",
        on_delete=models.PROTECT,
        related_name="inventory_records",
    )

    quantity = models.PositiveIntegerField(default=0)

    minimum_stock = models.PositiveIntegerField(default=5)

    date_added = models.DateTimeField(auto_now_add=True)

    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_added"]
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"

    @property
    def is_low_stock(self):
        return self.quantity <= self.minimum_stock

    def __str__(self):
        return f"{self.component} - Stock: {self.quantity}"
