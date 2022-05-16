#!/usr/bin/env python3
import ST7789
from datetime import time as dtTime
from datetime import datetime
from PIL import ImageFont
from PIL import ImageDraw
from PIL import Image
import sys
import time
import numpy as np
import threading
import RPi.GPIO as GPIO

BL_PIN = 19
# GPIO.setwarnings(False)			#disable warnings
# GPIO.setmode(GPIO.BOARD)		#set pin numbering system
# GPIO.setup(BL_PIN,GPIO.OUT)


# Create ST7789 LCD display class.
disp = ST7789.ST7789(
    height=240,
    rotation=90,
    port=0,
    cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
    dc=9,
    backlight=19,               # 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=80 * 1000 * 1000,
    offset_left=0,
    offset_top=0
)

# Initialize display.
disp.begin()

WIDTH = 240
HEIGHT = 240
MARGIN_X = 5
MARGIN_Y = 1
ALARM_TIME = "07:00"


img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
font_MainTime = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
iconFont = ImageFont.truetype("IconBitOne.ttf", 30)

alarm_text_size_x, alarm_text_size_y = draw.textsize(ALARM_TIME, font)
icon_size_x, icon_size_y = draw.textsize("q ", font)
alarm_text_size_x, alarm_text_size_y = draw.textsize(ALARM_TIME, font)

time_now = datetime.now()

TEXT_COLOUR = (130, 130, 130)
HIGHLIGHT_COLOUR = (130, 130, 130)
HIGHLIGHT_TEXT_COLOUR = (0, 0, 0)
SUNRISE_COLOURS = [(45, 29, 122), (87, 49, 112), (128, 69, 101), (170, 88, 91), (211, 108, 80),
                   (253, 128, 70), (253, 128, 70), (240, 185, 74), (158, 255, 242), (219, 255, 250)]
BG_COLOUR = (0, 0, 0)  # SUNRISE_COLOURS[phase % len(SUNRISE_COLOURS)]
CURRENT_PAGE = "Main"
ENCODER_VALUE = 0
ENCODER_CLICK = False

ALARM_PAGE = 0

# (<time>, <active>, <sunrise>)
ALARMS = [["Back"], [dtTime(3, 36, 0), True],
          [dtTime(1, 0, 0), True], [dtTime(2, 30, 0), False], [
    dtTime(3, 36, 0), True],
    [dtTime(4, 0, 0), True], [dtTime(5, 30, 0), False], [
        dtTime(6, 36, 0), True],
    [dtTime(7, 0, 0), True], [dtTime(8, 30, 0), False], [
        dtTime(9, 36, 0), True],
    [dtTime(10, 0, 0), True], [dtTime(11, 30, 0), False], [
        dtTime(12, 36, 0), True], ["New Alarm"]]


key_input = ''
phase = 0

img = Image.new("RGB", (WIDTH, HEIGHT), "black")
draw = ImageDraw.Draw(img)


def drawText(x, y, text, font, colour, outlineColour, outlineSize, use_outline):
    if(use_outline):
        outline(x, y, text, font, outlineColour, outlineSize)
    draw.text((x, y), text, font=font, fill=colour)


def outline(x, y, text, font, colour, size):
    draw.text((x-size, y), text, font=font, fill=colour)
    draw.text((x+size, y), text, font=font, fill=colour)
    draw.text((x, y-size), text, font=font, fill=colour)
    draw.text((x, y+size), text, font=font, fill=colour)


def setPage(page):
    global CURRENT_PAGE
    global ENCODER_VALUE
    CURRENT_PAGE = page
    ENCODER_VALUE = 0


def encoder_step_forward():
    global ENCODER_VALUE
    ENCODER_VALUE += 1


def encoder_step_backward():
    global ENCODER_VALUE
    ENCODER_VALUE -= 1


def encoder_click():
    global ENCODER_CLICK
    ENCODER_CLICK = True
    return


def getTimeFromNow(now, time):
    hour_diff = (24 - now.hour + time.hour - 1) if (now.hour >
                                                    time.hour) else (time.hour - now.hour - 1)
    minute_diff = (60 - now.minute +
                   time.minute) if (now.minute > time.minute) else (time.minute - now.minute)
    return (hour_diff, minute_diff)


def getNextAlarmText():
    alarm_times = [row[0]
                   for row in ALARMS[1:-1] if row[1]]  # get enabled alarm list
    sorted_by_time_distance = sorted(
        alarm_times, key=lambda z: getTimeFromNow(time_now, z))

    return '{0:%H:%M}'.format(sorted_by_time_distance[0])


def drawPage_Main():  # Reset background to blank colour
    next_alarm_text = getNextAlarmText()

    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)

    # Alarm time text
    drawText(MARGIN_X, MARGIN_Y, "q ", iconFont,
             TEXT_COLOUR, (0, 0, 0), 1, True)
    drawText(MARGIN_X + icon_size_x, MARGIN_Y, next_alarm_text,
             font, TEXT_COLOUR, (0, 0, 0), 1, True)

    # Main time text
    time_now_text = '{0:%H:%M}'.format(time_now)
    time_now_text_size_x, time_now_text_size_y = draw.textsize(
        time_now_text, font_MainTime)
    main_time_x = (WIDTH - time_now_text_size_x) / 2
    main_time_y = (HEIGHT - time_now_text_size_y) / 2
    drawText(main_time_x, main_time_y, time_now_text,
             font_MainTime, TEXT_COLOUR, (0, 0, 0), 3, True)

    return


