# Generated by Django 5.0 on 2024-11-23 11:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App_Escolar', '0017_curso_profesor_profesor_cursos_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curso',
            name='profesor',
        ),
        migrations.AlterField(
            model_name='curso',
            name='estudiantes',
            field=models.ManyToManyField(blank=True, related_name='cursos', to='App_Escolar.estudiante'),
        ),
        migrations.AlterField(
            model_name='curso',
            name='limite_estudiantes',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='curso',
            name='profesor_jefe',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cursos', to='App_Escolar.profesorjefe'),
        ),
    ]
