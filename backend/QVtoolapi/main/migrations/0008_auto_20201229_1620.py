# Generated by Django 3.1.2 on 2020-12-29 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_remove_conversation_site_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='report_id',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddField(
            model_name='conversation',
            name='show_report',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
