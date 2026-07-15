"""Visuals for "The Geometry of Hidden Things" (5:08 song, timed to vocals).

Based on: Bryan W. Roberts, "Heat as a gauge connection", arXiv:2503.08753
(2025). London School of Economics.

The paper: heat defines a gauge connection on a line bundle over the space
of work configurations. When the connection's curvature vanishes, entropy
and temperature functions exist locally and heat can be written TdS -- the
familiar thermodynamics. When the curvature does NOT vanish, a thermal
analogue of a geometric (Berry) phase appears: a hidden holonomy that the
ordinary "shadow" bookkeeping of heat and work never shows. So two hundred
years of thermodynamics turn out to carry a hidden geometry -- not new
physics, a new way to see the old physics.

The video leans on a warm(visible heat) vs cool(hidden geometry) duality,
a rolling marble whose shadow can't confess the colour inside it, and a
fibre bundle whose parallel transport comes back rotated.

Render (from the manim/ directory):
    manim -pql scenes/the_geometry_of_hidden_things.py TheGeometryOfHiddenThings
    manim -pqh scenes/the_geometry_of_hidden_things.py TheGeometryOfHiddenThings

Timing anchored on a Whisper pass for the spoken/lyric-dense stretches;
the sung choruses are estimated, paced between solid anchors. A long
instrumental tail (~287-308s) holds the citation card.
"""

import random
from pathlib import Path

import numpy as np
from manim import *

MP3 = (Path(__file__).resolve().parents[2] / "songs"
       / "the-geometry-of-hidden-things"
       / "ep 115 The Geometry of Hidden Things.mp3")

HEAT = "#ff8c42"      # warm orange - visible heat / fire
FIRE_HOT = "#ffd23f"  # hot yellow core
WORK = "#c8a24a"      # brass - work / piston (mechanical, observable)
HIDDEN = "#5b8cff"    # cool blue - the hidden geometry
GEO = "#8b7bff"       # violet - geometry
COOL = "#4cc9f0"      # cyan accent
STEEL = "#9aa4b4"     # steel grey
SHADOW = "#191a20"    # near-black shadow
INK = "#ece7db"       # warm parchment caption text
DIM = "#8f8a7e"       # dim warm grey
random.seed(3)


# --------------------------------------------------------------------------
# Atmosphere / motion helpers
# --------------------------------------------------------------------------

def soft_blob(pos, radius, color, peak=0.05, layers=26):
    g = VGroup()
    for i in range(layers):
        frac = i / (layers - 1)
        r = radius * (1 - 0.92 * frac)
        op = peak * (frac ** 1.7)
        if op < 0.0015:
            continue
        g.add(Circle(radius=r, color=color, fill_opacity=op,
                     stroke_width=0).move_to(pos))
    return g


def sphere3d(radius, color, pos=ORIGIN, light=(-0.5, 0.6, 0), layers=26):
    """A fake-3D sphere: dark rim -> bright centre offset toward the light,
    plus a specular highlight."""
    lu = np.array(light, dtype=float)
    lu = lu / (np.linalg.norm(lu) + 1e-9)
    dark = interpolate_color(ManimColor(color), ManimColor("#070707"), 0.62)
    lite = interpolate_color(ManimColor(color), WHITE, 0.5)
    g = VGroup()
    for i in range(layers):
        frac = i / (layers - 1)
        r = radius * (1 - 0.98 * frac)
        off = lu * radius * frac * 0.55
        col = interpolate_color(dark, lite, frac ** 0.85)
        g.add(Circle(radius=max(r, 0.006), color=col, fill_opacity=1,
                     stroke_width=0).move_to(pos + off))
    g.add(Circle(radius=radius * 0.15, color=WHITE, fill_opacity=0.75,
                 stroke_width=0).move_to(pos + lu * radius * 0.5))
    g.add(Circle(radius=radius * 0.05, color=WHITE, fill_opacity=0.9,
                 stroke_width=0).move_to(pos + lu * radius * 0.58))
    return g


def trail_group(mob, color=HEAT, segments=14, radius=0.045):
    trail = VGroup(*[Dot(radius=radius, color=color, fill_opacity=0)
                     for _ in range(segments)])
    history = []

    def upd(m, dt):
        history.append(mob.get_center().copy())
        if len(history) > segments:
            history.pop(0)
        for i, seg in enumerate(m):
            if i < len(history):
                seg.move_to(history[-(i + 1)])
                seg.set_opacity(max(0, 0.5 * (1 - i / segments)))
            else:
                seg.set_opacity(0)

    trail.add_updater(upd)
    return trail


def landscape(bumps, x_range=(-4, 4), color=GEO, stroke_width=3.5):
    def f(x):
        return sum(h * np.exp(-((x - cx) ** 2) / (2 * w ** 2))
                   for cx, h, w in bumps)
    return FunctionGraph(f, x_range=list(x_range), color=color,
                         stroke_width=stroke_width), f


