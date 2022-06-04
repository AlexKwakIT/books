import os
import re

from django.db import transaction
from django.http import HttpResponse

from books.models import VideoSeries, Video, VIDEO_CHOICE_SERIES


@transaction.atomic
def import_video_series(request):
    Video.objects.all().delete()
    VideoSeries.objects.all().delete()
    base_path = "E:\\Series"
    for series in os.listdir(base_path):
         for entry in os.scandir(f"{base_path}\{series}"):
            if entry.is_file():
                import_video_serie_episode(series, 0, entry.name, entry.stat().st_size)
            else:
                try:
                    season = int(re.compile('\d+').findall(entry.name)[0])
                except:
                    season = 0
                for entry in os.scandir(f"{base_path}\{series}\{entry.name}"):
                    import_video_serie_episode(series, season, entry.name, entry.stat().st_size)

    print("READY")
    return HttpResponse(status=201, content="OK")


def import_video_serie_episode(series, season, episode, size):
    if series == "Doctor Who":
        return
    if episode.endswith("srt") or episode.endswith("sub") or size < 1000000:
        return
    if import_s01e01(series, season, episode, size):
        return
    if import_s1(series, season, episode, size):
        return
    if import_01x01(series, season, episode, size):
        return
    if import_season_disc(series, season, episode, size):
        return
    if import_season_0(series, season, episode, size):
        return
    if import_one_season(series, season, episode, size):
        return
    print("Not found:", series, season, episode)


def import_one_season(series, season, episode, size):
    if episode.lower().startswith(series.lower()):
        sep = re.compile(' \d\d\d ')
        se = sep.findall(episode.replace(".", " ")[len(series):])
        if len(se) == 1:
            try:
                season_episode = se[0]
                season_nr = int(season_episode[1])
                episode_nr = int(season_episode[2:4])
                title = episode[len(series)+4:]
                video_series, _ = VideoSeries.objects.get_or_create(name=series)
                Video(
                    kind=VIDEO_CHOICE_SERIES,
                    series=video_series,
                    season=0,
                    episode=episode_nr,
                    title=f"Part {episode_nr}",
                    size=size
                ).save()
                return True
            except Exception as e:
                print(f"Error {e}")
    return False


def import_s01e01(series, season, episode, size):
    sep = re.compile('[sS]\d+[eE]\d+')
    se = sep.findall(episode)
    if len(se) == 1:
        season_nr = int(se[0][1:3])
        episode_nr = int(se[0][4:6])
        title = episode.split(se[0])[1]
        if title.startswith("-"):
            title = title[1:]
        title = title[0:len(title)-4].replace(".", " ").replace("_", " ").strip()
        video_series, _ = VideoSeries.objects.get_or_create(name=series)
        Video(
            kind=VIDEO_CHOICE_SERIES,
            series=video_series,
            season=season_nr,
            episode=episode_nr,
            title=title,
            size=size
        ).save()
        return True

    return False


def import_s1(series, season, episode, size):
    sep = re.compile('[sS]\d\d')
    se = sep.findall(episode)
    if len(se) == 1:
        season_nr = int(se[0][1:3])
        episode_nr = 1
        title = episode.split(se[0])[1]
        if title.startswith("-"):
            title = title[1:]
        title = title[0:len(title)-4].replace(".", " ").replace("_", " ").strip()
        video_series, _ = VideoSeries.objects.get_or_create(name=series)
        Video(
            kind=VIDEO_CHOICE_SERIES,
            series=video_series,
            season=season_nr,
            episode=episode_nr,
            title=title,
            size=size
        ).save()
        return True

    return False


def import_01x01(series, season, episode, size):
    sep = re.compile('\d+[xX]\d+')
    se = sep.findall(episode)
    if len(se) == 1:
        se_nrs = se[0].lower().split('x')
        season_nr = int(se_nrs[0])
        episode_nr = int(se_nrs[1])
        title = episode.split(se[0])[1].replace(".", " ").replace("_", " ").strip()
        if title.startswith("-"):
            title = title[1:]
        title = title[0:len(title)-4].replace(".", " ").replace("_", " ").strip()
        video_series, _ = VideoSeries.objects.get_or_create(name=series)
        Video(
            kind=VIDEO_CHOICE_SERIES,
            series=video_series,
            season=season_nr,
            episode=episode_nr,
            title=title,
            size=size
        ).save()
        return True
    return False


def import_season_0(series, season, episode, size):
    sep = re.compile('^\d\d ')
    se = sep.findall(episode)
    if len(se) == 1:
        title = episode.split(se[0])[1].replace(".", " ").replace("_", " ").strip()
        if title.startswith("-"):
            title = title[1:]
        title = title[0:len(title)-4]
        episode_nr = int(episode[0:2])
        video_series, _ = VideoSeries.objects.get_or_create(name=series)
        Video(
            kind=VIDEO_CHOICE_SERIES,
            series=video_series,
            season=0,
            episode=episode_nr,
            title=title,
            size=size
        ).save()
        return True
    return False


