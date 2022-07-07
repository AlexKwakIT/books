import copy
import datetime
import json
import urllib
from tempfile import NamedTemporaryFile

import requests
from bs4 import BeautifulSoup
from django.core.files import File
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from books.maintenance import get_publisher_by_isbn, get_genres_by_isbn
from books.models import (
    Author,
    Book,
    Series,
    Genre,
)

PROGRESS = []
SOURCES = [
    {"source": "bibliotheek.nl", "num": 0},
    {"source": "boekenplatform.nl", "num": 0},
    {"source": "vindboek.nl", "num": 0},
    {"source": "worldcat.org", "num": 0},
    {"source": "openlibrary.org", "num": 0},
]


def import_isbn(request, isbn):
    if len(isbn) == 10:
        isbn = "978" + isbn[:9]
        sum = 0
        for i in range(0, 12):
            f = 1 if i % 2 == 0 else 3
            sum += f * int(isbn[i])
        mod = sum % 10
        if mod == 0:
            isbn += '0'
        else:
            isbn += str(10 - int(mod))
    book = get_book("", isbn)
    if book:
        return HttpResponseRedirect(reverse("book_detail", kwargs={"pk": book.pk}))
    else:
        return HttpResponseRedirect(reverse("book_list"))


def get_book(genre, isbn):
    book = None
    add_isbn_to_progress(isbn)
    for source in SOURCES:
        PROGRESS.append(source.get("source"))
        b = try_source(source.get("source"), genre, isbn)
        if b:
            book = copy.copy(b)
            PROGRESS[len(PROGRESS) - 1] += f": {book.title}"
            source["num"] = source.get("num") + 1
        else:
            PROGRESS[len(PROGRESS) - 1] += f": NOT FOUND"
    if book:
        with open("isbn.lst", "a") as myfile:
            myfile.write(f"{book.isbn}\n")
    return book


def try_source(source, genre, isbn):
    if source == "openlibrary.org":
        return get_from_openlibrary(genre, isbn)
    if source == "bibliotheek.nl":
        return get_from_bibliotheek_nl(genre, isbn)
    if source == "boekenplatform.nl":
        return get_from_boekenplatform_nl(genre, isbn)
    if source == "vindboek.nl":
        return get_from_vindboek_nl(genre, isbn)
    if source == "worldcat.org":
        return get_from_worldcat_org(genre, isbn)
    return None


def get_from_openlibrary(genre, isbn):
    def get_json(url):
        url = f"https://openlibrary.org/{url}.json"
        return json.loads(urllib.request.urlopen(url).read())

    try:
        data = get_json(f"isbn/{isbn}")
        if "title" in data:
            title = data["title"]
            summary = data["subtitle"] if "subtitle" in data else ""
        else:
            work = get_json(data["works"][0])
            title = work["title"]
            summary = work["description"]
        authors = []
        for author in data["authors"]:
            author_json = get_json(author["key"])
            authors.append(author_json["name"])
        if "contributions" in data:
            for author in data["contributions"]:
                authors.append(author)
        if title:
            book = add_book(
                title=title,
                isbn=isbn,
                summary=summary,
                genre=genre,
                authors=authors,
            )
            return book
    except Exception as e:
        print(f"get_from_openlibrary: {e}")
    return None


def get_from_bibliotheek_nl(genre, isbn):
    url = f"https://www.bibliotheek.nl/catalogus.catalogus.html?q={isbn}"
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        h3 = soup.find("h3")
        if h3.text.startswith("Helaas"):
            return None
        author = h3.findChildren()[0].text.strip()
        title = h3.findChildren()[1].text.strip()
        summary = soup.find("p", {"class": "maintext separate"}).text.strip()
        if title:
            book = add_book(
                title=title,
                isbn=isbn,
                genre=genre,
                summary=summary,
                authors=[author],
            )
            return book
    except Exception as e:
        print(f"get_from_bibliotheek_nl: {e}")
    return None


