import base64
import json
from tempfile import NamedTemporaryFile

from django.core.files import File
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from books.models import Book


@csrf_exempt
def new_photos(request):
    try:
        photos = json.loads(request.body)
        for photo in photos:
            id = photo.get("book_id")
            image_string = photo.get("image")

            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(base64.b64decode(image_string))

            book = Book.objects.get(id=id)
            book.cover_image.save(f"{book.isbn}.jpg", File(img_temp), save=True)

            book.save()

        return HttpResponse(status=201, content="OK")
    except Exception as e:
        return HttpResponse(status=500, content=f"NOK: {e}")
