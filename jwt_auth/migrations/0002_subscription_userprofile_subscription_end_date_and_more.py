# Generated by Django 4.1.3 on 2023-04-11 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("jwt_auth", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50, unique=True)),
                ("credit", models.IntegerField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name="userprofile",
            name="subscription_end_date",
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="subscription_start_date",
            field=models.DateField(default=None, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="user_credits",
            field=models.IntegerField(default=1000),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="current_subscription",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="jwt_auth.subscription",
            ),
        ),
    ]
