# Generated by Django 5.1.6 on 2025-03-06 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_shop', '0005_category_slug'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccount',
            name='email',
            field=models.EmailField(max_length=254, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='first_name',
            field=models.CharField(max_length=50, verbose_name='First_name'),
        ),
        migrations.AlterField(
            model_name='useraccount',
            name='last_name',
            field=models.CharField(max_length=50, verbose_name='Last_name'),
        ),
    ]
