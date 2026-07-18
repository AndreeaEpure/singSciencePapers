"""Visuals for "Everything Is Made of Tiny Things" (4:30 kids' song, timed to vocals).

A children's science song about atoms: your hand is mostly empty space; zoom
past dust and sand to another country where everything is built from tiny
bricks (atoms); the nucleus (protons + neutrons) with electrons in fuzzy
clouds -- NOT planet-like orbits (the song says so); the football-stadium /
marble-on-the-50-yard-line scale; elements by proton count (H, C, Au); same
alphabet, different poetry; and a wink toward the strange quantum rules to come.

Anchored to Rutherford's mostly-empty nuclear atom (1911).

Render (from manim/):
    manim -pql scenes/everything_tiny_things.py EverythingTinyThings
    manim -pqh --fps 30 scenes/everything_tiny_things.py EverythingTinyThings

Timing anchored on a Whisper pass; the sung choruses (78-112s, 200-209s) and
a couple of instrumental gaps are estimated between solid anchors. An
instrumental tail (~250-270s) holds the citation card. Captions crossfade
(never Transform between different strings).
"""

import random
from pathlib import Path

import numpy as np
from manim import *

MP3 = (Path(__file__).resolve().parents[2] / "songs"
       / "Everything Is Made of Tiny Things"
       / "ep 111 kids_ Everything Is Made of Tiny Things.mp3")

BG = "#141a2e"
ELECTRON = "#4fd1ff"   # cyan
PROTON = "#ff6b6b"     # coral red
NEUTRON = "#b8c0cc"    # soft grey
GOLD = "#ffd24a"
LIFE = "#5bd6a0"       # green - carbon / life
HYDRO = "#cfe8ff"      # pale blue - hydrogen
WARM = "#ffb454"       # firefly warmth
STARC = "#fff2b0"      # star
INK = "#f2ecdd"        # cream caption text
DIM = "#8b93a7"
random.seed(5)


# --------------------------------------------------------------------------
# Atmosphere / motion helpers
# --------------------------------------------------------------------------

def soft_blob(pos, radius, color, peak=0.05, layers=22):
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


def sphere3d(radius, color, pos=ORIGIN, light=(-0.5, 0.6, 0), layers=18):
    lu = np.array(light, dtype=float)
    lu = lu / (np.linalg.norm(lu) + 1e-9)
    dark = interpolate_color(ManimColor(color), ManimColor("#070707"), 0.55)
    lite = interpolate_color(ManimColor(color), WHITE, 0.5)
    g = VGroup()
    for i in range(layers):
        frac = i / (layers - 1)
        r = radius * (1 - 0.98 * frac)
        off = lu * radius * frac * 0.5
        col = interpolate_color(dark, lite, frac ** 0.85)
        g.add(Circle(radius=max(r, 0.005), color=col, fill_opacity=1,
                     stroke_width=0).move_to(pos + off))
    g.add(Circle(radius=radius * 0.16, color=WHITE, fill_opacity=0.7,
                 stroke_width=0).move_to(pos + lu * radius * 0.5))
    return g


def trail_group(mob, color=ELECTRON, segments=14, radius=0.04):
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


def add_drift(mob, amp=0.06, speed=1.0):
    mob.d_t = random.uniform(0, TAU)
    mob.d_prev = np.zeros(3)

    def upd(m, dt):
        m.d_t += dt
        off = np.array([0.6 * np.sin(0.6 * speed * m.d_t),
                        np.sin(speed * m.d_t), 0]) * amp
        m.shift(off - m.d_prev)
        m.d_prev = off

    mob.add_updater(upd)


def add_breathe(mob, amp=0.04, speed=1.0):
    mob.b_t = random.uniform(0, TAU)
    mob.b_prev = 1.0

    def upd(m, dt):
        m.b_t += dt
        target = 1 + amp * np.sin(speed * m.b_t)
        m.scale(target / m.b_prev)
        m.b_prev = target

    mob.add_updater(upd)


def add_spin(mob, rate=0.6):
    mob.add_updater(lambda m, dt: m.rotate(rate * dt))


# --------------------------------------------------------------------------
# Atom building blocks
# --------------------------------------------------------------------------

def nucleus(n_p=6, n_n=6, center=ORIGIN, r=0.11, glow=True):
    """A packed cluster of protons (coral) and neutrons (grey)."""
    parts = VGroup()
    if glow:
        parts.add(soft_blob(center, r * 3.4, PROTON, peak=0.11, layers=12))
    kinds = [PROTON] * n_p + [NEUTRON] * n_n
    random.shuffle(kinds)
    total = max(1, len(kinds))
    golden = PI * (3 - np.sqrt(5))
    for i, col in enumerate(kinds):
        rad = r * 1.75 * np.sqrt(i + 0.5) / np.sqrt(total) * np.sqrt(total) * 0.62
        ang = i * golden
        p = center + rad * np.array([np.cos(ang), np.sin(ang), 0])
        parts.add(sphere3d(r, col, pos=p, layers=10))
    return parts


def electron_cloud(center=ORIGIN, radius=1.5, n=80, color=ELECTRON,
                   squish=0.85):
    """A fuzzy probability cloud of electron specks -- density peaks partway
    out, thins toward the edge. The honest picture: no orbits."""
    g = VGroup()
    for _ in range(n):
        rr = radius * (0.22 + 0.78 * random.random() ** 0.6)
        ang = random.uniform(0, TAU)
        p = center + rr * np.array([np.cos(ang), squish * np.sin(ang), 0])
        g.add(Dot(p, radius=random.uniform(0.012, 0.032), color=color,
                  fill_opacity=random.uniform(0.22, 0.7)))
    return g


