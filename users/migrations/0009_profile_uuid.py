# users/migrations/0007_auto_....py

from django.db import migrations, models
import uuid

def generate_unique_uuids(apps, schema_editor):
    Profile = apps.get_model('users', 'Profile')
    for profile in Profile.objects.all():
        # Przypisanie nowego UUID do każdego istniejącego rekordu
        profile.uuid = uuid.uuid4()
        profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_remove_profile_uuid'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
        migrations.RunPython(generate_unique_uuids),

    ]
