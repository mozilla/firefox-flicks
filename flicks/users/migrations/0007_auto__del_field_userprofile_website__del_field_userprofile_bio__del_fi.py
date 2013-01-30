# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'UserProfile.website'
        db.delete_column('users_userprofile', 'website')

        # Deleting field 'UserProfile.bio'
        db.delete_column('users_userprofile', 'bio')

        # Deleting field 'UserProfile.address'
        db.delete_column('users_userprofile', 'address')

        # Deleting field 'UserProfile.youth_contest'
        db.delete_column('users_userprofile', 'youth_contest')

        # Adding field 'UserProfile.locale'
        db.add_column('users_userprofile', 'locale',
                      self.gf('flicks.base.models.LocaleField')(default='en-US', max_length=32, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.nickname'
        db.add_column('users_userprofile', 'nickname',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'UserProfile.address1'
        db.add_column('users_userprofile', 'address1',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.address2'
        db.add_column('users_userprofile', 'address2',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.mailing_country'
        db.add_column('users_userprofile', 'mailing_country',
                      self.gf('flicks.base.models.CountryField')(default=u'us', max_length=16, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.state'
        db.add_column('users_userprofile', 'state',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)


        # Changing field 'UserProfile.city'
        db.alter_column('users_userprofile', 'city', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'UserProfile.postal_code'
        db.alter_column('users_userprofile', 'postal_code', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'UserProfile.full_name'
        db.alter_column('users_userprofile', 'full_name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # Changing field 'UserProfile.country'
        db.alter_column('users_userprofile', 'country', self.gf('flicks.base.models.CountryField')(max_length=16))

    def backwards(self, orm):
        # Adding field 'UserProfile.website'
        db.add_column('users_userprofile', 'website',
                      self.gf('django.db.models.fields.URLField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.bio'
        db.add_column('users_userprofile', 'bio',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.address'
        db.add_column('users_userprofile', 'address',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'UserProfile.youth_contest'
        db.add_column('users_userprofile', 'youth_contest',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'UserProfile.locale'
        db.delete_column('users_userprofile', 'locale')

        # Deleting field 'UserProfile.nickname'
        db.delete_column('users_userprofile', 'nickname')

        # Deleting field 'UserProfile.address1'
        db.delete_column('users_userprofile', 'address1')

        # Deleting field 'UserProfile.address2'
        db.delete_column('users_userprofile', 'address2')

        # Deleting field 'UserProfile.mailing_country'
        db.delete_column('users_userprofile', 'mailing_country')

        # Deleting field 'UserProfile.state'
        db.delete_column('users_userprofile', 'state')


        # Changing field 'UserProfile.city'
        db.alter_column('users_userprofile', 'city', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'UserProfile.postal_code'
        db.alter_column('users_userprofile', 'postal_code', self.gf('django.db.models.fields.CharField')(max_length=50))

        # Changing field 'UserProfile.full_name'
        db.alter_column('users_userprofile', 'full_name', self.gf('django.db.models.fields.CharField')(max_length=100))

        # Changing field 'UserProfile.country'
        db.alter_column('users_userprofile', 'country', self.gf('django.db.models.fields.CharField')(max_length=100))

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
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
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
        'users.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'address1': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country': ('flicks.base.models.CountryField', [], {'default': "u'us'", 'max_length': '16'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'locale': ('flicks.base.models.LocaleField', [], {'default': "'en-US'", 'max_length': '32', 'blank': 'True'}),
            'mailing_country': ('flicks.base.models.CountryField', [], {'default': "u'us'", 'max_length': '16', 'blank': 'True'}),
            'nickname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['users']