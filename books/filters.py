import django_filters
from django.db.models import Q
from django.forms import TextInput

from books.models import Book, Author, Genre, Series, Publisher, Video


class BookFilter(django_filters.FilterSet):
    combined_title = django_filters.CharFilter(lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'Title contains'}))
    isbn = django_filters.CharFilter(lookup_expr="icontains", widget=TextInput(attrs={'placeholder': 'ISBN contains'}))

    class Meta:
        model = Book
        fields = ["combined_title", "isbn"]


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


class VideoFilter(django_filters.FilterSet):
    combined_title = django_filters.CharFilter(method='my_custom_filter',label="Search")

    class Meta:
        model = Video
        fields = ["type", "combined_title"]

    def my_custom_filter(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(seasons__icontains=value) | Q(series__icontains=value)
        )
