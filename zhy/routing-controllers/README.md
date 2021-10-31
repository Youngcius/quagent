# Optical_Switch_Controller
Software to control the optical switch using the PySerial python libraries along with a GUI constructed from PyQt5.

## Libraries
In order to run the 5x16 or 8x8 optical switch controller directly from the python file, you need to install the PyQt5 and PySerial libraries. Testing changes is most easily done in the python file directly. If there is any confusion on either of these libraries, there is useful online documentation for both.

Once testing is done, it is more user friendly to compile the code into a self contained application using PyInstaller. A tutorial is included in the directory as PyInstaller_tutorial.html. Open this file in your web browser of choice. If compiled properly, you should have a .exe application that can be run without having the proper python libraries installed. This makes it easier if the program ever needs to be shared between computers.

Install libraries using pip. If python is added to PATH, this can be run directly from the command line.

*pip install PyQt5*

*pip install PySerial*

*pip install PyInstaller*

## Drivers
In order to connect to the optical switch, drivers must be installed. These drivers, along with documentation are included in the driver folder in this repository. You should just need to run the application, PL2303-Prolific_DriverInstaller_v1200.exe to install the driver.

