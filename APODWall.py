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
import requests
import ctypes
import csv
import json
from PIL import Image
from pathlib import Path
from configparser import ConfigParser
from datetime import datetime


def test_connection(RESP_URL):
    '''
    Test network connection. Return the response or handle the
    exceptions.
    '''

    for attempt in range(4):
        try:
            resp = requests.get(RESP_URL, timeout=(12.2, 30))
            attempt += 1
            return resp
        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.TooManyRedirects:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.RequestException as e:
            raise SystemExit(1)


def generate_data(API_KEY):

    rand_month = gen_month()
    rand_year = gen_year()
    rand_day = gen_day(rand_month, rand_year)
    test_valid(rand_day, rand_month, rand_year)
    rand_url, rand_apod_date = make_url(API_KEY, rand_year, rand_month,
                                                                            rand_day)
    resp = test_connection(rand_url)
    return resp


def formulate_data(APP_DATA, IMAGE_QUALITY, API_KEY, FIELD_NAMES, resp):
    '''
    Check if an image is in the response text. If the filename is in the
    data file run the function generate_data to get a new APOD.
    '''

    escape_list = ['(', ')', '{', '}']
    regex_string = r'image/[0-9]{4}/(.*\.(jpg|jpeg|png))'

    try:
        resp_dict = json.loads(resp.text)
        try:
            apod_copyright = resp_dict['copyright']
        except:
            pass

        apod_date = resp_dict['date']
        apod_explanation = resp_dict['explanation']
        hd_apod_url = resp_dict['hdurl']
        apod_title = resp_dict['title']
        apod_url = resp_dict['url']

        file_name = re.search(regex_string, apod_url, re.I).group(1)
        hd_file_name = re.search(regex_string, hd_apod_url, re.I).group(1)
        apod_html = ('https://apod.nasa.gov/apod/ap{}.html'.format(
                                  apod_date[2:].replace('-', '')))

        if IMAGE_QUALITY.lower() == 'hd':
            file_name = hd_file_name
            apod_url = hd_apod_url

        for char in escape_list:
            if char in file_name:
                file_name = file_name.replace(char, '')

        reader = read_data_rows(APP_DATA, FIELD_NAMES)
        for row in reader:
            if file_name in row['filename']:
                return formulate_data(APP_DATA, IMAGE_QUALITY, API_KEY,
                                                            FIELD_NAMES, generate_data(API_KEY))
        return (apod_url, file_name, apod_html, apod_date)

    except:
        return formulate_data(APP_DATA, IMAGE_QUALITY, API_KEY, FIELD_NAMES,
                                                    generate_data(API_KEY))


def download_apod(DATE, SAVE_DIR, THUMBNAIL_DIR, APP_DATA, IMAGE_QUALITY,
                  IMAGE_MIN_SIZE, API_KEY, FIELD_NAMES, apod_url, file_name,
                  apod_html, apod_date):
    '''
    Download an APOD. Call functions to check the header and then a function
    to append the apod data to the data file.
    '''

    # Open the response and download the image. Open the data file and
    # append the filename to the file.
    resp = requests.get(apod_url, stream=True)
    resp.raw.decode_content = True

    with open('{}{}'.format(SAVE_DIR, file_name), 'wb') as d:
        d.write(resp.content)
    create_thumbnail(DATE, SAVE_DIR, THUMBNAIL_DIR, APP_DATA, FIELD_NAMES,
                                      file_name, apod_html, apod_date)
    return file_name


