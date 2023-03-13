# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import logging
import time
import re
from math import ceil, floor
from pathlib import Path, PurePath
from collections import namedtuple
from webbrowser import open_new_tab
from random import randint

from PyQt6.QtCore import (Qt, pyqtSlot, QAbstractTableModel, QSize, QEvent,
                          QSortFilterProxyModel, QSettings, QMimeData, QRunnable,
                           QThreadPool, QMutex, QThread, QTimer, QCoreApplication,
                           QPoint)
from PyQt6.QtGui import (QAction, QPixmap, QImage, QPainter, QIcon, QDrag, QCursor)
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QGridLayout,
                             QGroupBox, QPushButton, QStackedWidget,
                             QFormLayout, QLabel, QSpinBox, QComboBox,
                             QLineEdit, QCheckBox, QMenuBar, QMenu, QStatusBar,
                             QToolBar, QFileDialog, QStyledItemDelegate,
                             QTableView, QHeaderView, QGraphicsScene,
                             QGraphicsView, QSystemTrayIcon)

from fetchAPOD import (test_connection, generate_data, formulate_data,
                      download_apod, set_background, gen_day, gen_month,
                      gen_year, test_valid, make_url, verify_dimensions,
                      create_thumbnail, crop_image, check_data_header,
                      write_data_header, append_data, write_data_rows,
                      read_data_rows, sort_categories, dir_cleanup,
                      delete_file, reset_field_dict)
from fetchAPOD import main as main_cli
from config import SetupConfig
from ui_main import Ui_MainWindow
import qdarktheme


