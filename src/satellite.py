from numpy.random import random
import numpy as np
from datetime import datetime, timedelta
import pickle

times = {}
az = {}
alt = {}
for sat_height in (30, 60, 80):
    with open(f"satellite_{sat_height}.pickle", "rb") as f:
        times[sat_height], az[sat_height], alt[sat_height] = pickle.load(f)

class Satellite:
    _SPEEDUP = 20
    def __init__(self, height: int):
        az_shift = random() * 2 * np.pi
        self.start_time = datetime.now()
        self.times = times[height] / Satellite._SPEEDUP
        self.az = lambda t: az[height](t * Satellite._SPEEDUP) + az_shift
        self.alt = lambda t: alt[height](t * Satellite._SPEEDUP)
        self.end_time = self.start_time + timedelta(seconds=self.times[-1])
        self.packets_seen = np.zeros((480,))

    def position(self):
        """Get (alt, az) in degrees"""
        t = datetime.now()
        if t > self.end_time:
            return -0.5, np.rad2deg(self.az(1000))  # Slightly below the horizon so that still within reticle
        seconds_since_start = (t - self.start_time).total_seconds()
        return np.rad2deg(self.alt(seconds_since_start)[()]), np.rad2deg(self.az(seconds_since_start)[()])

    def set_seen(self):
        """Indicate that we saw it"""
        t = datetime.now().timestamp()
        # Start 'transmitting' 5 seconds after satellite rises
        t0 = (self.start_time + timedelta(seconds=5)).timestamp()
        if t < t0:
            return
        t1 = self.end_time.timestamp()
        seen_index = round(np.interp(t, [t0, t1], [0, 479]))
        self.packets_seen[seen_index] = 1
