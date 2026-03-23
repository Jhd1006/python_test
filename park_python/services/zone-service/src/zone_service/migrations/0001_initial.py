from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='SlotType',
            fields=[
                # factories의 create_slot_type에서 사용하는 ID 필드명
                ('slot_type_id', models.BigAutoField(primary_key=True, serialize=False)),
                # factories의 defaults={"type_name": type_name}와 일치
                ('type_name', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'SLOT_TYPE'},
        ),
        migrations.CreateModel(
            name='Zone',
            fields=[
                ('zone_id', models.BigAutoField(primary_key=True, serialize=False)),
                # factories의 zone_name 필드와 일치
                ('zone_name', models.CharField(max_length=100, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'db_table': 'ZONE'},
        ),
        migrations.CreateModel(
            name='ParkingSlot',
            fields=[
                ('slot_id', models.BigIntegerField(primary_key=True, serialize=False)),
                # ★ 중요: factories의 create_slot에서 "slot_code"를 사용하므로 반드시 추가
                ('slot_code', models.CharField(max_length=20)), 
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parking_slots', to='zone_service.zone')),
                ('slot_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='parking_slots', to='zone_service.slottype')),
            ],
            options={'db_table': 'ZONE_PARKING_SLOT'},
        ),
    ]