def set_background(SAVE_DIR, IMAGE_QUALITY, CUSTOM_CMD, CUSTOM_ENV_VAR,
                   CUSTOM_STRING, file_name):
    '''
    Set the downloaded APOD as wallpaper. Determine the users
    $XDG_CURRENT_DESKTOP if on linux, if on windows or mac use sys to
    check platform.
    '''

    background_path = SAVE_DIR + file_name
    wallpaper_cmd = ''
    check_desktop_var = 'XDG_CURRENT_DESKTOP'
    check_session_string = 'XDG_SESSION_TYPE'

    if CUSTOM_CMD.strip() != '':
        wallpaper_cmd = CUSTOM_CMD

    else:
        if CUSTOM_ENV_VAR.strip() != '':
            check_desktop_var = CUSTOM_ENV_VAR
        check_desktop = str(subprocess.check_output('echo ${}'.format(check_desktop_var),
                                               shell=True)).lower()

        if CUSTOM_STRING.strip() != '':
            check_session_string = CUSTOM_STRING
        check_session = str(subprocess.check_output('echo $'.format(check_session_string),
                                              shell=True)).lower()

        gnome_list = ['gnome', 'unity', 'budgie-desktop', 'lubuntu']
        check_gnome_color = (subprocess.check_output('echo gsettings get org'
                                               + '.gnome.desktop.interface '
                                               + 'color-scheme', shell=True))

        # gnome - Loop gnome list to check if gnome.desktop is used.
        for item in gnome_list:
            if item  in check_desktop:
                if 'prefer-dark' in check_gnome_color:
                    wallpaper_cmd = ('gsettings set org.gnome.desktop.background'
                                                   + ' picture-uri-dark {}')
                else:
                    wallpaper_cmd = ('gsettings set org.gnome.desktop.background'
                                                   + ' picture-uri {}')
        #lxde
        if 'lxde' in check_desktop:
            wallpaper_cmd = 'pcmanfm --set-wallpaper={}'

        #lxqt
        if 'lxqt' in check_desktop:
            wallpaper_cmd = 'pcmanfm-qt --set-wallpaper={}'

        # xfce
        if 'xfce' in check_desktop:
            wallpaper_cmd = ('xfconf-query -c xfce4-desktop -p /backdrop/screen0'
                                           + '/monitor0/workspace0/last-image -s s {}')

        # kde
        if 'kde' in check_desktop:
            wallpaper_cmd = 'plasma-apply-wallpaperimage {}'

        # windows
        if 'win32' in sys.platform.lower():
            wallpaper_cmd = ('ctypes.windll.user32.SystemParametersInfoW'
                                           + '(0x14, 0, {}, 0x2)').format(background_path)

        # mac
        if 'darwin' in sys.platform.lower():
            wallpaper_cmd = ('osascript -e ‘tell application “Finder” to set'
                                           + ' desktop image to POSIX file'
                                           + ' “{}”‘'.format(background_path))

    wallpaper = str(wallpaper_cmd).format(background_path)
    set_wallpaper = subprocess.Popen(wallpaper, shell=True).wait()
    return


def gen_day(rand_month, rand_year):
    '''
    Generate a valid random day of the month. Factor for leap year,
    and days in accompanying month.
    '''

    # Check if the month is Febuary, if so determine if it is a leap
    # year. If year divisible by 4, and not divisible by 100, unless
    # also divisible by 400.
    if int(rand_month) == 2:
        if int(rand_year) % 4 == 0 and int(rand_year) % 100 != 0:
            if int(rand_year) % 400 == 0:
                rand_day = random.randint(1, 29)
                return rand_day
        else:
            rand_day = random.randint(1, 28)
            return rand_day

    # Determine if the month has 30 days, else the only option left
    # is 31.
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

    date = datetime.now().strftime('%Y%m%d')
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
        rand_month = str('0{}'.format(rand_month))

    if len(str(rand_day)) == 1:
        rand_day = str('0{}'.format(rand_day))

    # Assemble the apod url using the random date. YYMMDD
    rand_date = str(rand_year) + '-' + str(rand_month) + '-' + str(rand_day)
    rand_url = ('https://api.nasa.gov/planetary/apod'
                        +'?api_key={}&date={}'.format(API_KEY, rand_date))
    rand_apod_date = (str(rand_year) + '-' + str(rand_month)
                                      + '-' + str(rand_day))
    return rand_url, rand_apod_date


def verify_dimensions(DATE, SAVE_DIR, APP_DATA, IMAGE_QUALITY,
                      IMAGE_MIN_SIZE, API_KEY, FIELD_NAMES, apod_url,
                      file_name, apod_html, apod_date):
    '''
    Verify the APOD images dimensions. If the images are less than
    the value of IMAGE_MIN_SIZE return False.
    '''
    image_min_size = IMAGE_MIN_SIZE.split('x')
    min_width, min_height = image_min_size[0], image_min_size[1]
    wallpaper = Image.open(SAVE_DIR + file_name)
    width = wallpaper.width
    height = wallpaper.height

    if int(width) < int(min_width) or int(height) < int(min_height) is True:
        append_data(DATE, APP_DATA, FIELD_NAMES, file_name, apod_html,
                    apod_date, 'tmp')
        return False
    else:
        return apod_url, file_name, apod_html, apod_date


def create_thumbnail(DATE, SAVE_DIR, THUMBNAIL_DIR, APP_DATA, FIELD_NAMES,
                                          file_name, apod_html, apod_date):
    '''Create a thumbnail of an APOD.'''
    wallpaper = Image.open(SAVE_DIR + file_name)
    wallpaper.thumbnail((310, 310))
    file_name = file_name.split('.')[0] + '-thumbnail.PNG'
    wallpaper.save(THUMBNAIL_DIR + file_name)

    append_data(DATE, APP_DATA, FIELD_NAMES, file_name, apod_html,
                             apod_date, 'timg')


