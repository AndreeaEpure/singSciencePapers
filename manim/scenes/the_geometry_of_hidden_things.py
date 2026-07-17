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
    """Layered flame with a hot core, outer tongues, and ember wisps."""
    glow = soft_blob(ORIGIN, 0.9 * scale, HEAT, peak=0.09, layers=16)
    halo = soft_blob(ORIGIN, 0.55 * scale, FIRE_HOT, peak=0.13, layers=10)

    outer = flame_shape(HEAT, h=1.0 * scale)
    outer.stretch(1.08, 0)
    outer.stretch(1.10, 1)

    inner = flame_shape(FIRE_HOT, h=0.60 * scale).shift(DOWN * 0.03 * scale)
    inner.stretch(0.86, 0)
    inner.stretch(0.92, 1)

    core = Circle(radius=0.11 * scale, color=WHITE, fill_opacity=0.85,
                  stroke_width=0).move_to(DOWN * 0.06 * scale)
    core2 = Circle(radius=0.20 * scale, color=FIRE_HOT, fill_opacity=0.45,
                   stroke_width=0).move_to(DOWN * 0.04 * scale)

    wisps = VGroup()
    for dx, dy, r in (
        (-0.20, 0.22, 0.05),
        (0.18, 0.34, 0.045),
        (-0.34, 0.08, 0.04),
        (0.30, 0.16, 0.038),
    ):
        wisps.add(Circle(radius=r * scale, color=FIRE_HOT, fill_opacity=0.34,
                         stroke_width=0).move_to(np.array([dx * scale, dy * scale, 0])))

    embers = VGroup()
    for dx, dy, rr in (
        (-0.18, -0.10, 0.025),
        (0.16, -0.14, 0.022),
        (-0.04, -0.22, 0.018),
    ):
        embers.add(Circle(radius=rr * scale, color=HEAT, fill_opacity=0.55,
                          stroke_width=0).move_to(np.array([dx * scale, dy * scale, 0])))

    return VGroup(glow, halo, outer, inner, wisps, embers, core2, core).move_to(pos)


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
    body = RoundedRectangle(width=1.8, height=0.96, corner_radius=0.10,
                            stroke_color=STEEL, stroke_width=2.7,
                            fill_color="#11130f", fill_opacity=0.92)
    body_inner = RoundedRectangle(width=1.58, height=0.74, corner_radius=0.07,
                                  stroke_color="#2f3540", stroke_width=1.2,
                                  fill_color="#191c16", fill_opacity=1)
    body_inner.move_to(body)

    # Head and rod sit inside a darker chamber with small mechanical accents.
    hx = -0.36 + extend * 0.58
    head = RoundedRectangle(width=0.48, height=0.72, corner_radius=0.06,
                            fill_color=WORK, fill_opacity=1,
                            stroke_color=interpolate_color(ManimColor(WORK), WHITE, 0.25),
                            stroke_width=1.4).move_to([hx, 0, 0])
    head_band = Rectangle(width=0.48, height=0.12, stroke_width=0,
                          fill_color="#8a6c2f", fill_opacity=0.95).move_to([hx, 0.20, 0])
    head_band2 = head_band.copy().move_to([hx, -0.20, 0])

    rod = Line([hx + 0.24, 0, 0], [1.72, 0, 0], stroke_color=STEEL,
               stroke_width=6.5)
    rod2 = Line([hx + 0.24, 0, 0], [1.72, 0, 0], stroke_color="#5f6876",
                stroke_width=2.2)
    knob = Circle(radius=0.11, color=WORK, fill_opacity=1, stroke_width=1.1,
                  stroke_color=interpolate_color(ManimColor(WORK), WHITE, 0.2)
                  ).move_to([1.78, 0, 0])
    crank = Circle(radius=0.20, color="#d6d0bc", fill_opacity=0.0,
                   stroke_width=2.0, stroke_color=STEEL).move_to([1.62, 0, 0])
    port = Dot([-0.56, 0, 0], radius=0.05, color="#606873")
    bolts = VGroup(*[
        Dot(p, radius=0.02, color="#7f8793")
        for p in ([[-0.73, 0.33, 0], [-0.73, -0.33, 0], [0.73, 0.33, 0], [0.73, -0.33, 0]])
    ])
    grp = VGroup(body, body_inner, port, bolts, head, head_band, head_band2,
                 rod, rod2, crank, knob).move_to(pos)
    return grp, head, rod


