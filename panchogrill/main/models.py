from django.db import models


class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField()

    class Meta:
        ordering = ["id"]

    @property
    def items(self):
        return self.menu_items.all()

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    category = models.ForeignKey(Category, related_name="menu_items", on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    price = models.PositiveIntegerField()
    weight = models.CharField(max_length=30)
    badge = models.CharField(max_length=50)
    image = models.CharField(max_length=20)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.name


class Promo(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class ContactInfo(models.Model):
    city = models.CharField(max_length=100)
    schedule = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.city


class CartItem(models.Model):
    session_key = models.CharField(max_length=40, default="")
    menu_item = models.ForeignKey(MenuItem, related_name="cart_lines", on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["id"]
        # добавляем ограничение: одна сессия - один предмет, для устранения дублей в корзине
        constraints = [
            models.UniqueConstraint(fields=["session_key", "menu_item"], name="unique_session_menu_item")
        ]

    @property
    def name(self):
        return self.menu_item.name

    @property
    def price(self):
        return self.menu_item.price

    @property
    def line_total(self):
        return self.menu_item.price * self.qty

    def __str__(self):
        return f"{self.menu_item.name} × {self.qty}"