def crop_image(DATE, SAVE_DIR, APP_DATA, IMAGE_QUALITY, IMAGE_MIN_SIZE,
                               IMAGE_CROP_RATIO, API_KEY, FIELD_NAMES, resp, apod_url,
                               file_name, apod_html, apod_date):
    '''
    Crop the image to a specific aspect ratio.
    '''

    crop_ratio = IMAGE_CROP_RATIO.split(':')
    crop_ratio = int(crop_ratio[1]) / int(crop_ratio[0])

    wallpaper = Image.open(SAVE_DIR + file_name)
    width = wallpaper.width
    height = wallpaper.height
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

    crop_file_name = file_name.split('.')
    crop_file_name = crop_file_name[0] + '-crop.' + crop_file_name[1]

    with Image.open(SAVE_DIR + file_name) as wallpaper:
        crop = wallpaper.crop((left, bottom, right, top))
        crop.save(SAVE_DIR + crop_file_name)

    file_name = crop_file_name
    append_data(DATE, APP_DATA, FIELD_NAMES, file_name, apod_html, apod_date,
                              'crop')
    return file_name


def check_data_header(APP_DATA, FIELD_NAMES):
    '''
    Check if header exists on data file, if not call function to write the
    header
    '''

    try:
        sniffer = csv.Sniffer()
        check_header = sniffer.has_header(data_file.read())
        if data_file.seek(0):
            return True
    except:
        write_data_header(APP_DATA, FIELD_NAMES)


def write_data_header(APP_DATA, FIELD_NAMES):
    '''Write data file header with field names.'''

    with open(APP_DATA, 'w', newline='') as data_file:
        writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
        writer.writeheader()


def append_data(DATE, APP_DATA, FIELD_NAMES, file_name, apod_html, apod_date,
                                 save_value):
    '''Append data to the data file.'''

    with open(APP_DATA, 'a', newline='') as data_file:
        writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
        writer.writerow({'url': apod_html,
                                        'apod-date': apod_date,
                                        'filename': file_name,
                                        'uid': DATE,
                                        'status': save_value})


def write_data_rows(APP_DATA, FIELD_NAMES, *arg):
    '''Write a new data file from a list.'''

    with open(APP_DATA, 'w', newline='') as data_file:
        writer = csv.DictWriter(data_file, fieldnames=FIELD_NAMES)
        writer.writerows(*arg)


def read_data_rows(APP_DATA, FIELD_NAMES):
    '''Read data file, return a list of dictionaries, sorted by UID'''

    data_rows = []
    with open(APP_DATA, 'r', newline='') as data_file:
        reader = csv.DictReader(data_file, FIELD_NAMES)
        [data_rows.append(row) for row in reader]
        data_rows = sorted(data_rows, key=lambda item: item['uid'],
                                              reverse=True)
        return data_rows


def dir_cleanup(DATE, APP_DATA, DATA_SIZE, HISTORY_SIZE, SAVE_DIR,
                              THUMBNAIL_DIR, KEEP_SAVED, CROP_SAVED, TMP_SAVED,
                              FIELD_NAMES):
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
    delete_rows = []

    reader = read_data_rows(APP_DATA, FIELD_NAMES)
    for row in reader:
        if row['status'] in {'timg'}:
            timg_rows.append(row)
        elif row['status'] in {'crop'}:
            crop_rows.append(row)
        elif row['status'] in {'tmp'}:
            tmp_rows.append(row)
        else:
            data_rows.append(row)

    for row in data_rows:
        if row['uid'] in data_rows[:int(KEEP_SAVED)]:
            delete_rows.append(row)

    for row in timg_rows:
        if row in timg_rows[:int(HISTORY_SIZE)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)

    for row in crop_rows:
        if row in crop_rows[:int(CROP_SAVED)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)

    for row in tmp_rows:
        if row in tmp_rows[:int(TMP_SAVED)]:
            data_rows.append(row)
        else:
            delete_rows.append(row)

    for file_name in delete_rows:
        if row['status'] in {'timg'}:
            delete_file(THUMBNAIL_DIR, file_name['filename'])
        else:
            delete_file(SAVE_DIR, file_name['filename'])

    write_data_rows(APP_DATA, FIELD_NAMES, data_rows)
    return SystemExit(0)


def delete_file(SAVE_DIR, file_name):
    '''Delete file. Takes a path and a filename as arguments.'''

    try:
        os.remove(SAVE_DIR + file_name)
    except FileNotFoundError as e:
        print(e)


