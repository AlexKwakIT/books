import django_tables2 as tables
from django.db.models import Count
from django.utils.safestring import mark_safe
from django_tables2.utils import A  # alias for Accessor

from books.models import Author, Book, Publisher, SubCategory, Serie


class BookTable(tables.Table):
    cover = tables.Column(orderable=False)
    combined_title = tables.LinkColumn("book_detail", args=[A("pk")], verbose_name="Title")
    publisher = tables.LinkColumn(
        "publisher_detail",
        args=[A("publisher_id")],
        verbose_name="Publisher",
    )
    authors = tables.Column(empty_values=(), orderable=False)
    category = tables.Column(accessor="sub_category", verbose_name="Category")
    serie = tables.Column()

    class Meta:
        model = Book
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ("cover", "combined_title", "isbn", "publisher", "authors", "category", "serie")


    def render_authors(self, value, record):
        return mark_safe(record.author_list(True))

    def render_publisher(self, value, record):
        if value.name.startswith("Unknown"):
            return "?"
        return value.name

    def render_cover(self, record, value):
        return mark_safe(f"<img src='{record.cover.url}' width='150' />")

    def render_title(self, record, value):
        text = f'<a href="{record.get_absolute_url()}">{record}</a>'
        if record.summary:
            text += f"<br><i>{record.summary}</i>"
        return mark_safe(text)

    def render_isbn(self, record, value):
        return mark_safe(record.formatted_isbn)


class AuthorTable(tables.Table):
    name = tables.LinkColumn("author_detail", args=[A("pk")])
    number_of_books = tables.Column(empty_values=())

    class Meta:
        model = Author
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ["name", "number_of_books"]

    def order_number_of_books(self, queryset, is_descending):
        queryset = queryset.annotate(num_books=Count("books")).order_by(
            ("-" if is_descending else "") + "num_books"
        )
        return (queryset, True)


class SubCategoryTable(tables.Table):
    name = tables.LinkColumn("sub_category_detail", args=[A("pk")], empty_values=[])
    number_of_books = tables.Column(empty_values=())

    class Meta:
        model = SubCategory
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ["name", "number_of_books"]

    def render_name(self, record, value):
        return record.extended_name

    def order_number_of_books(self, queryset, is_descending):
        queryset = queryset.annotate(num_books=Count("books")).order_by(
            ("-" if is_descending else "") + "num_books"
        )
        return (queryset, True)


class SerieTable(tables.Table):
    name = tables.LinkColumn("serie_detail", args=[A("pk")])
    number_of_books = tables.Column(empty_values=())

    class Meta:
        model = Serie
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ["name", "number_of_books"]

    def order_number_of_books(self, queryset, is_descending):
        queryset = queryset.annotate(num_books=Count("books")).order_by(
            ("-" if is_descending else "") + "num_books"
        )
        return (queryset, True)


class PublisherTable(tables.Table):
    name = tables.LinkColumn("publisher_detail", args=[A("pk")])
    number_of_books = tables.Column(empty_values=())

    class Meta:
        model = Publisher
        template_name = "django_tables2/bootstrap-responsive.html"
        fields = ["name", "number_of_books"]

    def order_number_of_books(self, queryset, is_descending):
        queryset = queryset.annotate(num_books=Count("books")).order_by(
            ("-" if is_descending else "") + "num_books"
        )
        return (queryset, True)