def equals_post(pos, color=WORK):
    """An '=' sign that doubles as a little fence post."""
    top = Line(LEFT * 0.18, RIGHT * 0.18, stroke_width=4, color=color)
    bot = Line(LEFT * 0.18, RIGHT * 0.18, stroke_width=4, color=color)
    top.shift(UP * 0.09)
    bot.shift(DOWN * 0.09)
    return VGroup(top, bot).move_to(pos)


def bproj(u, v, h=0.0, cx=-1.4, base_y=-1.4):
    """Oblique 3D->2D projection of a base point (u,v) at fibre height h,
    for drawing the gauge bundle in perspective."""
    return np.array([cx + u + 0.42 * v, base_y + 0.34 * v + h, 0.0])


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
            (np.array([0.0, 0.0, 0]), 5.8, DIM),
        ):
            blob = soft_blob(pos, r, col, peak=0.03, layers=30)
            blob.drift = np.array([random.uniform(-0.02, 0.02),
                                   random.uniform(-0.012, 0.012), 0])
            blob.add_updater(lambda m, dt: m.shift(m.drift * dt))
            nebulae.add(blob)

        motes = VGroup()
        for _ in range(54):
            depth = random.random()
            dot = Circle(radius=0.018 + 0.05 * depth,
                        color=random.choice([HEAT, HIDDEN, COOL, DIM]),
                        fill_opacity=0.05 + 0.12 * depth, stroke_width=0)
            dot.move_to([random.uniform(-7, 7), random.uniform(-4.2, 4.2), 0])
            dot.drift = np.array([random.uniform(-0.04, 0.04),
                                  0.015 + 0.055 * depth, 0])

            def upd(m, dt):
                m.shift(m.drift * dt)
                if m.get_center()[1] > 4.6:
                    m.shift(DOWN * 9.2)

            dot.add_updater(upd)
            motes.add(dot)

        bokeh = VGroup()
        for _ in range(7):
            b = soft_blob([random.uniform(-7, 7), random.uniform(-4, 4), 0],
                          random.uniform(0.9, 1.6),
                          random.choice([HEAT, HIDDEN, COOL]), peak=0.05,
                          layers=20)
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

        # Opening beat (~4-9s, sparse audio): faint fragments of two centuries
        # of thermodynamic arithmetic drift up, so it isn't dead air.
        frags = VGroup(*[
            Text(s, font_size=sz, color=DIM).move_to(
                [random.uniform(-5.2, 5.2), random.uniform(-2.7, -0.4), 0])
            for s, sz in (("Q = W", 26), ("ΔU = Q − W", 24), ("dS = đQ / T", 24),
                          ("PV = nRT", 26), ("η = 1 − Tc / Th", 22),
                          ("W = ∮ P dV", 24), ("dU = T dS − P dV", 22))])
        self.play_t(LaggedStart(*[FadeIn(fr, shift=UP * 0.3) for fr in frags],
                    lag_ratio=0.18), run_time=2.8)
        self.play_t(frags.animate.shift(UP * 0.4).set_opacity(0.22),
                    run_time=1.4)

        # A ledger of heat = work: equal-sign fence posts across a landscape.
        ground, f = landscape([(-2.5, 0.5, 1.1), (1.8, -0.4, 1.0)],
                              x_range=(-6, 6), color=DIM, stroke_width=2)
        ground.shift(DOWN * 1.2)
        posts = VGroup()
        for x in np.arange(-5, 5.1, 1.25):
            posts.add(equals_post([x, f(x) - 1.2 + 0.35, 0]))
        self.wait_until(9.0)
        cap = self.swap(cap, self.cap_text("the arithmetic balanced.", 30),
                        FadeOut(frags), Create(ground), run_time=1.5)
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
        self.play_t(FadeOut(ground), grid.animate.set_stroke(opacity=0.18),
                    run_time=1.5)

        # Instrumental stretch (~48-62s): keep it moving. The freshly-arrived
        # map comes alive -- a lone surveyor's dot traces the unnamed country
        # while the flat grid warps into curved coordinates (the hidden
        # geometry, quietly emerging).
        survey = Dot(LEFT * 5.4 + DOWN * 1.2, color=COOL, radius=0.07)
        sglow = Circle(radius=0.16, color=COOL, fill_opacity=0.3, stroke_width=0)
        sglow.add_updater(lambda m: m.move_to(survey))
        strail = trail_group(survey, color=HIDDEN, segments=22, radius=0.04)
        self.play_t(FadeIn(survey), FadeIn(sglow), run_time=1.2)
        self.add(strail)

        def warp(p):
            x, y, z = p
            return np.array([x, y + 0.55 * np.exp(-((x + 1.5) ** 2) / 3.0)
                             - 0.45 * np.exp(-((x - 2.2) ** 2) / 2.4), z])

        self.play_t(grid.animate.apply_function(warp),
                    survey.animate.move_to(LEFT * 1.4 + UP * 0.5),
                    run_time=4.2, rate_func=smooth)
        contour = Circle(radius=0.5, color=HIDDEN, stroke_width=2).move_to(
            survey.get_center())
        self.play_t(Broadcast(contour, focal_point=survey.get_center(), n_mobs=3),
                    survey.animate.move_to(RIGHT * 1.8 + DOWN * 0.2),
                    run_time=3.6, rate_func=linear)
        self.play_t(survey.animate.move_to(RIGHT * 3.4 + UP * 0.3),
                    run_time=2.8, rate_func=smooth)
        strail.clear_updaters()
        sglow.clear_updaters()
        self.play_t(FadeOut(survey), FadeOut(sglow), FadeOut(strail),
                    grid.animate.set_stroke(opacity=0.09), run_time=1.4)
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
        eng, head, rod = piston(pos=LEFT * 3.6 + UP * 0.7)
        eng.scale(0.82)
        cap = self.enter_cap(cap, FadeIn(eng, shift=RIGHT * 0.3), run_time=1.5)
        self.play_t(head.animate.shift(RIGHT * 0.34), rod.animate.shift(RIGHT * 0.34),
                    run_time=0.6)
        self.play_t(head.animate.shift(LEFT * 0.34), rod.animate.shift(LEFT * 0.34),
                    run_time=0.6)

        # A P-V diagram: work is exactly the area the cycle encloses.
        axes = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], x_length=3.3,
                    y_length=2.5, axis_config={"stroke_color": STEEL,
                    "stroke_width": 2, "include_ticks": False, "include_tip": True})
        axes.move_to(RIGHT * 3.0 + DOWN * 0.3)
        vlab = Text("V", font_size=20, color=STEEL).next_to(axes.x_axis.get_end(),
                                                            DR, buff=0.06)
        plab = Text("P", font_size=20, color=STEEL).next_to(axes.y_axis.get_end(),
                                                            UL, buff=0.06)

        self.wait_until(135.0)
        cap2 = self.cap_text("Heat... leaves fingerprints.", 29)
        heat_cloud = VGroup(*[Dot(eng.get_center()
                              + np.array([random.uniform(-0.3, 0.3),
                                          random.uniform(-0.55, -0.15), 0]),
                              radius=random.uniform(0.03, 0.07), color=HEAT)
                              for _ in range(22)])
        cap = self.swap(cap, cap2, FadeIn(axes), FadeIn(vlab), FadeIn(plab),
                        FadeIn(heat_cloud, scale=0.4), run_time=1.5)
        self.play_t(*[d.animate.shift(np.array([random.uniform(-0.7, 0.8),
                                                random.uniform(-0.5, 0.5), 0]))
                      .set_opacity(random.uniform(0.3, 0.7))
                      for d in heat_cloud], run_time=1.5)

        self.wait_until(139.0)
        cyc = ParametricFunction(
            lambda t: axes.c2p(2 + 1.15 * np.cos(t), 2 + 0.95 * np.sin(t)),
            t_range=[0, TAU], color=WORK, stroke_width=3)
        cap = self.swap(cap, self.cap_text("One can move a piston.", 29),
                        Indicate(eng, color=WORK, scale_factor=1.08), run_time=1.5)
        self.play_t(Create(cyc), run_time=1.4)

        self.wait_until(143.0)
        area = cyc.copy().set_fill(WORK, 0.16).set_stroke(width=0)
        wlbl = Text("work = ∮ P dV", font_size=22, color=WORK).next_to(axes, DOWN,
                                                                      buff=0.2)
        cap = self.swap(cap, self.cap_text("The other slips quietly through every bargain nature made.", 23),
                        heat_cloud.animate.set_opacity(0.4), FadeIn(area),
                        FadeIn(wlbl), run_time=1.6)

        self.wait_until(149.0)
        cap2 = self.cap_text("Different voices...", 30)
        dW = Text("đW", font_size=28, color=WORK).move_to(LEFT * 3.6 + DOWN * 1.7)
        dQ = Text("đQ", font_size=28, color=HEAT).next_to(dW, RIGHT, buff=0.55)
        cap = self.swap(cap, cap2, FadeIn(dW, shift=UP * 0.2),
                        FadeIn(dQ, shift=UP * 0.2), run_time=1.6)

        self.wait_until(153.0)
        # ...but they sum to a state function: đQ + đW = dU.
        ident = Text("đQ + đW = dU", font_size=28, color=INK).move_to(
            LEFT * 3.6 + DOWN * 1.7)
        cap = self.swap(cap, self.cap_text("Same conversation.", 30),
                        ReplacementTransform(VGroup(dW, dQ), ident), run_time=1.5)
        self.wait_until(157.0)
        self.play_t(FadeOut(eng), FadeOut(heat_cloud), FadeOut(axes),
                    FadeOut(vlab), FadeOut(plab), FadeOut(cyc), FadeOut(area),
                    FadeOut(wlbl), FadeOut(ident), run_time=1.4)
        self._cap = cap

    # ----------------------------------------------------------------
    def gauge_theory(self):
        # 3b1b-style construction: a bundle over work-configuration space, a
        # closed base cycle whose lift does NOT close (the net heat = holonomy
        # = curvature over the enclosed area, by Stokes).
        R, KA = 1.7, 1.15 / TAU

        self.wait_until(157.2)
        cap = self.cap_text("Gauge theory.   Funny phrase.", 28)
        # Base space: a disk of work configurations, in perspective.
        base_disk = VGroup()
        for rr in np.linspace(0.55, R + 0.35, 4):
            base_disk.add(ParametricFunction(
                lambda t, rr=rr: bproj(rr * np.cos(t), rr * np.sin(t)),
                t_range=[0, TAU], color=DIM, stroke_width=1, stroke_opacity=0.32))
        for a in np.linspace(0, TAU, 8, endpoint=False):
            base_disk.add(Line(bproj(0, 0), bproj((R + 0.35) * np.cos(a),
                          (R + 0.35) * np.sin(a)), color=DIM, stroke_width=1,
                          stroke_opacity=0.28))
        base_lbl = Text("work configurations", font_size=20, color=WORK).move_to(
            bproj(0, -R - 0.55) + DOWN * 0.15)
        cap = self.enter_cap(cap, Create(base_disk), FadeIn(base_lbl),
                             run_time=1.8)

        self.wait_until(161.1)
        cap2 = self.cap_text("Sounds like something you'd borrow from an old mechanic.", 23)
        # Fibres rise from the base -- the hidden heat coordinate.
        fibres = VGroup(*[
            Line(bproj(R * np.cos(a), R * np.sin(a), 0),
                 bproj(R * np.cos(a), R * np.sin(a), 1.55), color=HIDDEN,
                 stroke_width=1.4, stroke_opacity=0.4)
            for a in np.linspace(0, TAU, 10, endpoint=False)])
        loop = ParametricFunction(lambda t: bproj(R * np.cos(t), R * np.sin(t)),
                                  t_range=[0, TAU], color=WORK, stroke_width=4)
        cap = self.swap(cap, cap2, LaggedStart(*[
                        GrowFromPoint(f, bproj(0, 0)) for f in fibres],
                        lag_ratio=0.05), run_time=1.6)
        self.play_t(Create(loop), run_time=1.0)

        self.wait_until(165.7)
        cap2 = self.cap_text("It's how physicists keep track of things that refuse to stand still.", 22)
        start_dot = Dot(bproj(R, 0, 0), color=WORK, radius=0.08)
        th = ValueTracker(0.0)
        lift = always_redraw(lambda: ParametricFunction(
            lambda t: bproj(R * np.cos(t), R * np.sin(t), KA * t),
            t_range=[0, max(1e-3, th.get_value())], color=HEAT, stroke_width=4))
        bead = always_redraw(lambda: Dot(
            bproj(R * np.cos(th.get_value()), R * np.sin(th.get_value()),
                  KA * th.get_value()), color=HEAT, radius=0.09))
        cap = self.swap(cap, cap2, FadeIn(start_dot), run_time=1.4)
        self.add(lift, bead)
        self.play_t(th.animate.set_value(TAU), run_time=3.6,
                    rate_func=rate_functions.ease_in_out_sine)
        # Freeze the lifted path and the endpoint that came back higher.
        lift_static = ParametricFunction(
            lambda t: bproj(R * np.cos(t), R * np.sin(t), KA * t),
            t_range=[0, TAU], color=HEAT, stroke_width=4)
        end_dot = Dot(bproj(R, 0, KA * TAU), color=HEAT, radius=0.09)
        self.remove(lift, bead)
        self.add(lift_static, end_dot)

        self.wait_until(172.7)
        cap2 = self.cap_text("Maybe the universe has never hidden its secrets.", 25)
        # The gap that didn't close -- the holonomy, the net heat.
        gap = DashedLine(bproj(R, 0, 0), bproj(R, 0, KA * TAU), color=WHITE,
                         stroke_width=3)
        brace = Brace(gap, direction=RIGHT, color=INK)
        hol = Text("∮ đQ", font_size=32, color=HEAT).next_to(brace, RIGHT, buff=0.14)
        hol_sub = Text("=  net heat  (holonomy)", font_size=20, color=INK).next_to(
            hol, RIGHT, buff=0.18)
        cap = self.swap(cap, cap2, Create(gap), GrowFromCenter(brace),
                        FadeIn(hol), FadeIn(hol_sub), run_time=1.8)

        self.wait_until(176.3)
        cap2 = self.cap_text("Maybe we've been reading the shadow...", 27)
        # The base loop IS the shadow of the lifted path: it closes, hiding the
        # gap. Drop projection lines from the object (lift) to its shadow (loop).
        drops = VGroup(*[
            DashedLine(bproj(R * np.cos(a), R * np.sin(a), KA * a),
                       bproj(R * np.cos(a), R * np.sin(a), 0), color=STEEL,
                       stroke_width=1.2, stroke_opacity=0.5)
            for a in np.linspace(0.3, TAU - 0.2, 7)])
        shadow_lbl = Text("the shadow (loop) closes", font_size=19,
                          color=STEEL).to_edge(RIGHT, buff=0.7).shift(UP * 0.5)
        cap = self.swap(cap, cap2, LaggedStart(*[Create(d) for d in drops],
                        lag_ratio=0.1), Indicate(loop, color=WORK),
                        FadeIn(shadow_lbl), run_time=1.8)

        self.wait_until(180.0)
        obj_lbl = Text("the object (lift) does not", font_size=19,
                       color=HEAT).next_to(shadow_lbl, DOWN, buff=0.22).align_to(
            shadow_lbl, LEFT)
        cap = self.swap(cap, self.cap_text("instead of the object.", 29),
                        Indicate(lift_static, color=HEAT), FadeIn(obj_lbl),
                        run_time=1.6)

        self.wait_until(185.0)
        cap2 = self.cap_text("Alright...   alright...   alright...", 29)
        # Stokes: the gap equals the curvature over the enclosed area.
        area = ParametricFunction(lambda t: bproj(R * np.cos(t), R * np.sin(t)),
                                  t_range=[0, TAU], color=HIDDEN)
        area.set_fill(HIDDEN, opacity=0.16).set_stroke(width=0)
        stokes = Text("=  ∬ F   (curvature)", font_size=22, color=HIDDEN).next_to(
            hol_sub, DOWN, buff=0.25).align_to(hol_sub, LEFT)
        cap = self.swap(cap, cap2, FadeIn(area), FadeIn(stokes), run_time=1.5)
        bundle = VGroup(base_disk, base_lbl, fibres, loop, start_dot, end_dot,
                        lift_static, gap, brace, hol, hol_sub, drops, shadow_lbl,
                        obj_lbl, area, stokes)

        self.wait_until(191.0)
        self.play_t(FadeOut(bundle), run_time=1.5)
        self._cap = cap

    # ----------------------------------------------------------------
    def entropy_perspective(self):
        self.wait_until(195.0)
        cap = self.cap_text("Entropy...", 31)
        # Microstates scattered on axes -- from close up, noise.
        axes = Axes(x_range=[-3.4, 3.4, 1], y_range=[0, 2.4, 1], x_length=7.2,
                    y_length=2.6, axis_config={"stroke_color": DIM,
                    "stroke_width": 1.5, "include_ticks": False,
                    "include_tip": False})
        axes.move_to(DOWN * 0.5)

        def macro(x):
            return 1.9 * np.exp(-(x ** 2) / 2.2)

        pts = VGroup()
        for _ in range(70):
            x = random.uniform(-3.2, 3.2)
            y = max(0.03, macro(x) + random.uniform(-0.85, 0.85))
            pts.add(Dot(axes.c2p(x, y), radius=0.05,
                        color=random.choice([HEAT, COOL, DIM])))
        cap = self.enter_cap(cap, FadeIn(axes),
                             LaggedStart(*[FadeIn(p) for p in pts],
                                         lag_ratio=0.01), run_time=1.8)

        self.wait_until(199.0)
        cap = self.swap(cap, self.cap_text("Perhaps it was never disorder.", 29),
                        run_time=1.5)
        self.wait_until(204.0)
        slabel = Text("S = k log W", font_size=24, color=INK).to_corner(UR, buff=0.9)
        cap = self.swap(cap, self.cap_text("Perhaps... it's perspective.", 29),
                        FadeIn(slabel), run_time=1.5)

        self.wait_until(209.0)
        cap = self.swap(cap, self.cap_text("Stand too close...", 30),
                        pts.animate.scale(1.5), run_time=1.6)
        self.wait_until(214.5)
        cap = self.swap(cap, self.cap_text("Life looks like chaos.", 29), run_time=1.4)

        self.wait_until(218.0)
        cap2 = self.cap_text("Step back...", 30)
        # Step back: microstates snap onto the smooth macrostate distribution.
        cap = self.swap(cap, cap2, pts.animate.scale(1 / 1.5), run_time=1.2)
        xs = np.linspace(-3.2, 3.2, len(pts))
        self.play_t(*[p.animate.move_to(axes.c2p(x, macro(x))).set_color(GEO)
                      for p, x in zip(pts, xs)], run_time=2.0)

        self.wait_until(221.0)
        curve = axes.plot(macro, x_range=[-3.2, 3.2], color=GEO, stroke_width=3)
        cap = self.swap(cap, self.cap_text("Geometry begins to rhyme.", 28),
                        Create(curve), run_time=1.6)

        self.wait_until(227.9)
        cap2 = self.cap_text("Even a black hole...", 29)
        # Two systems, one entropy geometry: black hole S=A/4, engine dS=đQ/T.
        hole = VGroup(soft_blob(LEFT * 3.6 + DOWN * 0.3, 0.7, HIDDEN, peak=0.14,
                                layers=14),
                      Circle(radius=0.32, color=BLACK, fill_opacity=1,
                             stroke_color=HIDDEN, stroke_width=2)
                      .move_to(LEFT * 3.6 + DOWN * 0.3))
        bh_law = Text("S = A / 4", font_size=20, color=HIDDEN).move_to(
            LEFT * 3.6 + DOWN * 1.55)
        cap = self.swap(cap, cap2, FadeOut(pts), FadeOut(curve), FadeOut(axes),
                        FadeOut(slabel), FadeIn(hole, scale=0.5), FadeIn(bh_law),
                        run_time=1.6)
        self.wait_until(231.0)
        cap2 = self.cap_text("might be speaking the very same language as a steam engine.", 22)
        eng, _, _ = piston(pos=RIGHT * 3.6 + DOWN * 0.3)
        eng.scale(0.8)
        eng_law = Text("dS = đQ / T", font_size=20, color=HEAT).move_to(
            RIGHT * 3.6 + DOWN * 1.55)
        link = Text("same geometry", font_size=20, color=GEO).move_to(DOWN * 0.35)
        cap = self.swap(cap, cap2, FadeIn(eng, shift=LEFT * 0.3),
                        FadeIn(eng_law), FadeIn(link), run_time=1.8)
        self.wait_until(238.0)
        self.play_t(FadeOut(hole), FadeOut(bh_law), FadeOut(eng),
                    FadeOut(eng_law), FadeOut(link), run_time=1.5)
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
