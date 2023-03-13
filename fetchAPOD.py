# -*- mode: python ; coding: utf-8 -*-
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
import ctypes
import time
from pathlib import Path
from datetime import datetime
from json import loads, decoder

from PIL import Image
import requests

from config import SetupConfig


def init_variables():
    '''Initiate config varliables'''
    conf = SetupConfig()
    FIELD_NAMES = conf.FIELD_NAMES
    IMAGE_DIR = conf.IMAGE_DIR
    TIMG_DIR = conf.TIMG_DIR
    DATA_FILE = conf.DATA_FILE
    TIMG_SAVE = conf.TIMG_SAVE
    ORIG_SAVE = conf.ORIG_SAVE
    CROP_SAVE = conf.CROP_SAVE
    TMP_SAVE = conf.TMP_SAVE
    QUALITY = conf.QUALITY
    MIN_SIZE = conf.MIN_SIZE
    CROP_RATIO = conf.CROP_RATIO
    CUSTOM_CMD = conf.CUSTOM_CMD
    CUSTOM_ENV = conf.CUSTOM_ENV
    API_KEY = conf.API_KEY
    RESP_URL = conf.RESP_URL + API_KEY
    SET_WALLPAPER = conf.SET_WALLPAPER
    TIME_INTERVAL = conf.TIME_INTERVAL
    field_dict = conf.field_dict
    TIME_INTERVAL = int(TIME_INTERVAL) * 60
    REDOWNLOAD = conf.REDOWNLOAD

    main(FIELD_NAMES, IMAGE_DIR, TIMG_DIR, DATA_FILE, ORIG_SAVE, TIMG_SAVE,
         CROP_SAVE, TMP_SAVE, QUALITY, MIN_SIZE, CROP_RATIO, API_KEY,
         CUSTOM_CMD, CUSTOM_ENV, SET_WALLPAPER, RESP_URL, TIME_INTERVAL,
         REDOWNLOAD, field_dict)

    return (FIELD_NAMES, IMAGE_DIR, TIMG_DIR, DATA_FILE, ORIG_SAVE, TIMG_SAVE,
            CROP_SAVE, TMP_SAVE, QUALITY, MIN_SIZE, CROP_RATIO, API_KEY,
            CUSTOM_CMD, CUSTOM_ENV, SET_WALLPAPER, RESP_URL, TIME_INTERVAL,
            REDOWNLOAD, field_dict)


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
                requests.exceptions.ConnectionError) as error:
                print(f"download_apod(1): {error}")
                pass

        except requests.exceptions.RequestException as error:
            print(f"download_apod(2): {error}")
            return


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


def formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, REDOWNLOAD,
                   field_dict, date_time, resp):
    '''
    Check if an image is in the response text. If the filename is in the
    data file run the function generate_data to get a new APOD.
    '''
    escape_list = ["(", ")", "{", "}", "|" "\\"]
    regex_string = r"image/[0-9]{4}/(.*\.(jpg|jpeg|png))"

    try:
        resp_dict = loads(resp.text)
        field_dict["uid"] = date_time
        field_dict["date"] = resp_dict["date"]
        field_dict["title"] = resp_dict["title"]
        field_dict["explanation"] = resp_dict["explanation"]
        field_dict["img-url"] = resp_dict["url"]
        field_dict["filename"] = re.search(regex_string,
                                           resp_dict["url"],
                                           re.I).group(1)
        hd_apod_filename = re.search(
            regex_string,
            resp_dict["hdurl"],
            re.I).group(1)

    except (decoder.JSONDecodeError, re.error, KeyError, AttributeError) as \
            error:
        print(f"ERROR: formulate_data(1): {error}")
        return False

    try:
        field_dict["copyright"] = resp_dict["copyright"]

    except KeyError:
        pass

    field_dict["html"] = ("https://apod.nasa.gov/apod/ap{}.html".format(
        field_dict["date"][2:].replace("-", ""))
                          )

    if "orig" not in field_dict["category"]:
        field_dict["category"].append("orig")

    if QUALITY.lower() == "hd":
        field_dict["img-url"] = resp_dict["hdurl"]
        field_dict["filename"] = hd_apod_filename

    for char in escape_list:
        for item in field_dict["filename"]:
            if char in item:
                field_dict["filename"] = field_dict["filename"].replace(
                        char, ""
                        )

    reader = read_data_rows(DATA_FILE, FIELD_NAMES)
    for row in reader:
        if field_dict["filename"] in row["filename"]:
            if REDOWNLOAD.lower() == "true":
                return True

            else:
                return False

    else:
        return True


