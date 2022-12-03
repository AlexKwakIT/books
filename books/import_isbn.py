import datetime
import functools
import json
import threading
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

lock = threading.Lock()

PROGRESS = []
SOURCES = [
    {"source": "bibliotheek.nl", "num": 0},
    {"source": "boekenplatform.nl", "num": 0},
    {"source": "vindboek.nl", "num": 0},
    {"source": "worldcat.org", "num": 0},
    {"source": "openlibrary.org", "num": 0},
]
BOOK = []


def import_isbn(request, isbn):

    PROGRESS.clear()
    isbn = isbn.replace("-", "")
    log("<b>ISBN</b>", f"<b>{isbn}</b>")
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
    get_book("", isbn)
    return HttpResponseRedirect(reverse("import"))


def get_book(genre, isbn):
    threads = []

    thread1 = threading.Thread(target=get_from_openlibrary, args=(genre, isbn))
    threads.append(thread1)
    thread1.start()

    thread2 = threading.Thread(target=get_from_bibliotheek_nl, args=(genre, isbn))
    threads.append(thread2)
    thread2.start()

    thread3 = threading.Thread(target=get_from_boekenplatform_nl, args=(genre, isbn))
    threads.append(thread3)
    thread3.start()

    thread4 = threading.Thread(target=get_from_vindboek_nl, args=(genre, isbn))
    threads.append(thread4)
    thread4.start()

    thread5 = threading.Thread(target=get_from_worldcat_org, args=(genre, isbn))
    threads.append(thread5)
    thread5.start()


def get_from_openlibrary(genre, isbn):
    log("OpenLibrary.org", "start")
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
        if "authors" in data:
            for author in data["authors"]:
                author_json = get_json(author["key"])
                authors.append(author_json["name"])
        if "contributions" in data:
            for author in data["contributions"]:
                authors.append(author)
        if title:
            add_book(
                title=title,
                isbn=isbn,
                summary=summary,
                genre=genre,
                authors=authors,
            )
            log("OpenLibrary.org", "FOUND")
    except Exception as e:
        log("OpenLibrary.org", f"{e}")
    return None


def get_from_bibliotheek_nl(genre, isbn):
    log("Bibliotheek.nl", "start")
    url = f"https://www.bibliotheek.nl/catalogus.catalogus.html?q={isbn}"
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        h3 = soup.find("h3")
        if not h3.text.startswith("Helaas"):
            href = h3.findChildren()[0]['href']
            url = f"https://www.bibliotheek.nl{href}"
            html = urllib.request.urlopen(url).read()
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find("span", "title").text.strip()
            author = soup.find("span", "creator").text.strip()
            summary = soup.find("div", {"class": "intro"}).text.strip()

            if title:
                add_book(
                    title=title,
                    isbn=isbn,
                    genre=genre,
                    summary=summary,
                    authors=[author],
                )
                log("Bibliotheek.nl", "FOUND")
        log("Bibliotheek.nl", "ended")
    except Exception as e:
        log("Bibliotheek.nl", f"{e}")


def get_from_worldcat_org(genre, isbn):
    log("WorldCat.org", "start")
    url = f"https://www.worldcat.org/search?q={isbn}&qt=owc_search"
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        td_coverart = soup.find("td", {"class": "coverart"})

        cover_img = soup.find("img", {"class": "cover"})
        cover_url = "https:" + cover_img.attrs["src"] if cover_img else None

        detail_url = td_coverart.findChild("a").attrs["href"]
        url = f"https://www.worldcat.org{detail_url}"
        html = urllib.request.urlopen(url, timeout=5).read().decode()
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
            add_book(
                title=title,
                summary=summary,
                isbn=isbn,
                genre=genre,
                authors=authors,
                cover_url=cover_url,
            )
            log("WorldCat.org", "FOUND")
        else:
            log("WorldCat.org", "ended")
    except Exception as e:
        log("WorldCat.org", f"{e}")


def get_from_boekenplatform_nl(genre, isbn):
    log("BoekenPlatform.nl", "start")
    url = f"https://www.boekenplatform.nl/isbn/{isbn}"
    try:
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")
        tds = soup.find_all("td")
        for td in tds:
            if td.text.strip() == "Hoofdtitel":
                tdText = td.nextSibling
                title = tdText.text.strip()
                add_book(title=title, isbn=isbn, genre=genre)
                log("found in BoekenPlatform.nl")
            else:
                log("BoekenPlatform.nl", "ended")
    except Exception as e:
        if e.code != 404:
            log("BoekenPlatform.nl", f"{e}")
        else:
            log("BoekenPlatform.nl", "ended")


def get_from_vindboek_nl(genre, isbn):
    log("VindBoek.nl", "start")
    try:
        url = f"https://vindboek.nl/books/term/{isbn}"
        data = urllib.request.urlopen(url, timeout=5)
        html = data.read()
        if html.decode().startswith("No result"):
            log("VindBoek.nl", "ended")
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
            add_book(
                title=title,
                isbn=isbn,
                genre=genre,
                authors=authors,
                cover_url=cover_url,
            )
            log("VindBoek.nl", "FOUND")
        else:
            log("VindBoek.nl", "ended")
    except Exception as e:
        log("VindBoek.nl", f"{e}")


def synchronized(lock):
    """ Synchronization decorator """
    def wrap(f):
        @functools.wraps(f)
        def newFunction(*args, **kw):
            with lock:
                return f(*args, **kw)
        return newFunction
    return wrap


@synchronized(lock)
def add_book(
        title,
        isbn,
        summary=None,
        authors=None,
        series=None,
        genre=None,
        cover_url=None,
):
    if Book.objects.filter(isbn=isbn).exists():
        log("<b>Book already exists</b>", "")
        return
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
        url = reverse("book_detail", args=[book.pk])
        log("<b>Book found</b>", f'<a href="{url}">See book</a>')
        return book
    except Exception as e:
        log("Add book", f"{e}")


def show_import_status(request):
    html = "<table>"
    for mess1, mess2 in PROGRESS:
        if mess2 == "":
            html += f'<tr><td colspan="2">{mess1}</td></tr>'
        else:
            html += f'<tr><td>{mess1}</td><td>{mess2}</td></tr>'
    html += "</table>"
    return HttpResponse(status=201, content=html)


def add_isbn_to_progress(isbn):
    e = datetime.datetime.now()
    t = "%02d:%02d:%02d" % (e.hour, e.minute, e.second)
    print(f"<br><b>{t} ISBN: {isbn}</b>")


def add_title_to_progress(title):
    index = len(PROGRESS) - 1
    while index >= 0:
        line = PROGRESS[index]
        if "<b>" in line:
            line = line.split("</b>")[0] + "</b> (" + title + ")"
            PROGRESS[index] = line
            break
        index -= 1


def log(source, message):
    found = False
    for index in range(0, len(PROGRESS)):
        mess1, mess2 = PROGRESS[index]
        if mess1 == source:
            PROGRESS[index] = (source, message)
            found = True
    if not found:
        PROGRESS.append((source, message))
    e = datetime.datetime.now()
    t = "%02d:%02d:%02d" % (e.hour, e.minute, e.second)
    print(f"{t}: {source} {message}")
