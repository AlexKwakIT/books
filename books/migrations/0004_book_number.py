# Generated by Django 4.0.3 on 2022-03-30 20:01

from django.db import migrations, models


def fill_number(apps, schema_editor):
    Book = apps.get_model('books', 'Book')
    for book in Book.objects.all():
        title = book.title.lower()
        if len(title) > 4 and title[0] >= '0' and title[0] <= '9' and title[1] >= '0' and title[1] <= '9' and title[2] == ' ':
            book.number = book.title[0:2]
            book.title = book.title[3:]
            book.save()


class Migration(migrations.Migration):

    dependencies = [
        ('books', '0003_coverocr_book'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='number',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.RunPython(fill_number, reverse_code=migrations.RunPython.noop),
    ]
