# -*- coding: utf-8 -*-
from itertools import product

from south.v2 import DataMigration

from flicks.videos.models import Award

class Migration(DataMigration):

    def forwards(self, orm):
        """Create awards."""
        regions = ['america', 'latin_america', 'europe',
                   'asia_africa_australia']
        categories = ['thirty_spot', 'animation', 'new_technology', 'psa']

        # Grand prize winners
        for region in regions:
            Award.objects.create(award_type='grand_winner', region=region)

        # Category winners and runner ups.
        for award_type, region, category in product(
            ['category_winner', 'runner_up'], regions, categories):
            Award.objects.create(award_type=award_type, region=region,
                                 category=category)

        # Special awards
        Award.objects.create(award_type='panavision')
        Award.objects.create(award_type='bavc')


    def backwards(self, orm):
        """Remove all awards from the DB."""
        Award.objects.all().delete()


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'videos.award': {
            'Meta': {'object_name': 'Award'},
            'award_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'category': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'preview': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'region': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['videos.Video']", 'null': 'True', 'blank': 'True'})
        },
        'videos.video': {
            'Meta': {'object_name': 'Video'},
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'views': ('django.db.models.fields.BigIntegerField', [], {'default': '0'}),
            'votes': ('django.db.models.fields.BigIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['videos']
    symmetrical = True
