import json
import os
import urllib
from os import listdir
from os.path import isfile, join

from bs4 import BeautifulSoup
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse

from books.models import Author, Publisher, Book, IsbnPrefix, format_isbn, Genre, get_combined_book_title


def cleaning():
    yield "Cleaning authors\n"
    empty = []
    for author in Author.objects.all():
        if author.number_of_books == 0:
            empty.append(author.pk)
    Author.objects.filter(pk__in=empty).delete()
    yield f"Cleaned {len(empty)} authors\n"

    yield "Cleaning publishers\n"
    empty = []
    for publisher in Publisher.objects.all():
        if publisher.number_of_books == 0:
            empty.append(publisher.pk)
    Publisher.objects.filter(pk__in=empty).delete()
    yield f"Cleaned {len(empty)} publishers\n"

    yield "Cleaning covers\n"
    media_path = settings.MEDIA_ROOT + "\\covers"
    cover_files = [f for f in listdir(media_path) if isfile(join(media_path, f))]
    count = 0
    for cover_file in cover_files:
        book = Book.objects.filter(cover_image="covers/" + cover_file)
        if not book:
            os.remove(media_path + "\\" + cover_file)
            count += 1
    yield f"Cleaned {count} covers\n"

    yield "Ready"


def clean(request):
    stream = cleaning()
    response = StreamingHttpResponse(stream, status=200, content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response


def do_test(request):
    for book in Book.objects.all():
        book.combined_title = get_combined_book_title(book)
        book.save()
    return HttpResponse(status=200, content="OK")


def get_publishers_by_isbn(request):
    IsbnPrefix.objects.all().delete()
    Publisher.objects.all().delete()

    for book in Book.objects.exclude(isbn__isnull=True):
        print(book)
        isbn = book.isbn.replace("-", "").replace("&#8209;", "")
        publisher = None
        for isbn_prefix in IsbnPrefix.objects.all():
            if isbn.startswith(isbn_prefix.prefix_stripped):
                publisher = isbn_prefix.publisher
                break
        if not publisher:
            publisher = get_publisher_by_isbn(book.isbn)
        book.publisher = publisher
        book.isbn = format_isbn(book.isbn)
        book.save()

    return HttpResponse(status=200, content="OK")


def get_publisher_by_isbn(isbn):
    isbn = isbn.replace("-", "").replace("&#8209;", "")
    for isbn_prefix in IsbnPrefix.objects.all():
        if isbn.startswith(isbn_prefix.prefix_stripped):
            return isbn_prefix.publisher
    end = 12
    while end >= 5:
        publisher_name, isbn_prefixes = get_publisher_from_prefix(isbn[0:end])
        if publisher_name:
            publisher, _ = Publisher.objects.get_or_create(name=publisher_name)
            for prefix in isbn_prefixes:
                IsbnPrefix(prefix=prefix, prefix_stripped=prefix.replace("-", ""), publisher=publisher).save()
            return publisher
        end -= 1

    publisher, _ = Publisher.objects.get_or_create(name=f"Unknown publisher")
    IsbnPrefix(prefix=isbn, prefix_stripped=isbn.replace("-", ""), publisher=publisher).save()
    return publisher


def get_publisher_from_prefix(isbn_prefix):
    url = f"https://grp.isbn-international.org/piid_rest_api/piid_search?q=*:*&fq=ISBNPrefix:({isbn_prefix})&wt=json"
    try:
        data = json.loads(urllib.request.urlopen(url).read())
        response = data["response"]
        num_found = response["numFound"]
        for i in range(0, num_found):
            doc = response["docs"][i]
            for prefix in doc["ISBNPrefix"]:
                if prefix.replace("-", "") == isbn_prefix:
                    return doc["RegistrantName"], doc["ISBNPrefix"]
    except Exception as e:
        return None, None
    return None, None


def fix_genres(request):
    ids = []
    for genre in Genre.objects.all():
        ids.append(genre.pk)
    for id in ids:
        genre = Genre.objects.filter(pk=id).first()
        if genre:
            for sub in Genre.objects.exclude(pk=genre.pk).filter(name=genre.name).all():
                for book in sub.books.all():
                    book.genres.remove(sub)
                    book.genres.add(genre)
                Genre.objects.filter(pk=sub.pk).delete()

    return HttpResponse(status=200, content="OK")


def get_genres(request):
    for book in Book.objects.filter(isbn__isnull=False, genres__isnull=True):
        get_genres_by_isbn(book)
    return HttpResponse(status=200, content="OK")


def get_genres_by_isbn(book):
    soup = get_genre_by_isbn(book, f'http://classify.oclc.org/classify2/ClassifyDemo?search-standnum-txt={book.isbn}&startRec=0')
    if soup:
        table = soup.find("table", {"id": "results-table"})
        if table is not None:
            tbody = table.find("tbody")
            trs = tbody.find_all("tr")
            for tr in trs:
                tds = tr.find_all("td")
                td = tds[0]
                span = td.find("span")
                a = span.find("a")
                href = a.attrs['href']
                url = f'http://classify.oclc.org{href}'
                get_genre_by_isbn(book, url)


def get_genre_by_isbn(book, url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", {"id": "subheadtbl"})
    if table is not None:
        tbody = table.find("tbody")
        trs = tbody.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            td = tds[0]
            cat = td.text
            print(cat)
            genre, _ = Genre.objects.get_or_create(name=cat)
            book.genres.add(genre)
        return None
    return soup
