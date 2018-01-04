#!/usr/bin/python

import subprocess
import sys
import os
import time
import numpy as np
import imutils
from characters import *
from arena_resources import *

###################################################
#############      HELP SECTION      ##############
###################################################
# How To Run Program (CONSOLE): python main.py <sampling-time>
# @param <sampling-time>: optional parameter for wait-time each capture sample

###################################################
#############        GLOBALS         ##############
###################################################

draft_chars = 0
detected_obj = '[None]'
coords = np.array([None, None])

###################################################
#############       CHECK ROOT       ##############
###################################################
def check_root():
    setup = 'adb root; adb remount; adb wait-for-device'
    subprocess.call(setup, shell=True)


###################################################
#############     TRACKING TEMP      ##############
###################################################
'''
def logtemp(num_sec, filename):
    f = open(filename, 'w+')

    command_line1 = 'adb shell \'cat /sys/devices/virtual/thermal/thermal_zone9/temp\''
    command_line2 = 'adb shell \'cat /sys/devices/virtual/thermal/thermal_zone11/temp\''
    command_line3 = 'adb shell \'cat /sys/devices/virtual/thermal/thermal_zone22/temp\''

    start_time = time.time()
    interval = 1
    idx = 0
    while (True):
        #print str(datetime.now().strftime('%H:%M:%S')) + ',',
        out_back = subprocess.check_output(command_line1, shell=True).rstrip()
        out_sen0 = subprocess.check_output(command_line2, shell=True).rstrip()
        out_sen13 = subprocess.check_output(command_line3, shell=True).rstrip()
        print idx, out_back, out_sen0, out_sen13
        line = str(idx) + ' ' + str(out_back) + ' ' + str(out_sen0) + ' ' + str(out_sen13) + '\n'
        f.write(line)
        idx = idx + 1
        time.sleep(start_time + idx * interval - time.time())
        if idx * interval > num_sec:
            break
    f.close()
'''


