#!/usr/bin/env python
'''
Downloads the lastest APOD (Astronomy Picture of the Day) from apod.nasa.gov
and sets the image as desktop wallpaper. If the APOD is already in library
generate a valid random url to a APOD and set that as wallpaper.
 '''


import sys
import os
import subprocess
import random
import re
import csv
from PIL import Image
from pathlib import Path
from datetime import datetime
from json import loads, decoder

import requests

from config import SetupConfig


CONF = SetupConfig()
HOME = CONF.HOME
FIELD_NAMES = CONF.FIELD_NAMES
IMAGE_DIR = HOME + CONF.IMAGE_DIR
TIMG_DIR = HOME + CONF.TIMG_DIR
DATA_FILE = HOME + CONF.DATA_FILE
TIMG_SAVE = CONF.TIMG_SAVE
ORIG_SAVE = CONF.ORIG_SAVE
CROP_SAVE = CONF.CROP_SAVE
TMP_SAVE = CONF.TMP_SAVE
QUALITY = CONF.QUALITY
MIN_SIZE = CONF.MIN_SIZE
CROP_RATIO = CONF.CROP_RATIO
CUSTOM_CMD = CONF.CUSTOM_CMD
CUSTOM_ENV = CONF.CUSTOM_ENV
API_KEY = CONF.API_KEY
RESP_URL = "https://api.nasa.gov/planetary/apod?api_key=" + API_KEY


def test_connection(RESP_URL):
    '''
    Test network connection. Return the response or handle the
    exceptions.
    '''
    for attempt in range(4):
        try:
            resp = requests.get(RESP_URL, timeout=(12.2, 30), stream=True)
            attempt += 1
            return resp
        except (requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.ConnectionError):
            pass
        except requests.exceptions.RequestException:
            raise SystemExit(1)
    raise SystemExit(1)


def generate_data(API_KEY):
    '''
    Run nessicary funtions to generate a random date and url. Return
    a response.
    '''
    rand_month = gen_month()
    rand_year = gen_year()
    rand_day = gen_day(rand_month, rand_year)
    test_valid(rand_day, rand_month, rand_year)
    rand_url, rand_apod_date = make_url(API_KEY, rand_year, rand_month,
                                        rand_day)
    resp = test_connection(rand_url)
    return resp


def formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, resp):
    '''
    Check if an image is in the response text. If the filename is in the
    data file run the function generate_data to get a new APOD.
    '''
    escape_list = ["(", ")", "{", "}"]
    regex_string = r"image/[0-9]{4}/(.*\.(jpg|jpeg|png))"
    apod_copyright = ""
    try:
        resp_dict = loads(resp.text)
        apod_date = resp_dict["date"]
        apod_title = resp_dict["title"]
        apod_explanation = resp_dict["explanation"]
        apod_url = resp_dict["url"]
        hd_apod_url = resp_dict["hdurl"]
        apod_filename = re.search(regex_string, apod_url, re.I).group(1)
        hd_apod_filename = re.search(regex_string, hd_apod_url, re.I).group(1)
    except (decoder.JSONDecodeError, re.error, KeyError, AttributeError):
        return formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES,
                              generate_data(API_KEY))
    try:
        apod_copyright = resp_dict["copyright"]
    except KeyError:
        pass
    apod_html = ("https://apod.nasa.gov/apod/ap{}.html".format(
                 apod_date[2:].replace("-", "")))
    if QUALITY.lower() == "hd":
        apod_filename = hd_apod_filename
        apod_url = hd_apod_url
    for char in escape_list:
        if char in apod_filename:
            apod_filename = apod_filename.replace(char, "")
    reader = read_data_rows(DATA_FILE, FIELD_NAMES)
    for row in reader:
        if apod_filename in row["filename"]:
            return formulate_data(DATA_FILE, QUALITY, API_KEY,
                                  FIELD_NAMES, generate_data(API_KEY))
    return (apod_date, apod_title, apod_explanation, apod_url, apod_filename,
            apod_copyright, apod_html)