class GUI(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)

        if getattr(sys, 'frozen', False):
            self.app_path = sys._MEIPASS
        else:
            self.app_path = os.path.dirname(os.path.abspath(__file__))

        self.setupUi(self)
        self.settings = QSettings('fetchAPOD', 'fetchAPOD')

        self.mutex = QMutex()
        # gui settings
        try:
            self.resize(
                    self.settings.value(
                    "window size")
                    )
            self.move(
                self.settings.value(
                    "window position")
                )
            self.save_path.setText(
                self.settings.value(
                    "save_path")
                )
            self.timg_path.setText(
                self.settings.value(
                    "timg_path")
                )
            self.appdata_path.setText(
                self.settings.value(
                    "appdata_path")
                )
            self.apikey_lineedit.setText(
                self.settings.value(
                    "apikey_lineedit")
                )
            self.command_lineedit.setText(
                self.settings.value(
                    "command_lineedit")
                )
            self.envvar_lineedit.setText(
                self.settings.value(
                    "envvar_lineedit")
                )
            self.autorun_checkbox.setCheckState(
                self.settings.value(
                    "autorun_checkbox")
                )
            self.quality_combobox.setCurrentText(
                self.settings.value(
                    "quality_combobox")
                )
            self.quality_combobox.setCurrentText(
                self.settings.value(
                    "theme_combobox")
                )
            self.minsizeW_spinbox.setValue(
                    int(self.settings.value(
                        "minsizeW_spinbox"))
                    )
            self.minsizeH_spinbox.setValue(
                    int(self.settings.value(
                        "minsizeH_spinbox"))
                    )
            self.cropratioW_spinbox.setValue(
                    int(self.settings.value(
                        "cropratioW_spinbox"))
                    )
            self.cropratioH_spinbox.setValue(
                    int(self.settings.value(
                        "cropratioH_spinbox"))
                    )
            self.save_spinbox.setValue(
                    int(self.settings.value(
                        "save_spinbox"))
                    )
            self.timg_spinbox.setValue(
                    int(self.settings.value(
                        "timg_spinbox"))
                    )
            self.crop_spinbox.setValue(
                    int(self.settings.value(
                        "crop_spinbox"))
                    )
            self.tmp_spinbox.setValue(
                    int(self.settings.value(
                        "tmp_spinbox"))
                    )
            self.timeinterval_spinbox.setValue(
                    int(self.settings.value(
                        "timeinterval_spinbox"))
                    )

        except (AttributeError, TypeError) as error:
            print(error)
            pass

        # named tuple till find better way to send image
        self.image_data = namedtuple("image_data",
                                        ["id", "tooltip", "image", "html"]
                                     )

        try:
            conf = SetupConfig()
            self.FIELD_NAMES = conf.FIELD_NAMES
            self.field_dict = conf.field_dict
            self.RESP_URL = conf.RESP_URL
            self.IMAGE_DIR = Path(self.save_path.text())
            self.TIMG_DIR = Path(self.timg_path.text())
            self.DATA_FILE = self.appdata_path.text()
            self.ORIG_SAVE = self.save_spinbox.value()
            self.TIMG_SAVE = self.timg_spinbox.value()
            self.CROP_SAVE = self.crop_spinbox.value()
            self.TMP_SAVE = self.tmp_spinbox.value()
            self.QUALITY =  self.quality_combobox.currentText()

            self.MIN_SIZE = "{}x{}".format(
                    str(self.minsizeW_spinbox.value()),
                    str(self.minsizeH_spinbox.value())
                    )
            self.CROP_RATIO = "{}:{}".format(
                    str(self.cropratioW_spinbox.value()),
                    str(self.cropratioH_spinbox.value())
                    )

            self.API_KEY = self.apikey_lineedit.text()
            self.CUSTOM_CMD = self.command_lineedit.text()
            self.CUSTOM_ENV = self.envvar_lineedit.text()
            self.TIME_INTERVAL_GUI = self.timeinterval_spinbox.value()
            self.REDOWNLOAD = conf.REDOWNLOAD

        except (AttributeError, TypeError):
            pass

        # connect top menu
        self.menu_quit.triggered.connect(
                lambda: sys.exit(self.close())
                )
        self.menu_apodnasa.triggered.connect(
                lambda: open_new_tab("https://apod.nasa.gov")
                )
        self.menu_fetchapodgit.triggered.connect(
                lambda: open_new_tab("https://github.com/jameseh/fetchAPOD")
                )

        # settings page - connect buttons
        self.save_button.clicked.connect(self.folder_dialog)
        self.timg_button.clicked.connect(self.folder_dialog)
        self.appdata_button.clicked.connect(self.file_dialog)

        # settings page - connect line edits
        self.apikey_lineedit.textChanged.connect(self.set_apikey)
        self.command_lineedit.textChanged.connect(self.set_command)
        self.envvar_lineedit.textChanged.connect(self.set_envvar)

        # settings page - connect checkboxes and comboboxes
        self.autorun_checkbox.clicked.connect(self.autorun_value)
        self.quality_combobox.currentTextChanged.connect(self.quality_status)
        self.theme_combobox.currentTextChanged.connect(qdarktheme.setup_theme)

        # settings page - connect list of spinboxes
        spinbox_list = [self.minsizeW_spinbox,
                        self.minsizeH_spinbox,
                        self.cropratioW_spinbox,
                        self.cropratioH_spinbox,
                        self.save_spinbox,
                        self.timg_spinbox,
                        self.crop_spinbox,
                        self.tmp_spinbox, 
                        self.timeinterval_spinbox
                        ]

        for item in spinbox_list:
            item.valueChanged.connect(self.spinbox_value)

        # initiate qgraphicsview and scene
        self.view = PixmapView(self.fetch_scene)
        self.fetch_grid.layout().addWidget(self.view)
        self.view.installEventFilter(self.view.view_scene)

        # add qdarktheme to combobox
        self.theme_combobox.addItems(
            qdarktheme.get_themes()
            )
        # set main window icon
        window_icon = QIcon(str(
                Path(self.app_path).joinpath(
                    "data",
                    "fetchapod.ico"))
                            )
        self.setWindowIcon(window_icon)

        # connect bottom button menu and set icons
        try:
            self.settings_button.clicked.connect(
                    lambda: self.set_index(1)
                    )
            self.settings_button.setIcon(QIcon(str(
                Path(self.app_path).joinpath(
                    "data",
                    "google_icon_adminsettings.png")))
                                         )
            self.gallery_button.clicked.connect(
                    lambda: self.set_index(
                        3, self.start_thread(self.populate_gallery()))
                    )
            self.gallery_button.setIcon(QIcon(str(
                Path(self.app_path).joinpath(
                    "data",
                    "google_icon_gallerythumbnail.png")))
                                        )
            self.fetch_button.clicked.connect(
                    lambda: self.start_thread(self.fetchapod("false"))
                    )
            self.fetch_button.setIcon(window_icon)
            self.apod_button.clicked.connect(
                    lambda: self.set_index(2)
                    )
            self.apod_button.setIcon(QIcon(str(
                Path(self.app_path).joinpath(
                    "data",
                    "google_icon_imagesearch.png")))
                                     )
            self.setwallpaper_button.clicked.connect(
                    lambda: self.setwallpaper_current()
                    )
            self.setwallpaper_button.setIcon(QIcon(str(
                Path(self.app_path).joinpath(
                    "data",
                    "google_icon_setwallpaper.png")))
                                             )
        except IndexError:
            pass

        # init qthreadpool
        self.threadpool = QThreadPool.globalInstance()
        self.threadpool.waitForDone(-1)

        # init qtimer and connect signals
        self.fetch_timer = QTimer(self)
        self.fetch_timer.timeout.connect(
                lambda: self.start_thread(self.fetchapod("true", None, "false"))
                )
        self.timeinterval_spinbox.valueChanged.connect(
                lambda: self.start_thread_interval()
                )

        # init a bunch of gui components
        self.init_fetch_timer()
        self.init_systray()
        self.init_defaults()
        self.init_gallery()
        self.init_splash()

    def index_set_visible(self, index=None, fn=None):
        # sets the application to visible, then calls set_index if both
        # fn and index are supplied.
        if not self.isVisible():
            self.setWindowState(Qt.WindowState.WindowActive)

        if index != None and fn != None:
            self.set_index(index, fn)

    def set_index(self, index=None, fn=None):
        # set index then call function if one is supplied.
        if self.stacked.currentIndex() != index:
            self.stacked.setCurrentIndex(index)

        if fn != None:
            fn

    def start_thread(self, fn):
        # takes a funcion as argument, starts function in it's own thread.
        self.threadpool.clear()
        worker = Threaded(fn)
        self.threadpool.start(worker)

    def start_thread_interval(self):
        # start a thread to run on time interval using qtimer.
        if self.fetch_timer.isActive():
            self.fetch_timer.stop()

        if self.TIME_INTERVAL_GUI != 0:
            self.fetch_timer.start(self.TIME_INTERVAL_GUI * 60000)

    def folder_dialog(self):
        try:
            # create a folder dialog
            folder_path = QFileDialog().getExistingDirectory(
                    self,
                    'Select Folder',
                    )

            # check what object sent signal, set text accordingly
            if self.sender() is self.save_button:
                self.save_path.setText(folder_path)
                self.IMAGE_DIR = self.save_path.text()

            if self.sender() is self.timg_button:
                self.timg_path.setText(folder_path)
                self.TIMG_DIR = self.timg_path.text()

        except AttributeError:
            pass

    def file_dialog(self):
        try:
            # create a file dialog
            filename, _ = QFileDialog().getOpenFileName(
                    self,
                    "Select File",
                    "","All Files (*)",
                    )

            self.appdata_path.setText(filename)
            self.DATA_FILE = self.appdata_path.text()

        except AttributeError:
            pass

    def set_apikey(self):
        self.API_KEY = self.apikey_lineedit.text()

    def set_command(self):
        self.CUSTOM_CMD = self.command_lineedit.text()

    def set_envvar(self):
        self.CUSTOM_ENV = self.envvar_lineedit.text()

    def autorun_value(self):
        self.AUTORUN = self.autorun_checkbox.checkState()

    def quality_status(self):
        if "HD" in self.quality_combobox.currentText():
            self.QUALITY = "HD"

        else:
            self.QUALITY = "STD"

    def spinbox_value(self):
        # set values variables that use spinbox. Use sender()
        # to identify the input spinbox.
        if "minsize" in str(self.sender()):
            minW = self.minsizeW_spinbox.value()
            minH = self.minsizeH_spinbox.value()
            self.MIN_SIZE = f"{minW}x{minH}"

        elif "cropratio" in str(self.sender()):
            cropW = self.cropratioW_spinbox.value()
            cropH = self.cropratioH_spinbox.value()
            self.CROP_RATIO = f"{cropW}:{cropH}"

        elif self.save_spinbox == self.sender():
            self.ORIG_SAVE = self.save_spinbox.value()

        elif self.timg_spinbox == self.sender():
            self.TIMG_SAVE = self.timg_spinbox.value()

        elif self.crop_spinbox == self.sender():
            self.CROP_SAVE = self.crop_spinbox.value()

        elif self.tmp_spinbox == self.sender():
            self.TMP_SAVE = self.tmp_spinbox.value()

        elif self.timeinterval_spinbox == self.sender():
            self.TIME_INTERVAL_GUI = self.timeinterval_spinbox.value()

    def launch_apodurl(self, cell):
        cell = self.gallery_selected()
        open_new_tab(cell[3])

    def gallery_selected(self):
        # get the the row and column of the currently selected index.
        row_col = self.gallery_tableview.selectionModel().selectedIndexes()
        for item in row_col:
            row = item.row()
            col = item.column()
        # get the html link located in the image_data model.
        # find its index by column + row * number of columns
        try:
            cell = self.gallery_model.image_data[
                       row * self.gallery_model.table_columns + col]

        except IndexError:
            pass

        return cell

    def setwallpaper_current(self):
        self.mutex.lock()
        row = read_data_rows(self.DATA_FILE, self.FIELD_NAMES)[-1]
        set_background(self.IMAGE_DIR, self.QUALITY, self.CUSTOM_CMD,
                       self.CUSTOM_ENV, row)
        self.mutex.unlock()

    def fetchapod(self, setwallpaper, resp_url=None, redownload="false"):
        # run fetchAPOD main() imported as main_cli(), then get the most
        # recent entry in data file.
        self.mutex.lock()
        
        if resp_url is None:
            resp_url = self.RESP_URL        

        else:
            apod_date = re.search(r"[0-9]{6}", resp_url).group()

            if int(apod_date[:2]) >= 96:
                apod_year = f"19{apod_date[:2]}"
            else:
                apod_year = f"20{apod_date[:2]}"
                resp_url = (f"{self.RESP_URL}{self.API_KEY}&date="
                            + "{str(apod_year)}-{str(apod_date[2:4])}-"
                            + "{str(apod_date[4:6])}")

        # the int "0" is time interval, set to 0 in gui to turn off.
        # uses a qtimer to run on time interval in gui
        main_cli(self.FIELD_NAMES, self.IMAGE_DIR, self.TIMG_DIR,
                 self.DATA_FILE, self.ORIG_SAVE, self.TIMG_SAVE,
                 self.CROP_SAVE, self.TMP_SAVE, self.QUALITY,
                 self.MIN_SIZE, self.CROP_RATIO, self.API_KEY,
                 self.CUSTOM_CMD, self.CUSTOM_ENV, setwallpaper,
                 resp_url, "0", redownload, self.field_dict)

        row = read_data_rows(self.DATA_FILE, self.FIELD_NAMES)[-1]
        self.mutex.unlock()

        # format tooltip text
        html = row["html"]
        file = Path(self.IMAGE_DIR).joinpath(row["filename"])

        tooltip = (f'{row["title"]} - {row["copyright"]}\n'
                 + f'{row["date"]}\n\n'
                 + f'{row["explanation"]}\n\n'
                 +  'Dimensions:\n\n'
                 + f'{row["img-WxH"]}\n'
                 + f'Size: {row["img-size"]}'
                   )

        self.view.pixmap = QPixmap(str(file))
        self.fetch_scene.setToolTip(tooltip)
        self.view.html = html

    def populate_gallery(self):
        # populate gallery with the data file.
        self.gallery_tableview.setModel(None)
        self.init_gallery()
        try:
            self.mutex.lock()
            self.apod_data = read_data_rows(self.DATA_FILE,
                                            self.FIELD_NAMES)[1:]

            for num, row in enumerate(self.apod_data):
                tooltip = (f'{row["title"]} - {row["copyright"]}\n'
                         + f'{row["date"]}\n\n'
                         + f'{row["explanation"]}\n\n'
                         +  'Dimensions:\n\n'
                         + f'{row["img-WxH"]}\n'
                         + f'Size: {row["img-size"]}'
                           )

                image = QImage(str(self.TIMG_DIR.joinpath(row["filename"])))
                item = self.image_data(num, tooltip, image, row["html"])
                self.gallery_model.image_data.append(item)
                self.resizeEvent(event=None)

        except (TypeError, AttributeError, IndexError) as error:
            print(f"populate_gallery: {error}")
            pass

        self.mutex.unlock()
        self.gallery_tableview.resizeRowsToContents()
        self.gallery_tableview.resizeColumnsToContents()
        self.gallery_model.layoutChanged.emit()

    def init_fetch_timer(self):
        # initiate run on time interval if not 0.
        if self.timeinterval_spinbox.value() != 0:
            self.start_thread_interval()

    def init_splash(self):
        # initiat the fetchapod logo splash screen
        self.stacked.setCurrentIndex(2)
        splash = QPixmap(
                str(Path(self.app_path).joinpath(
                    "data",
                    "fetchapod.png"))
                )
        new_pixmap = QPixmap(splash)
        self.view.pixmap = new_pixmap
        self.view.scale(2.5, 2.5)

    def init_defaults(self):
        # set default folders and data file if none.
        if self.save_path.text() == None:
            self.save_path.setCurrentText(
                    str(Path(self.app_path).joinpath(
                        "image"))
                    )

        if self.timg_path.text() == None:
            self.timg_path.setCurrentText(
                    str(Path(self.app_path).joinpath(
                        "image",
                        "thumbnail"))
                    )

        if self.appdata_path.text() == None:
            self.appdata_path.setCurrentText(
                    str(Path(self.app_path).joinpath(
                        "app.data"))
                    )

    def init_gallery(self):
        # initiate gallery model and delegate
        delegate = DelegateData()
        self.gallery_model = GalleryModel()
        self.gallery_tableview.setItemDelegate(delegate)
        self.gallery_tableview.setModel(self.gallery_model)
        self.gallery_tableview.horizontalHeader().hide()
        self.gallery_tableview.verticalHeader().hide()
        self.gallery_tableview.setGridStyle(Qt.PenStyle.NoPen)
        self.gallery_tableview.doubleClicked.connect(self.launch_apodurl)
        self.gallery_tableview.installEventFilter(self)
        self.gallery_tableview.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self.gallery_tableview.customContextMenuRequested.connect(delegate.contextMenuEvent)

    def init_systray(self):
        # system tray
        tray_icon = QIcon(
                str(Path(self.app_path).joinpath(
                    "data",
                    "fetchapod.ico"))
                )
        tray = QSystemTrayIcon(self)
        tray.setIcon(tray_icon)
        tray.setVisible(True)

        menu = QMenu(self)
        action_fetchpage = QAction(
                "fetch! APOD",
                self
                )
        action_gallerypage = QAction(
                "Gallery",
                self
                )
        action_settings = QAction(
                "Settings",
                self
                )
        action_nasaapod = QAction(
                "NasaAPOD Homepage",
                self
                )
        action_fetchapod = QAction(
                "fetchAPOD Homepage",
                self
                )
        action_exit = QAction(
                "Close Application",
                self
                )

        action_fetchpage.triggered.connect(
            lambda: self.index_set_visible(2)
            )
        action_gallerypage.triggered.connect(
            lambda: self.index_set_visible(
                3,
                self.populate_gallery())
            )
        action_settings.triggered.connect(
            lambda: self.index_set_visible(1)
            )
        action_nasaapod.triggered.connect(
            lambda: open_new_tab(
                "https://apod.nasa.gov")
            )
        action_fetchapod.triggered.connect(
            lambda: open_new_tab(
                "https://github.com/jameseh/fetchAPOD")
            )
        action_exit.triggered.connect(
            lambda: sys.exit()
            )

        menu.addAction(action_fetchpage)
        menu.addAction(action_gallerypage)
        menu.addSeparator()
        menu.addAction(action_fetchapod)
        menu.addAction(action_nasaapod)
        menu.addSeparator()
        menu.addAction(action_settings)
        menu.addAction(action_exit)
        tray.setContextMenu(menu)
        menu.show()
        tray.show()

    def closeEvent(self, event):
        # override closeEvent() to save qsettings on close
        self.settings.setValue(
                "window size",
                self.size()
                )
        self.settings.setValue(
                "window position",
                self.pos()
                )
        self.settings.setValue(
                "save_path",
                self.save_path.text()
                )
        self.settings.setValue(
                "timg_path",
                self.timg_path.text()
                )
        self.settings.setValue(
                "appdata_path",
                self.appdata_path.text()
                )
        self.settings.setValue(
                "apikey_lineedit",
                self.apikey_lineedit.text()
                )
        self.settings.setValue(
                "command_lineedit",
                self.command_lineedit.text()
                )
        self.settings.setValue(
                "envvar_lineedit",
                self.envvar_lineedit.text()
                )
        self.settings.setValue(
                "autorun_checkbox",
                self.autorun_checkbox.checkState()
                )
        self.settings.setValue(
                "quality_combobox",
                self.quality_combobox.currentText()
                )
        self.settings.setValue(
                "theme_combobox",
                self.theme_combobox.currentText()
                )
        self.settings.setValue(
                "minsizeW_spinbox",
                self.minsizeW_spinbox.value()
                )
        self.settings.setValue(
                "minsizeH_spinbox",
                self.minsizeH_spinbox.value()
                )
        self.settings.setValue(
                "cropratioW_spinbox",
                self.cropratioW_spinbox.value()
                )
        self.settings.setValue(
                "cropratioH_spinbox",
                self.cropratioH_spinbox.value()
                )
        self.settings.setValue(
                "save_spinbox",
                self.save_spinbox.value()
                )
        self.settings.setValue(
                "timg_spinbox",
                self.timg_spinbox.value()
                )
        self.settings.setValue(
                "crop_spinbox",
                self.crop_spinbox.value()
                )
        self.settings.setValue(
                "tmp_spinbox",
                self.tmp_spinbox.value()
                )
        self.settings.setValue(
                "timeinterval_spinbox",
                self.timeinterval_spinbox.value()
                )

    def resizeEvent(self, event):
    #  override resize event to resize gallery columns dynamically
        width = self.width()
        self.gallery_model.table_columns = ceil(width / 375)


