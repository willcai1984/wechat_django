from django.db import models

# Create your models here.
from django.db import models
import django.utils.timezone as timezone


# Create your models here.
class Book(models.Model):
    book_name = models.CharField('书名', max_length=64, default='')
    add_time = models.DateTimeField('创建日期', default=timezone.now)