def curve_glow(curve, color, widths=(18, 11, 6), opacity=0.05):
    g = VGroup()
    for w in widths:
        c = curve.copy().set_stroke(color=color, width=w, opacity=opacity)
        c.set_fill(opacity=0)
        g.add(c)
    return g


def dashed(mobject, num_dashes=24, color=None):
    d = DashedVMobject(mobject, num_dashes=num_dashes, dashed_ratio=0.55)
    if color:
        d.set_color(color)
    return d


def flame_shape(color, h=1.0):
    m = VMobject(fill_color=color, fill_opacity=0.85, stroke_width=0)
    m.set_points_smoothly([
        np.array([0, h, 0]), np.array([0.34 * h, 0.34 * h, 0]),
        np.array([0.24 * h, -0.05 * h, 0]), np.array([0, -0.14 * h, 0]),
        np.array([-0.24 * h, -0.05 * h, 0]), np.array([-0.34 * h, 0.34 * h, 0]),
        np.array([0, h, 0]),
    ])
    return m


def flame(scale=1.0, pos=ORIGIN):
    outer = flame_shape(HEAT, h=1.0 * scale)
    inner = flame_shape(FIRE_HOT, h=0.58 * scale).shift(DOWN * 0.05 * scale)
    glow = soft_blob(ORIGIN, 0.8 * scale, HEAT, peak=0.08, layers=12)
    return VGroup(glow, outer, inner).move_to(pos)


def add_drift(mob, amp=0.06, speed=1.0):
    mob.drift_t = random.uniform(0, TAU)
    mob.drift_prev = np.zeros(3)

    def upd(m, dt):
        m.drift_t += dt
        off = np.array([0.5 * np.sin(0.6 * speed * m.drift_t),
                        np.sin(speed * m.drift_t), 0]) * amp
        m.shift(off - m.drift_prev)
        m.drift_prev = off

    mob.add_updater(upd)


def add_breathe(mob, amp=0.03, speed=1.0):
    mob.br_t = random.uniform(0, TAU)
    mob.br_prev = 1.0

    def upd(m, dt):
        m.br_t += dt
        target = 1 + amp * np.sin(speed * m.br_t)
        m.scale(target / m.br_prev)
        m.br_prev = target

    mob.add_updater(upd)


def add_flicker(mob, amp=0.14, speed=9.0):
    mob.fl_t = random.uniform(0, TAU)
    mob.fl_prev = 1.0

    def upd(m, dt):
        m.fl_t += dt
        target = 1 + amp * (np.sin(speed * m.fl_t)
                            + 0.4 * np.sin(2.3 * speed * m.fl_t + 1))
        m.stretch(max(0.6, target) / m.fl_prev, 1)
        m.fl_prev = max(0.6, target)

    mob.add_updater(upd)


def add_twinkle(mob, speed=None):
    mob.tw_t = random.uniform(0, TAU)
    sp = speed or random.uniform(1.5, 3.0)
    base = mob.get_fill_opacity() or 0.7

    def upd(m, dt):
        m.tw_t += sp * dt
        m.set_opacity(max(0.05, base * (0.5 + 0.5 * np.sin(m.tw_t))))

    mob.add_updater(upd)


# --------------------------------------------------------------------------
# Story-specific building blocks
# --------------------------------------------------------------------------

def marble_and_shadow(radius=0.7, pos=ORIGIN, ground_y=-2.2, hidden=True):
    """A 3D marble sitting in a warm spotlight, casting a flat grey shadow on
    the ground below. Optionally a hidden glowing core inside -- the colour
    the shadow can never confess. Returns (group, marble, shadow, core)."""
    spot = soft_blob([pos[0], ground_y + 0.05, 0], radius * 2.6, HEAT,
                     peak=0.10, layers=16)
    shadow = Ellipse(width=radius * 2.1, height=radius * 0.5, color=SHADOW,
                     fill_opacity=0.75, stroke_width=0)
    shadow.move_to([pos[0], ground_y + 0.05, 0])
    marble = sphere3d(radius, STEEL, pos=pos, layers=24)
    grp = VGroup(spot, shadow, marble)
    core = None
    if hidden:
        core = VGroup(soft_blob(pos, radius * 0.7, HIDDEN, peak=0.5, layers=14),
                      Dot(radius=radius * 0.22, color=HIDDEN).move_to(pos))
        core.set_opacity(0)
        grp.add(core)
    return grp, marble, shadow, core


def fibre_bundle(base_y=-1.7, x_range=(-4.2, 4.2), n=11, fibre_h=1.5,
                 color=HIDDEN):
    """A base line (work configurations) with vertical fibres (heat) rising
    from each point -- the line bundle the paper builds."""
    base = Line([x_range[0], base_y, 0], [x_range[1], base_y, 0],
                color=STEEL, stroke_width=2.5)
    fibres = VGroup()
    for x in np.linspace(x_range[0] + 0.35, x_range[1] - 0.35, n):
        fibres.add(Line([x, base_y, 0], [x, base_y + fibre_h, 0],
                        color=color, stroke_width=1.6, stroke_opacity=0.5))
    caps = VGroup(*[Dot([ln.get_start()[0], base_y, 0], radius=0.04,
                        color=STEEL) for ln in fibres])
    return VGroup(base, fibres, caps)


