import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.files import File
from django.db import models
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save

from BudgetAnalysisWeb.settings import AUTH_USER_MODEL


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


class CategoryModel(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    category_name = models.CharField(max_length=100, blank=True)
    icon = models.ImageField(upload_to='users/static/images/')


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