class PixmapView(QGraphicsView):
    '''
    Resize, fit to screen, and keeping aspect ratio of pixmap.
    Provides context menu for this view.
    '''

    def __init__(self, parent=None):
        QGraphicsView.__init__(self, parent)
        self.setHorizontalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(
                Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        self.setTransformationAnchor(
                QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setResizeAnchor(
                QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setOptimizationFlags(
                QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing)

        self.setMouseTracking(True)

        self.view_scene = QGraphicsScene()
        self.setScene(self.view_scene)
        self.new_pixmap = self.scene().addPixmap(QPixmap())
        self.html = None
        self.viewport().update()

    def paint(self, painter, option):
        painter.setDevicePixelRatio(2.0)
        painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True
                )
        painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform,
                True
                )

        painter.drawImage(
                ceil(option.rect.x()),
                ceil(option.rect.y()),
                self.new_pixmap
                )

    @property
    def pixmap(self):
        new_pixmap = self.new_pixmap = self.m_pixmapItem.pixmap()
        new_pixmap.setDevicePixelRatio(dpi)
        return new_pixmap

    def setPixmapRect(self, new_pixmap):
        self.setSceneRect(0, 0, new_pixmap.width(),
                          new_pixmap.height()
                          )

    @pixmap.setter
    def pixmap(self, new_pixmap):
        self.new_pixmap.setPixmap(new_pixmap)
        self.setPixmapRect(new_pixmap)
        self.alignPixmap()

    def alignPixmap(self):
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.fitInView(self.new_pixmap,
                       Qt.AspectRatioMode.KeepAspectRatio
                       )

    def closeEvent (self, event):
        self.scene.clear()
        event.accept()

    def contextMenuEvent(self, event):
        zoom_button = QAction(
                "Zoom",
                self
                )
        zoomout_buttom = QAction(
                "Zoom Out",
                self
                )
        sizeto_button = QAction(
                "Fit to Screen",
                self
                )
        openapod_button = QAction(
                "Open Selections Webpage",
                self
                )
        truesize_button = QAction(
                "Set True Size"
                )

        zoom_button.triggered.connect(
                lambda: self.scale(1.5, 1.5)
                )
        zoomout_buttom.triggered.connect(
                lambda: self.scale(0.5, 0.5)
                )
        sizeto_button.triggered.connect(
                lambda: self.alignPixmap()
                )
        openapod_button.triggered.connect(
                lambda: open_new_tab(self.html)
                )
        truesize_button.triggered.connect(
                lambda: self.resetTransform()
                )

        menu = QMenu(self)
        menu.addAction(zoom_button)
        menu.addAction(zoomout_buttom)
        menu.addAction(sizeto_button)
        menu.addAction(truesize_button)
        menu.addSeparator()
        menu.addAction(openapod_button)
        menu.exec(QCursor.pos())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
           self.alignPixmap()

        if event.button() == Qt.MouseButton.LeftButton:
            self.toggleDragMode()
        super().mousePressEvent(event)

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)

        else:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def wheelEvent(self,event):
            if event.angleDelta().y() > 0:
                scale = 1.1
            else:
                scale = 0.9
            self.scale(scale, scale)


