import json
import os
import urllib
from os import listdir
from os.path import isfile, join

from django.conf import settings
from django.http import StreamingHttpResponse, HttpResponse

from books.models import Author, Publisher, Book, get_combined_title, IsbnPrefix


# ISBN_978_LANGUAGE_RANGES = [
#     ['0', '5'],
#     ['7', '7'],
#     ['80', '94'],
#     ['600', '649'],
#     ['950', '989'],
#     ['9900', '9989'],
#     ['99900', '99999'],
# ]
#
# ISBN_PUBLISHER_RANGES = [
#     ['00', '02'],
#     ['04', '06'],
#     ['000', '009'],
#     ['030', '034'],
#     ['100', '397'],
#     ['714', '716'],
#     ['0350', '0399'],
#     ['0700', '0999'],
#     ['3980', '5499'],
#     ['6500', '6799'],
#     ['6860', '7139'],
#     ['7170', '7319'],
#     ['7900', '7999'],
#     ['8672', '8675'],
#     ['9730', '9877'],
#     ['55000', '64999'],
#     ['68000', '68599'],
#     ['74000', '77499'],
#     ['77540', '77639'],
#     ['77650', '77699'],
#     ['77830', '78999'],
#     ['80000', '83799'],
#     ['83850', '86719'],
#     ['86760', '86979'],
#     ['869800', '915999'],
#     ['916506', '916869'],
#     ['916908', '919599'],
#     ['919655', '972999'],
#     ['987800', '991149'],
#     ['991200', '998989'],
#     ['7320000', '7399999'],
#     ['7750000', '7753999'],
#     ['7764000', '7764999'],
#     ['7770000', '7782999'],
#     ['8380000', '8384999'],
#     ['9160000', '9165059'],
#     ['9168700', '9169079'],
#     ['9196000', '9196549'],
#     ['9911500', '9911999'],
#     ['9989900', '9999999']
# ]


# def get_isbn_parts(isbn_code):
#     isbn = isbn_code.replace("-", "").replace("&#8209;", "")
#     if len(isbn) != 13:
#         return None, None, None, None, None
#
#     isbn_prefix_element = isbn[0:3]
#     isbn_language_element = ""
#     isbn_registrant_element = ""
#     isbn_publication_element = ""
#     index = 3
#     if isbn_prefix_element == '979':
#         if isbn[index] == "8":
#             isbn_language_element = isbn[index]
#             index += 1
#         if isbn[index:index + 2] in ("10", "11", "12"):
#             isbn_language_element = isbn[index]
#             index += 2
#         else:
#             print(f"Unknown language for {isbn}")
#             return isbn
#     elif isbn_prefix_element == '978':
#         found = False
#         for start, end in ISBN_978_LANGUAGE_RANGES:
#             l = len(start)
#             if start <= isbn[index:index + l] <= end:
#                 isbn_language_element = isbn[index:index + l]
#                 index += l
#                 found = True
#                 break
#         if not found:
#             print(f"Unknown language for {isbn}")
#             return isbn
#
#     found = False
#     for start, end in ISBN_PUBLISHER_RANGES:
#         l = len(start)
#         if start <= isbn[index:index + l] <= end:
#             isbn_registrant_element = isbn[index:index + l]
#             isbn_publication_element = isbn[index + l:12]
#             found = True
#             break
#     if not found:
#         print(f"Unknown registrant for {isbn}")
#         return isbn
#
#     isbn_checksum = isbn[12]
#     return isbn_prefix_element, isbn_language_element, isbn_registrant_element, isbn_publication_element, isbn_checksum


def format_isbn(isbn_code):
    isbn = isbn_code.replace("-", "").replace("&#8209;", "")
    for isbn_prefix in IsbnPrefix.objects.all():
        if isbn.startswith(isbn_prefix.prefix_stripped):
            return isbn_prefix.prefix + "-" + isbn[len(isbn_prefix.prefix_stripped):12] + "-" + isbn[12]
    return isbn_code.replace("-", "&#8209;")


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
            return isbn_prefix.publisher, isbn_prefix.prefix
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
