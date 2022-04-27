from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse


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


class Category(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        if not SubCategory.objects.filter(category=self).exists():
            SubCategory(category=self).save()


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100, blank=True, null=False)

    class Meta:
        ordering = ("category__name", "name")
        verbose_name_plural = "subcategories"

    def __str__(self):
        return self.extended_name

    @property
    def extended_name(self):
        if len(self.name) > 0:
            return f"{self.category} ({self.name})"
        else:
            return f"{self.category}"

    @property
    def number_of_books(self):
        return self.books.count()


class Serie(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def number_of_books(self):
        return self.books.count()


class InfoSource(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name or "-"


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
    serie = models.ForeignKey(
        Serie, on_delete=models.DO_NOTHING, blank=True, null=True, related_name="books"
    )
    sub_category = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="books",
    )
    cover = models.ImageField(blank=True, null=True, upload_to="covers/")
    sources = models.ManyToManyField(
        to=InfoSource, related_name="author_set", blank=True
    )
    combined_title = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ("combined_title", "isbn")

    def get_absolute_url(self):
        return reverse("book_detail", args=[self.pk])

    def __str__(self):
        return self.combined_title

    def category(self):
        return self.sub_category if self.sub_category else "-"

    def author_list(self, with_links):
        authors = [
            f'<a href="{author.get_absolute_url()}">{author.name}</a>' if with_links and author.name != 'et al' else author.name
            for author in self.authors.all()
        ]
        return ", ".join(authors)

    @property
    def formatted_isbn(self):
        return format_isbn(self.isbn)


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
            if book.serie:
                title = f' "{title}"' if len(title) > 0 else ""
                return f'{book.serie.name} {number}{title}'
            return f"{title} ({number})"
        return title
    except:
        return title


@receiver(pre_save, sender=Book)
def my_callback(sender, instance, *args, **kwargs):
    instance.combined_title = get_combined_title(instance)
