#!/usr/bin/env python3
from errno import ENOANO
from os import getloadavg
import sys
import time
from turtle import color
import cv2
import numpy as np
import threading

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from datetime import datetime
from datetime import time as dtTime


WIDTH = 240
HEIGHT = 240
MARGIN_X = 5
MARGIN_Y = 1
ALARM_TIME = "07:00"


img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))

draw = ImageDraw.Draw(img)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
font_MainTime = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
iconFont = ImageFont.truetype("IconBitOne.ttf",30)

alarm_text_size_x, alarm_text_size_y = draw.textsize(ALARM_TIME, font)
icon_size_x, icon_size_y = draw.textsize("q ", font)
alarm_text_size_x, alarm_text_size_y = draw.textsize(ALARM_TIME, font)

time_now = datetime.now()

TEXT_COLOUR = (255,255,255)
HIGHLIGHT_COLOUR = (240,240,240)
HIGHLIGHT_TEXT_COLOUR = (0,0,0)
SUNRISE_COLOURS = [(45, 29, 122), (87, 49, 112),(128, 69, 101),(170, 88, 91),(211, 108, 80),(253, 128, 70),(253, 128, 70),(240, 185, 74),(158, 255, 242),(219, 255, 250)]
BG_COLOUR = (255, 0, 0) # SUNRISE_COLOURS[phase % len(SUNRISE_COLOURS)]
CURRENT_PAGE = "Main"
ENCODER_VALUE = 0
ENCODER_CLICK = False

## (<time>, <active>, <sunrise>)
ALARMS = [(dtTime(7,0,0),True),(dtTime(7,30,0),True),(dtTime(11,36,0),True)]


key_input = ''
phase = 0;

def drawText(x,y,text,font,colour,outlineColour,outlineSize,use_outline):
    if(use_outline):
        outline(x,y,text,font,outlineColour,outlineSize)
        
    draw.text((x,y), text, font=font, fill =colour)
    
    
def outline(x,y,text,font,colour,size):
    draw.text((x-size, y), text, font=font, fill=colour)
    draw.text((x+size, y), text, font=font, fill=colour)
    draw.text((x, y-size), text, font=font, fill=colour)
    draw.text((x, y+size), text, font=font, fill=colour)

canvas = Image.new("RGB",(WIDTH,HEIGHT),"black")


## (<text>. <destination page>,)
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


def drawPage_Main():# Reset background to blank colour
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)
    
    # Alarm time text
    
    drawText( MARGIN_X,MARGIN_Y, "q ", iconFont,TEXT_COLOUR,(0,0,0),1,True)
    drawText(MARGIN_X + icon_size_x, MARGIN_Y, ALARM_TIME, font, TEXT_COLOUR,(0,0,0),1,True)

    # Main time text
    time_now_text = '{0:%H:%M}'.format(time_now)
    time_now_text_size_x, time_now_text_size_y = draw.textsize(time_now_text, font_MainTime)
    main_time_x = (WIDTH - time_now_text_size_x) / 2
    main_time_y = (HEIGHT - time_now_text_size_y) / 2
    drawText(main_time_x,main_time_y, time_now_text, font_MainTime, TEXT_COLOUR, (0,0,0),3,True)
    
    return


def drawPage_Menu():
    global ENCODER_VALUE
    global ENCODER_CLICK
    global CURRENT_PAGE
    
    menu_items = [("Back","Main",0),("Alarms","Alarms",0),("Mode","Mode",0),("Settings","Settings",0)]
    
    ##wipe screen
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)
    
    ## draw menu
    menu_item_height = 60 #HEIGHT / len(menu_items)
    menu_item_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(30))
    use_outline = True
    
    for i,menu_item in enumerate(menu_items):
        colour = TEXT_COLOUR
        if(i == ENCODER_VALUE % len(menu_items)):    
            
            if(ENCODER_CLICK):
                print("Setting page to" + menu_item[1])
                CURRENT_PAGE = menu_item[1]
                return
                
            draw.rectangle((0, i * menu_item_height, WIDTH, i * menu_item_height + menu_item_height), (HIGHLIGHT_COLOUR))
            colour = HIGHLIGHT_TEXT_COLOUR
            use_outline = False
            
        text = menu_item[0]
        text_size_x, text_size_y = draw.textsize(text, menu_item_font)
        drawText(MARGIN_X,  MARGIN_Y + i * menu_item_height, text, menu_item_font, colour,(0,0,0),1,use_outline)
        
    return

def drawPage_Alarms():
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG_COLOUR)
    
    alarm_item_height = 60
    alarm_item_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", int(30))
    for i,alarm in enumerate(ALARMS):
        colour = TEXT_COLOUR
        if(i == ENCODER_VALUE % len(ALARMS)):  
            if(ENCODER_CLICK):
                print("Enabling alarm to",i)
                alarm[1] = not(alarm[1])
                return
                
            draw.rectangle((0, i * alarm_item_height, WIDTH, i * alarm_item_height + alarm_item_height), (HIGHLIGHT_COLOUR))
            colour = HIGHLIGHT_TEXT_COLOUR
            use_outline = False
            
    text = '{0:%H:%M}'.format(alarm[0])
    text_size_x, text_size_y = draw.textsize(text, alarm_item_font)
    drawText(MARGIN_X,  MARGIN_Y + i * alarm_item_height, text, alarm_item_font, colour,(0,0,0),1,use_outline)
 
    
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


PAGES = [("Main", drawPage_Main),("Menu", drawPage_Menu), ("Alarms", drawPage_Alarms),("Mode",drawPage_Mode),("Setings",drawPage_Settings)]

initialised_kbdListener = False

while True:
    
    time_now = datetime.now()
    
    old_encoder_val = ENCODER_VALUE
    
    if(key_input == 'd'):
        encoder_step_forward()
    elif(key_input == 'a'):
        encoder_step_backward()
    elif(key_input=='s'):
        encoder_click()
    
    key_input = ''
 
    new_encoder_val = ENCODER_VALUE
        
    
    cv2.imshow("light", np.array(img))
    cv2.waitKey(10)
    
    ## Page system state machine
    if(CURRENT_PAGE == "Main"):
        ## On any input on main page, go to menu
        if(old_encoder_val != new_encoder_val):
            CURRENT_PAGE = "Menu"
            ENCODER_VALUE = 0

                    
    ## Draw whatever out current page is
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
    
    time.sleep(0.1)
    
