# -*- coding: utf-8 -*-

from datetime import datetime

from core.airplayscr import window_capture
import os
from PIL import Image
from PIL import ImageFilter
from shutil import copyfile

def analyze_current_screen_text_ios(crop_area, directory=".", compress_level=1):
    print("截屏时间: ", datetime.now().strftime("%H:%M:%S"))
    screenshot_filename = "screenshot.png"
    save_text_area = os.path.join(directory, "text_area.png")
    capture_screen_ios(screenshot_filename, directory)
    parse_answer_area_ios(os.path.join(directory, screenshot_filename), save_text_area, compress_level, crop_area)
    return get_area_data_ios(save_text_area)

def analyze_stored_screen_text_ios(screenshot_filename="screenshot.png", directory=".", compress_level=1):
    save_text_area = os.path.join(directory, "text_area.png")
    parse_answer_area_ios(os.path.join(directory, screenshot_filename), save_text_area, compress_level)
    return get_area_data_ios(save_text_area)

def capture_screen_ios(filename="screenshot.png", directory="."):
    window_capture(os.path.join(directory, filename))

def save_screen_ios(filename="screenshot.png", directory="."):
    copyfile(os.path.join(directory, filename),
             os.path.join(directory, datetime.now().strftime("%m%d_%H%M%S").join(os.path.splitext(filename))))

def parse_answer_area_ios(source_file, text_area_file, compress_level, crop_area):
    image = Image.open(source_file)
    if compress_level == 1:
        image = image.convert("L")
    elif compress_level == 2:
        image = image.convert("1")
    width, height = image.size[0], image.size[1]
    #print("屏幕宽度: {0}, 屏幕高度: {1}".format(width, height))
    region = image.crop((width * crop_area[0], height * crop_area[1], width * crop_area[2], height * crop_area[3]))
    region = region.filter(ImageFilter.EDGE_ENHANCE)
    region.save(text_area_file)


def get_area_data_ios(text_area_file):
    with open(text_area_file, "rb") as fp:
        image_data = fp.read()
        return image_data
    return ""
