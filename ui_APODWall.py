# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'APODWallFbLyyz.ui'
##
## Created by: Qt User Interface Compiler version 5.15.8
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *  # type: ignore
from PySide2.QtGui import *  # type: ignore
from PySide2.QtWidgets import *  # type: ignore

from klineedit import KLineEdit


class Ui_apodwall_main_window(object):
    def setupUi(self, apodwall_main_window):
        if not apodwall_main_window.objectName():
            apodwall_main_window.setObjectName(u"apodwall_main_window")
        apodwall_main_window.resize(597, 742)
        apodwall_main_window.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.actionQUIT = QAction(apodwall_main_window)
        self.actionQUIT.setObjectName(u"actionQUIT")
        self.actionQUIT.setCheckable(True)
        self.actionQUIT.setChecked(False)
        font = QFont()
        font.setPointSize(10)
        self.actionQUIT.setFont(font)
        self.actionAPODWall_HOMEPAGE = QAction(apodwall_main_window)
        self.actionAPODWall_HOMEPAGE.setObjectName(u"actionAPODWall_HOMEPAGE")
        self.actionAPODWall_HOMEPAGE.setCheckable(True)
        self.actionAPODWALL_HOME = QAction(apodwall_main_window)
        self.actionAPODWALL_HOME.setObjectName(u"actionAPODWALL_HOME")
        self.actionAPODWALL_HOME.setCheckable(True)
        self.actionQUIT_2 = QAction(apodwall_main_window)
        self.actionQUIT_2.setObjectName(u"actionQUIT_2")
        self.actionQUIT_2.setCheckable(True)
        self.apodwall_main_widget = QWidget(apodwall_main_window)
        self.apodwall_main_widget.setObjectName(u"apodwall_main_widget")
        self.verticalLayout = QVBoxLayout(self.apodwall_main_widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.apodwall_tab_menu = QTabWidget(self.apodwall_main_widget)
        self.apodwall_tab_menu.setObjectName(u"apodwall_tab_menu")
        self.apodwall_tab_menu.setContextMenuPolicy(Qt.NoContextMenu)
        self.apodwall_tab_menu.setLayoutDirection(Qt.LeftToRight)
        self.apodwall_tab_menu.setTabPosition(QTabWidget.South)
        self.apodwall_tab_menu.setMovable(False)
        self.main_tab = QWidget()
        self.main_tab.setObjectName(u"main_tab")
        self.gridLayout_3 = QGridLayout(self.main_tab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.scrollArea = QScrollArea(self.main_tab)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 555, 481))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.gridLayout_3.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.apodwall_tab_menu.addTab(self.main_tab, "")
        self.settings_tab = QWidget()
        self.settings_tab.setObjectName(u"settings_tab")
        self.gridLayout_2 = QGridLayout(self.settings_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.image_group = QGroupBox(self.settings_tab)
        self.image_group.setObjectName(u"image_group")
        self.gridLayout = QGridLayout(self.image_group)
        self.gridLayout.setObjectName(u"gridLayout")
        self.image_quality_combobox = QComboBox(self.image_group)
        self.image_quality_combobox.addItem("")
        self.image_quality_combobox.addItem("")
        self.image_quality_combobox.setObjectName(u"image_quality_combobox")
        font1 = QFont()
        font1.setFamily(u"Noto Sans Mono")
        font1.setBold(False)
        font1.setWeight(50)
        self.image_quality_combobox.setFont(font1)

        self.gridLayout.addWidget(self.image_quality_combobox, 1, 1, 1, 1)

        self.keep_saved_label = QLabel(self.image_group)
        self.keep_saved_label.setObjectName(u"keep_saved_label")

        self.gridLayout.addWidget(self.keep_saved_label, 0, 0, 1, 1)

        self.crop_ratio_label = QLabel(self.image_group)
        self.crop_ratio_label.setObjectName(u"crop_ratio_label")

        self.gridLayout.addWidget(self.crop_ratio_label, 2, 1, 1, 1)

        self.custom_crop_ratio_lineedit = QLineEdit(self.image_group)
        self.custom_crop_ratio_lineedit.setObjectName(u"custom_crop_ratio_lineedit")

        self.gridLayout.addWidget(self.custom_crop_ratio_lineedit, 5, 1, 1, 1)

        self.custom_min_size_label = QLabel(self.image_group)
        self.custom_min_size_label.setObjectName(u"custom_min_size_label")

        self.gridLayout.addWidget(self.custom_min_size_label, 4, 0, 1, 1)

        self.crop_ratio_combobox = QComboBox(self.image_group)
        self.crop_ratio_combobox.addItem("")
        self.crop_ratio_combobox.addItem("")
        self.crop_ratio_combobox.addItem("")
        self.crop_ratio_combobox.addItem("")
        self.crop_ratio_combobox.setObjectName(u"crop_ratio_combobox")

        self.gridLayout.addWidget(self.crop_ratio_combobox, 3, 1, 1, 1)

        self.keep_saved_spinbox = QSpinBox(self.image_group)
        self.keep_saved_spinbox.setObjectName(u"keep_saved_spinbox")

        self.gridLayout.addWidget(self.keep_saved_spinbox, 1, 0, 1, 1)

        self.custom_min_size_lineedit = QLineEdit(self.image_group)
        self.custom_min_size_lineedit.setObjectName(u"custom_min_size_lineedit")

        self.gridLayout.addWidget(self.custom_min_size_lineedit, 5, 0, 1, 1)

        self.quality_label = QLabel(self.image_group)
        self.quality_label.setObjectName(u"quality_label")
        self.quality_label.setFont(font1)

        self.gridLayout.addWidget(self.quality_label, 0, 1, 1, 1)

        self.min_size_combobox = QComboBox(self.image_group)
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.addItem("")
        self.min_size_combobox.setObjectName(u"min_size_combobox")

        self.gridLayout.addWidget(self.min_size_combobox, 3, 0, 1, 1)

        self.min_size_label = QLabel(self.image_group)
        self.min_size_label.setObjectName(u"min_size_label")

        self.gridLayout.addWidget(self.min_size_label, 2, 0, 1, 1)

        self.custom_crop_ratio_label = QLabel(self.image_group)
        self.custom_crop_ratio_label.setObjectName(u"custom_crop_ratio_label")

        self.gridLayout.addWidget(self.custom_crop_ratio_label, 4, 1, 1, 1)


        self.gridLayout_2.addWidget(self.image_group, 0, 1, 1, 1)

        self.custom_settings_group = QGroupBox(self.settings_tab)
        self.custom_settings_group.setObjectName(u"custom_settings_group")
        self.verticalLayout_3 = QVBoxLayout(self.custom_settings_group)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.command_label = QLabel(self.custom_settings_group)
        self.command_label.setObjectName(u"command_label")

        self.verticalLayout_3.addWidget(self.command_label)

        self.command_lineedit = KLineEdit(self.custom_settings_group)
        self.command_lineedit.setObjectName(u"command_lineedit")

        self.verticalLayout_3.addWidget(self.command_lineedit)

        self.env_var_label = QLabel(self.custom_settings_group)
        self.env_var_label.setObjectName(u"env_var_label")

        self.verticalLayout_3.addWidget(self.env_var_label)

        self.env_var_lineedit = KLineEdit(self.custom_settings_group)
        self.env_var_lineedit.setObjectName(u"env_var_lineedit")

        self.verticalLayout_3.addWidget(self.env_var_lineedit)

        self.env_var_value_label = QLabel(self.custom_settings_group)
        self.env_var_value_label.setObjectName(u"env_var_value_label")

        self.verticalLayout_3.addWidget(self.env_var_value_label)

        self.env_var_value_lineedit = KLineEdit(self.custom_settings_group)
        self.env_var_value_lineedit.setObjectName(u"env_var_value_lineedit")

        self.verticalLayout_3.addWidget(self.env_var_value_lineedit)


        self.gridLayout_2.addWidget(self.custom_settings_group, 1, 0, 1, 1)

        self.general_group = QGroupBox(self.settings_tab)
        self.general_group.setObjectName(u"general_group")
        self.verticalLayout_2 = QVBoxLayout(self.general_group)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.apod_directory_label = QLabel(self.general_group)
        self.apod_directory_label.setObjectName(u"apod_directory_label")

        self.verticalLayout_2.addWidget(self.apod_directory_label)

        self.apod_directory_lineedit = KLineEdit(self.general_group)
        self.apod_directory_lineedit.setObjectName(u"apod_directory_lineedit")

        self.verticalLayout_2.addWidget(self.apod_directory_lineedit)

        self.data_file_label = QLabel(self.general_group)
        self.data_file_label.setObjectName(u"data_file_label")

        self.verticalLayout_2.addWidget(self.data_file_label)

        self.data_file_lineedit = KLineEdit(self.general_group)
        self.data_file_lineedit.setObjectName(u"data_file_lineedit")

        self.verticalLayout_2.addWidget(self.data_file_lineedit)

        self.data_file_size_label = QLabel(self.general_group)
        self.data_file_size_label.setObjectName(u"data_file_size_label")

        self.verticalLayout_2.addWidget(self.data_file_size_label)

        self.data_file_size_spinbox = QSpinBox(self.general_group)
        self.data_file_size_spinbox.setObjectName(u"data_file_size_spinbox")

        self.verticalLayout_2.addWidget(self.data_file_size_spinbox)


        self.gridLayout_2.addWidget(self.general_group, 0, 0, 1, 1)

        self.nasa_group = QGroupBox(self.settings_tab)
        self.nasa_group.setObjectName(u"nasa_group")
        self.verticalLayout_4 = QVBoxLayout(self.nasa_group)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.api_key_lineedit = KLineEdit(self.nasa_group)
        self.api_key_lineedit.setObjectName(u"api_key_lineedit")

        self.verticalLayout_4.addWidget(self.api_key_lineedit)

        self.api_key_lineedit_2 = KLineEdit(self.nasa_group)
        self.api_key_lineedit_2.setObjectName(u"api_key_lineedit_2")

        self.verticalLayout_4.addWidget(self.api_key_lineedit_2)

        self.api_key_lineedit_3 = KLineEdit(self.nasa_group)
        self.api_key_lineedit_3.setObjectName(u"api_key_lineedit_3")

        self.verticalLayout_4.addWidget(self.api_key_lineedit_3)

        self.api_key_lineedit_4 = KLineEdit(self.nasa_group)
        self.api_key_lineedit_4.setObjectName(u"api_key_lineedit_4")

        self.verticalLayout_4.addWidget(self.api_key_lineedit_4)


        self.gridLayout_2.addWidget(self.nasa_group, 1, 1, 1, 1)

        self.apodwall_tab_menu.addTab(self.settings_tab, "")

        self.verticalLayout.addWidget(self.apodwall_tab_menu)

        self.apodwall_group = QGroupBox(self.apodwall_main_widget)
        self.apodwall_group.setObjectName(u"apodwall_group")
        self.gridLayout_4 = QGridLayout(self.apodwall_group)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.main_button_spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout_4.addItem(self.main_button_spacer, 2, 1, 1, 1)

        self.auto_run_checkbox = QCheckBox(self.apodwall_group)
        self.auto_run_checkbox.setObjectName(u"auto_run_checkbox")
        self.auto_run_checkbox.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout_4.addWidget(self.auto_run_checkbox, 1, 2, 1, 1)

        self.daily_apod_button = QPushButton(self.apodwall_group)
        self.daily_apod_button.setObjectName(u"daily_apod_button")

        self.gridLayout_4.addWidget(self.daily_apod_button, 1, 3, 1, 1)

        self.random_apod_button_2 = QPushButton(self.apodwall_group)
        self.random_apod_button_2.setObjectName(u"random_apod_button_2")

        self.gridLayout_4.addWidget(self.random_apod_button_2, 1, 0, 1, 1)

        self.launch_apodhome_button = QPushButton(self.apodwall_group)
        self.launch_apodhome_button.setObjectName(u"launch_apodhome_button")

        self.gridLayout_4.addWidget(self.launch_apodhome_button, 2, 0, 1, 1)

        self.random_apod_button = QPushButton(self.apodwall_group)
        self.random_apod_button.setObjectName(u"random_apod_button")

        self.gridLayout_4.addWidget(self.random_apod_button, 2, 3, 1, 1)

        self.set_wallpaper_checkBox = QCheckBox(self.apodwall_group)
        self.set_wallpaper_checkBox.setObjectName(u"set_wallpaper_checkBox")
        self.set_wallpaper_checkBox.setLayoutDirection(Qt.LeftToRight)

        self.gridLayout_4.addWidget(self.set_wallpaper_checkBox, 2, 2, 1, 1)


        self.verticalLayout.addWidget(self.apodwall_group)

        apodwall_main_window.setCentralWidget(self.apodwall_main_widget)
        self.apodwall_menubar = QMenuBar(apodwall_main_window)
        self.apodwall_menubar.setObjectName(u"apodwall_menubar")
        self.apodwall_menubar.setGeometry(QRect(0, 0, 597, 29))
        self.menuMENU = QMenu(self.apodwall_menubar)
        self.menuMENU.setObjectName(u"menuMENU")
        apodwall_main_window.setMenuBar(self.apodwall_menubar)
        self.apodwall_statusbar = QStatusBar(apodwall_main_window)
        self.apodwall_statusbar.setObjectName(u"apodwall_statusbar")
        apodwall_main_window.setStatusBar(self.apodwall_statusbar)
        QWidget.setTabOrder(self.apodwall_tab_menu, self.apod_directory_lineedit)
        QWidget.setTabOrder(self.apod_directory_lineedit, self.data_file_lineedit)
        QWidget.setTabOrder(self.data_file_lineedit, self.api_key_lineedit)
        QWidget.setTabOrder(self.api_key_lineedit, self.command_lineedit)
        QWidget.setTabOrder(self.command_lineedit, self.env_var_lineedit)
        QWidget.setTabOrder(self.env_var_lineedit, self.env_var_value_lineedit)

        self.apodwall_menubar.addAction(self.menuMENU.menuAction())
        self.menuMENU.addAction(self.actionAPODWALL_HOME)
        self.menuMENU.addAction(self.actionQUIT_2)

        self.retranslateUi(apodwall_main_window)
        self.actionQUIT.triggered.connect(apodwall_main_window.close)
        self.actionAPODWall_HOMEPAGE.triggered.connect(apodwall_main_window.update)
        self.min_size_combobox.currentIndexChanged.connect(self.daily_apod_button.update)
        self.command_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.data_file_size_spinbox.valueChanged.connect(self.daily_apod_button.update)
        self.custom_min_size_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.api_key_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.env_var_value_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.apod_directory_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.crop_ratio_combobox.currentIndexChanged.connect(self.daily_apod_button.update)
        self.custom_crop_ratio_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.image_quality_combobox.currentIndexChanged.connect(self.daily_apod_button.update)
        self.env_var_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.data_file_lineedit.textChanged.connect(self.daily_apod_button.update)
        self.keep_saved_spinbox.valueChanged.connect(self.daily_apod_button.update)
        self.daily_apod_button.clicked.connect(self.daily_apod_button.update)

        self.apodwall_tab_menu.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(apodwall_main_window)
    # setupUi

    def retranslateUi(self, apodwall_main_window):
        apodwall_main_window.setWindowTitle(QCoreApplication.translate("apodwall_main_window", u"MainWindow", None))
        self.actionQUIT.setText(QCoreApplication.translate("apodwall_main_window", u"QUIT", None))
#if QT_CONFIG(tooltip)
        self.actionQUIT.setToolTip(QCoreApplication.translate("apodwall_main_window", u"Quit application.", None))
#endif // QT_CONFIG(tooltip)
        self.actionAPODWall_HOMEPAGE.setText(QCoreApplication.translate("apodwall_main_window", u"APODWall HOMEPAGE", None))
        self.actionAPODWALL_HOME.setText(QCoreApplication.translate("apodwall_main_window", u"APODWALL HOME", None))
        self.actionQUIT_2.setText(QCoreApplication.translate("apodwall_main_window", u"QUIT", None))
        self.apodwall_tab_menu.setTabText(self.apodwall_tab_menu.indexOf(self.main_tab), QCoreApplication.translate("apodwall_main_window", u"MAIN", None))
        self.image_group.setTitle(QCoreApplication.translate("apodwall_main_window", u"Image Options", None))
        self.image_quality_combobox.setItemText(0, QCoreApplication.translate("apodwall_main_window", u"HD", None))
        self.image_quality_combobox.setItemText(1, QCoreApplication.translate("apodwall_main_window", u"STANDARD", None))

        self.keep_saved_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">KEEP SAVED:</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.crop_ratio_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Pick a standard apsect ratio, or define a custom one in the format: 16:9</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.crop_ratio_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">CROP RATIO:</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.custom_min_size_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Minimum size of an image to set as wallpaper. A new image will be retrieved if the image is under the size set. Use the following format to define a custom amount, ex: 1366x736</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.custom_min_size_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">CUSTOM MIN SIZE:</span></p></body></html>", None))
        self.crop_ratio_combobox.setItemText(0, QCoreApplication.translate("apodwall_main_window", u"16:9", None))
        self.crop_ratio_combobox.setItemText(1, QCoreApplication.translate("apodwall_main_window", u"4:3", None))
        self.crop_ratio_combobox.setItemText(2, QCoreApplication.translate("apodwall_main_window", u"21:9", None))
        self.crop_ratio_combobox.setItemText(3, QCoreApplication.translate("apodwall_main_window", u"32:9", None))

        self.quality_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">QUALITY:</span></p></body></html>", None))
        self.min_size_combobox.setItemText(0, QCoreApplication.translate("apodwall_main_window", u"500x500", None))
        self.min_size_combobox.setItemText(1, QCoreApplication.translate("apodwall_main_window", u"600x400", None))
        self.min_size_combobox.setItemText(2, QCoreApplication.translate("apodwall_main_window", u"800x400", None))
        self.min_size_combobox.setItemText(3, QCoreApplication.translate("apodwall_main_window", u"800x600", None))
        self.min_size_combobox.setItemText(4, QCoreApplication.translate("apodwall_main_window", u"800x800", None))
        self.min_size_combobox.setItemText(5, QCoreApplication.translate("apodwall_main_window", u"1000x600", None))
        self.min_size_combobox.setItemText(6, QCoreApplication.translate("apodwall_main_window", u"1000x800", None))
        self.min_size_combobox.setItemText(7, QCoreApplication.translate("apodwall_main_window", u"1000x1000", None))
        self.min_size_combobox.setItemText(8, QCoreApplication.translate("apodwall_main_window", u"1200x600", None))
        self.min_size_combobox.setItemText(9, QCoreApplication.translate("apodwall_main_window", u"1200x800", None))
        self.min_size_combobox.setItemText(10, QCoreApplication.translate("apodwall_main_window", u"1200x1000", None))
        self.min_size_combobox.setItemText(11, QCoreApplication.translate("apodwall_main_window", u"1366x768", None))
        self.min_size_combobox.setItemText(12, QCoreApplication.translate("apodwall_main_window", u"1400x1050", None))
        self.min_size_combobox.setItemText(13, QCoreApplication.translate("apodwall_main_window", u"1600x900", None))
        self.min_size_combobox.setItemText(14, QCoreApplication.translate("apodwall_main_window", u"1920x1080", None))

