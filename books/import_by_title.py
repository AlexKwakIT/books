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

    url = f"https://www.worldcat.org/search?qt=worldcat_org_all&q={text}"
    # print(url)
    # html = urllib.request.urlopen(url).read()
    #
    # link = "http://example.com"
    r = urllib.request.urlopen(url)
    # r.add_header('Cookie', 'sessionid=13cxrt4uytfc6ijvgeoflmb3u9jmjuhil; csrftoken=jdEKPN8iL62hdaq1hmMuID9DMALiiDIq')
    r.add_header('Upgrade-Insecure-Requests', '1')
    r.add_header('Accept-Encoding', 'gzip, deflate, sdch, br')
    r.add_header('User-Agent',
                 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36')
    r.add_header('Connection', 'keep-alive')
    r.add_header('Cache-Control', 'max-age=0')
    r.add_header('Accept-Language', 'en-US,en;q=0.8,pt;q=0.6')
    r.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
    response = urllib.urlopen(r)
    html = response.read()

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
