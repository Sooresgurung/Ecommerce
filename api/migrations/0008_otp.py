# Generated by Django 4.0.4 on 2022-06-26 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_rename_item_cart_items'),
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=400)),
                ('otp', models.CharField(max_length=20)),
            ],
        ),
    ]