from django import forms
from django_select2 import forms as s2forms

from .models import Book


class AuthorWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "name__icontains",
    ]


class PublisherWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]


class SerieWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains",
    ]


class SubCategorieWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "name__icontains", "category__name__icontains",
    ]


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        exclude = ("sources", "combined_title",)
        widgets = {
            "authors": AuthorWidget,
            "serie": SerieWidget,
            "sub_category": SubCategorieWidget,
            "publisher": PublisherWidget,
        }
