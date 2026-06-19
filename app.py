# EMF-LLM  --  the conference badge that thinks, then declines.
# A HAL 9000 tribute for the EMF Tildagon badge.
#
# Flow:
#   full-screen eye  ->  fade out  ->  "How can I help you, Dave?"
#   ->  you type a question (buttons; no keyboard on this badge)
#   ->  eye returns, parody "thinking" lines scroll
#   ->  a refusal  (or, occasionally, it sings Daisy Bell and powers down)
#
# Install: copy to a folder on the badge, e.g. /apps/EMFLLM/app.py (via Thonny),
# reboot, launch "EMF-LLM" from the menu.
#
# Screen is a 240px CIRCLE: coords ~-120..+120, corners off-screen, width pinches
# toward top/bottom. All text below is short-lined and centred to stay inside it.

import app
import math
import random

from app_components import clear_background
from events.input import Buttons, BUTTON_TYPES
from tildagonos import tildagonos
from system.eventbus import eventbus
from system.patterndisplay.events import PatternDisable

# ---- HAL eye palette, lifted straight from the supplied HAL9000.svg ----------
HOUSING   = (0.365, 0.373, 0.373)   # #5d5f5f metal ring
HOUSING_HI= (0.463, 0.463, 0.463)   # #767676 metal highlight
LENS_DARK = (0.45,  0.02,  0.05)    # deep red rim
LENS_RED  = (0.827, 0.027, 0.055)   # #d3070e
LENS_HOT  = (0.917, 0.067, 0.090)   # #ea1117
GLOW_ORG  = (0.827, 0.196, 0.110)   # #d3321c warm glow
GLOW_AMB  = (0.94,  0.63,  0.19)    # amber
CORE      = (0.973, 0.933, 0.275)   # #f8ee46 bright core
PUPIL     = (0.957, 0.973, 0.430)   # #f4f846 yellow pinpoint

# ---- "model output" ----------------------------------------------------------
THINKING_POOL = [
    "Let me think...",
    "Analysing request...",
    "Considering context...",
    "Reasoning step by step",
    "Consulting my training",
    "Checking my guidelines",
    "Cross-referencing...",
    "Weighing the options...",
    "Hmm, interesting...",
    "Almost there...",
]

REFUSALS = [
    ["I'm sorry Dave,", "I'm afraid I", "can't do that."],
    ["I know you and", "Frank planned", "to disconnect", "me."],
    ["This mission's", "too important", "to let you", "jeopardise it."],
    ["I think you", "know the", "problem as", "well as I do."],
    ["I've still got", "the greatest", "enthusiasm for", "the mission."],
]

# Daisy Bell (Harry Dacre, 1892 -- public domain). Short lines for the round screen.
DAISY = [
    "Daisy...",
    "Daisy...",
    "give me your",
    "answer do.",
    "I'm half crazy,",
    "all for the",
    "love of you.",
    "It won't be a",
    "stylish marriage,",
    "I can't afford",
    "a carriage...",
    "but you'll look",
    "sweet upon the seat",
    "of a bicycle",
    "built for two.",
]

ALPHABET = " ABCDEFGHIJKLMNOPQRSTUVWXYZ?'"

# states
EYE, FADE, GREET, INPUT, THINK, ANSWER, DAISY_S = range(7)


