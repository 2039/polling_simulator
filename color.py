import re
import colorsys

class Color:
    def __init__(self, hex):
        m = re.match(r"#([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})", hex)
        self.rgb = tuple(int(n, 16)/256 for n in m.groups())

    def darken(self, pct):
        hsv = list(colorsys.rgb_to_hsv(*self.rgb))
        hsv[2] = max(0, hsv[2] - pct/100)
        return colorsys.hsv_to_rgb(*hsv)

    def __str__(self):
        return str(self.rgb)