def import_123(series, season, episode, size):
    sep = re.compile('\.\d\d\d\.')
    se = sep.findall(episode)
    if len(se) == 1:
        season_nr = int(se[0][0])
        episode_nr = int(se[0][1:2])
        title = episode.split(se[0])[1]
        if title.startswith("-"):
            title = title[1:]
        title = title[0:len(title)-4].replace(".", " ").replace("_", " ").strip()
        video_series, _ = VideoSeries.objects.get_or_create(name=series)
        Video(
            kind=VIDEO_CHOICE_SERIES,
            series=video_series,
            season=season_nr,
            episode=episode_nr,
            title=title,
            size=size
        ).save()
        return True

    return False


def import_season_disc(series, season, episode, size):
    sep = re.compile('Season\d+ Disc\d+-\d+')
    se = sep.findall(episode)
    if len(se) == 1:
        se_nrs = se[0].split(' Disc')
        season_nr = int(se_nrs[0].replace("Season", ""))
        episode_nr = int(se_nrs[1].split("-")[1])
        title = episode.split(se[0])[1]
        if title.startswith("-"):
            title = title[1:]
        title = title[0:len(title)-4].replace(".", " ").replace("_", " ").strip()
        video_series, _ = VideoSeries.objects.get_or_create(name=series)
        Video(
            kind=VIDEO_CHOICE_SERIES,
            series=video_series,
            season=season_nr,
            episode=episode_nr,
            title=title,
            size=size
        ).save()
        return True

    return False




