from django.db import models


class Category(models.Model):
    """Модель Категория."""

    title = models.CharField(max_length=100, verbose_name="Категория")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-идентификатор")
    image = models.ImageField(upload_to="categories/", null=True, blank=True, verbose_name="Изображение")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Subcategory(models.Model):
    """Модель Подкатегория."""

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories", verbose_name="Категория")
    title = models.CharField(max_length=100, verbose_name="Подкатегория")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-идентификатор")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"

    def __str__(self):
        return self.title


class Product(models.Model):
    """Модель Продукт."""

    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name="products", verbose_name="Подкатегория")
    title = models.CharField(max_length=200, verbose_name="Название товара")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-идентификатор")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    stock = models.PositiveIntegerField(default=0, verbose_name="Остаток товаров")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title


class Cart(models.Model):
    """Модель Корзина."""

    user = models.OneToOneField(
        "TelegramUser",
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Корзина пользователя {self.user}"


class CartItem(models.Model):
    """Модель Содержимое корзины."""

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

    def __str__(self):
        return f"{self.product} x{self.quantity}"


class Order(models.Model):
    """Модель Заказ."""

    STATUS_CHOICES = [
        ("new", "Новый"),
        ("processing", "В обработке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    ]

    user = models.ForeignKey("TelegramUser", on_delete=models.CASCADE, related_name="orders", verbose_name="Пользователь")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Итоговая сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ {self.id} ({self.user.user_id})"


class Delivery(models.Model):
    """Модель Доставка."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="delivery", verbose_name="Заказ")
    address = models.TextField(verbose_name="Адрес доставки")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")

    class Meta:
        verbose_name = "Доставка"
        verbose_name_plural = "Доставки"

    def __str__(self):
        return f"Доставка для заказа {self.order.id}"


class TelegramUser(models.Model):
    """Модель Пользователя. Возможно когда то будет предусмотрена полная регистрация пользователя, сейчас нам достаточно ID, и мы сами зарегистрируем пользователя при отправке команды /start."""

    user_id = models.BigIntegerField(unique=True, verbose_name="ID пользователя")
    username = models.CharField(max_length=100, null=True, blank=True, verbose_name="Username")
    first_name = models.CharField(max_length=100, verbose_name="Имя", blank=True, null=True)
    last_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Телефон")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f'{self.user_id}'
