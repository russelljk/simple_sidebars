# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sidebar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=300)),
                ('template', models.CharField(default=None, max_length=300, null=True, blank=True)),
                ('widget_schema', models.TextField(default=b'', blank=True)),
                ('css_classes', models.TextField(blank=True, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[a-zA-Z_\\-\\s]+$')])),
                ('version', models.PositiveIntegerField(default=0, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