def download_apod(IMAGE_DIR, field_dict):
    '''
    Download an APOD. Call functions to check the header and then a function
    to append the apod data to the data file.
    '''
    # Open the response and download the image. Open the data file and
    resp = test_connection(field_dict["img-url"])
    resp.raw.decode_content = True

    try:
        with open(str(Path(IMAGE_DIR).joinpath(field_dict["filename"])),
                  "wb") as image:
            image.write(resp.content)

    except (PermissionError, OSError) as error:
        print(f"download_apod: {error}")


def set_background(IMAGE_DIR, QUALITY, CUSTOM_CMD, CUSTOM_ENV, field_dict):
    '''
    Set the downloaded APOD as wallpaper. Determine the users
    $XDG_CURRENT_DESKTOP if on linux, if on windows or mac use sys to
    check platform.
    '''
    background_path = IMAGE_DIR.joinpath(field_dict["filename"])
    wallpaper_cmd = ""
    check_desktop_var = "XDG_CURRENT_DESKTOP"
    check_desktop = str(
            subprocess.check_output("echo ${}".format(check_desktop_var),
                                    shell=True)).lower()

    # check if custom command, apply wallpaper and return if so.
    if CUSTOM_CMD.strip() != "":
        wallpaper_cmd = CUSTOM_CMD
        wallpaper = wallpaper_cmd.format(str(background_path))

    # set windows wallpaper and return
    elif "win32" in sys.platform.lower():
        ctypes.windll.user32.SystemParametersInfoW(
                0x14,
                0,
                f"{background_path}",
                0x2
                )
        return

    else:
        if CUSTOM_ENV.strip() != "":
            check_desktop_var = CUSTOM_ENV

        gnome_list = ["gnome", "unity", "budgie-desktop", "lubuntu"]
        check_gnome_color = subprocess.check_output(
                "echo gsettings get org.gnome.desktop.interface color-scheme",
                shell=True)

        # gnome - Loop gnome list to check if gnome.desktop is used.
        for item in gnome_list:
            if item in check_desktop:
                if "prefer-dark" in check_gnome_color:
                    wallpaper_cmd = ("gsettings set org.gnome.desktop"
                                     + ".background picture-uri-dark {}"
                                     )

                else:
                    wallpaper_cmd = ("gsettings set org.gnome.desktop"
                                     + ".background picture-uri {}"
                                     )
        # lxde
        if "lxde" in check_desktop:
            wallpaper_cmd = "pcmanfm --set-wallpaper={}"
        # lxqt
        elif "lxqt" in check_desktop:
            wallpaper_cmd = "pcmanfm-qt --set-wallpaper={}"
        # xfce
        elif "xfce" in check_desktop:
            wallpaper_cmd = ("xfconf-query -c xfce4-desktop -p /backdrop"
                             + "/screen0/monitor0/workspace0/last-image"
                             + "-s s {}"
                             )
        # kde
        elif "kde" in check_desktop:
            wallpaper_cmd = "plasma-apply-wallpaperimage {}"
        # mac
        elif "darwin" in sys.platform.lower():
            wallpaper_cmd = (
                    'osascript -e ‘tell application “Finder” to set desktop'
                    + ' image to POSIX file “{}”‘'
                    )

    wallpaper = wallpaper_cmd.format(str(background_path))

    try:
        subprocess.Popen(wallpaper, shell=True).wait()

    except (FileNotFoundError, PermissionError, OSError) as error:
        print(f"set_background: {error}")
        return


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
    rand_date = (str(rand_year)
                 + str(rand_month)
                 + str(rand_day)
                 )
    newrand_date = (str(rand_year)
                    + str(rand_month)
                    + str(gen_day(rand_month, rand_year))
                    )
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
        rand_month = str(f"0{rand_month}")

    if len(str(rand_day)) == 1:
        rand_day = str(f"0{rand_day}")

    # Assemble the apod url using the random date. YYMMDD
    rand_apod_date = f"{str(rand_year)}-{str(rand_month)}-{str(rand_day)}"

    rand_url = ("https://api.nasa.gov/planetary/apod"
                + f"?api_key={API_KEY}&date={rand_apod_date}"
                )
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
        pass

    try:
        wallpaper = Image.open(IMAGE_DIR.joinpath(field_dict["filename"]))
        apod_width = wallpaper.width
        apod_height = wallpaper.height
        apod_size = int(
                IMAGE_DIR.joinpath(field_dict["filename"]).stat().st_size
                )

        if float(apod_size) < 102400:
            _size = round((apod_size / 1024), 2)
            apod_size = str(_size) + " Kb"

        else:
            _size = round(((apod_size / 1024) / 1024), 2)
            apod_size = str(_size) + " Mb" 

        apod_WxH = "{}x{}".format(str(wallpaper.width), str(wallpaper.height))
        field_dict["img-WxH"] = apod_WxH
        field_dict["img-size"] = apod_size
        wallpaper.close()

    except (FileNotFoundError, PermissionError, OSError) as error:
        print(f"verify_dimensions: {error}")
        return True


    if int(apod_width) < int(min_width) or int(apod_height) < int(min_height):
        if "orig" in field_dict["category"]:
            field_dict["category"].remove("orig")

        if "tmp" not in field_dict["category"]:
            field_dict["category"].append("tmp")
        return False