def download_apod(IMAGE_DIR, apod_url, apod_filename):
    '''
    Download an APOD. Call functions to check the header and then a function
    to append the apod data to the data file.
    '''
    # Open the response and download the image. Open the data file and
    # append the filename to the file.
    resp = test_connection(apod_url)
    resp.raw.decode_content = True
    try:
        with open("{}{}".format(IMAGE_DIR, apod_filename), "wb") as d:
            d.write(resp.content)
    except (PermissionError, OSError):
        raise SystemExit(1)


def set_background(IMAGE_DIR, QUALITY, CUSTOM_CMD, CUSTOM_ENV,
                   apod_filename):
    '''
    Set the downloaded APOD as wallpaper. Determine the users
    $XDG_CURRENT_DESKTOP if on linux, if on windows or mac use sys to
    check platform.
    '''
    background_path = IMAGE_DIR + apod_filename
    wallpaper_cmd = ""
    check_desktop_var = "XDG_CURRENT_DESKTOP"
    if CUSTOM_CMD.strip() != "":
        wallpaper_cmd = CUSTOM_CMD
    else:
        if CUSTOM_ENV.strip() != "":
            check_desktop_var = CUSTOM_ENV
        check_desktop = str(subprocess.check_output("echo ${}".format(
                            check_desktop_var), shell=True)).lower()
        gnome_list = ["gnome", "unity", "budgie-desktop", "lubuntu"]
        check_gnome_color = (subprocess.check_output("echo gsettings get org"
                             + ".gnome.desktop.interface "
                             + "color-scheme", shell=True))
        # gnome - Loop gnome list to check if gnome.desktop is used.
        for item in gnome_list:
            if item in check_desktop:
                if "prefer-dark" in check_gnome_color:
                    wallpaper_cmd = ("gsettings set org.gnome.desktop"
                                     + ".background picture-uri-dark {}")
                else:
                    wallpaper_cmd = ("gsettings set org.gnome.desktop"
                                     + ".background picture-uri {}")
        # lxde
        if "lxde" in check_desktop:
            wallpaper_cmd = "pcmanfm --set-wallpaper={}"
        # lxqt
        if "lxqt" in check_desktop:
            wallpaper_cmd = "pcmanfm-qt --set-wallpaper={}"
        # xfce
        if "xfce" in check_desktop:
            wallpaper_cmd = ("xfconf-query -c xfce4-desktop -p /backdrop"
                             + "/screen0/monitor0/workspace0/last-image"
                             + "-s s {}")
        # kde
        if "kde" in check_desktop:
            wallpaper_cmd = "plasma-apply-wallpaperimage {}"
        # windows
        if "win32" in sys.platform.lower():
            wallpaper_cmd = ("ctypes.windll.user32.SystemParametersInfoW"
                             + "(0x14, 0, {}, 0x2)").format(background_path)
        # mac
        if "darwin" in sys.platform.lower():
            wallpaper_cmd = ('osascript -e ‘tell application “Finder” to set'
                             + ' desktop image to POSIX file'
                             + ' “{}”‘'.format(background_path))
    wallpaper = str(wallpaper_cmd).format(background_path)
    try:
        subprocess.Popen(wallpaper, shell=True).wait()
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)


def gen_day(rand_month, rand_year):
    '''
    Generate a valid random day of the month. Factor for leap year,
    and days in accompanying month.
    '''
    # Check if the month is Febuary, if so determine if it is a leap year.
    # If year divisible by 4, and not divisible by 100, unless also divisible
    # by 400.
    if int(rand_month) == 2:
        if int(rand_year) % 4 == 0 and int(rand_year) % 100 != 0:
            if int(rand_year) % 400 == 0:
                rand_day = random.randint(1, 29)
                return rand_day
        else:
            rand_day = random.randint(1, 28)
            return rand_day
    # Determine if the month has 30 days, else the only option left is 31.
    if rand_month in [4, 6, 9, 11] and rand_month != 1:
        rand_day = random.randint(1, 30)
        return rand_day
    else:
        rand_day = random.randint(1, 31)
        return rand_day


