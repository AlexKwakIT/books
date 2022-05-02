import django_filters
from django.forms import TextInput

from books.models import Book, Author, Genre, Series, Publisher


class BookFilter(django_filters.FilterSet):
    combined_title = django_filters.CharFilter(lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'Title contains'}))

    class Meta:
        model = Book
        fields = ["combined_title"]


class AuthorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Author
        fields = ["name"]


class GenreFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Genre
        fields = ["name"]


class SeriesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Series
        fields = ["name"]


class PublisherFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Publisher
        fields = ["name"]
