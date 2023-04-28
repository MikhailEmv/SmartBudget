import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files import File
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save

from BudgetAnalysisWeb.settings import AUTH_USER_MODEL
from users.validators import positive_number_validator


class User(AbstractUser):

    email = models.EmailField(
        _('email address'),
        unique=True,
    )

    email_verify = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class UserDataModel(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    surname = models.CharField(max_length=100, blank=True)
    patronymic = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    sex = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.name}: {self.user}"


class CategoryModel(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100, blank=True)
    icon = models.ImageField(upload_to='users/static/images/')

    def __str__(self):
        return f"{self.category_name}: {self.user}"


class Account(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    icon = models.ImageField(upload_to='users/static/images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name}"


class Transaction(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    from_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_transactions')
    to_account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[positive_number_validator])
    date = models.DateField(default=timezone.now, editable=True)
    comment = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.from_account} -> {self.to_account}: {self.amount}"


def create_default_categories(sender, instance, created, **kwargs):
    if created:
        if CategoryModel.objects.filter(user=instance).count() == 0:
            default_categories = [
                {'name': 'Продукты', 'icon': 'users/static/images/icon1.jpeg'},
                {'name': 'Транспорт', 'icon': 'users/static/images/icon2.jpeg'},
                {'name': 'Переводы', 'icon': 'users/static/images/icon3.jpeg'},
                {'name': 'Одежда и обувь', 'icon': 'users/static/images/icon4.jpeg'},
                {'name': 'Интернет и связь', 'icon': 'users/static/images/icon5.jpeg'},
            ]
            for category_data in default_categories:
                category = CategoryModel(user=instance, category_name=category_data['name'])
                icon_path = os.path.join(settings.MEDIA_ROOT, category_data['icon'])
                with open(icon_path, 'rb') as f:
                    category.icon.save(os.path.basename(icon_path), File(f), save=True)
                category.save()


post_save.connect(create_default_categories, sender=AUTH_USER_MODEL)
