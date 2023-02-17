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
from pathlib import Path
from datetime import datetime
from json import loads, decoder

from PIL import Image
import requests

from config import SetupConfig


CONF = SetupConfig()
FIELD_NAMES = CONF.FIELD_NAMES
IMAGE_DIR = str(CONF.IMAGE_DIR)
TIMG_DIR = str(CONF.TIMG_DIR)
DATA_FILE = str(CONF.DATA_FILE)
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
field_dict = CONF.field_dict


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


def formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, field_dict,
                   date_time, resp):
    '''
    Check if an image is in the response text. If the filename is in the
    data file run the function generate_data to get a new APOD.
    '''
    escape_list = ["(", ")", "{", "}"]
    regex_string = r"image/[0-9]{4}/(.*\.(jpg|jpeg|png))"
    try:
        resp_dict = loads(resp.text)
        field_dict["uid"] = date_time
        field_dict["date"] = resp_dict["date"]
        field_dict["title"] = resp_dict["title"]
        field_dict["explanation"] = resp_dict["explanation"]
        field_dict["img-url"] = resp_dict["url"]
        field_dict["filename"] = re.search(regex_string, resp_dict["url"],
                                           re.I).group(1)
        hd_apod_filename = re.search(regex_string, resp_dict["hdurl"],
                                     re.I).group(1)
    except (decoder.JSONDecodeError, re.error, KeyError, AttributeError):
        return formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES,
                              field_dict, date_time, generate_data(API_KEY))
    try:
        field_dict["copyright"] = resp_dict["copyright"]
    except KeyError:
        pass
    field_dict["html"] = ("https://apod.nasa.gov/apod/ap{}.html".format(
                              field_dict["date"][2:].replace("-", "")))
    if QUALITY.lower() == "hd":
        field_dict["img-url"] = resp_dict["hdurl"]
        field_dict["filename"] = hd_apod_filename
    for char in escape_list:
        if char in field_dict["filename"]:
            field_dict["filename"].replace(char, "")
    reader = read_data_rows(DATA_FILE, FIELD_NAMES)
    for row in reader:
        if field_dict["filename"] in row["filename"]:
            return formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES,
                                  field_dict, date_time, 
                                  generate_data(API_KEY))


def download_apod(IMAGE_DIR, field_dict):
    '''
    Download an APOD. Call functions to check the header and then a function
    to append the apod data to the data file.
    '''
    # Open the response and download the image. Open the data file and
    # append the filename to the file.
    resp = test_connection(field_dict["img-url"])
    resp.raw.decode_content = True
    try:
        with open(IMAGE_DIR + field_dict["filename"], "wb") as d:
            d.write(resp.content)
    except (PermissionError, OSError):
        raise SystemExit(1)


def set_background(IMAGE_DIR, QUALITY, CUSTOM_CMD, CUSTOM_ENV, field_dict):
    '''
    Set the downloaded APOD as wallpaper. Determine the users
    $XDG_CURRENT_DESKTOP if on linux, if on windows or mac use sys to
    check platform.
    '''
    background_path = IMAGE_DIR + field_dict["filename"]
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


def verify_dimensions(IMAGE_DIR, MIN_SIZE, field_dict):
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
        wallpaper = Image.open(IMAGE_DIR + field_dict["filename"])
        apod_width = wallpaper.width
        apod_height = wallpaper.height
        apod_size = Path(IMAGE_DIR + field_dict["filename"]).stat().st_size
        apod_WxH = "{}x{}".format(str(wallpaper.width), str(wallpaper.height))
        field_dict["img-WxH"] = apod_WxH
        field_dict["img-size"] = apod_size
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)
    if int(apod_width) < int(min_width) or int(apod_height) < int(min_height): 
        return True


def create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES, field_dict):
    '''Create a thumbnail of an APOD.'''
    try:
        wallpaper = Image.open(IMAGE_DIR + field_dict["filename"])
        wallpaper.thumbnail((310, 310))
        wallpaper.save(TIMG_DIR + field_dict["filename"].split(".")[0]
                       + "-timg.png")
        if "timg" not in field_dict["category"]:
            field_dict["category"].append("timg")
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)


def crop_image(IMAGE_DIR, DATA_FILE, QUALITY, MIN_SIZE, CROP_RATIO,
               FIELD_NAMES, field_dict):
    '''
    Crop the image to a specific aspect ratio.
    '''
    crop_ratio = CROP_RATIO.split(":")
    crop_ratio = int(crop_ratio[1]) / int(crop_ratio[0])
    try:
        wallpaper = Image.open(IMAGE_DIR + field_dict["filename"])
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
    crop_apod_filename = field_dict["filename"].split(".")
    crop_apod_filename = (crop_apod_filename[0] + "-crop."
                          + crop_apod_filename[1])
    field_dict["category"].append("crop")
    try:
        with Image.open(IMAGE_DIR + field_dict["filename"]) as wallpaper:
            crop = wallpaper.crop((left, bottom, right, top))
            crop.save(IMAGE_DIR + crop_apod_filename)
    except (FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)


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