#if QT_CONFIG(tooltip)
        self.min_size_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Minimum size of an image to set as wallpaper. A new image will be retrieved if the image is under the size set. Use the following format to define a custom amount, ex: 1366x736</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.min_size_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">MIN SIZE:</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.custom_crop_ratio_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Pick a standard apsect ratio, or define a custom one in the format: 16:9</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.custom_crop_ratio_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">CUSTOM CROP RATIO:</span></p></body></html>", None))
        self.custom_settings_group.setTitle(QCoreApplication.translate("apodwall_main_window", u"CUSTOM SETTINGS", None))
#if QT_CONFIG(tooltip)
        self.command_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>A custom command to set the background, use {}  where the path to wallpaper should go. Ex: qtile cmd-obj -o group screen1 -f set_wallpaper -a {} fill</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.command_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">COMMAND</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.env_var_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Set a custom environment variable, default is $XDG_CURRENT_DESKTOP.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.env_var_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">ENVIRONMENT VARIABLE</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.env_var_value_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>A custom string to look for when returning the value of your environment variable. </p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.env_var_value_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">ENVIRONMENT VARIABLE VALUE</span></p></body></html>", None))
        self.general_group.setTitle(QCoreApplication.translate("apodwall_main_window", u"GENERAL SETTINGS", None))