def orbit_electron(center, a, b, color=ELECTRON):
    """A single electron on an elliptical orbit (the OLD planetary picture)."""
    ellipse = Ellipse(width=2 * a, height=2 * b, color=color, stroke_width=1.5,
                      stroke_opacity=0.5).move_to(center)
    e = Dot(color=color, radius=0.07)
    tr = ValueTracker(random.uniform(0, TAU))

    def upd(m):
        t = tr.get_value()
        m.move_to(center + np.array([a * np.cos(t), b * np.sin(t), 0]))

    e.add_updater(upd)
    upd(e)
    return VGroup(ellipse, e), tr


def dot_outline(vmob, n=44, color=INK, r=0.03):
    """Represent a shape as a string of little dots -- 'made of tiny things'."""
    return VGroup(*[Dot(vmob.point_from_proportion((i % n) / n), radius=r,
                        color=color) for i in range(n)])


def scatter_atoms(region_center, w, h, n=26, color=ELECTRON):
    return VGroup(*[
        Dot(region_center + np.array([random.uniform(-w / 2, w / 2),
                                      random.uniform(-h / 2, h / 2), 0]),
            radius=random.uniform(0.02, 0.045), color=color,
            fill_opacity=random.uniform(0.4, 0.9))
        for _ in range(n)])


# ---- simple kid-friendly icon outlines (rendered as dot-outlines) ----

def star_shape(rad=0.55, color=STARC):
    return Star(n=5, outer_radius=rad, inner_radius=rad * 0.44, color=color)


def heart_shape(scale=0.42, color=PROTON):
    return ParametricFunction(
        lambda t: scale * np.array([
            16 * np.sin(t) ** 3,
            13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t)
            - np.cos(4 * t), 0]) / 16,
        t_range=[0, TAU], color=color)


def fish_shape(s=0.7, color=ELECTRON):
    m = VMobject(color=color, stroke_width=3)
    m.set_points_smoothly([
        s * np.array([-0.9, 0, 0]), s * np.array([-1.3, 0.35, 0]),
        s * np.array([-1.3, -0.35, 0]), s * np.array([-0.9, 0, 0]),
        s * np.array([0.2, 0.5, 0]), s * np.array([1.1, 0.05, 0]),
        s * np.array([0.2, -0.5, 0]), s * np.array([-0.9, 0, 0]),
    ])
    return m


def tree_shape(s=0.7, color=LIFE):
    top = Triangle(color=color, stroke_width=3).scale(s)
    trunk = Rectangle(width=0.2 * s, height=0.4 * s, color="#a9743a",
                      stroke_width=3).next_to(top, DOWN, buff=0)
    return VGroup(top, trunk)


def mountain_shape(s=0.8, color=DIM):
    return Polygon(s * np.array([-0.9, -0.5, 0]), s * np.array([0, 0.7, 0]),
                   s * np.array([0.9, -0.5, 0]), color=color, stroke_width=3)


def pizza_shape(s=0.8, color=GOLD):
    wedge = Polygon(s * np.array([-0.7, -0.5, 0]), s * np.array([0.7, -0.5, 0]),
                    s * np.array([0, 0.8, 0]), color=color, stroke_width=3)
    return wedge


def whale_shape(s=0.9, color=ELECTRON):
    m = VMobject(color=color, stroke_width=3)
    m.set_points_smoothly([
        s * np.array([-1.2, 0.1, 0]), s * np.array([-1.55, 0.45, 0]),
        s * np.array([-1.5, -0.05, 0]), s * np.array([-1.2, -0.35, 0]),
        s * np.array([0.4, -0.55, 0]), s * np.array([1.3, -0.1, 0]),
        s * np.array([0.6, 0.35, 0]), s * np.array([-1.2, 0.1, 0]),
    ])
    return m


def cloud_shape(s=0.8, color="#c7d2e6"):
    circs = VGroup(*[
        Circle(radius=r * s, color=color, stroke_width=3).move_to(s * np.array(p))
        for p, r in (([-0.7, 0, 0], 0.45), ([0, 0.2, 0], 0.6),
                     ([0.7, 0, 0], 0.45), ([0, -0.1, 0], 0.5))])
    return circs


def stadium(pos=ORIGIN, w=6.0, h=3.2, color=LIFE):
    """An american-football field: rounded pitch + yard lines + goal ends."""
    field = RoundedRectangle(width=w, height=h, corner_radius=0.5,
                             stroke_color=color, stroke_width=2.5,
                             fill_color="#1a3a2a", fill_opacity=0.45).move_to(pos)
    lines = VGroup()
    for i in range(-4, 5):
        x = pos[0] + i * (w - 1.0) / 10
        lines.add(Line([x, pos[1] - h / 2 + 0.35, 0], [x, pos[1] + h / 2 - 0.35, 0],
                       color=WHITE, stroke_width=1, stroke_opacity=0.35))
    mid = Line([pos[0], pos[1] - h / 2 + 0.3, 0], [pos[0], pos[1] + h / 2 - 0.3, 0],
               color=WHITE, stroke_width=2, stroke_opacity=0.6)
    return VGroup(field, lines, mid)


