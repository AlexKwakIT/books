import django_filters

from books.models import Book, Author, SubCategory, Serie, Publisher


class BookFilter(django_filters.FilterSet):
    combined_title = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ["combined_title"]


class AuthorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Author
        fields = ["name"]


class SubCategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = SubCategory
        fields = ["name"]


class SerieFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Serie
        fields = ["name"]


class PublisherFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Publisher
        fields = ["name"]