def create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES, field_dict):
    '''Create a thumbnail of an APOD.'''
    try:
        wallpaper = Image.open(
                Path(IMAGE_DIR).joinpath(field_dict["filename"])
                )
        wallpaper.thumbnail((310, 310))
        wallpaper.convert("RGB").save(
            Path(TIMG_DIR).joinpath(field_dict["filename"]),
            quality=95,
            optimize=True,
            subsampling=0,
            compress_level=0,
            icc_profile=wallpaper.info.get('icc_profile')
            )
        wallpaper.close()

        if "timg" not in field_dict["category"]:
            field_dict["category"].append("timg")

    except (FileNotFoundError, PermissionError, OSError) as error:
        print(f"create_thumbnail: {error}")
        return


def crop_image(IMAGE_DIR, DATA_FILE, QUALITY, MIN_SIZE, CROP_RATIO,
               FIELD_NAMES, field_dict):
    '''
    Crop the image to a specific aspect ratio.
    '''
    crop_ratio = CROP_RATIO.split(":")
    crop_ratio = int(crop_ratio[1]) / int(crop_ratio[0])

    try:
        wallpaper = Image.open(IMAGE_DIR.joinpath(field_dict["filename"]))
        width = wallpaper.width
        height = wallpaper.height

    except (FileNotFoundError, PermissionError, OSError) as error:
        print(f"crop_image(1): {error}")
        return

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

    crop_filename = field_dict["filename"].split(".")
    crop_filename = f"{crop_filename[0]}-crop.{crop_filename[1]}"

    if "crop" not in field_dict["category"]:
        field_dict["category"].append("crop")

    try:
        with Image.open(IMAGE_DIR.joinpath(field_dict["filename"])) as \
                wallpaper:
            crop = wallpaper.crop((left, bottom, right, top))
            crop.convert("RGB").save(
                    IMAGE_DIR.joinpath(crop_filename),
                    quality=95,
                    optimize=True,
                    subsampling=0,
                    compress_level=0,
                    icc_profile=wallpaper.info.get(
                    'icc_profile')
                    )

    except (FileNotFoundError, PermissionError, OSError) as error:
        print(f"crop_image(2): {error}")
        return


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

    except (csv.Error, FileNotFoundError, PermissionError, OSError) as error:
        print(f"check_data_header: {error}")
        return write_data_header(DATA_FILE, FIELD_NAMES)


def check_data_exists(DATA_FILE):
    '''
    Create the data file if not already created.
    '''
    if not Path(DATA_FILE).is_file():
        Path(DATA_FILE).touch(mode=511,
                              exist_ok=True
                              )


