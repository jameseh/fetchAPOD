# fetchAPOD
fetchAPOD is a low dependancy, multi-platform application for downloading the Astronomy Picture of the Day, and setting it as desktop wallpaper. The application comes as a CLI script or a QT6 application.

An installer.exe for windows can be found on my dropbox.

```https://www.dropbox.com/s/ayw2e05q6xc1roy/fetchAPOD-installer.exe?dl=0```


## Gui Screenshots
![light-theme splash]([https://www.dropbox.com/h?preview=Screenshot+2023-03-13+061431.png](https://github.com/jameseh/fetchAPOD/blob/development/Screenshots/Screenshot%202023-03-13%20061431.png))
![dark-theme splash](https://www.dropbox.com/h?preview=Screenshot+2023-03-13+061455.png)
![dark-theme gallery](https://www.dropbox.com/h?preview=Screenshot+2023-03-13+061518.png)
![dark-theme settings](https://www.dropbox.com/h?preview=Screenshot+2023-03-13+061603.png)


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
 
 ```git clone https://github.com/YOUR-USERNAME/YOUR-REPOSITORY```

## **Dependancies**
+ python 3.11 +:
+ requests
+ pillow

## **Gui Specific Dependancies**
+ PyQt6
+ PySide6
+ pyqtdarktheme