def get_from_worldcat_org(genre, isbn):
    url = f"https://www.worldcat.org/search?q={isbn}&qt=owc_search"
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        td_coverart = soup.find("td", {"class": "coverart"})

        cover_img = soup.find("img", {"class": "cover"})
        cover_url = "https:" + cover_img.attrs["src"] if cover_img else None

        detail_url = td_coverart.findChild("a").attrs["href"]
        url = f"https://www.worldcat.org{detail_url}"
        html = urllib.request.urlopen(url).read().decode()
        if isbn not in html:
            raise Exception("ISBN not found in HTML")
        soup = BeautifulSoup(html, "html.parser")

        if not cover_url:
            cover_url = "https:" + soup.find("img", {"class": "cover"}).attrs["src"]

        titles = soup.find("h1", {"class": "title"}).text.strip().split((" : "))
        title = titles[0]
        summary = None
        if len(titles) > 1:
            summary = titles[1]
        try:
            authors = (
                soup.find("td", {"id": "bib-author-cell"}).text.strip().split("; ")
            )
        except:
            authors = None
        try:
            summary = soup.find("div", {"class": "abstracttxt"}).text.strip()
        except:
            pass

        if title:
            book = add_book(
                title=title,
                summary=summary,
                isbn=isbn,
                genre=genre,
                authors=authors,
                cover_url=cover_url,
            )
            return book
    except Exception as e:
        print(f"get_from_worldcat_org: {e}")
    return None


def get_from_boekenplatform_nl(genre, isbn):
    url = f"https://www.boekenplatform.nl/isbn/{isbn}"
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        tds = soup.find_all("td")
        for td in tds:
            if td.text.strip() == "Hoofdtitel":
                tdText = td.nextSibling
                title = tdText.text.strip()
                book = add_book(title=title, isbn=isbn, genre=genre)
                return book
    except Exception as e:
        if e.code == 404:
            return None
        print(f"get_from_boekenplatform_nl : {e}")
    return None


def get_from_vindboek_nl(genre, isbn):
    try:
        url = f"https://vindboek.nl/books/term/{isbn}"
        data = urllib.request.urlopen(url)
        html = data.read()
        if html.decode().startswith("No result"):
            return None
        soup = BeautifulSoup(html, "html.parser")
        authors = []
        title = soup.find("h1").text.strip()
        if title and title != isbn:
            for dt in soup.find_all("dt"):
                if dt.text.strip() == "Auteur:":
                    authors.append(dt.find_next_sibling().next.next.text.strip())
                cover_url = None
                cover_image = soup.find("div", {"class": "col-md-4 col-6 m-auto"})
                if cover_image:
                    cover_image = cover_image.find("img", {"class": "img-fluid"})
                if cover_image:
                    cover_url = cover_image.attrs["src"]
            book = add_book(
                title=title,
                isbn=isbn,
                genre=genre,
                authors=authors,
                cover_url=cover_url,
            )
            return book
        return None
    except Exception as e:
        print(f"get_from_vindboek_nl: {e}")


def add_book(
        title,
        isbn,
        summary=None,
        authors=None,
        series=None,
        genre=None,
        cover_url=None,
):
    try:
        if isbn:
            book, _ = Book.objects.get_or_create(isbn=isbn)
            book.publisher = get_publisher_by_isbn(isbn)
        else:
            book = Book()
        book.title = title
        if summary and len(summary) > 0:
            book.summary = summary
        if series and len(series) > 0:
            series, _ = Series.objects.get_or_create(name=series)
            book.series = series
        if cover_url:
            r = requests.get(cover_url)

            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(r.content)
            length = img_temp.tell()
            img_temp.flush()
            if length > 2000:
                book.cover_image.save(f"{isbn}.jpg", File(img_temp), save=True)

        book.save()
        if genre and len(genre) > 0:
            genre, _ = Genre.objects.get_or_create(name=genre)
            book.genres.add(genre)
        else:
            get_genres_by_isbn(book)
        if authors and len(authors) > 0:
            for author in book.authors.all():
                if author.number_of_books <= 1:
                    Author.objects.get(pk=author.pk).delete()
            book.authors.clear()
            for author in list(dict.fromkeys(authors)) or []:
                if len(author) > 0:
                    author, _ = Author.objects.get_or_create(name=author)
                    book.authors.add(author)
        return book
    except Exception as e:
        print(f"add_book: {e}")
        return None


def show_import_status(request):
    return HttpResponse(status=201, content="<br>".join(PROGRESS))


def add_isbn_to_progress(isbn):
    e = datetime.datetime.now()
    t = "%02d:%02d:%02d" % (e.hour, e.minute, e.second)
    PROGRESS.append(f"<br><b>{t} ISBN: {isbn}</b>")


def add_title_to_progress(title):
    index = len(PROGRESS) - 1
    while index >= 0:
        line = PROGRESS[index]
        if "<b>" in line:
            line = line.split("</b>")[0] + "</b> (" + title + ")"
            PROGRESS[index] = line
            break
        index -= 1


def add_source_to_progress(source):
    if "<b>" in PROGRESS[len(PROGRESS) - 1]:
        PROGRESS.append(source)
    else:
        PROGRESS[len(PROGRESS) - 1] += ", " + source
