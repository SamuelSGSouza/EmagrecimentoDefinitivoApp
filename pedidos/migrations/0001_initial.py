# Generated by Django 3.2.13 on 2022-08-03 19:08

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import localflavor.br.models
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PacoteDeVenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=250, verbose_name='Nome do Pacote')),
                ('preco', models.IntegerField(verbose_name='Preço do pacote')),
                ('imagem', models.ImageField(upload_to='produtos/imgs/%Y/%m', verbose_name='Imagem do Pacote')),
                ('descricao', models.TextField(verbose_name='Descrição do pacote')),
                ('quantidade', models.IntegerField(verbose_name='Quantidade de planos que será adicionado neste pacote')),
                ('quantidade_de_dias', models.IntegerField(verbose_name='Quantidade de dias a serem adicionados')),
            ],
            options={
                'verbose_name_plural': 'Pacotes à Venda',
            },
        ),
        migrations.CreateModel(
            name='Pedidos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('cpf', localflavor.br.models.BRCPFField(max_length=14, verbose_name='CPF')),
                ('nome', models.CharField(max_length=250, verbose_name='Nome Completo')),
                ('email', models.EmailField(max_length=254, verbose_name='Email')),
                ('preco_total', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Preço total')),
                ('pago', models.BooleanField(default=False)),
                ('pacote_de_planos', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='pacote_planos', to='pedidos.pacotedevenda', verbose_name='Pacote Selecionado')),
            ],
            options={
                'verbose_name_plural': 'Pedidos',
                'ordering': ('-created',),
            },
        ),
    ]
