# Generated by Django 3.2.5 on 2021-10-26 14:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Research',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('active', models.BooleanField(default=True)),
                ('createdat', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
                ('updatedat', models.DateTimeField(auto_now=True, db_column='updatedAt')),
            ],
            options={
                'db_table': 'Researchs',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Sector',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, null=True)),
                ('createdat', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
            ],
            options={
                'db_table': 'Sectors',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('ticket', models.CharField(max_length=6)),
                ('is_yahoo_available', models.BooleanField(default=False)),
                ('createdat', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
                ('updatedat', models.DateTimeField(auto_now=True, db_column='updatedAt')),
                ('sector', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='variableIncome.sector', verbose_name='Setor')),
            ],
            options={
                'db_table': 'Stocks',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RecommendationImporterLoger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdat', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
                ('updatedat', models.DateTimeField(auto_now=True, db_column='updatedAt')),
                ('text', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL, verbose_name='Usu??rio')),
            ],
        ),
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dateinitial', models.DateField()),
                ('datefinal', models.DateField()),
                ('rating', models.CharField(choices=[('CALL', 'Compra'), ('PUT', 'Venda'), ('NEUTRAL', 'Neutro')], max_length=30, verbose_name='Rating')),
                ('target', models.FloatField(verbose_name='Pre??o Alvo')),
                ('status', models.BooleanField(default=True)),
                ('createdat', models.DateTimeField(auto_now_add=True, db_column='createdAt')),
                ('updatedat', models.DateTimeField(auto_now=True, db_column='updatedAt')),
                ('research', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='variableIncome.research', verbose_name='Fonte')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='variableIncome.stock', verbose_name='A????o')),
            ],
            options={
                'db_table': 'Recommendations',
                'ordering': ('-datefinal',),
                'managed': True,
            },
        ),
    ]
