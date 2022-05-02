from django import forms
from django_select2 import forms as s2forms

from .models import Book, Wish


class AuthorWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
    ]


class PublisherWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]


class SeriesWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]


class GenreWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
    ]


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ("combined_title",)
        widgets = {
            "authors": AuthorWidget,
            "series": SeriesWidget,
            "genres": GenreWidget,
            "publisher": PublisherWidget,
        }


class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        fields = ("author", "title", "remarks",)
