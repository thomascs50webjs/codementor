# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_pen_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='pen',
            name='is_fork',
            field=models.BooleanField(default=False),
        ),
    ]
