from urllib.request import urlopen

from colorthief import ColorThief as ColourThief
from colorthief import MMCQ
from discord import Colour


def get_embed_colour(url):
    colour_thief = SaturatedColourThief(
        urlopen(url)
    )
    return colour_thief.get_color(1)


class SaturatedColourThief(ColourThief):
    def get_palette(self, color_count=10, quality=10):
        image = self.image.convert('RGBA')
        pixels = image.getdata()
        pixel_count = image.size[0] * image.size[1]
        valid_pixels = []
        for i in range(0, pixel_count, quality):
            # red, green, blue, alpha = pixels[i]

            if pixels[i][3] < 125:  # Skip pixels with high alpha
                continue
            max_rgb = max(pixels[i][:3]) / 255.0
            min_rgb = min(pixels[i][:3]) / 255.0
            lightness = 0.5 * (max_rgb + min_rgb)
            if lightness <= 0.1 or lightness > 0.9:
                continue  # Skip very dark/light pixels
            if lightness <= 0.5:
                saturation = (max_rgb - min_rgb) / (2 * lightness)
            else:
                saturation = (max_rgb - min_rgb) / (2 - 2 * lightness)
            if saturation > 0.5:  # Skip 'greyscale' pixels
                valid_pixels.append(pixels[i][:3])

        if not valid_pixels:  # Fall back to original method.
            palette = super(SaturatedColourThief, self).get_palette(
                color_count, quality
            )
            return palette

        # Send array to quantize function which clusters values
        # using median cut algorithm
        cmap = MMCQ.quantize(valid_pixels, color_count)
        return cmap.palette

    def get_color(self, quality):
        colour = super(SaturatedColourThief, self).get_color(quality)
        return Colour((colour[0] << 16) + (colour[1] << 8) + colour[2])