# @transaction.atomic
# def import_lotje(request):
#     series, _ = Series.objects.get_or_create(name="Lotje")
#     author, _ = Author.objects.get_or_create(name="Jaap ter Haar")
#     category = Category.objects.get(name="Fiction")
#     subcategory, _ = SubCategory.objects.get_or_create(name="Children", category=category)
#     for book in Book.objects.filter(title__istartswith="Lotje"):
#         book.series = series
#         book.save()
#         book.sub_categories.add(subcategory)
#         book.authors.add(author)
#     return HttpResponse(status=201, content="OK")
#
#
# def import_conny_coll(request):
#     book_file = os.path.join(BASE_DIR, "assets\\conny_coll.txt")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Fiction")
#     subcategory = SubCategory.objects.get(category=category, name="Western")
#     publisher, _ = Publisher.objects.get_or_create(name="Ridderhof")
#     author, _ = Author.objects.get_or_create(name="Conrad Kobbe")
#     series, _ = Series.objects.get_or_create(name="Conny Coll")
#
#     for line in data:
#         if line != "":
#             nr, title = line.split('. ')
#             book, _ = Book.objects.get_or_create(
#                 title=title,
#                 number=nr,
#                 publisher=publisher,
#                 series=series
#             )
#             book.save()
#             book.sub_categories.add(subcategory)
#             book.authors.add(author)
#     print("READY")
#
#     return HttpResponse(status=201, content="OK")
#
#
# def import_bruno_brazil(request):
#     book_file = os.path.join(BASE_DIR, "assets\\brono_brazil.csv")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Lombard")
#     author1, _ = Author.objects.get_or_create(name="William Vance")
#     author2, _ = Author.objects.get_or_create(name="Louise Albert")
#     series, _ = Series.objects.get_or_create(name="Bruno Brazil")
#
#     Book.objects.filter(series=series).delete()
#
#     for line in data:
#         if line != "":
#             nr, title = line.split(';')
#             book, _ = Book.objects.get_or_create(
#                 title=title,
#                 number=nr,
#                 publisher=publisher,
#                 series=series
#             )
#             book.save()
#             book.sub_categories.add(subcategory)
#             book.authors.add(author1)
#             book.authors.add(author2)
#     print("READY")
#
#     return HttpResponse(status=201, content="OK")
#
#
# def import_asterix(request):
#     book_file = os.path.join(BASE_DIR, "assets\\asterix.csv")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Het Spectrum")
#     author, _ = Author.objects.get_or_create(name="Goscinny")
#     series, _ = Series.objects.get_or_create(name="Asterix")
#
#     for line in data:
#         if line != "":
#             nr, title = line.split(';')
#             book, _ = Book.objects.get_or_create(
#                 title=title,
#                 number=nr,
#                 publisher=publisher,
#                 series=series
#             )
#             book.save()
#             book.sub_categories.add(subcategory)
#             book.authors.add(author)
#     print("READY")
#
#     return HttpResponse(status=201, content="OK")
#
#
# def import_miranda_blaise(request):
#     book_file = os.path.join(BASE_DIR, "assets\\miranda_blaise.txt")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Panda")
#     author, _ = Author.objects.get_or_create(name="Peter O'Donnell")
#     series, _ = Series.objects.get_or_create(name="Miranda Blaise")
#
#     for line in data:
#         if line != "":
#             nr, title = line.split(' - ')
#             book, _ = Book.objects.get_or_create(
#                 title=title,
#                 number=nr,
#                 publisher=publisher,
#                 series=series
#             )
#             book.save()
#             book.sub_categories.add(subcategory)
#             book.authors.add(author)
#     print("READY")
#
#     return HttpResponse(status=201, content="OK")
#
#
# def import_agent327(request):
#     book_file = os.path.join(BASE_DIR, "assets\\agent327.csv")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Uitgeverij M")
#     author, _ = Author.objects.get_or_create(name="Martin Lodewijk")
#     series, _ = Series.objects.get_or_create(name="Agent 327")
#
#     for line in data:
#         if line != "":
#             nr, title = line.split(';')
#             book, _ = Book.objects.get_or_create(
#                 title=title,
#                 number=nr,
#                 publisher=publisher,
#                 series=series
#             )
#             book.save()
#             book.sub_categories.add(subcategory)
#             book.authors.add(author)
#     print("READY")
#
#     return HttpResponse(status=201, content="OK")
#
#
# def import_evert_kwok(request):
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Syndikaat")
#     author1, _ = Author.objects.get_or_create(name="de Blouw")
#     author2, _ = Author.objects.get_or_create(name="Evenboer")
#     series, _ = Series.objects.get_or_create(name="Evert Kwok")
#     for i in (1, 2, 3, 4):
#         book, _ = Book.objects.get_or_create(
#             title=f"Evert Kwok {i}",
#             number=i,
#             publisher=publisher,
#             series=series,
#         )
#         book.save()
#         book.sub_categories.add(subcategory)
#         book.authors.add(author1)
#         book.authors.add(author2)
#     return HttpResponse(status=201, content="OK")
#
#
# def import_dirkjan(request):
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Big Balloon Publishers")
#     author, _ = Author.objects.get_or_create(name="Mark Retera")
#     series, _ = Series.objects.get_or_create(name="Dirkjan")
#     for i in (1, 2, 3, 6, 9, 10, 11):
#         book, _ = Book.objects.get_or_create(
#             title=f"Dirkjan {i}",
#             number=i,
#             publisher=publisher,
#             series=series,
#         )
#         book.save()
#         book.sub_categories.add(subcategory)
#         book.authors.add(author)
#     return HttpResponse(status=201, content="OK")
#
#
# def import_douwe_dabbert(request):
#     book_file = os.path.join(BASE_DIR, "assets\\douwe_dabbert.txt")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Standaard Uitgeverij")
#     author1, _ = Author.objects.get_or_create(name="Piet Wijn")
#     author2, _ = Author.objects.get_or_create(name="Thom Roep")
#     series, _ = Series.objects.get_or_create(name="Douwe Dabbert")
#
#     index = 0
#     for title in data:
#         index += 1
#         book, _ = Book.objects.get_or_create(
#             title=title,
#             number=index,
#             publisher=publisher,
#             series=series,
#         )
#         book.save()
#         book.sub_categories.add(subcategory)
#         book.authors.add(author1)
#         book.authors.add(author2)
#     return HttpResponse(status=201, content="OK")
#
#
# def import_suske_wiske(request):
#     book_file = os.path.join(BASE_DIR, "assets\\suske_wiske.csv")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     category = Category.objects.get(name="Comics")
#     subcategory = SubCategory.objects.get(category=category, name="")
#     publisher, _ = Publisher.objects.get_or_create(name="Standaard Uitgeverij")
#     author, _ = Author.objects.get_or_create(name="W. Vandersteen")
#     series, _ = Series.objects.get_or_create(name="Suske en Wiske")
#
#     for line in data:
#         if line != "":
#             print(line)
#             title, nr = line.split(';')
#             book, _ = Book.objects.get_or_create(
#                 title=title,
#                 number=nr,
#                 publisher=publisher,
#                 series=series
#             )
#             book.save()
#             book.sub_categories.add(subcategory)
#             book.authors.add(author)
#     print("READY")
#
#     return HttpResponse(status=201, content="OK")
#
#
# def import_test_bob_evers(request):
#     book_file = os.path.join(BASE_DIR, "assets\\bob_evers.txt")
#     with open(book_file, "r") as file:
#         data = file.read().split("\n")
#
#     publisher, _ = Publisher.objects.get_or_create(name="De Eekhoorn")
#     author1, _ = Author.objects.get_or_create(name="Willy van der Heide")
#     author2, _ = Author.objects.get_or_create(name="Peter de Zwaan")
#     series = Series.objects.get(name="Bob Evers")
#
#     index = 0
#     for title in data:
#         index += 1
#         book, _ = Book.objects.get_or_create(
#             title=title,
#             publisher=publisher,
#         )
#         book.series = series
#         book.save()
#         # book.authors.add(author1 if index<=36 else author2)
#
#     return HttpResponse(status=201, content="OK")