class DelegateData(QStyledItemDelegate):
    '''
    Delegate for the gallery model, paints APOD thumbnails in
    created cells
    '''
    def paint(self, painter, option, index):
        painter.setRenderHint(
                QPainter.RenderHint.Antialiasing,
                True
                )
        painter.setRenderHint(
                QPainter.RenderHint.SmoothPixmapTransform,
                True
                )

        cell_padding = 25
        # get the data for the image to display
        self.data = index.model().data(index, Qt.ItemDataRole.DisplayRole)

        if self.data is None:
            return

        if self.data.image.isNull():
            return

        # create cell to contain image and then scale image
        width = option.rect.width() - cell_padding * 2
        height = option.rect.height() - cell_padding * 2

        scaled = self.data.image.scaled(
                width,
                height,
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio
                )

        # position in the middle of area and paint it
        x = cell_padding + (width - scaled.width()) / 2
        y = cell_padding + (height - scaled.height())

        scaled.setDevicePixelRatio(dpi)
        painter.drawImage(
                ceil(option.rect.x() + x),
                ceil(option.rect.y() + y), scaled
                )

        # resize and emit change
        gui.gallery_tableview.resizeRowsToContents()
        gui.gallery_tableview.resizeColumnsToContents()
        gui.gallery_model.layoutChanged.emit()

    def sizeHint(self, dimensions, index):
        return QSize(310, 310)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.contextMenuEvent(event)
        return super().mousePressEvent(event)

    def eventFilter(self, event):
        self.contextMenuEvent(event)
        return super().eventFilter(event)

    def contextMenuEvent(self, event):
        totop_button = QAction(
                "to Top",
                self
                )
        tobottom_buttom = QAction(
                "to Bottom",
                self
                )
        setwallpaper_button = QAction(
                "Set APOD as Wallpaper",
                self
                )
        openapod_button = QAction(
                "Open APOD's Webpage",
                self
                )

        totop_button.triggered.connect(
                lambda: gui.gallery_tableview.scrollToTop()
                )
        tobottom_buttom.triggered.connect(
                lambda: gui.gallery_tableview.scrollToBottom()
                )
        setwallpaper_button.triggered.connect(
                lambda: gui.start_thread(
                    gui.fetchapod("true",
                                  gui.gallery_selected().html,
                                  "true"))
                )
        openapod_button.triggered.connect(
                lambda: open_new_tab(gui.gallery_selected()[3])
                )

        menu = QMenu()
        menu.addAction(totop_button)
        menu.addAction(tobottom_buttom)
        menu.addSeparator()
        menu.addAction(setwallpaper_button)
        menu.addAction(openapod_button)
        menu.exec(QCursor.pos())
        #self.sender().setContextMenu(menu)
        menu.show()

