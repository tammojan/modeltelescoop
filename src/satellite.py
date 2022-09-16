from numpy.random import random, choice
import numpy as np
from datetime import datetime, timedelta
import pickle
THRESHOLD_SATELLITE_DETECTED = 20.0

times = {}
az = {}
alt = {}
for sat_height in (30, 60, 80):
    with open(f"satellite_{sat_height}.pickle", "rb") as f:
        times[sat_height], az[sat_height], alt[sat_height] = pickle.load(f)

class Satellite:
    def __init__(self):
        height = choice([30, 30, 60, 60, 60, 60, 80, 80])

        az_shift = random() * 2 * np.pi
        direction = choice([-1, 1])
        self.start_time = datetime.now()
        speedup = times[height][-1] / 130  # Make sure a pass lasts 130 seconds
        self.times = times[height] / speedup
        self.az = lambda t: direction * (az[height](t * speedup) + az_shift)
        self.alt = lambda t: alt[height](t * speedup)
        self.end_time = self.start_time + timedelta(seconds=self.times[-1])
        self.packets_seen = np.zeros((480,))
        self.dist = 1000

    def position(self):
        """Get (alt, az) in degrees"""
        t = datetime.now()
        if t > self.end_time:
            return -0.5, np.rad2deg(self.az(1000))  # Slightly below the horizon so that still within reticle
        seconds_since_start = (t - self.start_time).total_seconds()
        return np.rad2deg(self.alt(seconds_since_start)[()]), np.rad2deg(self.az(seconds_since_start)[()])

    def seconds_up(self):
        """Returns the number of seconds that the satellite has been up"""
        return (datetime.now() - self.start_time).total_seconds()

    def set_dist(self, dist):
        """Indicate that we saw it, and at how many pixels distance"""
        self.dist = dist

        if self.dist < THRESHOLD_SATELLITE_DETECTED:
            t = datetime.now().timestamp()
            # Start 'transmitting' 5 seconds after satellite rises
            t0 = (self.start_time + timedelta(seconds=5)).timestamp()
            if t < t0:
                return
            t1 = self.end_time.timestamp()
            seen_index = int(round(np.interp(t, [t0, t1], [0, 479])))
            self.packets_seen[seen_index] = 1
