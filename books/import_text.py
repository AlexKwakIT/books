import urllib

from bs4 import BeautifulSoup
from django.shortcuts import redirect
from django.urls import reverse

from books.import_isbn import add_book
from books.ocr import OCR_API, Language


def use_ocr(request):
    image = request.body.decode()
    api = OCR_API(api_key="K89662893388957", language=Language.English)
    response_text = api.ocr_base64(image)
    title = get_from_worldcat_text(response_text)
    get_from_worldcat_text(title)


def get_from_worldcat_text(text):
    try:
        text = text.lower()
        valid_chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        index = 0
        while index < len(text):
            if text[index] not in valid_chars:
                text = text[:index] + " " + text[index + 1 :]
            index += 1
        while "  " in text:
            text = text.replace("  ", " ")
        text = text.strip().replace(" ", "%20")

        url = f"https://www.worldcat.org/search?qt=worldcat_org_all&q={text}"
        html = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")

        url = soup.find("td", {"class": "coverart"}).findChild("a").attrs["href"]
        get_book_by_url(None, url)
    except Exception as e:
        print(f"get_from_openlibrary: {e}")
        return None
    return None


def get_book_by_url(request):
    try:
        url = request.POST["url"]
        while url.startswith('/'):
            url = url[1:]
        html = urllib.request.urlopen(f"https://www.worldcat.org/{url}").read()
        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h1", {"class": "title"}).text.strip()
        cover_url = soup.find("img", {"class":"cover" }).attrs["src"]
        try:
            authors = (
                soup.find("td", {"id": "bib-author-cell"})
                .findChild("a")
                .text.strip()
                .split(" : ")
            )
        except:
            authors = None
        try:
            publisher = soup.find("td", {"id": "bib-publisher-cell"}).text.strip()
        except:
            publisher = None
        try:
            isbns = (
                soup.find("tr", {"id": "details-standardno"})
                .findChild("td")
                .text.strip()
                .split(" ")
            )
            isbn = None
            for part in isbns:
                if len(part) == 13:
                    isbn = part
        except:
            isbn = None
        if title:
            book = add_book(
                title=title,
                isbn=isbn,
                publisher=publisher,
                authors=authors,
                source=f"https://www.worldcat.org/{url}",
                cover_url=f"https:{cover_url}"
            )
            return redirect(book)
    except Exception as e:
        print(f"get_book_by_url: {e}")
    return reverse("book_list")