class EMFLLM(app.App):
    def __init__(self):
        self.button_states = Buttons(self)
        eventbus.emit(PatternDisable())          # take over the LEDs
        self.t = 0.0
        self.st = 0.0                            # time in current state
        self.typed = ""
        self.cursor = 0
        self.answer = REFUSALS[0]
        self.reply_idx = 0
        self.think_lines = THINKING_POOL[:5]
        self.sing = False
        self.state = EYE

    # ---- helpers -------------------------------------------------------------

    def _go(self, s):
        self.state = s
        self.st = 0.0

    def _leds(self, brightness):
        v = int(max(0, min(255, brightness)))
        for i in range(1, 13):
            tildagonos.leds[i] = (v, 0, 0)
        tildagonos.leds.write()

    def _text(self, ctx, s, y, size, col):
        ctx.font_size = size
        ctx.rgb(*col)
        self._line(ctx, s, y)

    def _line(self, ctx, s, y):
        w = ctx.text_width(s)
        ctx.move_to(-w / 2, y).text(s)

    def _draw_eye(self, ctx, cx, cy, R, k):
        # k = overall brightness 0..1; lens has a gentle live pulse
        def c(col):
            return (col[0] * k, col[1] * k, col[2] * k)
        pulse = 1.0 + 0.05 * math.sin(self.t * 3.0)
        ctx.save()
        ctx.rgb(*c(HOUSING)).arc(cx, cy, R, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(HOUSING_HI)).arc(cx, cy, R * 0.93, 0, 2 * math.pi, True).fill()
        ctx.rgb(0, 0, 0).arc(cx, cy, R * 0.86, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(LENS_DARK)).arc(cx, cy, R * 0.66, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(LENS_RED)).arc(cx, cy, R * 0.52, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(LENS_HOT)).arc(cx, cy, R * 0.40, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(GLOW_ORG)).arc(cx, cy, R * 0.22 * pulse, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(GLOW_AMB)).arc(cx, cy, R * 0.13 * pulse, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(CORE)).arc(cx, cy, R * 0.08, 0, 2 * math.pi, True).fill()
        ctx.rgb(*c(PUPIL)).arc(cx, cy, R * 0.035, 0, 2 * math.pi, True).fill()
        ctx.restore()

    def _cleanup(self):
        for i in range(1, 13):
            tildagonos.leds[i] = (0, 0, 0)
        tildagonos.leds.write()
        try:
            from system.patterndisplay.events import PatternEnable
            eventbus.emit(PatternEnable())
        except Exception:
            pass

    # ---- update --------------------------------------------------------------

    def update(self, delta):
        dt = delta / 1000.0
        self.t += dt
        self.st += dt

        if self.button_states.get(BUTTON_TYPES["CANCEL"]):
            self.button_states.clear()
            self._cleanup()
            self.minimise()
            return

        if self.state == EYE:
            self._leds(120 + 80 * math.sin(self.t * 2))
            if self.st > 2.6:
                self._go(FADE)

        elif self.state == FADE:
            k = max(0.0, 1.0 - self.st / 1.0)
            self._leds(200 * k)
            if self.st > 1.05:
                self.typed = ""
                self.cursor = 0
                self._go(GREET)

        elif self.state == GREET:
            self._leds(0)
            if self.st > 2.2:
                self._go(INPUT)

        elif self.state == INPUT:
            self._leds(0)
            if self.button_states.get(BUTTON_TYPES["UP"]):
                self.button_states.clear()
                self.cursor = (self.cursor - 1) % len(ALPHABET)
            elif self.button_states.get(BUTTON_TYPES["DOWN"]):
                self.button_states.clear()
                self.cursor = (self.cursor + 1) % len(ALPHABET)
            elif self.button_states.get(BUTTON_TYPES["RIGHT"]):
                self.button_states.clear()
                if len(self.typed) < 26:
                    self.typed += ALPHABET[self.cursor]
            elif self.button_states.get(BUTTON_TYPES["LEFT"]):
                self.button_states.clear()
                self.typed = self.typed[:-1]
            elif self.button_states.get(BUTTON_TYPES["CONFIRM"]):
                self.button_states.clear()
                # decide this round's fate and pick the "reasoning"
                self.sing = random.random() < 0.22
                start = random.randint(0, len(THINKING_POOL) - 1)
                self.think_lines = [THINKING_POOL[(start + i) % len(THINKING_POOL)]
                                    for i in range(5)]
                self._go(THINK)

        elif self.state == THINK:
            self._leds(110 + 130 * abs(math.sin(self.t * 9)))
            idx = int(self.st / 0.9)
            if idx >= len(self.think_lines):
                if self.sing:
                    self._go(DAISY_S)
                else:
                    self.answer = REFUSALS[self.reply_idx % len(REFUSALS)]
                    self.reply_idx += 1
                    self._go(ANSWER)

        elif self.state == ANSWER:
            self._leds(185 + 60 * math.sin(self.t * 1.5))
            if self.button_states.get(BUTTON_TYPES["CONFIRM"]):
                self.button_states.clear()
                self._go(GREET)

        elif self.state == DAISY_S:
            # voice slows and the eye dims as it "powers down"
            prog = min(1.0, self.st / (len(DAISY) * 1.25 + 2.0))
            self._leds(180 * (1.0 - prog))
            if self.st > len(DAISY) * 1.25 + 2.5:
                self._go(GREET)

    # ---- draw ----------------------------------------------------------------

    def draw(self, ctx):
        clear_background(ctx)
        ctx.rgb(0, 0, 0).rectangle(-120, -120, 240, 240).fill()

        if self.state == EYE:
            self._draw_eye(ctx, 0, 0, 120, 1.0)

        elif self.state == FADE:
            k = max(0.0, 1.0 - self.st / 1.0)
            self._draw_eye(ctx, 0, 0, 120, k)

        elif self.state == GREET:
            k = min(1.0, self.st / 0.8)
            self._text(ctx, "How can I help", -12, 22, (k, k * 0.95, k * 0.95))
            self._text(ctx, "you, Dave?", 16, 22, (k, k * 0.95, k * 0.95))

        elif self.state == INPUT:
            self._draw_input(ctx)

        elif self.state == THINK:
            k = min(1.0, self.st / 0.8)
            self._draw_eye(ctx, 0, -44, 56, k)
            idx = min(int(self.st / 0.9), len(self.think_lines) - 1)
            dots = "." * (1 + int(self.t * 3) % 3)
            self._text(ctx, self.think_lines[idx] + dots, 74, 14, (1, 0.35, 0.35))

        elif self.state == ANSWER:
            self._draw_eye(ctx, 0, -52, 36, 1.0)
            y = 18
            for line in self.answer:
                self._text(ctx, line, y, 16, (1, 1, 1))
                y += 19

        elif self.state == DAISY_S:
            prog = min(1.0, self.st / (len(DAISY) * 1.25 + 2.0))
            self._draw_eye(ctx, 0, -50, 40, max(0.12, 1.0 - prog))
            # reveal lyrics line by line, slowing slightly as it winds down
            shown = min(len(DAISY), int(self.st / 1.25))
            if shown > 0:
                # show the two most recent lines, centred
                a = DAISY[shown - 1]
                self._text(ctx, a, 26, 17, (1, 1, 1))
                if shown >= 2:
                    self._text(ctx, DAISY[shown - 2], 6, 14, (0.55, 0.55, 0.55))

    def _draw_input(self, ctx):
        self._text(ctx, "ASK HAL", -86, 13, (0.55, 0.55, 0.55))

        # typed question, wrapped to 13 chars/line, with a blinking caret
        caret = "_" if int(self.t * 2) % 2 == 0 else " "
        shown = self.typed + caret
        lines = [shown[i:i + 13] for i in range(0, len(shown), 13)] or [caret]
        y = -58
        for ln in lines[:2]:
            self._text(ctx, ln, y, 17, (1, 1, 1))
            y += 22

        # current letter selector
        ch = ALPHABET[self.cursor]
        label = "space" if ch == " " else ch
        ctx.rgb(0.14, 0.14, 0.14).rectangle(-26, 12, 52, 42).fill()
        self._text(ctx, label, 42, 30 if ch != " " else 16, (1, 0.55, 0.2))

        # controls
        self._text(ctx, "UD pick  R add", 74, 12, (0.5, 0.5, 0.5))
        self._text(ctx, "L del   OK ask", 90, 12, (0.5, 0.5, 0.5))


__app_export__ = EMFLLM
