# Generated by Django 4.0.3 on 2023-09-14 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='url_judge',
            fields=[
                ('prediction_result', models.BooleanField()),
                ('pri_url', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('ip_addr', models.CharField(max_length=50, null=True)),
                ('nation_code', models.CharField(max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='URLManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url_type', models.CharField(max_length=20)),
                ('type_explanation', models.TextField()),
                ('malicious', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='white_list',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=100)),
            ],
        ),
    ]
