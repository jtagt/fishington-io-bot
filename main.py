import cv2
from PIL import ImageGrab, Image
import numpy as np
from matplotlib import pyplot as plt, animation
import threading
import pydirectinput
import math
import time

bobber_low_h = 0
bobber_high_h = 180

bobber_low_s = 0
bobber_high_s = 9

bobber_low_v = 97
bobber_high_v = 255

red_bar_low_h = 103
red_bar_high_h = 115

red_bar_low_s = 193
red_bar_high_s = 194

red_bar_low_v = 176
red_bar_high_v = 255

green_bar_low_h = 37
green_bar_high_h = 104

green_bar_low_s = 211
green_bar_high_s = 255

green_bar_low_v = 172
green_bar_high_v = 236

close_x = 3233
close_y = 611
close_off_x = 40
close_off_y = 44

close_low_h = 0
close_high_h = 36

close_low_s = 0
close_high_s = 31

close_low_v = 36
close_high_v = 255

caught_x = 3030
caught_y = 405
caught_off_x = 21
caught_off_y = 43

caught_low_h = 80
caught_high_h = 123

caught_low_s = 222
caught_high_s = 255

caught_low_v = 180
caught_high_v = 255

x = 2769
y = 780
off_x = 534
off_y = 35

fishing_x = 2807
fishing_y = 815

shop_x = 3189
shop_y = 312

shop_select_all_x = 2614
shop_select_all_y = 314

shop_sell_x = 3032
shop_sell_y = 827

shop_sell_confirm_x = 3153
shop_sell_confirm_y = 711

off_window_x = 2789
off_window_y = 918

last_merge = np.zeros((off_y, off_x))
bobber_plain = np.zeros((off_y, off_x))
red_bar_plain = np.zeros((off_y, off_x))
green_bar_plain = np.zeros((off_y, off_x))
close_image_plain = np.zeros((close_off_y, close_off_x))
caught_image_plain = np.zeros((caught_off_y, caught_off_x))

max_fish = 12


def grab_image():
    image = ImageGrab.grab(bbox=(x, y, x + off_x, y + off_y))
    image = np.array(image)

    return image


def grab_close_image():
    image = ImageGrab.grab(bbox=(close_x, close_y, close_x + close_off_x, close_y + close_off_y))
    image = np.array(image)

    return image


def grab_catch_image():
    image = ImageGrab.grab(bbox=(caught_x, caught_y, caught_x + caught_off_x, caught_y + caught_off_y))
    image = np.array(image)

    return image


def grab_caught_mark_image(image):
    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    frame_threshold = cv2.inRange(frame_HSV, (caught_low_h, caught_low_s, caught_low_v),
                                  (caught_high_h, caught_high_s, caught_high_v))

    return frame_threshold


def grab_x_button_image(image):
    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    frame_threshold = cv2.inRange(frame_HSV, (close_low_h, close_low_s, close_low_v),
                                  (close_high_h, close_high_s, close_high_v))

    return frame_threshold


def grab_bobber_image(image):
    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    frame_threshold = cv2.inRange(frame_HSV, (bobber_low_h, bobber_low_s, bobber_low_v),
                                  (bobber_high_h, bobber_high_s, bobber_high_v))

    return frame_threshold


def grab_green_bar_image(image):
    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    frame_threshold = cv2.inRange(frame_HSV, (green_bar_low_h, green_bar_low_s, green_bar_low_v),
                                  (green_bar_high_h, green_bar_high_s, green_bar_high_v))

    return frame_threshold


def grab_red_bar_image(image):
    frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    frame_threshold = cv2.inRange(frame_HSV, (red_bar_low_h, red_bar_low_s, red_bar_low_v),
                                  (red_bar_high_h, red_bar_high_s, red_bar_high_v))

    return frame_threshold


def blend_images(bobber_img, green_bar_img, red_bar_img):
    first_blend = Image.blend(green_bar_img, red_bar_img, 0.5)
    second_blend = Image.blend(first_blend, bobber_img, 0.5)

    return second_blend


def calculate_mean_center(image):
    return np.mean(np.argwhere(image == 255), axis=0)


def convert_image(image_array):
    return Image.fromarray(np.uint8(image_array)).convert('RGBA')


def is_valid(image, count):
    if np.sum(image == 255) >= count:
        return True

    return False


def is_valid_below(image, count):
    if np.sum(image == 255) <= count:
        return True

    return False


def get_positions(bobber_image, green_bar_image, red_bar_image):
    bobber_center = calculate_mean_center(bobber_image)

    if is_valid(bobber_image, 25) and is_valid(green_bar_image, 100):
        green_bar_center = calculate_mean_center(green_bar_plain)

        if not np.isnan(green_bar_center[0]) and not np.isnan(green_bar_center[1]) and not np.isnan(
                bobber_center[0]) and not np.isnan(bobber_center[1]):
            return bobber_center, green_bar_center

        return None

    if is_valid(bobber_image, 25) and is_valid(red_bar_image, 100):
        red_bar_center = calculate_mean_center(red_bar_plain)

        if not np.isnan(red_bar_center[0]) and not np.isnan(red_bar_center[1]) and not np.isnan(
                bobber_center[0]) and not np.isnan(bobber_center[1]):
            return bobber_center, red_bar_center

        return None


