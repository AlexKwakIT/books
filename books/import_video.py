import cv2
import os
import re

from django.db import transaction
from django.http import HttpResponse

from books.models import Video, VIDEO_CHOICE_SERIES, VIDEO_CHOICE_MOVIE, VIDEO_CHOICE_MUSIC

VALID_EXTENTIONS = ('.avi', '.mkv', '.mp4')
INVALID_EXTENTIONS = ('.srt', '.sub', '.jpg', '.srtx', '.nfo', '.db', '.idx', '.doc')


@transaction.atomic
def video_import(request):
    print()
    import_video_series()

    import_doctor_who_new()
    import_doctor_who_original()
    import_doctor_who_specials()

    import_video_movies()
    import_video_imdb_top100()

    import_video_music()
    return HttpResponse(status=201, content="OK")


def import_video_series():
    Video.objects.filter(type=VIDEO_CHOICE_SERIES).delete()
    base_path = "E:\\Series"
    for series in os.listdir(base_path):
        print(".", end='')
        if series == "Doctor Who":
            continue
        seasons = []
        for entry in os.scandir(f"{base_path}\{series}"):
            if entry.is_file():
                continue
            try:
                season = int(re.compile('\d+').findall(entry.name)[0])
                seasons.append(season)
            except:
                pass
        Video(
            type=VIDEO_CHOICE_SERIES,
            series=series,
            seasons=", ".join(get_season_ranges(seasons))
        ).save()
    print("SERIES READY")


def import_doctor_who_new():
    seasons = []
    for entry in os.scandir("E:\\Series\\Doctor Who\\New Series (2005 - )"):
        print(".", end='')
        try:
            season = int(re.compile('\d+').findall(entry.name)[0])
            seasons.append(season)
        except:
            pass
    if len(seasons) > 0:
        Video(
            type=VIDEO_CHOICE_SERIES,
            series="Dr Who",
            title="New series",
            seasons=", ".join(get_season_ranges(seasons))
        ).save()
    print("DR WHO NEW READY")


def import_doctor_who_original():
    for entry in os.scandir("E:\\Series\\Doctor Who\\Original Series (1962 - 1989)"):
        print(".", end='')
        Video(
            type=VIDEO_CHOICE_SERIES,
            series="Dr Who",
            title="Original series",
            seasons=entry.name
        ).save()
    print("DR WHO ORIGINALS READY")


def import_doctor_who_specials():
    for entry in os.scandir("E:\\Series\\Doctor Who\\Specials"):
        print(".", end='')
        if entry.is_file() and has_valid_extention(entry.name):
            Video(
                type=VIDEO_CHOICE_SERIES,
                series="Dr Who",
                title=entry.name,
            ).save()
    print("DR WHO SPECIALS READY")


def import_video_movies():
    Video.objects.filter(type=VIDEO_CHOICE_MOVIE).delete()
    base_path = "E:\\Movies"
    for movie in os.listdir(base_path):
        print(".", end='')
        get_movies(VIDEO_CHOICE_MOVIE, base_path, movie)
    print("MOVIES READY")


def import_video_imdb_top100():
    base_path = "E:\\IMDB Top 100"
    for movie in os.listdir(base_path):
        print(".", end='')
        get_movies(VIDEO_CHOICE_MOVIE, base_path, movie, "IMDB Top 100")
    print("IMDB TOP 100 READY")


def import_video_music():
    Video.objects.filter(type=VIDEO_CHOICE_MUSIC).delete()
    base_path = "E:\\MusicVideo"
    for movies in os.listdir(base_path):
        print(".", end='')
        get_movies(VIDEO_CHOICE_MUSIC, f"{base_path}\{movies}", "", movies)
    print("MUSIC READY")


def get_movies(type, base_path, movie, series=None):
    for entry in os.scandir(f"{base_path}\{movie}"):
        try:
            if not entry.is_file():
                print(f'Warning: Found extra folder for "{movie}"')
                continue
            if has_valid_extention(entry.name):
                vid = cv2.VideoCapture(entry.path)
                width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
                Video(
                    type=type,
                    title=entry.name,
                    series=series if series else movie,
                    seasons="",
                    screen_width=width
                ).save()
        except Exception as e:
            print(f'Error for "{entry.name}": {e}')


def has_valid_extention(name):
    i = name.rfind(".")
    if i < 0:
        return False
    extention = name[i:]
    if extention not in VALID_EXTENTIONS + INVALID_EXTENTIONS:
        print(f'Warning, invalid extention: "{name}"')
        return False
    return extention in VALID_EXTENTIONS


def get_season_ranges(seasons):
    """
    seasons: List of integers
    """
    ranges = []
    range_low = 0
    range_high = 0
    while len(seasons) > 0:
        season = seasons[0]
        seasons.pop(0)
        if range_low == 0:
            range_low = season
            range_high = season
        else:
            if season == range_high + 1:
                range_high += 1
            else:
                if range_high > range_low:
                    ranges.append(f"{range_low}-{range_high}")
                else:
                    ranges.append(f"{range_low}")
                range_low = season
                range_high = season
    if range_low > 0:
        if range_high > range_low:
            ranges.append(f"{range_low}-{range_high}")
        else:
            ranges.append(f"{range_low}")
    return ranges
