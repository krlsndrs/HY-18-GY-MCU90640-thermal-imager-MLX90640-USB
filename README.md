# HY-18-GY-MCU90640-thermal-imager-MLX90640-USB

Script for reading the output of Thermal Imager like HY-18 (GY-MCU90640) on a computer with USB and Python 3.6, using another camera supported by Python.

This work is based on script of vvkuryshev (https://github.com/vvkuryshev/GY-MCU90640-RPI-Python/) and some code from https://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/  for a Thermal Imager based on MLX90640  who contains a microcontroller STM32F103, like this : https://es.aliexpress.com/item/33038772404.html?spm=a2g0o.store_home.productList_328396795.subject_0&spm=a2g0o.store_home.singleImageText_669346773.0

The Thermal Imager only needs to connect directly to USB, and a webcam recognized by Python 3.6. This script imports libraries like OpenCV for image transformations. This Thermal Imager connects to USB acting as a serial controller (CH341 UART) sending serial data from MLX90640 (but not receiving, so it's impossible to send commands to the module) at 115200 bauds.

![Conection of module](https://github.com/krlsndrs/HY-18-GY-MCU90640-thermal-imager-MLX90640-USB/blob/master/CapturaImagen.jpeg?raw=true "Captura de la conexión")

I apologize for the quality of the script, this is my very first attempt to program in Python.

![Example of capture](https://github.com/krlsndrs/HY-18-GY-MCU90640-thermal-imager-MLX90640-USB/blob/master/pic_2020-03-02_19-37-11.jpg?raw=true "Captura de la conexión")

USAGE:

There are few keys commands:

- pressing "s": Save the picture naming according to date and time
- pressing "f": Toggle Show Webcam image
- pressing "r": Toggle auto temperature range
- pressing "g": Toggle gaussian blurring
- pressing "e": Mirror mode
- pressing "p": Changes color mapping (dependind of the version of OpenCV, could be 21 differents mappings)
- pressing "i": Changes the interpolation mode (from 0 to 5)

For perspective transforming of the webcam's picture, there are keys for adjusting in real time the image (uses the four_point_transform script by Adrian Rosebrock):

- keys 1,2 and 3,4  are the coordinates (x,y) of the first point (1 increment x value and 2 decrements it; 3 increments the y value, 4 decrements it... and so on).
- keys 7,8 and 9,0 are the coordinates of the second point.
- keys z,x and c,v are the coordinates of the third point.
- keys v,b and n,m are the coordinates of the last point.

Feel free to modify it. Is a work in progress...

