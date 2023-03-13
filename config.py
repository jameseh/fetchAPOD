# -*- mode: python ; coding: utf-8 -*-

import tomllib
from pathlib import Path


class SetupConfig:
    def __init__(self):
        self.FIELD_NAMES = ["date", "title", "explanation", "html",
                            "img-url", "filename", "img-WxH", "img-size",
                            "copyright", "uid", "category"]

        self.field_dict = {"date": "", "title": "", "explanation": "",
                           "html-url": "", "img-url": "", "filename": "",
                           "img-WxH": "", "img-size": "", "copyright": "",
                           "uid": "", "category": []}
        try:
            with open(Path.cwd().joinpath("config.toml"), "rb") as config:
                self.conf = tomllib.load(config)

        except (tomllib.TOMLDecodeError, FileNotFoundError,
                PermissionError, OSError, AttributeError) as e:
            raise SystemExit(1)

        try:
            self.IMAGE_DIR = Path.home().joinpath(
                    self.conf["GENERAL"]["IMAGE_DIR"])
            self.TIMG_DIR = Path.home().joinpath(
                    self.conf["GENERAL"]["TIMG_DIR"])
            self.DATA_FILE = Path.home().joinpath(
                    self.conf["GENERAL"]["DATA_FILE"])
            self.TIMG_SAVE = self.conf["GENERAL"]["TIMG_SAVE"]
            self.ORIG_SAVE = self.conf["GENERAL"]["ORIG_SAVE"]
            self.CROP_SAVE = self.conf["GENERAL"]["CROP_SAVE"]
            self.TMP_SAVE = self.conf["GENERAL"]["TMP_SAVE"]
            self.TIME_INTERVAL = self.conf["GENERAL"]["TIME_INTERVAL"]
            self.QUALITY = self.conf["IMAGE"]["QUALITY"]
            self.MIN_SIZE = self.conf["IMAGE"]["MIN_SIZE"]
            self.CROP_RATIO = self.conf["IMAGE"]["CROP_RATIO"]
            self.SET_WALLPAPER = self.conf["IMAGE"]["SET_WALLPAPER"]
            self.REDOWNLOAD = self.conf["IMAGE"]["REDOWNLOAD"]
            self.CUSTOM_CMD = self.conf["CUSTOM"]["CUSTOM_CMD"]
            self.CUSTOM_ENV = self.conf["CUSTOM"]["CUSTOM_ENV"]
            self.API_KEY = self.conf["API"]["API_KEY"]
            self.RESP_URL = self.conf["API"]["RESP_URL"]

        except (ValueError, KeyError) as error:
            print("confing.py: {error}")
            raise SystemExit(1)