###################################################
#############    DETECTED COORDS     ##############
###################################################
def getCoordinates(img_bgr, temp_bgr, threshold):
    counter = 0
    found = 0
    coords = np.array([])

    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    temp_gray = cv2.cvtColor(temp_bgr, cv2.COLOR_BGR2GRAY)

    height, width = temp_gray.shape[::-1]

    normxcorr = cv2.matchTemplate(img_gray, temp_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(normxcorr >= threshold)
    for p_loc in zip(*loc[::-1]):
        found = 1
        # cv2.rectangle(img_bgr, p_loc, (int(p_loc[0] + width), int(p_loc[1] + height)), (0, 0, 255), 5)
        # cv2.circle(img_bgr, (int(p_loc[0] + width / 2), int(p_loc[1] + height / 2)), 1, (0, 0, 255), 5)
        coords = np.append(coords, (int(p_loc[0] + width / 2), int(p_loc[1] + height / 2)))

        # coords = np.append(coords, (p_loc[0], p_loc[1]))
        # coords = np.vstack([coords, [p_loc[0] + width, p_loc[1]]])
        # coords = np.vstack([coords, [p_loc[0], p_loc[1] + height]])
        # coords = np.vstack([coords, [p_loc[0] + width, p_loc[1] + height]])
        break

    # for debugging purposes
    # cv2.circle(img_bgr, coords[0], 1, (0, 0, 255), 1)
    # cv2.circle(img_bgr, coords[1], 1, (0, 0, 255), 1)
    # cv2.circle(img_bgr, coords[2], 1, (0, 0, 255), 1)
    # cv2.circle(img_bgr, coords[3], 1, (0, 0, 255), 1)

    # cv2.namedWindow('detected', cv2.WINDOW_NORMAL)
    # cv2.imshow('detected', img_bgr)
    # print(coords)
    return coords, found


###################################################
#############      SELECT CHAR       ##############
###################################################
def select_char(chars_drafted, chars):
    global draft_chars
    global detected_obj
    global coords
    coords_char, found_char = getCoordinates(img_bgr, chars[chars_drafted][1], 0.99)
    if (found_char == 1):
        draft_chars += 1
        detected_obj = chars[chars_drafted][0]
        coords = coords_char
        subprocess.call('adb shell input tap %d %d' % (coords[0], coords[1]))
        #confirmation
        time.sleep(1)
        subprocess.call('adb shell screencap /sdcard/preview.png')
        subprocess.call('adb pull /sdcard/preview.png')
        temp_bgr = cv2.imread('preview.png')
        #cv2.imshow('temp_bgr', temp_bgr)
        time.sleep(1)
        coords_confirm, found_confirm = getCoordinates(temp_bgr, confirm_btn[1], 0.99)
        #print(coords_confirm)
        if (found_confirm == 1):
            subprocess.call('adb shell input tap %d %d' % (coords_confirm[0], coords_confirm[1]))
        else:
            print('Error: Failed to confirm selection.')
            exit()


###################################################
#############    DEBUGGING INFO      ##############
###################################################
def debugInfo(frames, obj, coordx, coordy):
    print('--------------------------------')
    print('Frame #: %d' % frames)
    print('Object Detected: %s' % obj)
    print('Detection Coords: %s, %s' % (coordx, coordy))
    print('--------------------------------')


###################################################
#############          MAIN          ##############
###################################################
if __name__ == '__main__':
    frames = 0
    if len(sys.argv) == 1:
        sample_time = 0
    elif len(sys.argv) == 2:
        sample_time = int(sys.argv[1])
    else:
        print ('Input Error: Run the program by calling "python arena_main.py <sampling-time>')
        exit()

    # subprocess.call('adb root; adb remount; adb wait-for-device', shell=True)

    # MAKE A UI FOR CHARACTERS (???)
    chars = [Dark_Kalias, Light_Lynn, Fire_Jose, Water_Arendel, Light_Jose]
    draft_stage = 0
    draft_chars = 0

    while (True):
        frames += 1
        found = 0
        detected_obj = '[None]'
        coords = np.array([None, None])

        subprocess.call('adb shell screencap /sdcard/preview.png')
        # time.sleep(1)
        subprocess.call('adb pull /sdcard/preview.png')
        img_bgr = cv2.imread('preview.png')

        # TEST
        '''
        test_temp = cv2.imread('temp.png')
        coords, found = getCoordinates(img_bgr, test_temp, 0.99)
        if found == 1:
            detected_obj = 'Google Play Button'
            subprocess.call('adb shell input tap %d %d' % (coords[0], coords[1]))
        else:
            coords = np.array([None, None])
        '''

        # TEST
        '''
        player_turn = cv2.imread('./resources/player_turn.png')
        coords, found = getCoordinates(img_bgr, player_turn, 0.99)
        if found == 1:
            Drafting
        else:
            coords = np.array([None, None])
        '''

        # First Drafts
        coords_b1, found_b1 = getCoordinates(img_bgr, blue_1st_draft[1], 0.99)
        coords_r1, found_r1 = getCoordinates(img_bgr, red_1st_draft[1], 0.99)

        if found_b1 == 1 and draft_stage == 0:
            draft_stage = 1
            draft_chars = 0
            coords = coords_b1
            detected_obj = blue_1st_draft[0]

        elif found_r1 == 1 and draft_stage == 0:
            draft_stage = 2
            draft_chars = 0
            coords = coords_r1
            detected_obj = red_1st_draft[0]

        # Second Drafts
        coords_b2, found_b2 = getCoordinates(img_bgr, blue_2nd_draft[1], 0.99)
        coords_r2, found_r2 = getCoordinates(img_bgr, red_2nd_draft[1], 0.99)
        
        if found_b2 == 1:
            draft_stage = 3
            coords = coords_b2
            detected_obj = blue_2nd_draft[0]

        elif found_r2 == 1:
            draft_stage = 4
            coords = coords_r2
            detected_obj = red_2nd_draft[0]

        # Check AUTO
        # tap auto
        subprocess.call('adb shell input tap 50 900')

        # Replay

        #Execution Phase
        # 1 ==> b1
        if (draft_stage == 1) and (draft_chars < 2):
            select_char(draft_chars, chars)

        # 2 ==> r1
        elif (draft_stage == 2) and (draft_chars < 3):
            select_char(draft_chars, chars)

        # 3 ==> b2
        elif (draft_stage == 3) and (draft_chars < 5):
            select_char(draft_chars, chars)

        # 4 ==> r2
        elif (draft_stage == 4) and (draft_chars < 5):
            select_char(draft_chars, chars)

        if (frames > 1):
            cv2.destroyAllWindows()

        debugInfo(frames, detected_obj, coords[0], coords[1])

        # DO THIS IF USING PORTRAIT MODE
        '''
        # Preview
        # cv2.namedWindow('img_bgr', cv2.WINDOW_NORMAL)
        # cv2.imshow('img_bgr', img_bgr)
        dst_bgr = imutils.rotate_bound(img_bgr, 90)
        # cv2.namedWindow('dst_bgr', cv2.WINDOW_NORMAL)
        # cv2.imshow('dst_bgr', dst_bgr)
        resized = cv2.resize(dst_bgr, (960, 540))
        '''

        # DO THIS IF USING LANDSCAPE MODE
        resized = cv2.resize(img_bgr, (960, 540))

        # cv2.namedWindow('resized', cv2.WINDOW_NORMAL)
        cv2.imshow('resized', resized)

        time.sleep(sample_time)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    os.remove('preview.png')
    subprocess.call('adb shell rm /sdcard/preview.png')
    exit()