def gen_month():
    '''
    Generate a random month.
    '''
    rand_month = random.randint(1, 12)
    return rand_month


def gen_year():
    '''
    Generate a random year between the year of the first APOD(1995),
    and today's date.
    '''
    date = datetime.now().strftime("%Y%m%d")
    firstapod = str(19950616)
    rand_year = str(random.randint(int(firstapod), int(date)))[:4]
    return rand_year


def test_valid(rand_day, rand_month, rand_year):
    '''
    Test the generated date to determine if it is in the three days
    after the first APOD, they did not have an APOD. If so generate
    a new day in place and test again.
    '''
    misstime = [950617, 950618, 950619]
    rand_date = str(rand_year) + str(rand_month) + str(rand_day)
    newrand_date = str(rand_year) + str(rand_month) + str(gen_day(rand_month,
                                                                  rand_year))
    # Check if the generated random date is not one of the three days
    # after the first apod was released. No apods on those days.
    if rand_date in misstime:
        rand_date = newrand_date
        return rand_date


def make_url(API_KEY, rand_year, rand_month, rand_day):
    '''
    Format the random url.
    '''
    # Format month and day correctly.
    if len(str(rand_month)) == 1:
        rand_month = str("0{}".format(rand_month))
    if len(str(rand_day)) == 1:
        rand_day = str("0{}".format(rand_day))
    # Assemble the apod url using the random date. YYMMDD
    rand_apod_date = "{}-{}-{}".format(str(rand_year), str(rand_month),
                                       str(rand_day))
    rand_url = ("https://api.nasa.gov/planetary/apod"
                + "?api_key={}&date={}".format(API_KEY, rand_apod_date))
    return (rand_url, rand_apod_date)


def verify_dimensions(IMAGE_DIR, MIN_SIZE, apod_filename):
    '''
    Verify the APOD images dimensions. If the images are less than
    the value of MIN_SIZE return False.
    '''
    image_min_size = MIN_SIZE.split("x")
    try:
        min_width, min_height = image_min_size[0], image_min_size[1]
    except IndexError:
        min_width, min_height = (0, 0)
    try:
        wallpaper = Image.open(IMAGE_DIR + apod_filename)
        width = wallpaper.width
        height = wallpaper.height
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)
    if int(width) < int(min_width) or int(height) < int(min_height):
        return True


def create_thumbnail(date_time, IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES,
                     apod_date, apod_title, apod_explanation, apod_html,
                     apod_url, apod_filename, apod_copyright):
    '''Create a thumbnail of an APOD.'''
    try:
        apod_size = Path(IMAGE_DIR + apod_filename).stat().st_size
        wallpaper = Image.open(IMAGE_DIR + apod_filename)
        apod_WxH = "{}x{}".format(str(wallpaper.width), str(wallpaper.height))
        wallpaper.thumbnail((310, 310))
        apod_filename_timg = apod_filename.split(".")[0] + "-thumbnail.PNG"
        wallpaper.save(TIMG_DIR + apod_filename_timg)
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)
    append_data(date_time, DATA_FILE, FIELD_NAMES, apod_date, apod_title,
                apod_explanation, apod_html, apod_url, apod_filename, apod_WxH,
                apod_size, apod_copyright, "timg")


