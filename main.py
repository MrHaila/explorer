import time
import math
import _thread

from picographics import PicoGraphics, DISPLAY_PICO_EXPLORER # type: ignore

display = PicoGraphics(display=DISPLAY_PICO_EXPLORER)

current_hue = 0
def get_pen(index, hue_offset=0, saturation=0.48):
    # Clamp the index to the range 0-11.
    index = max(0, min(index, 11))
    lightness_lookup = [0.4, 0.13, 0.21, 0.29, 0.38, 0.46, 0.54, 0.62, 0.71, 0.79, 0.87, 0.98]
    return display.create_pen_hsv(current_hue + hue_offset, saturation, lightness_lookup[index])


display.set_backlight(0)

WIDTH, HEIGHT = display.get_bounds()

# Create a class to represent a ball.
class Ball:
    def __init__(self, x, y, row, column):
        self.x = x
        self.y = y
        self.row = row
        self.column = column

# Create a 10x10 grid of balls.
balls = []
DISTANCE = HEIGHT / 11
for column in range(0, 10):
    for row in range(0, 10):
        balls.append(
            Ball(
                (column + 1) * DISTANCE,
                (row + 1) * DISTANCE,
                row,
                column
            )
        )

font_scale = 2
text_y = int(HEIGHT / 2 - 10 * font_scale)

current_text_color = 0
currentText = 0
texts = [
    "She's up all night",
    "till the sun",
    "I'm up all night",
    "to get some",
    "She's up all night",
    "for good fun",
    "I'm up all night",
    "to get lucky",
]

# Second thread to animate the text so we can use sleeps for convenience.
def animate_text():
    global current_text_color
    global currentText
    next_text_color = 1
    while True:
        current_text_color += next_text_color
        if current_text_color >= 10:
            current_text_color = 10
            next_text_color = -1
            time.sleep(1.2)
        elif current_text_color <= 0:
            current_text_color = 0
            next_text_color = 1
            currentText += 1
            if currentText >= len(texts):
                currentText = 0
            time.sleep(0.7)
        else:
            time.sleep(0.05)

# Start the second thread.
_thread.start_new_thread(animate_text, ())

previous_ms = time.ticks_ms()

# Main loop.
while True:
    # Clear the screen.
    display.set_pen(display.create_pen(0, 0, 0))
    display.clear()

    tick = time.ticks_ms() / 1000
    current_hue = current_hue + tick / 1000000

    # Animate and draw the balls.
    for ball in balls:
        ball.radius = 5 + 5 * math.sin(tick + ball.row * 0.2 + ball.column * math.sin(tick * 0.5))

        display.set_pen(get_pen(int(ball.radius), ball.row + ball.column / 100))
        if ball.radius > 1:
            display.circle(int(ball.x), int(ball.y), int(ball.radius))

    # Draw text if color is more than 0.
    if current_text_color > 0:
        text_width = display.measure_text(texts[currentText], scale=font_scale)
        text_x = int(HEIGHT / 2 - text_width / 2) - 20
        display.set_pen(get_pen(current_text_color + 1, saturation=0.1))
        display.set_font("bitmap14_outline")
        display.text(texts[currentText], text_x, text_y, scale=font_scale)

    # Draw date.
    display.set_pen(get_pen(8))
    display.set_font("bitmap6")
    display.text("2023-08-27", 2, HEIGHT - 8, scale=1)

    # Draw FPS.
    ms = time.ticks_ms()
    display.text(str(int(1000 / (ms - previous_ms))) + " FPS", WIDTH - 30, HEIGHT - 8, scale=1)
    previous_ms = ms

    # Update the display.
    display.update()