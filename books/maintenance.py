import json
import os
import urllib
from os import listdir
from os.path import isfile, join

import pyisbn
from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse

from books.models import Author, Publisher, Book, get_combined_title, IsbnPrefix

ISBN_RANGES = [
    ['00', '02'],
    ['04', '06'],
    ['000', '009'],
    ['030', '034'],
    ['100', '397'],
    ['714', '716'],
    ['0350', '0399'],
    ['0700', '0999'],
    ['3980', '5499'],
    ['6500', '6799'],
    ['6860', '7139'],
    ['7170', '7319'],
    ['7900', '7999'],
    ['8672', '8675'],
    ['9730', '9877'],
    ['55000', '64999'],
    ['68000', '68599'],
    ['74000', '77499'],
    ['77540', '77639'],
    ['77650', '77699'],
    ['77830', '78999'],
    ['80000', '83799'],
    ['83850', '86719'],
    ['86760', '86979'],
    ['869800', '915999'],
    ['916506', '916869'],
    ['916908', '919599'],
    ['919655', '972999'],
    ['987800', '991149'],
    ['991200', '998989'],
    ['7320000', '7399999'],
    ['7750000', '7753999'],
    ['7764000', '7764999'],
    ['7770000', '7782999'],
    ['8380000', '8384999'],
    ['9160000', '9165059'],
    ['9168700', '9169079'],
    ['9196000', '9196549'],
    ['9911500', '9911999'],
    ['9989900', '9999999']
]


def format_isbn(isbn_code):
    isbn = isbn_code.replace("-", "").replace("&#8209;", "")
    isbn_prefix_element = isbn[0:3]
    index = 3
    if isbn[index] == "0":
        isbn_registration_group_element = isbn[index]
        index += 1
    elif isbn[index:index + 2] == "90":
        isbn_registration_group_element = isbn[index:index + 2]
        index += 2
    else:
        print(f"Unknown language for {isbn}")
        return isbn

    found = False
    for start, end in ISBN_RANGES:
        l = len(start)
        if start <= isbn[index:index + l] <= end:
            isbn_registrant_element = isbn[index:index + l]
            isbn_publication_element = isbn[index + l:12]
            found = True
            break
    if not found:
        print(f"Unknown registrant for {isbn}")
        return isbn

    isbn_checksum = isbn[12]
    return f"{isbn_prefix_element}&#8209;{isbn_registration_group_element}&#8209;{isbn_registrant_element}&#8209;{isbn_publication_element}&#8209;{isbn_checksum}"


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
        book = Book.objects.filter(cover="covers/" + cover_file)
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
        book.combined_title = get_combined_title(book)
        book.save()


def get_publishers_by_isbn(request):
    IsbnPrefix.objects.all().delete()
    Publisher.objects.all().delete()

    for book in Book.objects.exclude(isbn__isnull=True):
        print(f"1 Book {book}")
        isbn = book.isbn.replace("-", "")
        try:
            if isbn.startswith('97'):
                if not pyisbn.Isbn(isbn).validate():
                    print(f"Invalid isbn: {book.isbn}")
                    continue
            else:
                isbn = pyisbn.Isbn10(isbn).convert()
                if not pyisbn.Isbn(isbn).validate():
                    print(f"Invalid isbn: {book.isbn}")
                    continue
        except:
            isbn = None
        book.isbn = isbn
        book.save()

    for book in Book.objects.exclude(isbn__isnull=True):
        print(f"2 Book {book}")
        isbn = book.isbn.replace("-", "")
        isbn_prefix_element = book.isbn[0:3]
        isbn = isbn[3:]
        if isbn[0] == "0":
            isbn_registration_group_element = isbn[0]
            isbn = isbn[1:]
        elif isbn[0:2] == "90":
            isbn_registration_group_element = isbn[0:2]
            isbn = isbn[2:]
        else:
            print(f"Unknown language for {book}, {isbn}")
            continue

        for start, end in ISBN_RANGES:
            l = len(start)
            if start <= isbn[0:l] <= end:
                isbn_registrant_element = isbn[0:l]
                isbn_publication_element = isbn[l:13]
                isbn_prefix = f"{isbn_prefix_element}-{isbn_registration_group_element}-{isbn_registrant_element}"
                url = f"https://grp.isbn-international.org/piid_rest_api/piid_search?q=*:*&fq=ISBNPrefix:({isbn_prefix})&wt=json"
                try:
                    data = json.loads(urllib.request.urlopen(url).read())
                    response = data["response"]
                    num_found = response["numFound"]
                    if num_found == 0:
                        raise Exception("not found")
                    publishername = response["docs"][0]["RegistrantName"]
                    publisher, _ = Publisher.objects.get_or_create(name=publishername)
                    prefix, _ = IsbnPrefix.objects.get_or_create(prefix=isbn_prefix, publisher=publisher)
                    print(f"found {publishername}")
                except Exception as e:
                    publishername = f"Unknown publisher {isbn_prefix}"
                    publisher, created = Publisher.objects.get_or_create(name=publishername)
                    prefix, _ = IsbnPrefix.objects.get_or_create(prefix=isbn_prefix, publisher=publisher)
                book.publisher = publisher
                book.save()

    return HttpResponse(status=200, content="OK")