def crop_image(date_time, IMAGE_DIR, DATA_FILE, QUALITY, MIN_SIZE,
               CROP_RATIO, FIELD_NAMES, apod_filename):
    '''
    Crop the image to a specific aspect ratio.
    '''
    crop_ratio = CROP_RATIO.split(":")
    crop_ratio = int(crop_ratio[1]) / int(crop_ratio[0])
    try:
        wallpaper = Image.open(IMAGE_DIR + apod_filename)
        width = wallpaper.width
        height = wallpaper.height
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)
    left, top, right, bottom = (0, 0, 0, 0)
    crop_height = 0
    if int(width) >= int(height):
        crop_height = int(height * crop_ratio)
        left = 0
        right = width
        bottom = int((height - crop_height) / 2)
        top = bottom + crop_height
    if int(height) > int(width):
        crop_height = int(width * crop_ratio)
        bottom = int((height - crop_height) / 2)
        top = bottom + crop_height
        left = left
        right = left + width
    crop_apod_filename = apod_filename.split(".")
    crop_apod_filename = (crop_apod_filename[0] + "-crop."
                          + crop_apod_filename[1])
    try:
        with Image.open(IMAGE_DIR + apod_filename) as wallpaper:
            crop = wallpaper.crop((left, bottom, right, top))
            crop.save(IMAGE_DIR + crop_apod_filename)
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)
    apod_filename = crop_apod_filename
    append_data(date_time, DATA_FILE, FIELD_NAMES, "", "", "", "", "",
                apod_filename, "", "", "", "crop")
    return apod_filename


def check_data_header(DATA_FILE, FIELD_NAMES):
    '''
    Check if header exists on data file, if not call function to write the
    header
    '''
    try:
        with open(DATA_FILE, "r") as data_file:
            reader = data_file.readline()
            field_names = ",".join(FIELD_NAMES)
            if field_names not in reader:
                return write_data_header(DATA_FILE, FIELD_NAMES)
    except (csv.Error, FileNotFoundError, PermissionError, OSError):
        return write_data_header(DATA_FILE, FIELD_NAMES)


def write_data_header(DATA_FILE, FIELD_NAMES):
    '''Write data file header with field names.'''
    try:
        with open(DATA_FILE, "w", newline="") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
            writer.writeheader()
    except (csv.Error, PermissionError, OSError):
        raise SystemExit(1)


def append_data(date_time, DATA_FILE, FIELD_NAMES, apod_date, apod_title,
                apod_explanation, apod_html, apod_url, apod_filename,
                apod_WxH, apod_size, apod_copyright, apod_category):
    '''Append data to the data file.'''
    try:
        with open(DATA_FILE, "a", newline="") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
            writer.writerow({
                "apod-date": apod_date,
                "title": apod_title,
                "explanation": apod_explanation,
                "html-url": apod_html,
                "img-url": apod_url,
                "filename": apod_filename,
                "image-WxH": apod_WxH,
                "image-size": apod_size,
                "copyright": apod_copyright,
                "uid": date_time,
                "category": apod_category})
    except (csv.Error, PermissionError, OSError):
        raise SystemExit(1)


def write_data_rows(DATA_FILE, FIELD_NAMES, *arg):
    '''Write a new data file from a list.'''
    try:
        with open(DATA_FILE, "w", newline="") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
            writer.writeheader()
            writer.writerows(*arg)
    except (csv.Error, PermissionError, OSError):
        raise SystemExit(1)


def read_data_rows(DATA_FILE, FIELD_NAMES):
    '''Read data file, return a list of dictionaries sorted by UID'''
    data_rows = []
    try:
        with open(DATA_FILE, "r", newline="") as data_file:
            reader = csv.DictReader(data_file, FIELD_NAMES)
            [data_rows.append(row) for row in reader]
            data_rows = [data_rows[0]] + sorted(data_rows[1:], key=lambda
                                                item: item["uid"],
                                                reverse=True)
        return data_rows
    except (csv.Error, FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)


