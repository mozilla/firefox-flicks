# -*- coding: utf-8 -*-
from south.db import db
from south.v2 import SchemaMigration


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Renaming model 'Video'
        db.rename_table('videos_video', 'videos_video2012')

        # Changing field 'Award.video'
        db.alter_column('videos_award', 'video_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video2012'], null=True))

    def backwards(self, orm):
        # Renaming model 'Video2012'
        db.rename_table('videos_video2012', 'videos_video')

        # Changing field 'Award.video'
        db.alter_column('videos_award', 'video_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['videos.Video'], null=True))

    models = {
        'videos.award': {
            'Meta': {'object_name': 'Award'},
            'award_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video2012']", 'null': 'True', 'blank': 'True'})
        },
        'videos.video2012': {
            'Meta': {'object_name': 'Video2012'},
            'bitly_link_db': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2012, 2, 28, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'judge_mark': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shortlink': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'unsent'", 'max_length': '10'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'upload_url': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200'}),
            'user_country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'user_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100'}),
            'views': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'votes': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['videos']
