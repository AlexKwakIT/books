import urllib

from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from books.filters import BookFilter, AuthorFilter, SeriesFilter, GenreFilter, PublisherFilter, VideoFilter
from books.forms import BookForm, WishForm
from books.models import Author, Book, Publisher, Genre, Series, Wish, Video
from books.tables import (
    AuthorTable,
    BookTable,
    PublisherTable,
    SeriesTable, GenreTable, WishTable, VideoTable,
)


class BookListView(SingleTableMixin, FilterView):
    model = Book
    table_class = BookTable
    template_name = "book_list.html"
    filterset_class = BookFilter

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        comics = Genre.objects.filter(name__icontains="comics")
        num_comics = Book.objects.filter(genres__in=comics).count()
        num_books = Book.objects.count() - num_comics
        context["num_books"] = num_books
        context["num_comics"] = num_comics
        return context

    def get_queryset(self):
        return Book.objects.order_by("combined_title")


class BookDetailView(DetailView):
    model = Book
    template_name = "book_detail.html"


class AuthorListView(SingleTableMixin, FilterView):
    model = Author
    table_class = AuthorTable
    template_name = "author_list.html"
    filterset_class = AuthorFilter


class GenreListView(SingleTableMixin, FilterView):
    model = Genre
    table_class = GenreTable
    template_name = "genre_list.html"
    filterset_class = GenreFilter


class SeriesListView(SingleTableMixin, FilterView):
    model = Series
    table_class = SeriesTable
    template_name = "series_list.html"
    filterset_class = SeriesFilter


class PublisherListView(SingleTableMixin, FilterView):
    model = Publisher
    table_class = PublisherTable
    template_name = "publisher_list.html"
    filterset_class = PublisherFilter


class WishListView(SingleTableMixin, FilterView):
    model = Wish
    table_class = WishTable
    template_name = "wish_list.html"


class VideoListView(SingleTableMixin, FilterView):
    model = Video
    table_class = VideoTable
    template_name = "video_list.html"
    filterset_class = VideoFilter


class AuthorDetailView(DetailView):
    model = Author
    template_name = "author_detail.html"


class GenreDetailView(DetailView):
    model = Genre
    template_name = "genre_detail.html"


class SerieDetailView(DetailView):
    model = Series
    template_name = "series_detail.html"


class PublisherDetailView(DetailView):
    model = Publisher
    template_name = "publisher_detail.html"


class ImportView(TemplateView):
    template_name = "isbn_import.html"


class WishCreateView(CreateView):
    model = Wish
    template_name = "wish_form.html"
    form_class = WishForm

    def form_valid(self, form):
        form.save()
        return redirect('wish_create')


class BookCreateView(CreateView):
    model = Book
    template_name = "book_form.html"
    form_class = BookForm

    def form_valid(self, form):
        form.save()
        return redirect('book_create')


class BookUpdateView(UpdateView):
    model = Book
    template_name = "book_update_form.html"
    form_class = BookForm


def book_delete(request, pk):
    book = Book.objects.filter(pk=pk).first()
    if book:
        book.delete()
    return HttpResponseRedirect(reverse("book_list"))