def piston(pos=ORIGIN, extend=0.0):
    """A simple cylinder + sliding head + rod. `extend` in [0,1] slides the
    head out to the right. Returns (group, head, rod)."""
    body = RoundedRectangle(width=1.5, height=0.8, corner_radius=0.08,
                            stroke_color=STEEL, stroke_width=2.5,
                            fill_color="#14140f", fill_opacity=0.85)
    hx = -0.3 + extend * 0.55
    head = RoundedRectangle(width=0.42, height=0.66, corner_radius=0.06,
                            fill_color=WORK, fill_opacity=1,
                            stroke_width=0).move_to([hx, 0, 0])
    rod = Line([hx + 0.21, 0, 0], [1.5, 0, 0], stroke_color=STEEL,
               stroke_width=6)
    knob = Dot([1.5, 0, 0], radius=0.09, color=WORK)
    grp = VGroup(body, head, rod, knob).move_to(pos)
    return grp, head, rod


def equals_post(pos, color=WORK):
    """An '=' sign that doubles as a little fence post."""
    top = Line(LEFT * 0.18, RIGHT * 0.18, stroke_width=4, color=color)
    bot = Line(LEFT * 0.18, RIGHT * 0.18, stroke_width=4, color=color)
    top.shift(UP * 0.09)
    bot.shift(DOWN * 0.09)
    return VGroup(top, bot).move_to(pos)


