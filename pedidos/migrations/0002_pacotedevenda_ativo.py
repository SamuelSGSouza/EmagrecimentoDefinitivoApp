# Generated by Django 3.2.13 on 2022-08-08 17:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pacotedevenda',
            name='ativo',
            field=models.BooleanField(default=True, verbose_name='Pacote está ativo?'),
        ),
    ]