def check_data_exists(APP_DATA, FIELD_NAMES):
    '''Create the data file if not already created.'''

    try:
        open(APP_DATA, 'x')
        check_data_header(APP_DATA, FIELD_NAMES)

    except FileExistsError:
        pass


def main():
    DATE = datetime.now().strftime('%Y%m%d%H%M%S')
    HOME = str(Path.home())
    conf = ConfigParser()
    conf.read(HOME + '/.config/APODWall/config')

    SAVE_DIR = HOME + conf.get('GENERAL', 'SAVE_DIR', fallback='')
    THUMBNAIL_DIR = HOME + conf.get('GENERAL', 'THUMBNAIL_DIR', fallback='')
    APP_DATA = HOME + conf.get('GENERAL', 'APP_DATA', fallback='')
    DATA_SIZE = conf.get('GENERAL', 'DATA_SIZE', fallback='100')
    HISTORY_SIZE = conf.get('GENERAL', 'HISTORY_SIZE', fallback='100')
    KEEP_SAVED = conf.get('GENERAL', 'KEEP_SAVED', fallback='5')
    CROP_SAVED = conf.get('GENERAL', 'CROP_SAVED', fallback='1')
    TMP_SAVED = conf.get('GENERAL', 'CROP_SAVED', fallback='0')
    IMAGE_QUALITY = conf.get('IMAGE', 'IMAGE_QUALITY', fallback='hd')
    IMAGE_MIN_SIZE = conf.get('IMAGE', 'IMAGE_MIN_SIZE', fallback='1366x768')
    IMAGE_CROP_RATIO = conf.get('IMAGE', 'IMAGE_CROP_RATIO', fallback='16:9')
    CUSTOM_CMD = conf.get('CUSTOM', 'CUSTOM_CMD', fallback='')
    CUSTOM_ENV_VAR = conf.get('CUSTOM', 'CUSTOM_ENV_VAR', fallback='')
    CUSTOM_STRING = conf.get('CUSTOM', 'CUSTOM_STRING', fallback='')
    API_KEY = conf.get('NASA', 'API_KEY', fallback='')
    RESP_URL = 'https://api.nasa.gov/planetary/apod?api_key=' + API_KEY
    FIELD_NAMES = ['url', 'apod-date', 'filename', 'uid', 'status']

    resp = test_connection(RESP_URL)
    check_data_exists(APP_DATA, FIELD_NAMES)
    apod_url, file_name, apod_html, apod_date = (formulate_data(APP_DATA,
                                                                                            IMAGE_QUALITY, API_KEY,
                                                                                           FIELD_NAMES, resp))

    download_apod(DATE, SAVE_DIR, THUMBNAIL_DIR, APP_DATA, IMAGE_QUALITY,
                                    IMAGE_MIN_SIZE, API_KEY, FIELD_NAMES, apod_url, file_name,
                                    apod_html, apod_date)

    while verify_dimensions(DATE, SAVE_DIR, APP_DATA, IMAGE_QUALITY,
                                                  IMAGE_MIN_SIZE, API_KEY, FIELD_NAMES, apod_url,
                                                  file_name, apod_html, apod_date) is False:
        apod_url, file_name, apod_html, apod_date = (formulate_data(APP_DATA,
                                                                                               IMAGE_QUALITY, API_KEY,
                                                                                               FIELD_NAMES, resp))

        download_apod(DATE, SAVE_DIR, THUMBNAIL_DIR, APP_DATA, IMAGE_QUALITY,
                                        IMAGE_MIN_SIZE, API_KEY, FIELD_NAMES, apod_url,
                                        file_name, apod_html, apod_date)
    else:
        append_data(DATE, APP_DATA, FIELD_NAMES, file_name, apod_html,
                                  apod_date, 'orig')

        file_name = crop_image(DATE, SAVE_DIR, APP_DATA, IMAGE_QUALITY,
                                                      IMAGE_MIN_SIZE, IMAGE_CROP_RATIO, API_KEY,
                                                      FIELD_NAMES, resp, apod_url, file_name,
                                                      apod_html, apod_date)

        set_background(SAVE_DIR, IMAGE_QUALITY, CUSTOM_CMD,
                                        CUSTOM_ENV_VAR, CUSTOM_STRING, file_name)

        dir_cleanup(DATE, APP_DATA, DATA_SIZE, HISTORY_SIZE, SAVE_DIR,
                               THUMBNAIL_DIR, KEEP_SAVED, CROP_SAVED, 
                               TMP_SAVED, FIELD_NAMES)
        SystemExit(0)


if __name__ == '__main__':

    main()
