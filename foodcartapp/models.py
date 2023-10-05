from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.timezone import now


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    WAIT_MANAGER = 'WM'
    WAIT_RESTAURANT = 'WR'
    WAIT_COURIER = 'WC'
    CLOSED = 'CL'
    STATUSES = [
        (WAIT_MANAGER, 'Необработанный'),
        (WAIT_RESTAURANT, 'Ожидание рестарана'),
        (WAIT_COURIER, 'Ожидание курьера'),
        (CLOSED, 'Завершён'),
    ]

    ONLINE = 'ON'
    OFFLINE = 'OF'
    NOT_SPECIFIED = 'NS'
    PAYMENT_METHODS = [
        (ONLINE, 'Онлайн'),
        (OFFLINE, 'Наличными'),
        (NOT_SPECIFIED, 'Не указано')
    ]

    address = models.CharField(
        verbose_name='адрес',
        max_length=200,
    )
    firstname = models.CharField(
        verbose_name='имя',
        max_length=200,
    )
    lastname = models.CharField(
        verbose_name='фамилия',
        max_length=200,
    )
    phonenumber = PhoneNumberField()

    status = models.CharField(
        verbose_name='статус',
        max_length=2,
        choices=STATUSES,
        default=WAIT_MANAGER,
        db_index=True,
    )

    selected_restaurant = models.ForeignKey(
        Restaurant,
        related_name='restaurant_items',
        verbose_name="выбранный ресторан",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    comment = models.TextField(
        verbose_name='комментарий',
        blank=True,
    )

    registered_at = models.DateTimeField(
        verbose_name='время создания заказа',
        default=now,
        db_index=True,
    )

    called_at = models.DateTimeField(
        verbose_name='время звонка',
        db_index=True,
        null=True,
        blank=True,
    )

    delivered_at = models.DateTimeField(
        verbose_name='время доставки',
        db_index=True,
        null=True,
        blank=True,
    )

    payment_method = models.CharField(
        verbose_name='способ оплаты',
        max_length=2,
        choices=PAYMENT_METHODS,
        default=NOT_SPECIFIED,
        db_index=True,
    )

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'

    class Meta:
        verbose_name = 'заказы'
        verbose_name_plural = 'заказы'


class OrderItem(models.Model):
    item = models.ForeignKey(
        to=Product,
        verbose_name='продукт',
        related_name='products',
        on_delete=models.CASCADE,
    )
    previous_price = models.DecimalField(
        verbose_name='прежняя цена',
        decimal_places=2,
        max_digits=7,
        validators=[MinValueValidator(0)],
    )
    count = models.IntegerField(
        verbose_name='количество',
        validators=[MinValueValidator(1)],
    )

    order = models.ForeignKey(
        to=Order,
        verbose_name='заказ',
        related_name='products',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'[{self.id}]: для заказа {self.order.id}'

    class Meta:
        verbose_name = 'элемент заказа'
        verbose_name_plural = 'элементы заказа'