#if QT_CONFIG(tooltip)
        self.apod_directory_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Directory to save Astronomy Pictures of the Day.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.apod_directory_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">SAVE DIRECTORY</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.data_file_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>The location to save the apodwall.data file. It keeps track of APOD's downloaded and uses the file to complete operations such as removing cropped and temporary files and keep saved.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.data_file_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">DATA FILE PATH:</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.data_file_size_label.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Amount of saved apods to keep track of.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.data_file_size_label.setText(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p><span style=\" font-size:10pt;\">DATA FILE SIZE:</span></p></body></html>", None))
#if QT_CONFIG(tooltip)
        self.nasa_group.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>NASA API Key, register for one on <a href=\"https://api.nasa.gov\"><span style=\" text-decoration: underline; color:#0000ff;\">https://api.nasa.gov</span></a></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.nasa_group.setTitle(QCoreApplication.translate("apodwall_main_window", u"NASA API KEYS", None))
        self.apodwall_tab_menu.setTabText(self.apodwall_tab_menu.indexOf(self.settings_tab), QCoreApplication.translate("apodwall_main_window", u"SETTINGS", None))
        self.apodwall_group.setTitle(QCoreApplication.translate("apodwall_main_window", u"APODWall", None))
#if QT_CONFIG(tooltip)
        self.auto_run_checkbox.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Check box to auto-run apodwall on startup.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.auto_run_checkbox.setText(QCoreApplication.translate("apodwall_main_window", u"RUN ON START", None))
#if QT_CONFIG(tooltip)
        self.daily_apod_button.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Run APODWall</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.daily_apod_button.setText(QCoreApplication.translate("apodwall_main_window", u"GET DAILY APOD", None))
#if QT_CONFIG(tooltip)
        self.random_apod_button_2.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Run APODWall</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.random_apod_button_2.setText(QCoreApplication.translate("apodwall_main_window", u"BROWSE APOD HISTORY", None))
#if QT_CONFIG(tooltip)
        self.launch_apodhome_button.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Run APODWall</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.launch_apodhome_button.setText(QCoreApplication.translate("apodwall_main_window", u"LAUNCH APOD.NASA.GOV", None))
#if QT_CONFIG(tooltip)
        self.random_apod_button.setToolTip(QCoreApplication.translate("apodwall_main_window", u"<html><head/><body><p>Run APODWall</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.random_apod_button.setText(QCoreApplication.translate("apodwall_main_window", u"GET RANDOM APOD", None))
        self.set_wallpaper_checkBox.setText(QCoreApplication.translate("apodwall_main_window", u"SET AS WALLPAPER", None))
        self.menuMENU.setTitle(QCoreApplication.translate("apodwall_main_window", u"MENU", None))
    # retranslateUi

