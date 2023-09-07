# Generated by Django 4.2.4 on 2023-09-05 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='URLManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_type', models.CharField(max_length=20)),
                ('type_explanation', models.TextField()),
                ('malicious', models.BooleanField()),
            ],
        ),
    ]