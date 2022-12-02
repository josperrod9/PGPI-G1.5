# Generated by Django 2.2 on 2022-12-02 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20221130_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='statement',
            field=models.CharField(choices=[('CF', 'Confirmado'), ('EV', 'Enviado'), ('EP', 'En preparacion'), ('RB', 'Recibido'), ('AN', 'Anulado')], default='Confirmado', max_length=2, null=True),
        ),
    ]