def drawPage_Menu():
    global ENCODER_VALUE
    global ENCODER_CLICK
    global CURRENT_PAGE

    menu_items = [("Back", "Main", 0), ("Alarms", "Alarms", 0),
                  ("Mode", "Mode", 0), ("Settings", "Settings", 0)]

    # wipe screen
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)

    # draw menu
    menu_item_height = 60  # HEIGHT / len(menu_items)
    menu_item_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(30))
    use_outline = True

    for i, menu_item in enumerate(menu_items):

        colour = TEXT_COLOUR
        if(i == ENCODER_VALUE % len(menu_items)):
            if(ENCODER_CLICK):
                print("Setting page to" + menu_item[1])
                setPage(menu_item[1])
                return

            draw.rectangle((0, i * menu_item_height, WIDTH, i *
                           menu_item_height + menu_item_height), (HIGHLIGHT_COLOUR))
            colour = HIGHLIGHT_TEXT_COLOUR
            use_outline = False

        text = menu_item[0]
        text_size_x, text_size_y = draw.textsize(text, menu_item_font)
        drawText(MARGIN_X,  MARGIN_Y + i * menu_item_height, text,
                 menu_item_font, colour, (0, 0, 0), 1, use_outline)

    return


def getAlarmText(index):
    global ALARMS
    idx = index % len(ALARMS)

    if(idx != 0 and idx != len(ALARMS) - 1):
        return '{0:%H:%M}'.format(ALARMS[idx][0])
    else:
        return ALARMS[idx % len(ALARMS)][0]


def drawPage_Alarms():
    global CURRENT_PAGE
    global ENCODER_VALUE

    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)

    alarm_item_height = 60
    max_options_on_screen = 4
    pages = int(len(ALARMS) / max_options_on_screen)

    use_outline = True
    alarm_item_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(30))

    for i, alarm in enumerate(ALARMS):

        # Handle menu selection and clicking
        colour = TEXT_COLOUR
        if(i == ENCODER_VALUE % len(ALARMS)):

            if(ENCODER_CLICK):
                if(i == 0):
                    CURRENT_PAGE = "Main"
                    return
                elif(i == len(ALARMS) - 1):
                    CURRENT_PAGE = "NewAlarm"
                    return
                else:
                    alarm[1] = False if alarm[1] else True  # negate it

            draw.rectangle((0,  (HEIGHT - alarm_item_height) / 2, WIDTH,
                           (HEIGHT + alarm_item_height) / 2), (HIGHLIGHT_COLOUR))

            text = alarm[0]
            if(i != 0 and i != len(ALARMS) - 1):
                text = '{0:%H:%M}'.format(alarm[0])

                icon_text = "5" if alarm[1] else "4"
                alarm_iconFont = ImageFont.truetype("IconBitOne.ttf", 30)
                icon_size_x, icon_size_y = draw.textsize(
                    icon_text, alarm_item_font)
                drawText(WIDTH - MARGIN_Y - 2 * icon_size_x, (HEIGHT - icon_size_y) / 2,
                         icon_text, alarm_iconFont, HIGHLIGHT_TEXT_COLOUR, (0, 0, 0), 1, True)

            text_size_x, text_size_y = draw.textsize(text, alarm_item_font)
            drawText((WIDTH - text_size_x) / 2,  (HEIGHT - text_size_y) / 2, text, alarm_item_font,
                     HIGHLIGHT_TEXT_COLOUR, (0, 0, 0), 1, True)

            # Draw next and previous
            next_text = getAlarmText(i + 1)
            prev_text = getAlarmText(i - 1)

            alarm_alt_item_font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(24))

            # prev item text
            alt_text_size_x, alt_text_size_y = draw.textsize(
                prev_text, alarm_alt_item_font)
            drawText((WIDTH - alt_text_size_x) / 2,  (HEIGHT - 2.5 * alarm_item_height) / 2, prev_text,
                     alarm_alt_item_font, HIGHLIGHT_TEXT_COLOUR, TEXT_COLOUR, 1, True)

            # next item text
            alt_text_size_x, alt_text_size_y = draw.textsize(
                next_text, alarm_alt_item_font)
            drawText((WIDTH - alt_text_size_x) / 2,  (HEIGHT + 1.5 * alarm_item_height) / 2, next_text,
                     alarm_alt_item_font, HIGHLIGHT_TEXT_COLOUR, TEXT_COLOUR, 1, True)

    return


def drawPage_Mode():
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)
    return


def drawPage_Settings():
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)
    return


def kbdListener():
    global key_input
    while 1:
        key_input = input()


PAGES = [("Main", drawPage_Main), ("Menu", drawPage_Menu), ("Alarms",
                                                            drawPage_Alarms), ("Mode", drawPage_Mode), ("Setings", drawPage_Settings)]

initialised_kbdListener = False

while True:

    time_now = datetime.now()

    old_encoder_val = ENCODER_VALUE

    if(key_input == 'd'):
        encoder_step_forward()
    elif(key_input == 'a'):
        encoder_step_backward()
    elif(key_input == 's'):
        encoder_click()
    key_input = ''

    new_encoder_val = ENCODER_VALUE

    # Page system state machine
    if(CURRENT_PAGE == "Main"):
        # On any input on main page, go to menu
        if(old_encoder_val != new_encoder_val):
            setPage("Menu")

    # Draw whatever out current page is
    for page in PAGES:
        if(CURRENT_PAGE == page[0]):
            # print("DRAWING PAGE: " + page[0])
            page[1]()
            break

    if(ENCODER_CLICK):
        ENCODER_CLICK = False

    if(initialised_kbdListener == False):
        initialised_kbdListener = True
        listener = threading.Thread(target=kbdListener)
        listener.start()

    disp.display(img)

    time.sleep(0.05)
