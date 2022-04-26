import os

from django.db import transaction
from django.http import HttpResponse

from books.models import Publisher, Author, Book, Serie, Category, SubCategory
from books.settings import BASE_DIR


@transaction.atomic
def test(request):
    serie, _ = Serie.objects.get_or_create(name="Lotje")
    author, _ = Author.objects.get_or_create(name="Jaap ter Haar")
    category = Category.objects.get(name="Fiction")
    subcategory, _ = SubCategory.objects.get_or_create(name="Children", category=category)
    for book in Book.objects.filter(title__istartswith="Lotje"):
        book.serie = serie
        book.sub_category = subcategory
        book.save()
        book.authors.add(author)
    return HttpResponse(status=201, content="OK")


def import_conny_coll(request):
    book_file = os.path.join(BASE_DIR, "assets\\conny_coll.txt")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Fiction")
    subcategory = SubCategory.objects.get(category=category, name="Western")
    publisher, _ = Publisher.objects.get_or_create(name="Ridderhof")
    author, _ = Author.objects.get_or_create(name="Conrad Kobbe")
    serie, _ = Serie.objects.get_or_create(name="Conny Coll")

    for line in data:
        if line != "":
            nr, title = line.split('. ')
            book, _ = Book.objects.get_or_create(
                title=title,
                number=nr,
                publisher=publisher,
                sub_category=subcategory,
                serie=serie
            )
            book.save()
            book.authors.add(author)
    print("READY")

    return HttpResponse(status=201, content="OK")


def import_bruno_brazil(request):
    book_file = os.path.join(BASE_DIR, "assets\\brono_brazil.csv")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Lombard")
    author1, _ = Author.objects.get_or_create(name="William Vance")
    author2, _ = Author.objects.get_or_create(name="Louise Albert")
    serie, _ = Serie.objects.get_or_create(name="Bruno Brazil")

    Book.objects.filter(serie=serie).delete()

    for line in data:
        if line != "":
            nr, title = line.split(';')
            book, _ = Book.objects.get_or_create(
                title=title,
                number=nr,
                publisher=publisher,
                sub_category=subcategory,
                serie=serie
            )
            book.save()
            book.authors.add(author1)
            book.authors.add(author2)
    print("READY")

    return HttpResponse(status=201, content="OK")


def import_asterix(request):
    book_file = os.path.join(BASE_DIR, "assets\\asterix.csv")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Het Spectrum")
    author, _ = Author.objects.get_or_create(name="Goscinny")
    serie, _ = Serie.objects.get_or_create(name="Asterix")

    for line in data:
        if line != "":
            nr, title = line.split(';')
            book, _ = Book.objects.get_or_create(
                title=title,
                number=nr,
                publisher=publisher,
                sub_category=subcategory,
                serie=serie
            )
            book.save()
            book.authors.add(author)
    print("READY")

    return HttpResponse(status=201, content="OK")


def import_miranda_blaise(request):
    book_file = os.path.join(BASE_DIR, "assets\\miranda_blaise.txt")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Panda")
    author, _ = Author.objects.get_or_create(name="Peter O'Donnell")
    serie, _ = Serie.objects.get_or_create(name="Miranda Blaise")

    for line in data:
        if line != "":
            nr, title = line.split(' - ')
            book, _ = Book.objects.get_or_create(
                title=title,
                number=nr,
                publisher=publisher,
                sub_category=subcategory,
                serie=serie
            )
            book.save()
            book.authors.add(author)
    print("READY")

    return HttpResponse(status=201, content="OK")


def import_agent327(request):
    book_file = os.path.join(BASE_DIR, "assets\\agent327.csv")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Uitgeverij M")
    author, _ = Author.objects.get_or_create(name="Martin Lodewijk")
    serie, _ = Serie.objects.get_or_create(name="Agent 327")

    for line in data:
        if line != "":
            nr, title = line.split(';')
            book, _ = Book.objects.get_or_create(
                title=title,
                number=nr,
                publisher=publisher,
                sub_category=subcategory,
                serie=serie
            )
            book.save()
            book.authors.add(author)
    print("READY")

    return HttpResponse(status=201, content="OK")


def import_evert_kwok(request):
    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Syndikaat")
    author1, _ = Author.objects.get_or_create(name="de Blouw")
    author2, _ = Author.objects.get_or_create(name="Evenboer")
    serie, _ = Serie.objects.get_or_create(name="Evert Kwok")
    for i in (1, 2, 3, 4):
        book, _ = Book.objects.get_or_create(
            title=f"Evert Kwok {i}",
            number=i,
            publisher=publisher,
            sub_category=subcategory,
            serie=serie,
        )
        book.save()
        book.authors.add(author1)
        book.authors.add(author2)
    return HttpResponse(status=201, content="OK")


def import_dirkjan(request):
    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Big Balloon Publishers")
    author, _ = Author.objects.get_or_create(name="Mark Retera")
    serie, _ = Serie.objects.get_or_create(name="Dirkjan")
    for i in (1, 2, 3, 6, 9, 10, 11):
        book, _ = Book.objects.get_or_create(
            title=f"Dirkjan {i}",
            number=i,
            publisher=publisher,
            sub_category=subcategory,
            serie=serie,
        )
        book.save()
        book.authors.add(author)
    return HttpResponse(status=201, content="OK")


def import_douwe_dabbert(request):
    book_file = os.path.join(BASE_DIR, "assets\\douwe_dabbert.txt")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Standaard Uitgeverij")
    author1, _ = Author.objects.get_or_create(name="Piet Wijn")
    author2, _ = Author.objects.get_or_create(name="Thom Roep")
    serie, _ = Serie.objects.get_or_create(name="Douwe Dabbert")

    index = 0
    for title in data:
        index += 1
        book, _ = Book.objects.get_or_create(
            title=title,
            number=index,
            publisher=publisher,
            sub_category=subcategory,
            serie=serie,
        )
        book.save()
        book.authors.add(author1)
        book.authors.add(author2)
    return HttpResponse(status=201, content="OK")


def import_suske_wiske(request):
    book_file = os.path.join(BASE_DIR, "assets\\suske_wiske.csv")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    category = Category.objects.get(name="Comics")
    subcategory = SubCategory.objects.get(category=category, name="")
    publisher, _ = Publisher.objects.get_or_create(name="Standaard Uitgeverij")
    author, _ = Author.objects.get_or_create(name="W. Vandersteen")
    serie, _ = Serie.objects.get_or_create(name="Suske en Wiske")

    for line in data:
        if line != "":
            print(line)
            title, nr = line.split(';')
            book, _ = Book.objects.get_or_create(
                title=title,
                number=nr,
                publisher=publisher,
                sub_category=subcategory,
                serie=serie
            )
            book.save()
            book.authors.add(author)
    print("READY")

    return HttpResponse(status=201, content="OK")


def import_test_bob_evers(request):
    book_file = os.path.join(BASE_DIR, "assets\\bob_evers.txt")
    with open(book_file, "r") as file:
        data = file.read().split("\n")

    publisher, _ = Publisher.objects.get_or_create(name="De Eekhoorn")
    author1, _ = Author.objects.get_or_create(name="Willy van der Heide")
    author2, _ = Author.objects.get_or_create(name="Peter de Zwaan")
    serie = Serie.objects.get(name="Bob Evers")

    index = 0
    for title in data:
        index += 1
        book, _ = Book.objects.get_or_create(
            title=title,
            publisher=publisher,
        )
        book.serie = serie
        book.save()
        # book.authors.add(author1 if index<=36 else author2)

    return HttpResponse(status=201, content="OK")
