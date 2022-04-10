# -*- coding: utf-8 -*-
"""
Created on Tue May 21 14:14:28 2019

@author: S.P. van der Linden
"""

#from astropy.io import fits
import astropy.units as u
#from astropy.coordinates import EarthLocation, AltAz, Galactic, get_body, SkyCoord
#from astropy.time import Time
from util import altaz_to_unit, unit_to_skyxy, skyxy_to_unit, unit_to_altaz
import re
import numpy as np

#DWINGELOO_LOCATION = EarthLocation(lat="52d48m43.27", lon="6d23m46.21")


def get_body_skyxy(body: str):
    """
    Get xy coordinates for a sky body

    body can be:
       radec(0.4,0.5): ra and dec in radians
       altaz(0.4,0.5): alt and azimuth in radians
       name: something that is accepted by get_body (e.g. 'sun', 'moon', 'jupiter')
    """
    if "radec" in body:
        time = Time.now()
        ra, dec = re.split('[(,)]', body)[1:3]
        skycoord = SkyCoord(ra=float(ra)*u.rad, dec=float(dec)*u.rad)
        coords = skycoord.transform_to(AltAz(obstime=Time.now(), location=DWINGELOO_LOCATION))
        alt, az = coords.alt.degree, coords.az.degree
    elif "altaz" in body:
        alt, az = re.split('[(,)]', body)[1:3]
        alt = float(alt)
        az = float(az)
    else:
        time = Time.now()
        skycoord = get_body(body, time)
        coords = skycoord.transform_to(AltAz(obstime=Time.now(), location=DWINGELOO_LOCATION))
        alt, az = coords.alt.degree, coords.az.degree

    coords_unit = altaz_to_unit(alt, az)
    #coords_unit = altaz_to_unit(60.0, 180)
    
    
    coords_skyxy = unit_to_skyxy(coords_unit[0], coords_unit[1])
    #print('Sun Alt: {:.1f}; Az: {:.1f}'.format(coords.alt.degree, coords.az.degree))
    return (round(coords_skyxy[0]), round(coords_skyxy[1]))
    

def get_dist_milkyway(x: float, y: float):
    unit_x, unit_y = skyxy_to_unit(x, y)
    alt, az = unit_to_altaz(unit_x, unit_y)
    if (0 <= az <= 54 and alt < 44) or \
       (290 <= az <= 360 and alt < 50) or \
       (268 <= az <= 290 and alt < 42) or \
       (245 <= az <= 268 and alt < 34):
        return 3
    else:
        return 100

class RadioDataSet:
    
    def __init__(self):
        #fitsdata = fits.open("D:/Projects/sciencehub/trunk/resources/labh.fit")[0]
        #self.v0 = fitsdata.header.cards['CRVAL3'][1]*u.m/u.s
        #self.vincr = fitsdata.header.cards['CDELT3'][1]*u.m/u.s
        #self.data = fitsdata.data
        pass

    def frame_to_v(self, frame_nr):
        return self.v0 + frame_nr*self.vincr
    
    def v_to_frame(self, v):
        return round(((v*u.m/u.s - self.v0)/self.vincr).value)

    def lb_to_xy(self, l, b):
        """Convert galactic longitude, latitude to pixel coordinates
        
        Args:
            (l, b) (Tuple[int, int]): latitude and longitude in degrees
            
        Returns:
            Tuple[int, int]: x and y coordinates, x from 0 to 720, y from 0 to 360
        """
        return (2*((180-l)%360), 2*(b+90))


    def skycoord_to_xy(self, coord):
        """Convert a skycoord to x and y pixel coordinates"""
        l = round(coord.l.to(u.deg).value)
        b = round(coord.b.to(u.deg).value)
        return self.lb_to_xy(l, b)


    def get_line_data(self, skycoord, offset=(0,0)):
        x, y = self.skycoord_to_xy(skycoord)
        return self.data[:, y+offset[0], x+offset[1]]


    def altaz_to_skycoord(self, alt: float, az: float):
        """Get a SkyCoord object in Galactic coordinates based on the a AltAz"""
        # Define a reference point from the Dwingeloo location with the current
        # time.
        p_alt = alt * u.deg
        p_az = az * u.deg
        pointing_galactic = AltAz(obstime=Time.now(), location=DWINGELOO_LOCATION,
                      alt=p_alt, az=p_az).transform_to(Galactic)
        return pointing_galactic
    

        
        
    