def write_data_header(DATA_FILE, FIELD_NAMES):
    '''Write data file header with field names.'''
    try:
        with open(DATA_FILE, "w", newline="") as data_file:
            writer = csv.DictWriter(data_file,
                                    fieldnames=FIELD_NAMES
                                    )
            writer.writeheader()

    except (csv.Error, PermissionError, OSError, UnicodeEncodeError) as error:
        print(f"write_data_header: {error}")
        return


def append_data(DATA_FILE, FIELD_NAMES, field_dict):
    '''Append data to the data file.'''
    try:
        with open(DATA_FILE, "a", newline="") as data_file:
            writer = csv.DictWriter(data_file,
                                    fieldnames=FIELD_NAMES
                                    )
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
                "category": field_dict["category"]}
                            )

    except (csv.Error, PermissionError, OSError) as error:
        print(f"append_data(1): {error}")
        return

    except UnicodeEncodeError as error:
        print(f"append_data(2): {error}")
        pass


def write_data_rows(DATA_FILE, FIELD_NAMES, data_rows):
    '''Write a new data file from a list.'''
    try:
        with open(DATA_FILE, "w", newline="") as data_file:
            writer = csv.DictWriter(data_file,
                                    fieldnames=FIELD_NAMES
                                    )
            writer.writeheader()
            writer.writerows(data_rows)

    except (csv.Error, PermissionError, OSError) as error:
        print(f"write_data_rows: {error}")
        return


def read_data_rows(DATA_FILE, FIELD_NAMES):
    '''Read data file, return a list of dictionaries sorted by UID'''
    data_rows = []

    try:
        with open(DATA_FILE, "r", newline="") as data_file:
            reader = csv.DictReader(data_file,
                                    FIELD_NAMES
                                    )

            [data_rows.append(row) for row in reader]
            data_rows = [data_rows[0]] + sorted(data_rows[1:],
                                                key=lambda
                                                item: item["uid"],
                                                reverse=False
                                                )
        return data_rows

    except (csv.Error, FileNotFoundError, PermissionError, OSError) as error:
        print(f"read_data_rows(1): {error}")
        return

    except (IndexError, UnicodeEncodeError) as error:
        print(f"read_data_rows(2): {error}")
        pass


def sort_categories(IMAGE_DIR, TIMG_DIR, data_rows, data_category,
                    data_save):
    '''Sort list of dictionaries containing apod data.'''
    new_data_rows = []
    category_rows = []

    [category_rows.append(row) for row in data_rows if data_category in
     row["category"]]

    for row in data_rows:
        if row in category_rows[:len(category_rows) - int(data_save)]:
            try:
                # convert the category string back into a list
                category_list = list(
                        row["category"].strip("][").replace("'", ""
                                                            ).split(", "))

            except AttributeError:
                category_list = row["category"]

            category_list.remove(data_category)

            if len(category_list) != 0:
                row["category"] = category_list
                new_data_rows.append(row)

                if data_category == "timg":
                    delete_file(TIMG_DIR.joinpath(row["filename"]))

                elif data_category == "crop":
                    _crop_filename = row["filename"].split(".")
                    crop_filename = (
                            f"{_crop_filename[0]}-crop.{_crop_filename[1]}"
                            )
                    delete_file(Path(IMAGE_DIR).joinpath(crop_filename))

                #elif data_category == "tmp":
                #    if "orig" in row["category"]:
                #        row["category"].remove("orig")
                #    delete_file(Path(IMAGE_DIR).joinpath(row["filename"]))

                else:
                    if data_category == "orig" and "tmp" in row["category"]:
                        row["category"].remove("tmp")

                    delete_file(Path(IMAGE_DIR).joinpath(row["filename"]))

            else:
                new_data_rows.append(row)

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
            data_rows = sort_categories(IMAGE_DIR, TIMG_DIR, data_rows, key,
                                        value)

    write_data_rows(DATA_FILE, FIELD_NAMES, data_rows)


def delete_file(file):
    '''Delete file. Takes a path and a filename as arguments.'''
    try:
        os.remove(file)

    except FileNotFoundError as error:
        print(f"delete_file: {error}")
        pass


def reset_field_dict(field_dict):
    new_field_dict = {key: "" for key in field_dict}
    field_dict = new_field_dict
    field_dict["category"] = []
    return field_dict


