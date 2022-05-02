from django.contrib import admin

from books.models import (
    Author,
    Book,
    Genre,
    Publisher,
    Series,
)


class BookAdmin(admin.ModelAdmin):
    pass


class AuthorAdmin(admin.ModelAdmin):
    pass


class PublisherAdmin(admin.ModelAdmin):
    pass


class SeriesAdmin(admin.ModelAdmin):
    pass


class GenreAdmin(admin.ModelAdmin):
    pass


admin.site.register(Book, BookAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Series, SeriesAdmin)
admin.site.register(Genre, GenreAdmin)
