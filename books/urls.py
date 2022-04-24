from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from books.export import export_excel, export_json
from books.import_isbn import import_isbn, show_import_status
from books.import_text import use_ocr, get_book_by_url
from books.maintenance import clean, do_test
from books.views import (
    AuthorDetailView,
    AuthorListView,
    BookCreateView,
    BookDetailView,
    BookListView,
    BookUpdateView,
    CoverOcrView,
    ImportView,
    book_delete,
    PublisherDetailView,
    PublisherListView,
    SerieListView,
    SerieDetailView, SubCategoryListView, SubCategoryDetailView, book_add, import_text,
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
    path("books/add/", book_add, name="book_add"),
    path("books/scrape/text/<slug:text>/", import_text, name="book_scrape_text"),
    path("books/detail/<pk>/", BookDetailView.as_view(), name="book_detail"),
    path("books/scrape/isbn/<slug:isbn>/", import_isbn, name="book_scrape_isbn"),
    path("books/scrape/url/", get_book_by_url, name="book_scrape_url"),
    path("books/<pk>/update/", BookUpdateView.as_view(), name="book_update"),
    path("books/create/", BookCreateView.as_view(), name="book_create"),
    path("books/delete/<pk>/", book_delete, name="book_delete"),
    path("authors/", AuthorListView.as_view(), name="author_list"),
    path("authors/<pk>/", AuthorDetailView.as_view(), name="author_detail"),
    path("sub-categories/", SubCategoryListView.as_view(), name="sub_category_list"),
    path("sub-categories/<pk>/", SubCategoryDetailView.as_view(), name="sub_category_detail"),
    path("series/", SerieListView.as_view(), name="serie_list"),
    path("series/<pk>/", SerieDetailView.as_view(), name="serie_detail"),
    path("publishers/", PublisherListView.as_view(), name="publisher_list"),
    path("publishers/<pk>/", PublisherDetailView.as_view(), name="publisher_detail"),
    path("cover-ocr/", CoverOcrView.as_view(), name="cover_ocr"),
    path("use-ocr/", use_ocr, name="use_ocr"),
    path("clean/", clean, name="clean"),
    path("do-test/", do_test, name="do_test"),

    path("maintenance", TemplateView.as_view(template_name='maintenance.html'), name="maintenance"),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