def check_folders_exist(IMAGE_DIR, TIMG_DIR):
    data = [IMAGE_DIR, TIMG_DIR]
    for item in data:
        if not Path(item).is_dir():
            Path(item).mkdir(mode=511,
                             parents=True,
                             exist_ok=False
                             )


def return_formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, REDOWNLOAD,
                          field_dict, date_time, resp):
    return formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, REDOWNLOAD,
                          field_dict, date_time, resp)


def formulate_data_loop(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, REDOWNLOAD,
                        field_dict, date_time):
    for attempt in range(10):
        data = return_formulate_data(DATA_FILE, QUALITY, API_KEY,
                                     FIELD_NAMES, REDOWNLOAD, field_dict,
                                     date_time, generate_data(API_KEY))

        if data:
            return data

    else:
        return False


def main(FIELD_NAMES, IMAGE_DIR, TIMG_DIR, DATA_FILE, ORIG_SAVE, TIMG_SAVE,
         CROP_SAVE, TMP_SAVE, QUALITY, MIN_SIZE, CROP_RATIO, API_KEY,
         CUSTOM_CMD, CUSTOM_ENV, SET_WALLPAPER, RESP_URL, TIME_INTERVAL,
         REDOWNLOAD, field_dict):
    '''
       Runs defined functions to download, set wallpaper, and collect
       APOD data.
    '''
    date_time = str(datetime.now().strftime("%Y%m%d%H%M%S%f"))

    check_data_exists(DATA_FILE)
    check_folders_exist(IMAGE_DIR, TIMG_DIR)
    check_data_header(DATA_FILE, FIELD_NAMES)

    if REDOWNLOAD.lower() != "true":
        RESP_URL = RESP_URL + API_KEY
    print(RESP_URL)
    resp = test_connection(RESP_URL)
    data = formulate_data(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES, REDOWNLOAD,
                          field_dict, date_time, resp)

    if data != True:
        field_dict = reset_field_dict(field_dict)
        data = formulate_data_loop(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES,
                                   REDOWNLOAD, field_dict, date_time)

    download_apod(IMAGE_DIR, field_dict)
    dimensions = verify_dimensions(IMAGE_DIR, MIN_SIZE, field_dict)

    if REDOWNLOAD.lower() != "true":
        while dimensions is False:
            field_dict["uid"] = date_time

            create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES,
                             field_dict)
            append_data(DATA_FILE, FIELD_NAMES, field_dict)
            field_dict = reset_field_dict(field_dict)
            formulate_data_loop(DATA_FILE, QUALITY, API_KEY, FIELD_NAMES,
                                REDOWNLOAD, field_dict, date_time)
            download_apod(IMAGE_DIR, field_dict)
            dimensions = verify_dimensions(IMAGE_DIR, MIN_SIZE, field_dict)

    create_thumbnail(IMAGE_DIR, TIMG_DIR, DATA_FILE, FIELD_NAMES, field_dict)
    crop_image(IMAGE_DIR, DATA_FILE, QUALITY, MIN_SIZE, CROP_RATIO,
               FIELD_NAMES, field_dict)
    append_data(DATA_FILE, FIELD_NAMES, field_dict)

    if (SET_WALLPAPER.lower() == "true"):
        set_background(IMAGE_DIR, QUALITY, CUSTOM_CMD, CUSTOM_ENV, field_dict)
        dir_cleanup(DATA_FILE, TIMG_SAVE, IMAGE_DIR, TIMG_DIR, ORIG_SAVE,
                    CROP_SAVE, TMP_SAVE, FIELD_NAMES, date_time, field_dict)

    if int(TIME_INTERVAL) != 0:
        while True:
            time.sleep(TIME_INTERVAL)
            main(FIELD_NAMES, IMAGE_DIR, TIMG_DIR, DATA_FILE, ORIG_SAVE,
                 TIMG_SAVE, CROP_SAVE, TMP_SAVE, QUALITY, MIN_SIZE, CROP_RATIO,
                 API_KEY, CUSTOM_CMD, CUSTOM_ENV, SET_WALLPAPER, RESP_URL,
                 TIME_INTERVAL, field_dict)
        SystemExit(0)

if __name__ == "__main__":
    init_variables()
