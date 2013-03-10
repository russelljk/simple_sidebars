# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Sidebar'
        db.create_table('simple_sidebars_sidebar', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=300)),
            ('template', self.gf('django.db.models.fields.CharField')(default=None, max_length=300, null=True, blank=True)),
            ('widget_schema', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('css_classes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('simple_sidebars', ['Sidebar'])


    def backwards(self, orm):
        # Deleting model 'Sidebar'
        db.delete_table('simple_sidebars_sidebar')


    models = {
        'simple_sidebars.sidebar': {
            'Meta': {'object_name': 'Sidebar'},
            'css_classes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '300', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '300'}),
            'widget_schema': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'})
        }
    }

    complete_apps = ['simple_sidebars']