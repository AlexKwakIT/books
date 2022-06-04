import io
import json
from datetime import date
from datetime import datetime

import xlsxwriter
from django.http import FileResponse

from books.models import Book, Genre, Series, Author, format_isbn, Wish


def export_json(request):
    books = []
    for book in Book.objects.order_by("combined_title"):
        books.append(
            {
                "id": book.pk,
                "title": book.combined_title.replace("'", "\'").replace("   ", "  ").replace("  ",
                                                                                             " ") if book.combined_title else "",
                "isbn": format_isbn(book.isbn).replace("&#8209;", "-") if book.isbn else "",
                "summary": book.summary.replace("'", "\'") if book.summary else "",
                "remarks": book.remarks.replace("'", "\'") if book.remarks else "",
                "authors": [author.name.replace("'", "\'") for author in book.authors.all()],
                "publisher": book.publisher.name.replace("'", "\'") if book.publisher else "",
                "series": book.series.name.replace("'", "\'") if book.series else "",
                "number": book.number or "",
                "genres": [genre.name.replace("'", "\'") for genre in book.genres.all()]
            }
        )
    wishes = []
    for wish in Wish.objects.all():
        wishes.append(
            {
                "id": wish.pk,
                "author": wish.author if wish.author else "",
                "title": wish.title if wish.title else "",
                "remarks": wish.remarks if wish.remarks else ""
            }
        )
    data = {
        "date": date.today().strftime("%Y-%m-%d"),
        "books": books,
        "wishes": wishes
    }
    books = json.dumps(data)

    f = open('books.txt', 'w+')
    f.write(books)
    f.close()

    file = open("books.txt", "rb")
    response = FileResponse(file, as_attachment=True, filename="books.txt")
    return response

def export_excel(request):
    ts = datetime.utcnow().strftime('%Y-%m-%d %H-%M')
    filename = f'my_books_{ts}.xlsx'
    buffer = io.BytesIO()
    workbook = xlsxwriter.Workbook(buffer)

    header_format = workbook.add_format({'bold': True})
    header_format.set_size(20)

    subheader_format = workbook.add_format({'bold': True})
    subheader_format.set_size(16)

    worksheet_by_title = workbook.add_worksheet()
    worksheet_by_title.set_row(0, 24)
    worksheet_by_title.write('A1', 'Books by title', header_format)
    worksheet_by_title.name = "Title"
    index = 2
    for book in Book.objects.exclude(genre__name="Comics").order_by("title"):
        index += 1
        worksheet_by_title.write(f'A{index}', book.title)

    worksheet_comics = workbook.add_worksheet()
    worksheet_comics.set_row(0, 24)
    worksheet_comics.write('A1', 'Comics', header_format)
    worksheet_comics.name = "Comics"
    index = 1

    if Book.objects.filter(series__isnull=True, genre__name="Comics").exists():
        for book in Book.objects.filter(genre__name="Comics", series__isnull=True).order_by("title"):
            index += 2
            if book.number:
                worksheet_comics.write(f'A{index}', f"{book.number} {book.title}")
            else:
                worksheet_comics.write(f'A{index}', f"{book.title}")

    for series in Series.objects.all():
        if not Book.objects.filter(series=series, genre__name="Comics").exists():
            continue

        index += 2
        worksheet_comics.set_row(index, 20)
        worksheet_comics.write(f'A{index}', series.name, subheader_format)

        for book in Book.objects.filter(genre__name="Comics", series=series).order_by("series", "number", "title"):
            index += 1
            if book.number:
                worksheet_comics.write(f'A{index}', f"{book.number} {book.title}")
            else:
                worksheet_comics.write(f'A{index}', f"{book.title}")

    worksheet_author = workbook.add_worksheet()
    worksheet_author.set_row(0, 24)
    worksheet_author.write('A1', 'Authors', header_format)
    worksheet_author.name = "by Author"
    index = 1

    for author in Author.objects.all():
        index += 2
        worksheet_author.set_row(index, 20)
        worksheet_author.write(f'A{index}', author.name, subheader_format)

        for book in author.books.all():
            index += 1
            worksheet_author.write(f'A{index}', book.title)

    worksheet_serie = workbook.add_worksheet()
    worksheet_serie.set_row(0, 24)
    worksheet_serie.write('A1', 'Series', header_format)
    worksheet_serie.name = "by Series"
    index = 1

    for series in Series.objects.all():
        index += 2
        worksheet_serie.set_row(index, 20)
        worksheet_serie.write(f'A{index}', series.name, subheader_format)

        for book in series.books.all():
            index += 1
            if book.number:
                worksheet_serie.write(f'A{index}', f"{book.number} {book.title}")
            else:
                worksheet_serie.write(f'A{index}', f"{book.title}")

    workbook.close()
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename=filename)
