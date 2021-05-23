# Generated by Django 3.0.5 on 2021-05-19 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='on_blockchain',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='post',
            name='transaction_id',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
    ]
