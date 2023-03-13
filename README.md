# fetchAPOD
fetchAPOD is a low dependancy, multi-platform application for downloading the Astronomy Picture of the Day, and setting it as desktop wallpaper. The application comes as a CLI script or a QT6 application.

An installer.exe for windows can be found on my dropbox.

```https://www.dropbox.com/s/ayw2e05q6xc1roy/fetchAPOD-installer.exe?dl=0```


## Gui Screenshots
![light-theme splash](https://github.com/jameseh/fetchAPOD/blob/development/Screenshots/Screenshot%202023-03-13%20061431.png)

![dark-theme splash](https://github.com/jameseh/fetchAPOD/blob/development/Screenshots/Screenshot%202023-03-13%20061455.png)

![dark-theme gallery](https://github.com/jameseh/fetchAPOD/blob/development/Screenshots/Screenshot%202023-03-13%20061518.png)

![dark-theme settings](https://github.com/jameseh/fetchAPOD/blob/development/Screenshots/Screenshot%202023-03-13%20061603.png)


#### **Some of the customability options:**
+ image quality
+ crop ratio (crop image to resolution before setting as wallpaper)
+ minimum starting size of image to set as a wallpaper
+ where and how much of everything to save/keep logged.
+ run on time interval


*fetchAPOD is a WIP personal project using MIT license. I do my best will keep the functuality working on the master branch and excutables. The programs design and functionality may change durastically over time.*

## **CLI Installation:**
+ Copy fetchAPOD.py, config.toml, and config.py to the directory you want. 
+ Edit the config.toml file to your needs.
+ Run the fetchAPOD.py

 alternativly you can clone this repo:
 
 ```git clone https://github.com/iijameseh/fetchAPOD```

## **Dependancies**
+ python 3.11 +:
+ requests
+ pillow

## **Gui Specific Dependancies**
+ PyQt6
+ PySide6
+ pyqtdarktheme



## Some Love

+ Thank you to all the kind people on stackoverflow taking the time to answer people's questions. 

+ Elinvention@github, the histroy gallery idea was taken directly form the gnome apod extension. 

```https://github.com/Elinvention/gnome-shell-extension-nasa-apod```

+ Thank you to the contributors of pyqtdarktheme, the light and dark theme used in fetchAPOD's gui.

```https://github.com/5yutan5/PyQtDarkTheme```

+ Google, Google material icons

```https://fonts.google.com/icons```

+ QT6

```https://www.qt.io/product/qt6```

+ pillow for image processing

```https://python-pillow.org/```

+ requests for handing web requests.

```https://requests.readthedocs.io/```

+ and thank you python.

```https://python.org```