class GalleryModel(QAbstractTableModel):
    '''Gallery Model to comtain APOD thumbnails and information'''
    def __init__(self, todos=None):
        super().__init__()
        self.image_data = []
        self.table_columns = 1

    def data(self, index, role):
        try:
            # table structure, resize depending on self.table_columns value.
            data = self.image_data[
                    index.row() * self.table_columns + index.column()]

        except IndexError:
            return

        # set display role for our QImage
        if role == Qt.ItemDataRole.DisplayRole:
            return data

        # set tool tip role
        elif role == Qt.ItemDataRole.ToolTipRole:
            return data.tooltip

    # define columns / rows
    def columnCount(self, index):
        return self.table_columns

    def rowCount(self, index):
        items = len(self.image_data)
        return ceil(items / self.table_columns)


#class Worker(QObject):
#    def __init__(self, fn=None, timer=0):
#        super(Qthread, self).__init__()
#        self.fn = fn
#        self.timer = timer
#        self.loop_ctrl = {"break": False}

#    def run(self, fn):
#        self.fn

#    def long_run(self, fn, timer):
#        self.loop_ctrl["break"] = False

#        while True:
#            if self.ctrl["break"]:
#                return

#            self.fn
#            time.sleep(self.timer)


#class Controller(QObject):
#    worker_thread = QThread()

#    def create_thread(self):
#        worker = Worker()
#        worker.moveToThread(worker_thread)
#        workerThread.started.connect(worker.run)
#        workerThread.finished.connect(worker.deletedLater)
#        worker_thread.start()

#    def stop_thread(self):
#        self.loop_ctrl["break"] = True


class Threaded(QRunnable):
    def __init__(self, fn):
        super(Threaded, self).__init__()
        self.fn = fn

    @pyqtSlot()
    def run(self):
        self.fn


def main():
    gui = GUI()
    qdarktheme.setup_theme(custom_colors={"primary": "#818aab"},
                           corner_shape="sharp"
                           )
    gui.show()
    return gui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    gui = main()
    dpi = gui.devicePixelRatio()
    sys.exit(app.exec())
#logger_main = logging.getLogger("logger_main")
#logger_main.setLevel(logging.INFO)
#handler_main = logging.FileHandler(str(Path(gui.app_path).joinpath("data", "logger.data")))
#logger_main.addHandler(handler_main)
#log_format = logging.Formatter("%(asctime)s %(levelname)s:%(name)s:%(message)s")
