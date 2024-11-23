# Generated by Django 5.0 on 2024-11-23 10:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_Escolar', '0012_alter_curso_limite_estudiantes'),
    ]

    operations = [
        migrations.AddField(
            model_name='estudiante',
            name='curso',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estudiantes', to='App_Escolar.curso'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='grado',
            field=models.CharField(choices=[('1-A', '1° Básico A'), ('2-A', '2° Básico A'), ('3-A', '3° Básico A'), ('4-A', '4° Básico A'), ('5-A', '5° Básico A'), ('6-A', '6° Básico A'), ('7-A', '7° Básico A'), ('8-A', '8° Básico A')], max_length=10, unique=True),
        ),
        migrations.AlterField(
            model_name='curso',
            name='limite_estudiantes',
            field=models.PositiveIntegerField(default=4),
        ),
        migrations.AlterField(
            model_name='estudiante',
            name='asignaturas',
            field=models.ManyToManyField(blank=True, related_name='estudiantes', to='App_Escolar.asignatura'),
        ),
    ]