# Generated by Django 4.2.5 on 2023-09-10 14:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('xrp', '0003_alter_deposits_amount_fiat'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastProcessedLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ledger', models.IntegerField(default=81699196)),
            ],
        ),
    ]
