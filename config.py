#!/bin/python


import tomllib
from pathlib import Path


class SetupConfig:
    def __init__(self):
        self.HOME = str(Path.home())
        self.FIELD_NAMES = ["apod-date", "title", "explanation", "html-url",
                            "img-url", "filename", "image-WxH", "image-size",
                            "copyright", "uid", "category"]
        try:
            with open(self.HOME + "/.config/APODWall/config", "rb") as config:
                self.conf = tomllib.load(config)
        except (tomllib.TOMLDecodeError, FileNotFoundError,
                PermissionError, OSError, AttributeError) as e:
            print(e)
            raise SystemExit(1)

        try:
            self.IMAGE_DIR = self.conf["GENERAL"]["IMAGE_DIR"]
            self.TIMG_DIR = self.conf["GENERAL"]["TIMG_DIR"]
            self.DATA_FILE = self.conf["GENERAL"]["DATA_FILE"]
            self.TIMG_SAVE = self.conf["GENERAL"]["TIMG_SAVE"]
            self.ORIG_SAVE = self.conf["GENERAL"]["ORIG_SAVE"]
            self.CROP_SAVE = self.conf["GENERAL"]["CROP_SAVE"]
            self.TMP_SAVE = self.conf["GENERAL"]["TMP_SAVE"]
            self.QUALITY = self.conf["IMAGE"]["QUALITY"]
            self.MIN_SIZE = self.conf["IMAGE"]["MIN_SIZE"]
            self.CROP_RATIO = self.conf["IMAGE"]["CROP_RATIO"]
            self.CUSTOM_CMD = self.conf["CUSTOM"]["CUSTOM_CMD"]
            self.CUSTOM_ENV = self.conf["CUSTOM"]["CUSTOM_ENV"]
            self.API_KEY = self.conf["API"]["API_KEY"]
        except (ValueError, KeyError):
            raise SystemExit(1)
