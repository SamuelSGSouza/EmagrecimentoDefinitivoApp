# Generated by Django 3.2.12 on 2022-09-14 21:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_remove_planoalimentar_teste'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='assistiu_video',
            field=models.BooleanField(default=False, verbose_name='Assistiu o Vídeo'),
        ),
    ]