def dir_cleanup(date_time, DATA_FILE, TIMG_SAVE, IMAGE_DIR, TIMG_DIR,
                ORIG_SAVE, CROP_SAVE, TMP_SAVE, FIELD_NAMES):
    '''
    Clean up directory to specified amount of images, delete oldest first.
    '''
    # Determine if need to delete images. Enumerate the log to determine what
    # to remove. Remove files over the set limit to keep by finding the range
    # of the amount of files in the log and subtracting by the amount to save.
    data_rows = []
    timg_rows = []
    crop_rows = []
    tmp_rows = []
    orig_rows = []
    delete_rows = []
    reader = read_data_rows(DATA_FILE, FIELD_NAMES)
    for row in reader:
        if row["category"] in {"timg"}:
            timg_rows.append(row)
        elif row["category"] in {"crop"}:
            crop_rows.append(row)
        elif row["category"] in {"tmp"}:
            tmp_rows.append(row)
        elif date_time[:8] in row["apod-date"].replace("-", ""):
            data_rows.append(row)
        elif row['category'] in {"orig"}:
            orig_rows.append(row)
    for row in orig_rows:
        if row in orig_rows[:int(ORIG_SAVE)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)
    for row in timg_rows:
        if row in timg_rows[:int(TIMG_SAVE)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)
    for row in crop_rows:
        if row in crop_rows[:int(CROP_SAVE)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)
    for row in tmp_rows:
        if row in tmp_rows[:int(TMP_SAVE)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)
    for apod_filename in delete_rows:
        if row["category"] in {"timg"}:
            delete_file(TIMG_DIR, apod_filename["filename"])
        else:
            delete_file(IMAGE_DIR, apod_filename["filename"])
    write_data_rows(DATA_FILE, FIELD_NAMES, data_rows)
    return SystemExit(0)


def delete_file(IMAGE_DIR, apod_filename):
    '''Delete file. Takes a path and a filename as arguments.'''
    try:
        os.remove(IMAGE_DIR + apod_filename)
    except FileNotFoundError as e:
        print(e)


def main():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    apod_category = "orig"
    resp = test_connection(RESP_URL)
    check_data_header(DATA_FILE, FIELD_NAMES)
    (apod_date, apod_title, apod_explanation, apod_url, apod_filename,
     apod_copyright, apod_html) = formulate_data(DATA_FILE, QUALITY, API_KEY,
                                                 FIELD_NAMES, resp)
    download_apod(IMAGE_DIR, apod_url, apod_filename)

    while verify_dimensions(IMAGE_DIR, MIN_SIZE, apod_filename):
        create_thumbnail(date_time, IMAGE_DIR, TIMG_DIR, DATA_FILE,
                         FIELD_NAMES, apod_date, apod_title, apod_explanation,
                         apod_html, apod_url, apod_filename, apod_copyright)
        append_data(date_time, DATA_FILE, FIELD_NAMES, "", "", "", "", "",
                    apod_filename, "", "", "", "tmp")
        (apod_date, apod_title, apod_explanation, apod_url, apod_filename,
         apod_copyright, apod_html) = (formulate_data(DATA_FILE, QUALITY,
                                       API_KEY, FIELD_NAMES,
                                       generate_data(API_KEY)))
        download_apod(IMAGE_DIR, apod_url, apod_filename)

    create_thumbnail(date_time, IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES,
                     apod_date, apod_title, apod_explanation, apod_html,
                     apod_url, apod_filename, apod_copyright)
    append_data(date_time, DATA_FILE, FIELD_NAMES, apod_date, "", "", "", "",
                apod_filename, "", "", "", apod_category)
    apod_filename = crop_image(date_time, IMAGE_DIR, DATA_FILE, QUALITY,
                               MIN_SIZE, CROP_RATIO, FIELD_NAMES,
                               apod_filename)
    set_background(IMAGE_DIR, QUALITY, CUSTOM_CMD, CUSTOM_ENV, apod_filename)
    dir_cleanup(date_time, DATA_FILE, TIMG_SAVE, IMAGE_DIR, TIMG_DIR,
                ORIG_SAVE, CROP_SAVE, TMP_SAVE, FIELD_NAMES)
    SystemExit(0)


if __name__ == "__main__":

    main()
