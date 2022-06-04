from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse


VIDEO_CHOICE_MOVIE = "MOVIE"
VIDEO_CHOICE_CABARET = "CABARET"
VIDEO_CHOICE_IMDB100 = "IMDB100"
VIDEO_CHOICE_MUSIC = "MUSIC"
VIDEO_CHOICE_SERIES = "SERIES"
VIDEO_CHOICE_STARTREK = "STARTREK"

VIDEO_CHOICES = (
    (VIDEO_CHOICE_MOVIE, "Movie"),
    (VIDEO_CHOICE_CABARET, "Cabaret"),
    (VIDEO_CHOICE_IMDB100, "IMDB Top 100"),
    (VIDEO_CHOICE_MUSIC, "Music Video"),
    (VIDEO_CHOICE_SERIES, "Series"),
    (VIDEO_CHOICE_STARTREK, "StarTrek"),
)


class Publisher(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def number_of_books(self):
        return self.books.count()


class IsbnPrefix(models.Model):
    prefix = models.CharField(max_length=20, blank=True, null=True)
    prefix_stripped = models.CharField(max_length=20, blank=True, null=True)
    publisher = models.ForeignKey(
        Publisher, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="prefixes"
    )


class Author(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("author_detail", args=[self.pk])

    @property
    def number_of_books(self):
        return self.books.count()


class Genre(models.Model):
    name = models.CharField(max_length=100, blank=True, null=False, unique=True)

    class Meta:
        ordering = ("name",)
        verbose_name_plural = "genres"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("genre_detail", args=[self.pk])

    @property
    def number_of_books(self):
        return self.books.count()


class Series(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def number_of_books(self):
        return self.books.count()


class Book(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    number = models.IntegerField(blank=True, null=True)
    isbn = models.CharField(
        max_length=40, blank=True, null=True, unique=True, verbose_name="ISBN"
    )
    summary = models.CharField(max_length=10000, blank=True, null=True)
    remarks = models.CharField(max_length=100, blank=True, null=True)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        related_name="books",
        blank=True,
        null=True,
    )
    authors = models.ManyToManyField(to=Author, related_name="books", blank=True)
    series = models.ForeignKey(
        Series, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="books"
    )
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)
    cover = models.ImageField(blank=True, null=True, upload_to="covers/")
    combined_title = models.CharField(max_length=100, blank=True, null=False, default="")

    class Meta:
        ordering = ("combined_title", "isbn")

    def get_absolute_url(self):
        return reverse("book_detail", args=[self.pk])

    def __str__(self):
        return self.combined_title

    def author_list(self, with_links):
        authors = [
            f'<a href="{author.get_absolute_url()}">{author.name}</a>' if with_links and author.name != 'et al' else author.name
            for author in self.authors.all()
        ]
        return ", ".join(authors)

    def genre_list(self, with_links):
        genres = [
            f'<a href="{genre.get_absolute_url()}">{genre.name}</a>' if with_links else genre.name
            for genre in self.genres.all()
        ]
        return ", ".join(genres)

    @property
    def formatted_isbn(self):
        return format_isbn(self.isbn)


class Wish(models.Model):
    author = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, null=True)
    remarks = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        ordering = ("author", "title", "remarks")

    def __str__(self):
        str = []
        if self.author:
            str.append(self.author)
        if self.title:
            str.append(self.title)
        if self.remarks:
            str.append(self.remarks)
        return ", ".join(str)


class VideoSeries(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Video(models.Model):
    series = models.ForeignKey(
        VideoSeries, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="videos"
    )
    title = models.CharField(max_length=100, blank=False, null=False)
    kind = models.CharField(max_length=20, choices=VIDEO_CHOICES, blank=False, null=False)
    season = models.IntegerField(blank=True, null=True)
    episode = models.IntegerField(blank=True, null=True)
    size = models.BigIntegerField(blank=True, null=True)

    class Meta:
        ordering = ["series", "season", "episode", "title"]

    def save(self, *args, **kwargs):
        if self.title == "":
            return
        super().save(*args, **kwargs)


def format_isbn(isbn_code):
    isbn = isbn_code.replace("-", "").replace("&#8209;", "")
    for isbn_prefix in IsbnPrefix.objects.all():
        if isbn.startswith(isbn_prefix.prefix_stripped):
            return isbn_prefix.prefix + "-" + isbn[len(isbn_prefix.prefix_stripped):12] + "-" + isbn[12]
    return isbn_code.replace("-", "&#8209;")


def get_combined_title(book):
    title = book.title or ""
    try:
        if book.number and book.number != '':
            number = '{:3d}'.format(book.number)
            if book.series:
                title = f' "{title}"' if len(title) > 0 else ""
                return f'{book.series.name} {number}{title}'
            return f"{title} ({number})"
        return title
    except:
        return title


@receiver(pre_save, sender=Book)
def my_callback(sender, instance, *args, **kwargs):
    instance.combined_title = get_combined_title(instance)
