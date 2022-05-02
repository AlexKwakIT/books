import urllib

from bs4 import BeautifulSoup
from django.shortcuts import redirect, render
from django.urls import reverse

from books.import_isbn import add_book


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


def get_book_by_url(request):
    try:
        url = request.POST["url"]
        while url.startswith('/'):
            url = url[1:]
        html = urllib.request.urlopen(f"https://www.worldcat.org/{url}").read()
        soup = BeautifulSoup(html, "html.parser")

        title = soup.find("h1", {"class": "title"}).text.strip()
        cover_url = soup.find("img", {"class": "cover"}).attrs["src"]
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
                authors=authors,
                cover_url=f"https:{cover_url}"
            )
            return redirect(book)
    except Exception as e:
        print(f"get_book_by_url: {e}")
    return reverse("book_list")