class TheGeometryOfHiddenThings(Scene):
    def play_t(self, *anims, run_time=1.0, **kwargs):
        self.play(*anims, run_time=run_time, **kwargs)
        self.t += run_time

    def wait_until(self, t):
        if t > self.t:
            self.wait(t - self.t)
            self.t = t

    def swap(self, old, new, *extra, run_time=1.2):
        self.play_t(AnimationGroup(FadeOut(old, shift=UP * 0.15),
                                   FadeIn(new, shift=UP * 0.15), lag_ratio=0.55),
                    *extra, run_time=run_time)
        return new

    def enter_cap(self, new_cap, *extra, run_time=1.5):
        old = getattr(self, "_cap", None)
        if old is not None:
            self.play_t(FadeOut(old, shift=UP * 0.2),
                        FadeIn(new_cap, shift=UP * 0.2), *extra, run_time=run_time)
            self._cap = None
        else:
            self.play_t(Write(new_cap), *extra, run_time=run_time)
        return new_cap

    def cap_text(self, s, size=29):
        return Text(s, font_size=size, color=INK).to_edge(UP, buff=0.7)

    # ----------------------------------------------------------------
    def construct(self):
        if MP3.exists():
            self.add_sound(str(MP3))
        self.t = 0.0
        self.add_ambient_background()
        self.opening_arithmetic()       # 0:02 - 0:47
        self.the_marble()               # 0:47 - 1:35
        self.casts_evidence()           # 1:35 - 1:47
        self.geometry_beneath_fire()    # 1:47 - 2:10
        self.work_and_heat()            # 2:10 - 2:37
        self.gauge_theory()             # 2:37 - 3:15
        self.entropy_perspective()      # 3:15 - 3:58
        self.final_chorus()             # 3:58 - 4:27
        self.closing()                  # 4:27 - 5:08

    def add_ambient_background(self):
        """Warm/cool duality: heat glow on one side, hidden-geometry glow on
        the other, drifting motes, and soft foreground bokeh for depth."""
        nebulae = VGroup()
        for pos, r, col in (
            (np.array([-5.0, -1.8, 0]), 4.2, HEAT),
            (np.array([5.0, 2.0, 0]), 4.2, HIDDEN),
            (np.array([2.6, -2.6, 0]), 2.6, WORK),
            (np.array([-3.2, 2.6, 0]), 2.6, GEO),
        ):
            blob = soft_blob(pos, r, col, peak=0.045)
            blob.drift = np.array([random.uniform(-0.02, 0.02),
                                   random.uniform(-0.012, 0.012), 0])
            blob.add_updater(lambda m, dt: m.shift(m.drift * dt))
            nebulae.add(blob)

        motes = VGroup()
        for _ in range(30):
            depth = random.random()
            dot = Circle(radius=0.018 + 0.05 * depth,
                        color=random.choice([HEAT, HIDDEN, COOL, DIM]),
                        fill_opacity=0.05 + 0.12 * depth, stroke_width=0)
            dot.move_to([random.uniform(-7, 7), random.uniform(-4.2, 4.2), 0])
            dot.drift = np.array([random.uniform(-0.05, 0.05),
                                  0.02 + 0.07 * depth, 0])

            def upd(m, dt):
                m.shift(m.drift * dt)
                if m.get_center()[1] > 4.6:
                    m.shift(DOWN * 9.2)

            dot.add_updater(upd)
            motes.add(dot)

        bokeh = VGroup()
        for _ in range(4):
            b = soft_blob([random.uniform(-7, 7), random.uniform(-4, 4), 0],
                          random.uniform(0.9, 1.6),
                          random.choice([HEAT, HIDDEN, COOL]), peak=0.05,
                          layers=16)
            b.drift = np.array([random.uniform(-0.06, 0.06),
                                random.uniform(-0.03, 0.03), 0])
            b.add_updater(lambda m, dt: m.shift(m.drift * dt))
            bokeh.add(b)
        self.add(nebulae, motes, bokeh)

    # ----------------------------------------------------------------
    def opening_arithmetic(self):
        title = Text("The Geometry of Hidden Things", font_size=48,
                     gradient=(HEAT, HIDDEN))
        halo = Text("The Geometry of Hidden Things", font_size=48,
                    color=HIDDEN).set_opacity(0.14).scale(1.05).move_to(title)
        self.play_t(FadeIn(halo), Write(title), run_time=2.5)
        self.wait_until(2.1)
        cap = self.cap_text("For two hundred years,", 30)
        self.play_t(title.animate.scale(0.55).to_edge(UP, buff=0.55),
                    FadeOut(halo), FadeIn(cap, shift=UP * 0.2), run_time=1.5)
        self._cap = None
        self.play_t(FadeOut(title), run_time=0.6)
        self._cap = cap

        # A ledger of heat = work: equal-sign fence posts across a landscape.
        ground, f = landscape([(-2.5, 0.5, 1.1), (1.8, -0.4, 1.0)],
                              x_range=(-6, 6), color=DIM, stroke_width=2)
        ground.shift(DOWN * 1.2)
        posts = VGroup()
        for x in np.arange(-5, 5.1, 1.25):
            posts.add(equals_post([x, f(x) - 1.2 + 0.35, 0]))
        self.wait_until(9.0)
        cap = self.swap(cap, self.cap_text("the arithmetic balanced.", 30),
                        Create(ground), run_time=1.5)
        self.play_t(LaggedStartMap(FadeIn, posts, lag_ratio=0.1, shift=UP * 0.2),
                    run_time=2.0)

        self.wait_until(14.0)
        heat_lbl = Text("heat", font_size=26, color=HEAT).move_to(LEFT * 2.6 + UP * 1.2)
        work_lbl = Text("work", font_size=26, color=WORK).move_to(RIGHT * 2.6 + UP * 1.2)
        eq = equals_post(UP * 1.2).scale(1.6)
        cap = self.swap(cap, self.cap_text("Heat.   Work.", 30),
                        FadeIn(heat_lbl, shift=RIGHT * 0.3),
                        FadeIn(work_lbl, shift=LEFT * 0.3), run_time=1.6)
        self.play_t(FadeIn(eq), run_time=1.0)

        self.wait_until(19.0)
        cap = self.swap(cap, self.cap_text("Equal signs standing like fence posts", 27),
                        Indicate(posts, color=WORK, scale_factor=1.1),
                        run_time=1.8)
        self.wait_until(27.0)
        cap = self.swap(cap, self.cap_text("across the landscape.", 29),
                        FadeOut(heat_lbl), FadeOut(work_lbl), FadeOut(eq),
                        run_time=1.6)

        self.wait_until(31.0)
        # An engine chugs, unbothered.
        eng, head, rod = piston(pos=DOWN * 0.2)
        cap = self.swap(cap, self.cap_text("The engine never complained.", 29),
                        FadeOut(posts), FadeIn(eng, shift=UP * 0.2), run_time=1.6)
        for _ in range(2):
            self.play_t(head.animate.shift(RIGHT * 0.35),
                        rod.animate.shift(RIGHT * 0.35), run_time=0.5)
            self.play_t(head.animate.shift(LEFT * 0.35),
                        rod.animate.shift(LEFT * 0.35), run_time=0.5)

        self.wait_until(35.0)
        cap = self.swap(cap, self.cap_text("The equations behaved.", 29), run_time=1.4)

        self.wait_until(40.6)
        # A map arrives before the language: a cool grid unfurls over it all.
        grid = NumberPlane(x_range=[-7, 7, 1], y_range=[-4, 4, 1],
                           background_line_style={"stroke_color": HIDDEN,
                                                  "stroke_width": 1,
                                                  "stroke_opacity": 0.22},
                           axis_config={"stroke_opacity": 0})
        cap = self.swap(cap, self.cap_text("But sometimes a map arrives", 28),
                        FadeOut(eng), Create(grid), run_time=2.0)
        self.wait_until(44.0)
        cap = self.swap(cap, self.cap_text("long before the language to describe the country.", 25),
                        run_time=1.6)
        self.wait_until(47.0)
        self.play_t(FadeOut(ground), grid.animate.set_opacity(0.08), run_time=1.5)
        self.bg_grid = grid
        self._cap = cap

    # ----------------------------------------------------------------
    def the_marble(self):
        self.wait_until(64.0)
        cap = self.cap_text("Imagine a marble rolling through sunlight.", 27)
        grp, marble, shadow, core = marble_and_shadow(radius=0.75,
                                                       pos=LEFT * 3 + UP * 0.2,
                                                       ground_y=-2.2)
        cap = self.enter_cap(cap, FadeIn(grp), run_time=2.0)
        # It rolls to the right; the shadow tracks along the ground.
        self.play_t(grp.animate.shift(RIGHT * 3), run_time=2.5, rate_func=linear)

        self.wait_until(68.6)
        cap2 = self.cap_text("You see its shadow.  You measure its speed.", 26)
        cap = self.swap(cap, cap2, Indicate(shadow, color=STEEL, scale_factor=1.2),
                        run_time=1.8)
        self.wait_until(73.0)
        cap = self.swap(cap, self.cap_text("You know its weight.", 29), run_time=1.4)

        self.wait_until(76.7)
        cap2 = self.cap_text("Yet buried inside the stone...", 28)
        # The hidden colour glows on inside -- the shadow stays grey.
        cap = self.swap(cap, cap2, core.animate.set_opacity(1.0),
                        run_time=1.8)
        self.wait_until(80.0)
        cap2 = self.cap_text("is a colour the shadow can never confess.", 26)
        # Point from marble (colour) to shadow (no colour).
        arrow = Arrow(marble.get_center() + DOWN * 0.2,
                      shadow.get_center() + UP * 0.15, color=HIDDEN,
                      stroke_width=3, buff=0.15)
        cap = self.swap(cap, cap2, Create(arrow), run_time=1.6)
        self.play_t(Indicate(shadow, color=SHADOW, scale_factor=1.15),
                    FadeOut(arrow), run_time=1.5)

        self.wait_until(86.8)
        cap = self.swap(cap, self.cap_text("Can you discover the unseen...", 28),
                        run_time=1.5)
        self.wait_until(90.5)
        cap2 = self.cap_text("by studying what it leaves behind?", 27)
        # The shadow pulses -- the only evidence.
        cap = self.swap(cap, cap2, run_time=1.5)
        self.play_t(Broadcast(shadow.copy().set_fill(opacity=0)
                              .set_stroke(STEEL, 2), focal_point=shadow.get_center()),
                    run_time=2.5)
        self.wait_until(95.0)
        self.marble_grp = grp
        self.marble = marble
        self.marble_shadow = shadow
        self.marble_core = core
        self._cap = cap

    # ----------------------------------------------------------------
    def casts_evidence(self):
        cap = self.cap_text("Every mystery casts evidence.", 29)
        cap = self.enter_cap(cap, run_time=1.4)
        # Shadow throws off little evidence-marks.
        marks = VGroup(*[
            Line(ORIGIN, UP * 0.16, color=STEEL, stroke_width=2)
            .move_to(self.marble_shadow.get_center()
                     + RIGHT * random.uniform(-1, 1) + DOWN * 0.2)
            for _ in range(7)])
        self.play_t(LaggedStartMap(GrowFromCenter, marks, lag_ratio=0.12),
                    run_time=1.6)

        self.wait_until(100.0)
        cap = self.swap(cap, self.cap_text("The invisible is rarely silent.", 29),
                        FadeOut(marks), run_time=1.6)
        self.wait_until(107.0)
        self.play_t(FadeOut(self.marble_grp), run_time=1.4)
        self._cap = cap

    # ----------------------------------------------------------------
    def geometry_beneath_fire(self):
        self.wait_until(107.7)
        cap = self.cap_text("There's a geometry beneath the fire.", 27)
        fl = flame(scale=1.3, pos=UP * 0.6)
        add_flicker(fl[1]); add_flicker(fl[2])
        # A hidden geometric curve glows beneath the flame.
        curve, f = landscape([(-2, 0.6, 0.8), (0.4, -0.7, 0.7), (2.4, 0.5, 0.7)],
                             color=HIDDEN, stroke_width=3)
        curve.shift(DOWN * 1.6)
        cglow = curve_glow(curve, HIDDEN)
        cap = self.enter_cap(cap, FadeIn(fl, scale=0.5), run_time=2.0)
        self.play_t(FadeIn(cglow), Create(curve), run_time=1.6)

        self.wait_until(112.0)
        cap = self.swap(cap, self.cap_text("A hidden country inside desire.", 28),
                        run_time=1.5)
        self.wait_until(116.0)
        cap = self.swap(cap, self.cap_text("Heat isn't lost...", 30), run_time=1.3)
        self.wait_until(119.0)
        cap2 = self.cap_text("it simply lives where light can't go.", 27)
        # Heat particles fall from the flame down into the hidden curve.
        embers = VGroup(*[Dot(fl.get_center() + RIGHT * random.uniform(-0.4, 0.4),
                              radius=0.05, color=HEAT) for _ in range(8)])
        cap = self.swap(cap, cap2, FadeIn(embers), run_time=1.3)
        self.play_t(LaggedStart(*[
            e.animate.move_to([x, f(x) - 1.6, 0]).set_color(HIDDEN)
            for e, x in zip(embers, np.linspace(-2.4, 2.4, 8))],
            lag_ratio=0.08), run_time=2.2)

        self.wait_until(123.4)
        cap = self.swap(cap, self.cap_text("Every shadow writes a story—", 27),
                        FadeOut(embers), run_time=1.4)
        self.wait_until(127.0)
        cap = self.swap(cap, self.cap_text("only mathematics learns to know.", 27),
                        run_time=1.5)
        self.wait_until(130.0)
        self.play_t(FadeOut(fl), FadeOut(curve), FadeOut(cglow), run_time=1.5)
        self.hidden_f = f
        self._cap = cap

    # ----------------------------------------------------------------
    def work_and_heat(self):
        self.wait_until(131.0)
        cap = self.cap_text("Work shakes your hand.", 29)
        eng, head, rod = piston(pos=LEFT * 3 + UP * 0.3)
        cap = self.enter_cap(cap, FadeIn(eng, shift=RIGHT * 0.3), run_time=1.5)
        self.play_t(head.animate.shift(RIGHT * 0.4), rod.animate.shift(RIGHT * 0.4),
                    run_time=0.6)
        self.play_t(head.animate.shift(LEFT * 0.4), rod.animate.shift(LEFT * 0.4),
                    run_time=0.6)

        self.wait_until(135.0)
        cap2 = self.cap_text("Heat... leaves fingerprints.", 29)
        # Heat = a diffuse cloud of warm specks spreading on the right.
        heat_cloud = VGroup(*[Dot(RIGHT * 3 + UP * 0.3
                                  + np.array([random.uniform(-0.3, 0.3),
                                              random.uniform(-0.3, 0.3), 0]),
                                  radius=random.uniform(0.03, 0.07), color=HEAT)
                              for _ in range(24)])
        cap = self.swap(cap, cap2, FadeIn(heat_cloud, scale=0.4), run_time=1.5)
        self.play_t(*[d.animate.shift(np.array([random.uniform(-0.8, 0.9),
                                                random.uniform(-0.6, 0.6), 0]))
                      .set_opacity(random.uniform(0.3, 0.7))
                      for d in heat_cloud], run_time=1.5)

        self.wait_until(139.0)
        cap = self.swap(cap, self.cap_text("One can move a piston.", 29),
                        Indicate(eng, color=WORK, scale_factor=1.08), run_time=1.5)
        self.wait_until(143.0)
        cap = self.swap(cap, self.cap_text("The other slips quietly through every bargain nature made.", 23),
                        heat_cloud.animate.set_opacity(0.4), run_time=1.6)

        self.wait_until(149.0)
        cap2 = self.cap_text("Different voices...", 30)
        # Both connect down to one shared hidden structure.
        hub = Dot(DOWN * 1.8, radius=0.09, color=HIDDEN)
        l1 = Line(eng.get_bottom(), hub.get_center(), color=HIDDEN,
                  stroke_width=1.5, stroke_opacity=0.5)
        l2 = Line(RIGHT * 3 + UP * 0.1, hub.get_center(), color=HIDDEN,
                  stroke_width=1.5, stroke_opacity=0.5)
        cap = self.swap(cap, cap2, FadeIn(hub), Create(l1), Create(l2),
                        run_time=1.6)
        self.wait_until(153.0)
        cap = self.swap(cap, self.cap_text("Same conversation.", 30),
                        Indicate(hub, color=HIDDEN, scale_factor=1.8), run_time=1.5)
        self.wait_until(157.0)
        self.play_t(FadeOut(eng), FadeOut(heat_cloud), FadeOut(hub),
                    FadeOut(l1), FadeOut(l2), run_time=1.4)
        self._cap = cap

    # ----------------------------------------------------------------
    def gauge_theory(self):
        self.wait_until(157.2)
        cap = self.cap_text("Gauge theory.   Funny phrase.", 28)
        bundle = fibre_bundle()
        cap = self.enter_cap(cap, FadeIn(bundle, shift=UP * 0.2), run_time=1.8)

        self.wait_until(161.1)
        cap = self.swap(cap, self.cap_text("Sounds like something you'd borrow from an old mechanic.", 23),
                        run_time=1.6)

        self.wait_until(165.7)
        cap2 = self.cap_text("It's how physicists keep track of things that refuse to stand still.", 22)
        # Parallel transport: a vector rides a loop on the base and comes back
        # ROTATED -- the curvature / hidden thermal phase (holonomy).
        base_y = -1.7
        loop = Rectangle(width=3.4, height=1.3, color=WORK, stroke_width=2.5)
        loop.move_to([0, base_y + 0.65, 0])
        vbase = np.array([0, 0.7, 0])
        start_pt = loop.point_from_proportion(0)
        vec = Arrow(start_pt, start_pt + vbase, buff=0, color=HEAT,
                    stroke_width=5, max_tip_length_to_length_ratio=0.35)
        ghost = vec.copy().set_color(DIM).set_opacity(0.5)
        cap = self.swap(cap, cap2, Create(loop), FadeIn(ghost), FadeIn(vec),
                        run_time=1.8)
        # Parallel transport: carry the vector around the loop, turning it as it
        # goes; it returns ROTATED -- the curvature / hidden thermal phase.
        tp = ValueTracker(0)

        def vec_upd(m):
            a = tp.get_value()
            pt = loop.point_from_proportion(a)
            m.put_start_and_end_on(pt, pt + rotate_vector(vbase, -TAU * 0.25 * a))

        vec.add_updater(vec_upd)
        self.play_t(tp.animate.set_value(1), run_time=3.5, rate_func=linear)
        vec.clear_updaters()

        self.wait_until(172.7)
        cap2 = self.cap_text("Maybe the universe has never hidden its secrets.", 25)
        # The transported vector (rotated) no longer matches the ghost original.
        cap = self.swap(cap, cap2, Indicate(vec, color=HEAT),
                        Indicate(ghost, color=DIM), run_time=1.8)

        self.wait_until(176.3)
        cap2 = self.cap_text("Maybe we've been reading the shadow...", 27)
        # Object (3D marble) vs its shadow (flat disc).
        obj = sphere3d(0.55, HIDDEN, pos=LEFT * 3.2 + UP * 0.3, layers=20)
        shad = Ellipse(width=1.1, height=0.3, color=SHADOW, fill_opacity=0.8,
                       stroke_width=0).move_to(LEFT * 3.2 + DOWN * 1.5)
        cap = self.swap(cap, cap2, FadeOut(loop), FadeOut(vec), FadeOut(ghost),
                        FadeOut(bundle), FadeIn(obj), FadeIn(shad), run_time=1.8)
        self.wait_until(180.0)
        cap = self.swap(cap, self.cap_text("instead of the object.", 29),
                        Indicate(obj, color=HIDDEN, scale_factor=1.2), run_time=1.6)

        self.wait_until(185.0)
        cap = self.swap(cap, self.cap_text("Alright...   alright...   alright...", 29),
                        run_time=1.5)
        self.wait_until(191.0)
        self.play_t(FadeOut(obj), FadeOut(shad), run_time=1.5)
        self._cap = cap

    # ----------------------------------------------------------------
    def entropy_perspective(self):
        self.wait_until(195.0)
        cap = self.cap_text("Entropy...", 31)
        # A cloud of scattered points -- looks like chaos up close.
        pts = VGroup(*[Dot([random.uniform(-3.2, 3.2), random.uniform(-2.2, 1.6), 0],
                           radius=0.05, color=random.choice([HEAT, COOL, DIM]))
                       for _ in range(60)])
        cap = self.enter_cap(cap, LaggedStartMap(FadeIn, pts, lag_ratio=0.01),
                             run_time=1.8)

        self.wait_until(199.0)
        cap = self.swap(cap, self.cap_text("Perhaps it was never disorder.", 29),
                        run_time=1.5)
        self.wait_until(204.0)
        cap = self.swap(cap, self.cap_text("Perhaps... it's perspective.", 29),
                        run_time=1.5)

        self.wait_until(209.0)
        cap = self.swap(cap, self.cap_text("Stand too close...", 30),
                        pts.animate.scale(1.6), run_time=1.6)
        self.wait_until(214.5)
        cap = self.swap(cap, self.cap_text("Life looks like chaos.", 29), run_time=1.4)

        self.wait_until(218.0)
        cap2 = self.cap_text("Step back...", 30)
        # Step back: the points snap onto a smooth curve -- order from distance.
        _, gf = landscape([(-2, 0.7, 0.9), (1.5, -0.6, 0.8)], color=GEO)
        targets = np.linspace(-3.4, 3.4, len(pts))
        cap = self.swap(cap, cap2, pts.animate.scale(0.55), run_time=1.5)
        self.play_t(*[p.animate.move_to([x, gf(x) - 0.2, 0]).set_color(GEO)
                      for p, x in zip(pts, targets)], run_time=2.0)

        self.wait_until(221.0)
        curve, _ = landscape([(-2, 0.7, 0.9), (1.5, -0.6, 0.8)], color=GEO,
                             stroke_width=3)
        curve.shift(DOWN * 0.2)
        cap = self.swap(cap, self.cap_text("Geometry begins to rhyme.", 28),
                        Create(curve), run_time=1.6)

        self.wait_until(227.9)
        cap2 = self.cap_text("Even a black hole...", 29)
        # Black hole (left) and steam engine (right), same curve between them.
        hole = VGroup(soft_blob(LEFT * 3.4 + DOWN * 0.3, 0.8, HIDDEN, peak=0.14,
                                layers=14),
                      Circle(radius=0.35, color=BLACK, fill_opacity=1,
                             stroke_color=HIDDEN, stroke_width=2)
                      .move_to(LEFT * 3.4 + DOWN * 0.3))
        eng, _, _ = piston(pos=RIGHT * 3.4 + DOWN * 0.3)
        cap = self.swap(cap, cap2, FadeOut(pts), FadeOut(curve),
                        FadeIn(hole, scale=0.5), run_time=1.6)
        self.wait_until(231.0)
        cap2 = self.cap_text("might be speaking the very same language as a steam engine.", 22)
        link = DashedLine(LEFT * 2.8 + DOWN * 0.3, RIGHT * 2.6 + DOWN * 0.3,
                          color=GEO, stroke_width=2)
        cap = self.swap(cap, cap2, FadeIn(eng, shift=LEFT * 0.3), Create(link),
                        run_time=1.8)
        self.wait_until(238.0)
        self.play_t(FadeOut(hole), FadeOut(eng), FadeOut(link), run_time=1.5)
        self._cap = cap

    # ----------------------------------------------------------------
    def final_chorus(self):
        self.wait_until(238.8)
        cap = self.cap_text("There's a geometry beneath the flame.", 27)
        fl = flame(scale=1.2, pos=UP * 0.7)
        add_flicker(fl[1]); add_flicker(fl[2])
        curve, f = landscape([(-2.2, 0.6, 0.8), (0.5, -0.7, 0.7), (2.5, 0.5, 0.7)],
                             color=HIDDEN, stroke_width=3)
        curve.shift(DOWN * 1.5)
        cglow = curve_glow(curve, HIDDEN)
        cap = self.enter_cap(cap, FadeIn(fl, scale=0.5), FadeIn(cglow),
                             Create(curve), run_time=2.0)

        self.wait_until(243.0)
        cap = self.swap(cap, self.cap_text("Every answer changing names.", 28),
                        run_time=1.5)
        self.wait_until(247.0)
        cap = self.swap(cap, self.cap_text("The visible world is only the verse...", 26),
                        Indicate(fl, color=HEAT, scale_factor=1.1), run_time=1.6)
        self.wait_until(251.0)
        cap = self.swap(cap, self.cap_text("The hidden world completes the chorus.", 26),
                        Indicate(curve, color=HIDDEN, scale_factor=1.05),
                        run_time=1.7)

        self.wait_until(255.0)
        cap = self.swap(cap, self.cap_text("Two hundred years...   one deeper view.", 27),
                        run_time=1.6)
        self.wait_until(260.0)
        cap = self.swap(cap, self.cap_text("Not a new universe...", 29), run_time=1.4)
        self.wait_until(263.5)
        cap = self.swap(cap, self.cap_text("a new way to see the old one.", 28),
                        run_time=1.6)
        self.wait_until(267.0)
        self.play_t(FadeOut(fl), FadeOut(curve), FadeOut(cglow), run_time=1.5)
        self._cap = cap

    # ----------------------------------------------------------------
    def closing(self):
        self.wait_until(267.3)
        cap = self.cap_text("Science isn't the business of replacing certainty.", 25)
        cap = self.enter_cap(cap, run_time=1.8)
        self.wait_until(273.9)
        cap = self.swap(cap, self.cap_text("It's the art of discovering...", 28),
                        run_time=1.6)
        self.wait_until(280.0)
        # A grey shadow resolves into a glowing question mark.
        shadow = Ellipse(width=1.4, height=0.4, color=SHADOW, fill_opacity=0.8,
                         stroke_width=0).move_to(DOWN * 0.6)
        q = Text("?", font_size=90, gradient=(HEAT, HIDDEN)).move_to(DOWN * 0.2)
        cap = self.swap(cap, self.cap_text("that certainty was merely the shadow...", 26),
                        FadeIn(shadow), run_time=1.6)
        self.wait_until(284.0)
        cap = self.swap(cap, self.cap_text("of a better question.", 29),
                        ReplacementTransform(shadow, q), run_time=1.8)

        self.wait_until(289.0)
        # Instrumental tail: settle onto the citation card.
        self.play_t(FadeOut(cap), q.animate.scale(0.5).to_edge(UP, buff=0.9)
                    .set_opacity(0.5), run_time=2.0)
        title = Text("The Geometry of Hidden Things", font_size=40,
                     gradient=(HEAT, HIDDEN))
        cite = Text("Bryan W. Roberts — “Heat as a gauge connection”",
                    font_size=20, color=INK).next_to(title, DOWN, buff=0.5)
        cite2 = Text("arXiv:2503.08753 (2025)  ·  London School of Economics",
                     font_size=18, color=DIM).next_to(cite, DOWN, buff=0.2)
        self.play_t(FadeIn(title, scale=0.8), FadeOut(q), run_time=2.0)
        self.play_t(FadeIn(cite, shift=UP * 0.2), FadeIn(cite2, shift=UP * 0.2),
                    run_time=2.0)
        add_breathe(title, amp=0.012, speed=0.7)
        self.wait_until(305.5)
        title.clear_updaters()
        self.play_t(FadeOut(title), FadeOut(cite), FadeOut(cite2), run_time=2.0)
