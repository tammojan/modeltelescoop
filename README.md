# Project 'Modeltelescoop'
The software contained in this repository is being developed for use in the [Open Science Hub](http://www.opensciencedrenthe.nl/) in Dwingeloo, The Netherlands: a publicly accessible user information centre for the work of ASTRON (The Netherlands Institute of Radio Astronomy) and its partners. This specific application has been developed in collaboration with S[&]T in Delft, the Netherlands.

## Exhibit
The 'Modeltelescoop' exhibit is a scale model of the [Dwingeloo Radio Observatory](https://en.wikipedia.org/wiki/Dwingeloo_Radio_Observatory). It is able to be freely oriented in both azimuthal and altitudal axes by visitors at the centre. Its orientation is measured and transfered to a neartime visualisation machine in realtime. The viualisation consists of a reticle indicating the position at which the antenna is pointed in the local sky. Several interesting (radio-)astronomical objects are shown on the same screen; the visitor can find out more information by pointing the antenne towards these objects.

## Software Description
All software runs on two dedicated Raspberry Pis: one 'screen' unit and one 'antenna' unit. The former provides visualisation, while the latter is responsible for reading the values from two Hall sensors, which are converted to usable angles. The 'screen' unit also runs a simple socket server which listens for incoming JSON messages from the 'antenna' unit containing the latest altitude-azimuth readings.

## Running the Application
The following dependencies are required:
* Python 3
* pygame (which in turn required SDL)
* numpy
* astropy
* matplotlib
* scipy

A simple routine to gather these dependencies on a Debian or Ubuntu Linux installation is: 
```
sudo apt-get install python3 libsdl-dev python3-pygame python3-numpy python3-astropy python3-matplotlib python3-scipy
```
To start the application, first start the 'screen' unit: `python[3] ./src/screen_main.py`, followed by `python[3] ./src/antenna_main.py` on the 'antenna' unit.

![ASTRON][astronlogo]

![S&T][stlogo]

[astronlogo]: https://raw.githubusercontent.com/tammojan/modeltelescoop/master/src/resources/astronlogo.png
[stlogo]: https://raw.githubusercontent.com/tammojan/modeltelescoop/master/src/resources/stlogo.png
