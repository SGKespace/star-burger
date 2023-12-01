# Generated by Django 3.2.15 on 2023-03-29 02:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0005_alter_orderdetails_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderdetails',
            name='status',
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('RE', 'Получено'), ('PR', 'Подготовка'), ('DE', 'Доставка'), ('DO', 'Выполнено')], default='unprocessed', max_length=100, verbose_name='Статус'),
            preserve_default=False,
        ),
    ]
