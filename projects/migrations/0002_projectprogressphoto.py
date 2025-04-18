# Generated by Django 5.1.7 on 2025-03-29 15:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectProgressPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='progress_photos/%Y/%m/')),
                ('caption', models.CharField(blank=True, max_length=255)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('progress_update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='projects.projectprogress')),
            ],
            options={
                'verbose_name': 'Project Progress Photo',
                'verbose_name_plural': 'Project Progress Photos',
                'ordering': ['-upload_date'],
            },
        ),
    ]
