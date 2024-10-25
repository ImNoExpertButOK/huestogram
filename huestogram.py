from colorthief import ColorThief
from pathlib import Path
from colorsys import hsv_to_rgb, rgb_to_hsv
import altair as alt
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--bins", help="Number of subdivisions (bins) on the HSL scale. Default is 36.", type=int, default=36)
parser.add_argument("-p", "--path", help="Path to a directory containing images to be analyzed.")
parser.add_argument("-c", "--colors", help="How many dominant colors to extract for each image file. Default is 4.", default=4)
args = parser.parse_args()

path = args.path
palette_size = args.colors
bins = args.bins
hues = []

def generate_histogram(list_of_hues, bins):
    '''
    Takes in a list of hues and a number of desired bins 
    and returns a dictionary in the format:

    {"hue":[maximum_value1, maximum_value2, maximum_value3, etc], 
    "count":[count1, count2, count3 etc]}

    Both lists should contain the same number of elements.
    '''
    result = {"hue":[], "count":[]}
    bin_size = int(360/bins)

    for i in range(bins + 1):
        count = 0
        min = bin_size * (i - 1)
        max = bin_size * i

        # Note: Since I'm using i - 1 to get the previous value it 
        # creates negative values on the first iteration of the loop. 
        # Only proceed if it's equal or larger than zero.
        if min >= 0:
            for hue in sorted(list_of_hues):
                if hue >= min and hue < max:
                    count += 1

            result["hue"].append(max)
            result["count"].append(count)

    return result

for file in Path(path).glob("*"):
    if file.suffix == ".png" or file.suffix == ".jpg":
        color_thief = ColorThief(file)
        palette = color_thief.get_palette(color_count=palette_size, quality=5)

        # Note: ColorThief library does weird things when you specify palette sizes
        # smaller than 4. A palette size of 3 will generate 4 colors, a palette
        # size of 2 will generate 3 colors, and a palette size of 1 will not work.
        for color in palette:
            hues.append(round(rgb_to_hsv(*color)[0] * 360))

        # Uncomment this to work with just one dominant color per image
        # hues.append(rgb_to_hsv(*color_thief.get_color())[0] * 360)

huestogram = generate_histogram(hues, bins)
data = pd.DataFrame.from_dict(huestogram, orient="columns")

alt.Chart(data).mark_bar().encode(
    alt.X("hue:Q").scale(domain=[0, 360]),
    alt.Y("count:Q"),
    alt.Color("hue:Q").scale(scheme="sinebow")
).save("chart.svg")
