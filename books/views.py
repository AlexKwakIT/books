import urllib

from bs4 import BeautifulSoup
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DetailView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin

from books.filters import BookFilter, AuthorFilter, SerieFilter, SubCategoryFilter, PublisherFilter
from books.forms import BookForm, CoverOcrForm
from books.models import Author, Book, CoverOCR, Publisher, SubCategory, Serie
from books.tables import (
    AuthorTable,
    BookTable,
    PublisherTable,
    SerieTable, SubCategoryTable,
)


class BookListView(SingleTableMixin, FilterView):
    model = Book
    table_class = BookTable
    template_name = "book_list.html"
    filterset_class = BookFilter

    def get_context_data(self, **kwargs):
        context = super(BookListView, self).get_context_data(**kwargs)
        comics = SubCategory.objects.get(category__name="Comics")
        context["num_books"] = Book.objects.exclude(sub_category=comics).count()
        context["num_comics"] = Book.objects.filter(sub_category=comics).count()
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


class SubCategoryListView(SingleTableMixin, FilterView):
    model = SubCategory
    table_class = SubCategoryTable
    template_name = "sub_category_list.html"
    filterset_class = SubCategoryFilter


class SerieListView(SingleTableMixin, FilterView):
    model = Serie
    table_class = SerieTable
    template_name = "serie_list.html"
    filterset_class = SerieFilter


class PublisherListView(SingleTableMixin, FilterView):
    model = Publisher
    table_class = PublisherTable
    template_name = "publisher_list.html"
    filterset_class = PublisherFilter

    # def get_table_data(self):
    #     data = []
    #     for publisher in Publisher.objects.all():
    #         if publisher.number_of_books > 0:
    #             found = False
    #             index = -1
    #             for record in data:
    #                 index += 1
    #                 if record["name"] == publisher.display_name:
    #                     found = True
    #                     break
    #             if found:
    #                 data[index] = {
    #                     "pk": publisher.id,
    #                     "name": publisher.display_name,
    #                     "number_of_books": publisher.number_of_books
    #                     + data[index]["number_of_books"],
    #                 }
    #             else:
    #                 data.append(
    #                     {
    #                         "pk": publisher.id,
    #                         "name": publisher.display_name,
    #                         "number_of_books": publisher.number_of_books,
    #                     }
    #                 )
    #     return data


class AuthorDetailView(DetailView):
    model = Author
    template_name = "author_detail.html"


class SubCategoryDetailView(DetailView):
    model = SubCategory
    template_name = "sub_category_detail.html"


class SerieDetailView(DetailView):
    model = Serie
    template_name = "serie_detail.html"


class PublisherDetailView(DetailView):
    model = Publisher
    template_name = "publisher_detail.html"


class ImportView(TemplateView):
    template_name = "isbn_import.html"


class BookCreateView(CreateView):
    model = Book
    template_name = "book_form.html"
    exclude = "source"
    form_class = BookForm

    def form_valid(self, form):
        form.save()  # save form
        return redirect('book_create')


class BookUpdateView(UpdateView):
    model = Book
    template_name = "book_update_form.html"
    form_class = BookForm
    exclude = "source"


class CoverOcrView(CreateView):
    model = CoverOCR
    template_name = "cover_ocr.html"
    form_class = CoverOcrForm


def book_delete(request, pk):
    book = Book.objects.filter(pk=pk).first()
    if book:
        book.delete()
    return HttpResponseRedirect(reverse("book_list"))


def book_add(request):
    return render(request, "book_add.html")


def import_text(request, text):
    valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    for index in range(0, len(text)):
        if text[index] not in valid_chars:
            text = text[:index] + "+" + text[index + 1:]

    url = f"https://www.worldcat.org/search?qt=worldcat_org_all&q={text}&qt=results_page#%2528x0%253Abook%2Bx4%253Aprintbook%2529format"
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    data = []
    for tr in soup.find_all("tr", {"class": "menuElem"}):
        cover_art = tr.findChild("td", {"class", "coverart"})
        data.append(
            {
                "name": cover_art.findChild("a").findChild("img").attrs["title"],
                "img": cover_art.findChild("a").findChild("img").attrs["src"],
                "url": cover_art.findChild("a").attrs["href"]
            }
        )
    return render(request, 'book_choose.html', context={"data": data})