def append_data(DATA_FILE, FIELD_NAMES, field_dict):
    '''Append data to the data file.'''
    try:
        with open(DATA_FILE, "a", newline="") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
            writer.writerow({
                "date": field_dict["date"],
                "title": field_dict["title"],
                "explanation": field_dict["explanation"],
                "html": field_dict["html"],
                "img-url": field_dict["img-url"],
                "filename": field_dict["filename"],
                "img-WxH": field_dict["img-WxH"],
                "img-size": field_dict["img-size"],
                "copyright": field_dict["copyright"],
                "uid": field_dict["uid"],
                "category": field_dict["category"]})
    except (csv.Error, PermissionError, OSError):
        raise SystemExit(1)


def write_data_rows(DATA_FILE, FIELD_NAMES, data_rows):
    '''Write a new data file from a list.'''
    try:
        with open(DATA_FILE, "w", newline="") as data_file:
            writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
            writer.writeheader()
            writer.writerows(data_rows)
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
                                                reverse=False)
        return data_rows
    except (csv.Error, FileNotFoundError, PermissionError, OSError):
        raise SystemExit(1)


def sort_categories(IMAGE_DIR, TIMG_DIR, date_time, data_rows, data_category,
                    data_save):
    '''Sort list of dictionaries containing apod data.'''
    category_rows = []
    new_data_rows = []
    [category_rows.append(row) for row in data_rows if data_category in row["category"]] 
    for row in data_rows:
        if row in category_rows[:len(category_rows) - int(data_save)]:
            try:
                category_list = list(row["category"].strip("][").replace("'", ""
                                                                         ).split(", "))
            except AttributeError:
                category_list = row["category"]
            category_list.remove(data_category)
            if len(category_list) != 0:
                row["category"] = category_list
                new_data_rows.append(row)
                if data_category in "timg":
                    delete_file(TIMG_DIR, row["filename"].split(".")[0]
                                + "-timg.png")
                elif data_category in "crop":
                    crop_filename = row["filename"].split(".")
                    delete_file(IMAGE_DIR, crop_filename[0] + "-crop."
                                + crop_filename[1])
                else:
                    delete_file(IMAGE_DIR, row["filename"])
        else:
            new_data_rows.append(row)
    return new_data_rows


def dir_cleanup(DATA_FILE, TIMG_SAVE, IMAGE_DIR, TIMG_DIR, ORIG_SAVE,
                CROP_SAVE, TMP_SAVE, FIELD_NAMES, date_time, field_dict):
    '''
    Clean up directory to specified amount of images.
    '''
    category_dict = {"timg": TIMG_SAVE, "crop": CROP_SAVE, "orig": ORIG_SAVE,
                     "tmp": TMP_SAVE}
    data_rows = read_data_rows(DATA_FILE, FIELD_NAMES)[1:]
    for key, value in category_dict.items():
        for item in range(len(category_dict.items())):
            data_rows = sort_categories(IMAGE_DIR, TIMG_DIR, date_time,
                                        data_rows, key, value)
    write_data_rows(DATA_FILE, FIELD_NAMES, data_rows)
    return SystemExit(0)


def delete_file(IMAGE_DIR, apod_filename):
    '''Delete file. Takes a path and a filename as arguments.'''
    try:
        os.remove(IMAGE_DIR + apod_filename)
    except FileNotFoundError as e:
        print(e)


def reset_field_dict(field_dict):
    field_dict = SetupConfig().field_dict
    return field_dict


def main():
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))
    resp = test_connection(RESP_URL)
    check_data_header(DATA_FILE, FIELD_NAMES)
    formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, field_dict,
                   date_time, resp)
    download_apod(IMAGE_DIR, field_dict)

    while verify_dimensions(IMAGE_DIR, MIN_SIZE, field_dict):
        field_dict["uid"] = date_time
        if "tmp" not in field_dict["category"]:
            field_dict["category"].append("tmp")
        create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE,
                         FIELD_NAMES, field_dict)
        append_data(DATA_FILE, FIELD_NAMES, field_dict)
        formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, field_dict,
                       date_time, generate_data(API_KEY))
        download_apod(IMAGE_DIR, field_dict)
        create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES, field_dict)
    create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES, field_dict)
    crop_image(IMAGE_DIR, DATA_FILE, QUALITY, MIN_SIZE, CROP_RATIO,
               FIELD_NAMES, field_dict)
    if "orig" not in field_dict["category"]:
        field_dict["category"].append("orig")
    if "tmp" in field_dict["category"]:
        field_dict["category"].remove("tmp")
    append_data(DATA_FILE, FIELD_NAMES, field_dict)
    set_background(IMAGE_DIR, QUALITY, CUSTOM_CMD, CUSTOM_ENV, field_dict)
    dir_cleanup(DATA_FILE, TIMG_SAVE, IMAGE_DIR, TIMG_DIR, ORIG_SAVE,
                CROP_SAVE, TMP_SAVE, FIELD_NAMES, date_time, field_dict)
    SystemExit(0)


if __name__ == "__main__":

    main()
