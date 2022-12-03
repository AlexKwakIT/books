from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from books.new_photos import new_photos
from books.export import export_excel, export_json
from books.import_by_title import get_book_by_url, import_text
from books.import_isbn import import_isbn, show_import_status
from books.import_video import video_import
from books.maintenance import clean
from books.views import (
    AuthorDetailView,
    AuthorListView,
    BookCreateView,
    BookDetailView,
    BookListView,
    BookUpdateView,
    ImportView,
    book_delete,
    PublisherDetailView,
    PublisherListView,
    SeriesListView,
    SerieDetailView, GenreListView, GenreDetailView, WishListView, WishCreateView, VideoListView
)

urlpatterns = [
    path("", BookListView.as_view(), name="book_list"),
    path("select2/", include("django_select2.urls")),
    path("admin/", admin.site.urls),

    path("export-json/", export_json, name="export_json"),
    path("export-excel/", export_excel, name="export_excel"),

    path("import/", ImportView.as_view(), name="import"),
    path("import-status/", show_import_status, name="import_status"),
    path("import-isbn/", import_isbn, name="import_isbn"),

    path("books/add/isbn/<slug:isbn>/", import_isbn, name="book_add_isbn"),
    path("books/detail/<pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/scrape/isbn/<slug:isbn>/", import_isbn, name="book_scrape_isbn"),
    path("books/scrape/text/<slug:text>/", import_text, name="book_scrape_text"),
    path("books/scrape/url/", get_book_by_url, name="book_scrape_url"),
    path("books/<pk>/update/", BookUpdateView.as_view(), name="book_update"),
    path("books/create/", BookCreateView.as_view(), name="book_create"),
    path("books/delete/<pk>/", book_delete, name="book_delete"),

    path("wish/create/", WishCreateView.as_view(), name="wish_create"),
    path("wish/list/", WishListView.as_view(), name="wish_list"),

    path("authors/", AuthorListView.as_view(), name="author_list"),
    path("authors/<pk>/", AuthorDetailView.as_view(), name="author_detail"),

    path("genres/", GenreListView.as_view(), name="genre_list"),
    path("genres/<pk>/", GenreDetailView.as_view(), name="genre_detail"),

    path("series/", SeriesListView.as_view(), name="series_list"),
    path("series/<pk>/", SerieDetailView.as_view(), name="series_detail"),

    path("publishers/", PublisherListView.as_view(), name="publisher_list"),
    path("publishers/<pk>/", PublisherDetailView.as_view(), name="publisher_detail"),

    path("video/series/", VideoListView.as_view(), name="video_series_list"),

    path("new-photos/", new_photos, name="new_photos"),

    path("maintenance", TemplateView.as_view(template_name='maintenance.html'), name="maintenance"),
    path("clean/", clean, name="clean"),
    path("do-test/", video_import, name="do_test"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
