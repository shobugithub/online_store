# Generated by Django 5.1.6 on 2025-03-05 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('online_shop', '0004_category_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(default='placeholder-slug', unique=True),
            preserve_default=False,
        ),
    ]