class GameInterpreter(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.fishCount = 0

    def run(self):
        while True:
            global bobber_plain, green_bar_plain, red_bar_plain, last_merge, close_image_plain, caught_image_plain

            caught_image = grab_catch_image()
            caught_image_plain = grab_caught_mark_image(caught_image)

            if is_valid(caught_image_plain, 100) and is_valid_below(caught_image_plain, 350):
                print('Caught fish continuing to the awesome')
                pydirectinput.click(x=close_x + math.floor(close_off_x / 2), y=close_y + math.floor(close_off_y / 2))
                # use relative

            close_image = grab_close_image()
            close_image_plain = grab_x_button_image(close_image)

            if is_valid(close_image_plain, 25) and is_valid_below(close_image_plain, 500):
                print('Caught fish')
                self.fishCount += 1
                time.sleep(1)
                pydirectinput.doubleClick(x=close_x + math.floor(close_off_x / 2),
                                          y=close_y + math.floor(close_off_y / 2))

                print(f"Now at {self.fishCount}")

                if self.fishCount == max_fish:
                    print('Reached max fish going to sell')

                    pydirectinput.keyDown(key='w')
                    time.sleep(5)
                    pydirectinput.keyUp(key='w')

                    # at shop now

                    pydirectinput.click(x=shop_x, y=shop_y)  # click shop
                    time.sleep(0.25)

                    pydirectinput.click(x=shop_select_all_x, y=shop_select_all_y)  # click select all
                    time.sleep(0.25)

                    pydirectinput.click(x=shop_sell_x, y=shop_sell_y)  # click shop sell button
                    time.sleep(0.75)

                    pydirectinput.click(x=shop_sell_confirm_x, y=shop_sell_confirm_y)  # confirm sale
                    time.sleep(0.25)

                    pydirectinput.click(x=off_window_x, y=off_window_y)  # close shop window
                    time.sleep(0.75)

                    pydirectinput.keyDown(key='s')
                    time.sleep(1.5)
                    pydirectinput.keyUp(key='s')

                    self.fishCount = 0
                    print('Sold all fish now at 0 fish')

                    pydirectinput.mouseDown(x=fishing_x, y=fishing_y)
                    time.sleep(1)
                    pydirectinput.mouseUp()
                else:
                    time.sleep(1)

                    pydirectinput.mouseDown(x=fishing_x, y=fishing_y)
                    time.sleep(1)
                    pydirectinput.mouseUp()

            image = grab_image()
            bobber_plain = grab_bobber_image(image)
            green_bar_plain = grab_green_bar_image(image)
            red_bar_plain = grab_red_bar_image(image)

            positions = get_positions(bobber_plain, green_bar_plain, red_bar_plain)

            if positions:
                if positions[0][1] > positions[1][1]:
                    pydirectinput.mouseUp()

                    print(f"Releasing distance: {positions[0][1] - positions[1][1]}")
                else:
                    pydirectinput.mouseDown()

                    print(f"Pressing distance: {positions[1][1] - positions[0][1]}")

            bobber_converted = convert_image(bobber_plain)
            green_bar_converted = convert_image(green_bar_plain)
            red_bar_converted = convert_image(red_bar_plain)

            last_merge = np.array(blend_images(bobber_converted, green_bar_converted, red_bar_converted))

            if cv2.waitKey(1) & 0xFF == ord('q'):
                cv2.destroyAllWindows()
                break


class PlotVisual:
    def __init__(self):
        self.img = plt.imshow(last_merge)
        self.ani = animation.FuncAnimation(plt.gcf(), self.run, frames=off_y * off_y,
                                           interval=1)
        self.lastBobberDraw = None
        self.lastTargetDraw = None
        self.lastDifferenceDraw = None

    def draw_rois(self):
        if self.lastBobberDraw:
            self.lastBobberDraw.remove()
            self.lastBobberDraw = None

        if self.lastTargetDraw:
            self.lastTargetDraw.remove()
            self.lastTargetDraw = None

        if self.lastDifferenceDraw:
            self.lastDifferenceDraw.remove()
            self.lastDifferenceDraw = None

        positions = get_positions(bobber_plain, green_bar_plain, red_bar_plain)

        if positions:
            bobber = [[positions[0][1], positions[0][0]]]
            self.lastBobberDraw = plt.plot(*zip(*bobber), marker='o', color='g', ls='')[0]

            target = [[positions[1][1], positions[1][0]]]
            self.lastTargetDraw = plt.plot(*zip(*target), marker='|', color='r', ls='')[0]

            plot_line = [[positions[1][1], positions[1][0]], [positions[0][1], positions[0][0]]]
            self.lastDifferenceDraw = plt.plot(*zip(*plot_line), color='y')[0]

    def run(self, i):
        self.draw_rois()

        xi = i // off_y
        yi = i % off_x
        last_merge[xi, yi] = 1
        self.img.set_data(last_merge)


# start the visual
PlotVisual()

# start the interpreting
interpreter = GameInterpreter()
interpreter.start()

# show the visual
plt.show()