def element_tile(symbol, z, color, pos=ORIGIN):
    box = RoundedRectangle(width=1.15, height=1.25, corner_radius=0.1,
                           stroke_color=color, stroke_width=2.5,
                           fill_color=BG, fill_opacity=0.85).move_to(pos)
    num = Text(str(z), font_size=18, color=DIM).move_to(
        box.get_corner(UL) + RIGHT * 0.22 + DOWN * 0.2)
    sym = Text(symbol, font_size=40, color=color).move_to(box.get_center()
                                                          + DOWN * 0.08)
    return VGroup(box, num, sym)


class EverythingTinyThings(Scene):
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

    def cap_text(self, s, size=30):
        return Text(s, font_size=size, color=INK).to_edge(UP, buff=0.7)

    # ----------------------------------------------------------------
    def construct(self):
        if MP3.exists():
            self.add_sound(str(MP3))
        self.t = 0.0
        self.add_ambient_background()
        self.hand_and_empty_space()   # 0:00 - 0:42
        self.everything_is_atoms()    # 0:42 - 1:03
        self.stack_them_up()          # 1:03 - 1:18
        self.chorus_dance()           # 1:18 - 1:52
        self.the_nucleus()            # 1:52 - 2:26
        self.stadium_scale()          # 2:26 - 2:54
        self.elements()               # 2:54 - 3:20
        self.final_chorus()           # 3:20 - 3:48
        self.outro()                  # 3:48 - 4:30

    def add_ambient_background(self):
        """A warm night-sky feel: soft colored glows + drifting star-motes."""
        self.camera.background_color = BG
        nebulae = VGroup()
        for pos, r, col in (
            (np.array([-5.0, 2.0, 0]), 4.0, ELECTRON),
            (np.array([5.0, -2.0, 0]), 4.0, WARM),
            (np.array([3.0, 2.6, 0]), 2.6, GOLD),
            (np.array([-3.4, -2.6, 0]), 2.6, PROTON),
        ):
            blob = soft_blob(pos, r, col, peak=0.035, layers=24)
            blob.drift = np.array([random.uniform(-0.02, 0.02),
                                   random.uniform(-0.012, 0.012), 0])
            blob.add_updater(lambda m, dt: m.shift(m.drift * dt))
            nebulae.add(blob)
        motes = VGroup()
        for _ in range(46):
            depth = random.random()
            dot = Circle(radius=0.015 + 0.045 * depth,
                        color=random.choice([ELECTRON, WARM, STARC, GOLD]),
                        fill_opacity=0.05 + 0.13 * depth, stroke_width=0)
            dot.move_to([random.uniform(-7, 7), random.uniform(-4.2, 4.2), 0])
            dot.drift = np.array([random.uniform(-0.03, 0.03),
                                  0.015 + 0.05 * depth, 0])

            def upd(m, dt):
                m.shift(m.drift * dt)
                if m.get_center()[1] > 4.6:
                    m.shift(DOWN * 9.2)

            dot.add_updater(upd)
            motes.add(dot)
        self.add(nebulae, motes)

    # ----------------------------------------------------------------
    def hand_and_empty_space(self):
        title = Text("Everything Is Made of Tiny Things", font_size=42,
                     gradient=(ELECTRON, WARM))
        halo = Text("Everything Is Made of Tiny Things", font_size=42,
                    color=ELECTRON).set_opacity(0.14).scale(1.05).move_to(title)
        self.play_t(FadeIn(halo), Write(title), run_time=2.6)
        self.play_t(title.animate.scale(0.55).to_edge(UP, buff=0.5),
                    FadeOut(halo), run_time=1.2)

        # A cartoon hand.
        palm = RoundedRectangle(width=1.5, height=1.5, corner_radius=0.4,
                                fill_color="#e8b98f", fill_opacity=0.95,
                                stroke_color="#b98a5e", stroke_width=2)
        fingers = VGroup()
        for i, dx in enumerate((-0.5, -0.17, 0.17, 0.5)):
            f = RoundedRectangle(width=0.28, height=1.0 + 0.12 * (1 - abs(i - 1.5) / 2),
                                 corner_radius=0.13, fill_color="#e8b98f",
                                 fill_opacity=0.95, stroke_color="#b98a5e",
                                 stroke_width=2)
            f.next_to(palm.get_top(), UP, buff=-0.15).shift(RIGHT * dx)
            fingers.add(f)
        thumb = RoundedRectangle(width=0.28, height=0.7, corner_radius=0.13,
                                 fill_color="#e8b98f", fill_opacity=0.95,
                                 stroke_color="#b98a5e", stroke_width=2)
        thumb.rotate(0.9).next_to(palm.get_left(), UR, buff=-0.3)
        hand = VGroup(palm, fingers, thumb).move_to(DOWN * 0.4).scale(1.1)
        cap = self.cap_text("Take a look at your hand—  wiggle your fingers.", 27)
        cap = self.enter_cap(cap, FadeIn(hand, shift=UP * 0.3), FadeOut(title),
                             run_time=2.0)
        for _ in range(2):
            self.play_t(*[f.animate.rotate(0.12, about_point=f.get_bottom())
                          for f in fingers], run_time=0.5)
            self.play_t(*[f.animate.rotate(-0.12, about_point=f.get_bottom())
                          for f in fingers], run_time=0.5)
        self.wait_until(11.0)
        for _ in range(2):
            self.play_t(*[f.animate.rotate(0.1, about_point=f.get_bottom())
                          for f in fingers], run_time=0.45)
            self.play_t(*[f.animate.rotate(-0.1, about_point=f.get_bottom())
                          for f in fingers], run_time=0.45)

        self.wait_until(17.45)
        cap = self.swap(cap, self.cap_text("Looks pretty solid, don't it?", 29),
                        run_time=1.4)

        self.wait_until(21.71)
        cap2 = self.cap_text("But there's more empty space in there than stuff.", 25)
        # Zoom into the hand: it dissolves into a few sparse atoms in a big void.
        sparse = scatter_atoms(hand.get_center(), 4.0, 3.0, n=16, color=ELECTRON)
        cap = self.swap(cap, cap2, hand.animate.scale(3.2).set_opacity(0.0),
                        run_time=1.8)
        self.remove(hand)
        self.play_t(LaggedStart(*[FadeIn(a, scale=0.4) for a in sparse],
                    lag_ratio=0.06), run_time=1.6)

        self.wait_until(27.32)
        cap = self.swap(cap, self.cap_text("Way down past what your eyes can see,", 27),
                        run_time=1.5)
        self.wait_until(29.9)
        cap = self.swap(cap, self.cap_text("past dust, past grains of sand,", 28),
                        sparse.animate.scale(1.4), run_time=1.5)
        self.wait_until(32.86)
        cap = self.swap(cap, self.cap_text("past anything you've ever held—", 27),
                        run_time=1.4)

        self.wait_until(36.1)
        cap2 = self.cap_text("there's another country.", 30)
        # The sparse specks resolve into a field of little glowing atoms.
        atoms = VGroup(*[
            VGroup(soft_blob(p, 0.22, ELECTRON, peak=0.4, layers=8),
                   Dot(p, radius=0.06, color=ELECTRON))
            for p in [np.array([random.uniform(-5.5, 5.5),
                                random.uniform(-3, 2.4), 0]) for _ in range(22)]])
        cap = self.swap(cap, cap2, FadeOut(sparse),
                        LaggedStart(*[FadeIn(a, scale=0.3) for a in atoms],
                        lag_ratio=0.05), run_time=2.0)
        self.atoms_field = atoms
        self._cap = cap

    # ----------------------------------------------------------------
    def everything_is_atoms(self):
        self.wait_until(42.1)
        cap = self.cap_text("Everything you've ever touched—", 28)
        cap = self.enter_cap(cap, FadeOut(self.atoms_field), run_time=1.4)

        icons = [
            (mountain_shape(), "every mountain, every tree,"),
            (tree_shape(), None),
            (fish_shape(), "every puppy, every pizza,"),
            (pizza_shape(), None),
        ]
        # Show a little gallery of things.
        slots = [LEFT * 4.2, LEFT * 1.5, RIGHT * 1.5, RIGHT * 4.2]
        shown = VGroup()
        mtn = mountain_shape().move_to(slots[0] + DOWN * 0.3)
        tree = tree_shape().move_to(slots[1] + DOWN * 0.3)
        self.wait_until(44.24)
        cap = self.swap(cap, self.cap_text("every mountain, every tree,", 28),
                        FadeIn(mtn, shift=UP * 0.2), FadeIn(tree, shift=UP * 0.2),
                        run_time=1.4)
        shown.add(mtn, tree)

        self.wait_until(45.78)
        fish = fish_shape().move_to(slots[2] + DOWN * 0.3)
        pizza = pizza_shape().move_to(slots[3] + DOWN * 0.3)
        cap = self.swap(cap, self.cap_text("every puppy, every pizza,", 28),
                        FadeIn(fish, shift=UP * 0.2), FadeIn(pizza, shift=UP * 0.2),
                        run_time=1.4)
        shown.add(fish, pizza)
        self.wait_until(47.32)
        cap = self.swap(cap, self.cap_text("every fish out in the sea—", 28),
                        Indicate(fish, color=ELECTRON), run_time=1.4)

        self.wait_until(48.86)
        cap2 = self.cap_text("they're all built from little bricks,", 26)
        # Everything dissolves into clusters of atom-dots.
        atomized = VGroup()
        for ic in shown:
            atomized.add(scatter_atoms(ic.get_center(), 1.4, 1.4, n=18,
                                       color=random.choice([ELECTRON, WARM, GOLD, LIFE])))
        cap = self.swap(cap, cap2, FadeOut(shown),
                        LaggedStart(*[FadeIn(a, scale=0.4) for a in atomized],
                        lag_ratio=0.04), run_time=1.8)
        self.wait_until(50.4)
        cap = self.swap(cap, self.cap_text("too small for eyes to ever find.", 26),
                        run_time=1.5)

        self.wait_until(55.0)
        cap2 = self.cap_text("Atoms.", 40)
        # All the little bricks gather into the word / one bright atom.
        big = VGroup(soft_blob(ORIGIN, 0.7, ELECTRON, peak=0.35, layers=14),
                     nucleus(3, 3, center=ORIGIN, r=0.09),
                     electron_cloud(ORIGIN, 0.95, n=44))
        cap = self.swap(cap, cap2, FadeOut(atomized),
                        FadeIn(big, scale=0.4), run_time=1.8)
        self.wait_until(56.93)
        cap = self.swap(cap, self.cap_text("That's the name we gave", 29), run_time=1.3)
        self.wait_until(59.01)
        cap = self.swap(cap, self.cap_text("to nature's favorite kind.", 29),
                        Indicate(big, color=ELECTRON, scale_factor=1.15), run_time=1.5)
        self.wait_until(62.5)
        self.play_t(big.animate.scale(0.55).move_to(LEFT * 4.5 + UP * 1.6)
                    .set_opacity(0.5), run_time=1.5)
        self.one_atom = big
        self._cap = cap

    # ----------------------------------------------------------------
    def stack_them_up(self):
        self.wait_until(63.28)
        cap = self.cap_text("One little atom... doesn't seem like much.", 26)
        cap = self.enter_cap(cap, self.one_atom.animate.scale(1.4)
                             .move_to(ORIGIN).set_opacity(1.0), run_time=1.8)

        self.wait_until(67.85)
        cap2 = self.cap_text("But stack enough together—", 28)
        # A swarm of atoms multiplies.
        swarm = VGroup(*[
            Dot([random.uniform(-4.5, 4.5), random.uniform(-2.6, 2.2), 0],
                radius=random.uniform(0.03, 0.06),
                color=random.choice([ELECTRON, WARM, GOLD]), fill_opacity=0)
            for _ in range(120)])
        cap = self.swap(cap, cap2, FadeOut(self.one_atom),
                        LaggedStart(*[d.animate.set_opacity(random.uniform(0.5, 0.9))
                                      for d in swarm], lag_ratio=0.006),
                        run_time=2.2)

        self.wait_until(72.7)
        cap2 = self.cap_text("and you can build a blue whale,", 26)
        whale = whale_shape(0.95, ELECTRON).move_to(DOWN * 0.3)
        whale_dots = dot_outline(whale, n=54, color=ELECTRON, r=0.045)
        targets = [whale_dots[i % len(whale_dots)].get_center() for i in range(len(swarm))]
        cap = self.swap(cap, cap2, run_time=1.2)
        self.play_t(*[d.animate.move_to(t).set_color(ELECTRON)
                      for d, t in zip(swarm, targets)], run_time=1.6)

        self.wait_until(75.52)
        cap2 = self.cap_text("a thunderstorm... or someone you love.", 25)
        cloud = cloud_shape(0.85).move_to(LEFT * 2.5 + UP * 0.3)
        cloud_dots = VGroup()
        per = max(1, (len(swarm) // 2) // len(cloud))
        for circ in cloud:
            for k in range(per):
                cloud_dots.add(Dot(circ.point_from_proportion(k / per),
                                   radius=0.04, color="#c7d2e6"))
        bolt = VMobject(color=GOLD, stroke_width=4)
        bolt.set_points_as_corners([LEFT * 2.5 + DOWN * 0.4, LEFT * 2.7 + DOWN * 1.0,
                                     LEFT * 2.3 + DOWN * 1.0, LEFT * 2.6 + DOWN * 1.7])
        heart = heart_shape(0.5, PROTON).move_to(RIGHT * 2.6 + UP * 0.2)
        heart_dots = dot_outline(heart, n=len(swarm) - len(cloud_dots),
                                 color=PROTON, r=0.04)
        half = len(swarm) // 2
        cap = self.swap(cap, cap2, run_time=1.2)
        self.play_t(
            *[d.animate.move_to(cloud_dots[i % len(cloud_dots)].get_center())
              .set_color("#c7d2e6") for i, d in enumerate(swarm[:half])],
            *[d.animate.move_to(heart_dots[i % len(heart_dots)].get_center())
              .set_color(PROTON) for i, d in enumerate(swarm[half:])],
            run_time=1.8)
        self.play_t(Create(bolt), run_time=0.6)
        self.wait_until(77.5)
        self.play_t(FadeOut(swarm), FadeOut(bolt), run_time=1.2)
        self.swarm = swarm
        self._cap = cap

    # ----------------------------------------------------------------
    def chorus_dance(self):
        self.wait_until(78.0)
        cap = self.cap_text("Everything is made of tiny things,", 27)
        # A ring of little atoms, spinning and bobbing -- dancers.
        dancers = VGroup()
        n = 8
        for i in range(n):
            a = i / n * TAU
            p = 2.6 * np.array([np.cos(a), 0.75 * np.sin(a), 0])
            at = VGroup(nucleus(2, 2, center=p, r=0.06, glow=False),
                        electron_cloud(p, 0.5, n=18,
                                       color=[ELECTRON, WARM, GOLD, LIFE][i % 4]))
            dancers.add(at)
        cap = self.enter_cap(cap, LaggedStart(*[FadeIn(d, scale=0.3)
                             for d in dancers], lag_ratio=0.08), run_time=2.2)
        for d in dancers:
            add_breathe(d, amp=0.06, speed=random.uniform(1.5, 2.5))

        self.wait_until(84.0)
        cap = self.swap(cap, self.cap_text("little dancers, little strings,", 28),
                        run_time=1.4)
        self.wait_until(90.0)
        cap = self.swap(cap, self.cap_text("round and round they spin and sing,", 27),
                        run_time=1.4)
        self.play_t(Rotate(dancers, TAU * 0.6, about_point=ORIGIN), run_time=3.0,
                    rate_func=linear)
        self.wait_until(96.0)
        cap = self.swap(cap, self.cap_text("building every living thing.", 28),
                        run_time=1.4)
        self.play_t(Rotate(dancers, TAU * 0.4, about_point=ORIGIN), run_time=2.5,
                    rate_func=linear)

        self.wait_until(100.0)
        cap2 = self.cap_text("From the stars above at night", 27)
        stars = VGroup(*[star_shape(random.uniform(0.12, 0.24), STARC)
                         .move_to([random.uniform(-6, 6), random.uniform(1.5, 3.4), 0])
                         for _ in range(9)])
        cap = self.swap(cap, cap2, LaggedStart(*[GrowFromCenter(s) for s in stars],
                        lag_ratio=0.1), run_time=1.8)
        self.wait_until(103.0)
        cap2 = self.cap_text("to the firefly's little light,", 27)
        fireflies = VGroup(*[Dot([random.uniform(-6, 6), random.uniform(-3, -1), 0],
                                 radius=0.05, color=WARM) for _ in range(10)])
        for ff in fireflies:
            ff.add_updater(lambda m, dt: m.set_opacity(
                0.4 + 0.6 * abs(np.sin(self.t * 3 + m.get_x()))))
        cap = self.swap(cap, cap2, FadeIn(fireflies), run_time=1.6)

        self.wait_until(105.78)
        cap = self.swap(cap, self.cap_text("every story, every dream—", 28),
                        run_time=1.4)
        self.wait_until(110.04)
        cap = self.swap(cap, self.cap_text("started smaller than it seemed.", 27),
                        run_time=1.5)
        self.wait_until(112.4)
        for ff in fireflies:
            ff.clear_updaters()
        dancers.clear_updaters()
        self.play_t(FadeOut(dancers), FadeOut(stars), FadeOut(fireflies),
                    run_time=1.4)
        self._cap = cap

    # ----------------------------------------------------------------
    def the_nucleus(self):
        self.wait_until(112.84)
        cap = self.cap_text("Atoms have a busy middle: the nucleus.", 27)
        nuc = nucleus(6, 6, center=ORIGIN, r=0.16)
        cap = self.enter_cap(cap, FadeIn(nuc, scale=0.4), run_time=1.8)
        add_breathe(nuc, amp=0.03, speed=1.4)

        self.wait_until(123.58)
        cap2 = self.cap_text("That's where tiny protons gather,", 27)
        plabel = Text("proton", font_size=20, color=PROTON).to_corner(DL, buff=0.7)
        pdot = Dot(color=PROTON, radius=0.09).next_to(plabel, RIGHT, buff=0.12)
        cap = self.swap(cap, cap2, FadeIn(plabel), FadeIn(pdot),
                        Indicate(nuc, color=PROTON), run_time=1.6)
        self.wait_until(126.78)
        cap2 = self.cap_text("neutrons standing side by side.", 27)
        nlabel = Text("neutron", font_size=20, color=NEUTRON).next_to(
            plabel, UP, buff=0.2, aligned_edge=LEFT)
        ndot = Dot(color=NEUTRON, radius=0.09).next_to(nlabel, RIGHT, buff=0.12)
        cap = self.swap(cap, cap2, FadeIn(nlabel), FadeIn(ndot), run_time=1.6)

        self.wait_until(130.52)
        cap2 = self.cap_text("Then electrons zip around,", 28)
        # First show the OLD planetary picture (orbits).
        orb1, t1 = orbit_electron(ORIGIN, 1.8, 1.1)
        orb2, t2 = orbit_electron(ORIGIN, 1.3, 1.9)
        cap = self.swap(cap, cap2, FadeOut(plabel), FadeOut(pdot),
                        FadeOut(nlabel), FadeOut(ndot),
                        Create(orb1), Create(orb2), run_time=1.7)
        self.play_t(t1.animate.increment_value(TAU * 1.2),
                    t2.animate.increment_value(TAU * 1.2), run_time=1.5,
                    rate_func=linear)

        self.wait_until(136.06)
        cap = self.swap(cap, self.cap_text("Not like planets—", 30), run_time=1.2)
        self.wait_until(137.6)
        cap2 = self.cap_text("that's an old idea.", 30)
        # Cross out the orbits.
        cross = VGroup(Line(UL * 2.2, DR * 2.2, color=PROTON, stroke_width=6),
                       Line(UR * 2.2, DL * 2.2, color=PROTON, stroke_width=6))
        cap = self.swap(cap, cap2, Create(cross), run_time=1.4)

        self.wait_until(140.86)
        cap2 = self.cap_text("The truth's a little stranger than you've heard.", 24)
        # Orbits dissolve into a fuzzy probability CLOUD.
        cloud = electron_cloud(ORIGIN, 2.0, n=140, color=ELECTRON)
        orb1[1].clear_updaters()
        orb2[1].clear_updaters()
        cap = self.swap(cap, cap2, FadeOut(cross), FadeOut(orb1), FadeOut(orb2),
                        LaggedStart(*[FadeIn(d) for d in cloud], lag_ratio=0.004),
                        run_time=2.0)
        add_breathe(cloud, amp=0.03, speed=0.8)
        self.wait_until(145.5)
        nuc.clear_updaters()
        cloud.clear_updaters()
        self.play_t(FadeOut(cloud), nuc.animate.scale(0.9), run_time=1.2)
        self.nuc = nuc
        self._cap = cap

    # ----------------------------------------------------------------
    def stadium_scale(self):
        self.wait_until(146.75)
        cap = self.cap_text("Here's the funny part...", 30)
        cap = self.enter_cap(cap, self.nuc.animate.move_to(ORIGIN), run_time=1.5)

        self.wait_until(150.54)
        cap2 = self.cap_text("If you made an atom as big as a football stadium...", 24)
        field = stadium(pos=DOWN * 0.3, w=7.5, h=3.6)
        atom_ring = Circle(radius=3.9, color=ELECTRON, stroke_width=2,
                           stroke_opacity=0.5).move_to(DOWN * 0.3)
        cap = self.swap(cap, cap2, FadeOut(self.nuc),
                        Create(field), Create(atom_ring), run_time=2.0)

        self.wait_until(155.08)
        cap2 = self.cap_text("the nucleus would be about the size", 26)
        marble = sphere3d(0.09, PROTON, pos=DOWN * 0.3, layers=12)
        mglow = soft_blob(DOWN * 0.3, 0.3, PROTON, peak=0.3, layers=10)
        cap = self.swap(cap, cap2, FadeIn(mglow), FadeIn(marble, scale=0.3),
                        run_time=1.6)
        self.wait_until(159.04)
        cap2 = self.cap_text("of a marble on the fifty-yard line.", 26)
        arrow = Arrow(DOWN * 2.2, DOWN * 0.55, color=INK, stroke_width=3, buff=0.1)
        mlbl = Text("the whole nucleus", font_size=18, color=PROTON).next_to(
            arrow, DOWN, buff=0.1)
        cap = self.swap(cap, cap2, GrowArrow(arrow), FadeIn(mlbl), run_time=1.6)

        self.wait_until(163.04)
        cap = self.swap(cap, self.cap_text("Everything else? Just room.", 28),
                        FadeOut(arrow), FadeOut(mlbl),
                        atom_ring.animate.set_stroke(opacity=0.8), run_time=1.6)
        self.wait_until(168.56)
        cap = self.swap(cap, self.cap_text("Nature likes her elbow room.", 28),
                        run_time=1.5)
        self.wait_until(172.56)
        cap = self.swap(cap, self.cap_text("Alright... that's worth thinking about.", 25),
                        run_time=1.5)
        self.wait_until(174.4)
        self.play_t(FadeOut(field), FadeOut(atom_ring), FadeOut(marble),
                    FadeOut(mglow), run_time=1.2)
        self._cap = cap

    # ----------------------------------------------------------------
    def elements(self):
        self.wait_until(174.78)
        cap = self.cap_text("Different numbers, different atoms—", 26)
        cap = self.enter_cap(cap, run_time=1.4)

        self.wait_until(177.86)
        cap = self.swap(cap, self.cap_text("that's how every element grows.", 27),
                        run_time=1.4)

        self.wait_until(180.92)
        cap2 = self.cap_text("Hydrogen's light,  gold shines bright,", 27)
        h_tile = element_tile("H", 1, HYDRO, pos=LEFT * 4.2 + DOWN * 0.4)
        h_atom = VGroup(nucleus(1, 0, center=LEFT * 4.2 + UP * 1.3, r=0.1),
                        electron_cloud(LEFT * 4.2 + UP * 1.3, 0.55, n=16, color=HYDRO))
        au_tile = element_tile("Au", 79, GOLD, pos=ORIGIN + DOWN * 0.4)
        au_atom = VGroup(nucleus(10, 12, center=UP * 1.3, r=0.05, glow=False),
                         electron_cloud(UP * 1.3, 0.75, n=60, color=GOLD))
        cap = self.swap(cap, cap2, FadeIn(h_tile, shift=UP * 0.2), FadeIn(h_atom),
                        FadeIn(au_tile, shift=UP * 0.2), FadeIn(au_atom),
                        run_time=1.8)

        self.wait_until(184.1)
        cap2 = self.cap_text("carbon's where life's story flows.", 26)
        c_tile = element_tile("C", 6, LIFE, pos=RIGHT * 4.2 + DOWN * 0.4)
        c_atom = VGroup(nucleus(6, 6, center=RIGHT * 4.2 + UP * 1.3, r=0.07),
                        electron_cloud(RIGHT * 4.2 + UP * 1.3, 0.65, n=30, color=LIFE))
        cap = self.swap(cap, cap2, FadeIn(c_tile, shift=UP * 0.2), FadeIn(c_atom),
                        run_time=1.8)

        self.wait_until(187.52)
        cap = self.swap(cap, self.cap_text("Mix 'em up in different ways—", 27),
                        run_time=1.4)
        self.wait_until(189.7)
        cap = self.swap(cap, self.cap_text("that's the secret recipe.", 28),
                        run_time=1.4)

        self.wait_until(193.94)
        cap2 = self.cap_text("You, your dog, the Moon: same alphabet,", 25)
        cap = self.swap(cap, cap2, FadeOut(h_tile), FadeOut(au_tile),
                        FadeOut(c_tile), FadeOut(h_atom), FadeOut(au_atom),
                        FadeOut(c_atom), run_time=1.8)
        # same building blocks -> different arrangements
        blocks = VGroup(*[Dot([random.uniform(-1, 1), random.uniform(-1, 1), 0],
                              radius=0.06,
                              color=random.choice([PROTON, ELECTRON, LIFE, HYDRO]))
                          for _ in range(24)])
        blocks.move_to(ORIGIN)
        self.play_t(FadeIn(blocks, scale=0.5), run_time=1.0)
        self.wait_until(197.98)
        cap = self.swap(cap, self.cap_text("different poetry.", 30), run_time=1.4)
        self.play_t(blocks.animate.arrange_in_grid(4, 6, buff=0.35), run_time=1.5)
        self.wait_until(200.5)
        self.play_t(FadeOut(blocks), run_time=1.2)
        self._cap = cap

    # ----------------------------------------------------------------
    def final_chorus(self):
        self.wait_until(201.0)
        cap = self.cap_text("Everything is made of tiny things,", 27)
        ring = VGroup()
        n = 10
        for i in range(n):
            a = i / n * TAU
            p = 2.7 * np.array([np.cos(a), 0.8 * np.sin(a), 0])
            ring.add(VGroup(nucleus(2, 2, center=p, r=0.06, glow=False),
                            electron_cloud(p, 0.45, n=14,
                                           color=[ELECTRON, WARM, GOLD, LIFE][i % 4])))
        cap = self.enter_cap(cap, LaggedStart(*[FadeIn(d, scale=0.4) for d in ring],
                             lag_ratio=0.06), run_time=2.2)

        self.wait_until(205.0)
        cap = self.swap(cap, self.cap_text("quiet builders, hidden kings.", 28),
                        Rotate(ring, TAU * 0.3, about_point=ORIGIN), run_time=1.8)
        self.wait_until(209.04)
        cap = self.swap(cap, self.cap_text("Though you never see their face,", 27),
                        run_time=1.5)
        self.wait_until(211.36)
        cap = self.swap(cap, self.cap_text("they're the reason there is place.", 27),
                        Rotate(ring, TAU * 0.2, about_point=ORIGIN), run_time=1.6)

        self.wait_until(214.64)
        cap = self.swap(cap, self.cap_text("Every leaf and every cloud,", 27),
                        run_time=1.5)
        self.wait_until(219.04)
        cap = self.swap(cap, self.cap_text("every whisper, every crowd—", 27),
                        run_time=1.4)
        self.wait_until(220.8)
        cap = self.swap(cap, self.cap_text("tiny pieces, working free,", 27),
                        run_time=1.4)
        self.wait_until(225.74)
        cap = self.swap(cap, self.cap_text("making all that comes to be.", 27),
                        Indicate(ring, color=STARC, scale_factor=1.1), run_time=1.6)
        self.wait_until(229.0)
        self.play_t(FadeOut(ring), run_time=1.4)
        self._cap = cap

    # ----------------------------------------------------------------
    def outro(self):
        self.wait_until(230.0)
        cap = self.cap_text("Next time...", 31)
        # Zoom toward a single atom; the electron cloud shimmers with mystery.
        nuc = nucleus(3, 3, center=ORIGIN, r=0.12)
        cloud = electron_cloud(ORIGIN, 1.6, n=110, color=ELECTRON)
        cap = self.enter_cap(cap, FadeIn(nuc, scale=0.4),
                             LaggedStart(*[FadeIn(d) for d in cloud],
                             lag_ratio=0.004), run_time=2.0)
        add_breathe(cloud, amp=0.04, speed=1.0)

        self.wait_until(235.64)
        cap = self.swap(cap, self.cap_text("we're gonna meet those tiny things up close.", 24),
                        self.camera.frame.animate.scale(0.7) if hasattr(
                            self.camera, "frame") else nuc.animate.scale(1.3),
                        run_time=1.8)

        self.wait_until(240.69)
        cap2 = self.cap_text("And here's where it gets strange—", 27)
        # The cloud flickers between positions -- uncertainty.
        cap = self.swap(cap, cap2, cloud.animate.set_color(GOLD), run_time=1.5)
        for _ in range(3):
            self.play_t(cloud.animate.shift(RIGHT * 0.15).set_opacity(0.5),
                        run_time=0.3)
            self.play_t(cloud.animate.shift(LEFT * 0.15).set_opacity(0.8),
                        run_time=0.3)

        self.wait_until(244.0)
        cap = self.swap(cap, self.cap_text("Down in that little world,", 28),
                        run_time=1.5)
        self.wait_until(247.0)
        cap = self.swap(cap, self.cap_text("the rules ain't the same.", 29),
                        run_time=1.6)

        self.wait_until(250.5)
        cloud.clear_updaters()
        self.play_t(FadeOut(cap), FadeOut(cloud), nuc.animate.scale(0.5)
                    .to_edge(UP, buff=1.1).set_opacity(0.4), run_time=2.0)
        title = Text("Everything Is Made of Tiny Things", font_size=38,
                     gradient=(ELECTRON, WARM))
        cite = Text("after Ernest Rutherford — the nuclear atom (1911)",
                    font_size=20, color=INK).next_to(title, DOWN, buff=0.5)
        cite2 = Text("Philosophical Magazine 21, 669  ·  a mostly-empty atom",
                     font_size=18, color=DIM).next_to(cite, DOWN, buff=0.2)
        self.play_t(FadeIn(title, scale=0.8), FadeOut(nuc), run_time=2.0)
        self.play_t(FadeIn(cite, shift=UP * 0.2), FadeIn(cite2, shift=UP * 0.2),
                    run_time=2.0)
        add_breathe(title, amp=0.012, speed=0.7)
        self.wait_until(268.0)
        title.clear_updaters()
        self.play_t(FadeOut(title), FadeOut(cite), FadeOut(cite2), run_time=1.6)
