"""Visuals for "The Fat Knows When" (4:27 song, timed to the vocals).

Based on: Acin Perez, Assali, Veliova et al., "Mitochondrial calcium
regulates lipid metabolism by modulating tethering of mitochondria to
lipid droplets", The EMBO Journal (2026). CNIC (Madrid) & UCLA.
DOI 10.1038/s44318-026-00827-8.

The paper: mitochondria (the cell's powerhouses) physically dock onto
lipid droplets (stored fat). Calcium *inside* the mitochondria -- tuned
by the mitochondrial calcium exchanger NCLX -- is the switch. When
mitochondrial calcium rises, the mitochondria change shape and DETACH
from the droplet; only then can lipases reach in and burn the fat. Low
calcium keeps them tethered and the fat stored. So fat-burning is a
conversation between the droplet and the engine, choreographed by one ion.

Render (from the manim/ directory):
    manim -pql scenes/the_fat_knows_when.py TheFatKnowsWhen   # fast preview
    manim -pqh scenes/the_fat_knows_when.py TheFatKnowsWhen   # final 1080p60

Timing: 0-71s and 121-238s are anchored on a Whisper pass (the traffic-light
and bridge stretches transcribed cleanly). The sung choruses (73-120s,
190-218s) are estimated -- paced evenly between solid anchors. A long
instrumental tail (238-267s) holds the citation card.

Captions always crossfade (FadeOut old + FadeIn new), never Transform
between different strings.
"""

import random
from pathlib import Path

import numpy as np
from manim import *

MP3 = (Path(__file__).resolve().parents[2] / "songs" / "the-fat-knows-when"
       / "ep 121 the fat knows when.mp3")

FAT = "#f4b942"        # warm gold - stored fat / lipid droplet
FAT_DEEP = "#c98a2b"   # deeper amber
MITO = "#e8637f"       # rose - mitochondria (the engines)
MITO_DEEP = "#a83a58"
CA = "#4cc9f0"         # bright cyan - calcium ions
FIRE = "#ff7a33"       # flame
FIRE_HOT = "#ffd23f"   # hot core
MEMBRANE = "#63c7a6"   # teal-green membrane / tether
CALM = "#f0e6d2"       # warm cream - caption text
DIM = "#a89a86"        # warm grey
random.seed(7)


# --------------------------------------------------------------------------
# Reusable atmosphere / motion helpers
# --------------------------------------------------------------------------

def soft_blob(pos, radius, color, peak=0.05, layers=26):
    """Soft radial glow from many thin stacked fills (needs lots of layers
    with a smooth falloff, or the circles read as target bands)."""
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


def trail_group(mob, color=FIRE, segments=14, radius=0.045):
    """A fading comet-tail of dots tracing mob's recent path."""
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
    """A gentle continuous scale pulse -- keeps a static group alive."""
    mob.br_t = random.uniform(0, TAU)
    mob.br_prev = 1.0

    def upd(m, dt):
        m.br_t += dt
        target = 1 + amp * np.sin(speed * m.br_t)
        m.scale(target / m.br_prev)
        m.br_prev = target

    mob.add_updater(upd)


def add_flicker(mob, amp=0.14, speed=9.0):
    """Fast irregular vertical stretch -- flame liveliness."""
    mob.fl_t = random.uniform(0, TAU)
    mob.fl_prev = 1.0

    def upd(m, dt):
        m.fl_t += dt
        target = 1 + amp * (np.sin(speed * m.fl_t)
                            + 0.4 * np.sin(2.3 * speed * m.fl_t + 1))
        m.stretch(max(0.6, target) / m.fl_prev, 1)
        m.fl_prev = max(0.6, target)

    mob.add_updater(upd)


# --------------------------------------------------------------------------
# Cell-biology building blocks
# --------------------------------------------------------------------------

def lipid_droplet(radius=1.0, color=FAT, pos=ORIGIN, glow=True):
    """A golden droplet of stored fat: oily body, inner sheen, highlight."""
    parts = VGroup()
    if glow:
        parts.add(soft_blob(pos, radius * 1.55, color, peak=0.06, layers=14))
    body = Circle(radius=radius, color=FAT_DEEP, fill_opacity=0.92,
                  stroke_color=color, stroke_width=2.5).move_to(pos)
    sheen = Circle(radius=radius * 0.72, color=color, fill_opacity=0.55,
                   stroke_width=0).move_to(pos)
    core = Circle(radius=radius * 0.4, color=FIRE_HOT, fill_opacity=0.25,
                  stroke_width=0).move_to(pos)
    highlight = Circle(radius=radius * 0.2, color=WHITE, fill_opacity=0.5,
                       stroke_width=0).move_to(pos + radius * 0.42 * (UP + LEFT))
    parts.add(body, sheen, core, highlight)
    return parts


def mitochondrion(w=1.7, h=0.95, color=MITO, pos=ORIGIN, glow=True):
    """A bean-shaped powerhouse: double membrane + wavy internal cristae."""
    parts = VGroup()
    if glow:
        parts.add(soft_blob(pos, max(w, h) * 0.75, color, peak=0.05, layers=12))
    outer = RoundedRectangle(width=w, height=h, corner_radius=h / 2,
                             stroke_color=color, stroke_width=3,
                             fill_color=MITO_DEEP, fill_opacity=0.3).move_to(pos)
    inner = RoundedRectangle(width=w - 0.16, height=h - 0.16,
                             corner_radius=(h - 0.16) / 2, stroke_color=color,
                             stroke_width=1.4, stroke_opacity=0.6,
                             fill_opacity=0).move_to(pos)
    cristae = VGroup()
    span = w / 2 - 0.3
    for k, yoff in enumerate((0.15, -0.15)):
        pts = [pos + np.array([x, yoff + 0.085 * np.sin(x * 7 + k * PI), 0])
               for x in np.linspace(-span, span, 44)]
        line = VMobject(stroke_color=color, stroke_width=1.5,
                        stroke_opacity=0.75)
        line.set_points_smoothly(pts)
        cristae.add(line)
    parts.add(outer, inner, cristae)
    return parts


def calcium_dot(pos=ORIGIN, r=0.075):
    """A bright calcium ion with a soft halo."""
    halo = Circle(radius=r * 2.4, color=CA, fill_opacity=0.22,
                  stroke_width=0).move_to(pos)
    core = Dot(radius=r, color=CA).move_to(pos)
    core.set_sheen(0.3, UL)
    return VGroup(halo, core)


def flame_shape(color, h=1.0):
    m = VMobject(fill_color=color, fill_opacity=0.85, stroke_width=0)
    m.set_points_smoothly([
        np.array([0, h, 0]),
        np.array([0.34 * h, 0.34 * h, 0]),
        np.array([0.24 * h, -0.05 * h, 0]),
        np.array([0, -0.14 * h, 0]),
        np.array([-0.24 * h, -0.05 * h, 0]),
        np.array([-0.34 * h, 0.34 * h, 0]),
        np.array([0, h, 0]),
    ])
    return m


def flame(scale=1.0, pos=ORIGIN):
    """A flickering two-layer flame."""
    outer = flame_shape(FIRE, h=1.0 * scale)
    inner = flame_shape(FIRE_HOT, h=0.58 * scale).shift(DOWN * 0.05 * scale)
    glow = soft_blob(ORIGIN, 0.8 * scale, FIRE, peak=0.08, layers=12)
    grp = VGroup(glow, outer, inner).move_to(pos)
    return grp


def traffic_light(pos=ORIGIN, scale=1.0):
    """Returns (group, red, green). Light one up by raising its fill opacity."""
    housing = RoundedRectangle(width=0.52, height=1.02, corner_radius=0.12,
                               stroke_color=DIM, stroke_width=2.5,
                               fill_color="#14100c", fill_opacity=0.95)
    red = Circle(radius=0.16, color="#ff5555", fill_opacity=0.18,
                 stroke_color="#ff5555", stroke_width=1).move_to(UP * 0.25)
    green = Circle(radius=0.16, color="#5ce07a", fill_opacity=0.18,
                   stroke_color="#5ce07a", stroke_width=1).move_to(DOWN * 0.25)
    grp = VGroup(housing, red, green).scale(scale).move_to(pos)
    return grp, red, green


def tether(p1, p2, color=MEMBRANE):
    """A short protein bridge (a few parallel links) between two contacts."""
    v = np.array(p2) - np.array(p1)
    d = np.linalg.norm(v)
    if d < 1e-6:
        return VGroup()
    u = v / d
    perp = np.array([-u[1], u[0], 0])
    links = VGroup()
    for off in (-0.09, 0, 0.09):
        a = np.array(p1) + perp * off + u * d * 0.12
        b = np.array(p2) + perp * off - u * d * 0.12
        links.add(Line(a, b, color=color, stroke_width=3, stroke_opacity=0.85))
    return links


class TheFatKnowsWhen(Scene):
    def play_t(self, *anims, run_time=1.0, **kwargs):
        self.play(*anims, run_time=run_time, **kwargs)
        self.t += run_time

    def wait_until(self, t):
        if t > self.t:
            self.wait(t - self.t)
            self.t = t

    def swap(self, old, new, *extra, run_time=1.2):
        self.play_t(FadeOut(old), FadeIn(new), *extra, run_time=run_time)
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
        return Text(s, font_size=size, color=CALM).to_edge(UP, buff=0.7)

    # ----------------------------------------------------------------
    def construct(self):
        if MP3.exists():
            self.add_sound(str(MP3))
        self.t = 0.0
        self.add_ambient_background()
        self.title_and_savings()     # 0:03 - 0:48
        self.engines_and_fuel()      # 0:48 - 1:13
        self.switch_and_chorus()     # 1:13 - 1:54
        self.calcium_traffic()       # 1:54 - 2:16
        self.the_conversation()      # 2:16 - 2:46
        self.more_than_calories()    # 2:46 - 3:10
        self.symphony()              # 3:10 - 3:39
        self.closing()               # 3:40 - 4:27

    def add_ambient_background(self):
        """Warm, organic depth: amber/rose nebulae + slow floating vesicles."""
        nebulae = VGroup()
        for pos, r, col in (
            (np.array([-4.7, 2.0, 0]), 3.8, FAT),
            (np.array([4.9, -1.8, 0]), 4.0, MITO),
            (np.array([2.4, 2.7, 0]), 2.6, MEMBRANE),
            (np.array([-3.6, -2.6, 0]), 2.8, FAT_DEEP),
        ):
            blob = soft_blob(pos, r, col, peak=0.05)
            blob.drift = np.array([random.uniform(-0.02, 0.02),
                                   random.uniform(-0.012, 0.012), 0])
            blob.add_updater(lambda m, dt: m.shift(m.drift * dt))
            nebulae.add(blob)

        motes = VGroup()
        for _ in range(30):
            depth = random.random()
            dot = Circle(radius=0.02 + 0.05 * depth,
                        color=random.choice([FAT, MITO, MEMBRANE, CA]),
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
        self.add(nebulae, motes)

    # ----------------------------------------------------------------
    def title_and_savings(self):
        title = Text("The Fat Knows When", font_size=56,
                     gradient=(FAT, MITO))
        halo = Text("The Fat Knows When", font_size=56, color=FAT).set_opacity(0.16)
        halo.scale(1.05).move_to(title)
        self.play_t(FadeIn(halo), Write(title), run_time=2.5)
        self.wait_until(3.4)
        self.play_t(title.animate.scale(0.5).to_edge(UP, buff=0.55),
                    FadeOut(halo), run_time=1.5)

        # The "savings account": a golden droplet you stack up and spend down.
        droplet = lipid_droplet(radius=1.15, pos=DOWN * 0.4)
        add_breathe(droplet, amp=0.02, speed=0.8)
        cap = self.cap_text("Thought fat was just an old savings account—", 28)
        self.wait_until(10.0)
        self._cap = None
        cap = self.enter_cap(cap, FadeIn(droplet, scale=0.7),
                             FadeOut(title), run_time=2.0)

        # Coins stack up into it...
        coins = VGroup(*[
            VGroup(Circle(radius=0.2, color=FAT, fill_opacity=0.9,
                          stroke_color=FAT_DEEP, stroke_width=2),
                   Circle(radius=0.12, color=FAT_DEEP, fill_opacity=0.5,
                          stroke_width=0))
            .move_to(LEFT * 4.4 + UP * (1.6 - i * 0.1)) for i in range(6)
        ])
        self.play_t(LaggedStart(*[
            coin.animate.move_to(droplet.get_center()
                                 + 0.5 * np.array([np.cos(a), np.sin(a), 0]))
            for coin, a in zip(coins, np.linspace(0, TAU, 6, endpoint=False))],
            lag_ratio=0.25), droplet.animate.scale(1.12), run_time=4.0)
        self.play_t(FadeOut(coins, scale=0.3), run_time=1.5)

        self.wait_until(29.6)
        cap2 = self.cap_text("Stack it up... spend it down.", 28)
        # ...and spend it down: the droplet shrinks, a coin drifts off.
        spent = coins[:3].copy().set_opacity(0.9).move_to(droplet)
        cap = self.swap(cap, cap2, droplet.animate.scale(0.8), run_time=1.5)
        self.play_t(FadeIn(spent), spent.animate.shift(DOWN * 3 + RIGHT * 2)
                    .set_opacity(0), droplet.animate.scale(0.92), run_time=2.5)

        self.wait_until(36.0)
        cap = self.swap(cap, self.cap_text("Simple as that.", 30), run_time=1.2)
        self.wait_until(38.0)
        cap = self.swap(cap, self.cap_text("Turns out—", 32,), run_time=1.0)

        self.wait_until(40.0)
        cap2 = self.cap_text("every little fat cell's been keeping secrets,", 27)
        # A keyhole appears on the droplet: it was holding something back.
        keyhole = VGroup(
            Circle(radius=0.1, color=MITO_DEEP, fill_opacity=0.9, stroke_width=0),
            Triangle(color=MITO_DEEP, fill_opacity=0.9, stroke_width=0)
            .scale(0.13).stretch(1.4, 1).next_to(ORIGIN, DOWN, buff=0),
        ).move_to(droplet.get_center())
        cap = self.swap(cap, cap2, droplet.animate.scale(1.15), run_time=1.5)
        self.play_t(FadeIn(keyhole, scale=0.3), run_time=1.2)

        self.wait_until(44.5)
        cap2 = self.cap_text("waiting for the right knock on the door.", 27)
        knock = Circle(radius=0.15, color=CA, stroke_width=3).move_to(
            droplet.get_center())
        cap = self.swap(cap, cap2, run_time=1.2)
        self.play_t(Broadcast(knock, focal_point=droplet.get_center(),
                              n_mobs=3), run_time=2.0)
        # Hand the droplet to the next scene -- we zoom inside it.
        self.droplet = droplet
        self.droplet_keyhole = keyhole
        self._cap = cap

    # ----------------------------------------------------------------
    def engines_and_fuel(self):
        droplet = self.droplet
        cap = self.cap_text("Deep inside, where the engines run—", 29)
        # Shrink the droplet to one of several, and reveal the engines beside it.
        self.wait_until(48.0)
        cap = self.enter_cap(cap, FadeOut(self.droplet_keyhole),
                             droplet.animate.scale(0.8).move_to(LEFT * 1.2),
                             run_time=2.0)

        mito = mitochondrion(w=1.9, h=1.05, pos=RIGHT * 1.6 + UP * 0.1)
        add_breathe(mito, amp=0.025, speed=1.1)
        self.wait_until(56.0)
        cap2 = self.cap_text("tiny powerhouses—mitochondria—", 29)
        cap = self.swap(cap, cap2, FadeIn(mito, scale=0.7), run_time=1.5)

        self.wait_until(61.0)
        cap2 = self.cap_text("sit right beside little drops of stored fuel.", 27)
        link = tether(droplet.get_right() + RIGHT * 0.05,
                      mito.get_left() + LEFT * 0.05)
        cap = self.swap(cap, cap2, mito.animate.move_to(RIGHT * 1.15 + UP * 0.05),
                        run_time=1.5)
        self.play_t(Create(link), run_time=1.2)

        self.wait_until(66.2)
        cap2 = self.cap_text("Sometimes they're holding on...", 28)
        # Holding on: tether taut, mito hugs the droplet, a warm bond glow.
        bond_glow = soft_blob((droplet.get_right() + mito.get_left()) / 2, 0.5,
                              MEMBRANE, peak=0.12, layers=12)
        cap = self.swap(cap, cap2, mito.animate.move_to(RIGHT * 0.95),
                        FadeIn(bond_glow), run_time=2.0)

        self.wait_until(68.5)
        cap2 = self.cap_text("sometimes they let go.", 28)
        # Let go: tether releases, mito drifts away.
        cap = self.swap(cap, cap2, FadeOut(bond_glow),
                        Uncreate(link),
                        mito.animate.move_to(RIGHT * 2.5 + UP * 0.5),
                        run_time=1.6)

        self.wait_until(71.1)
        cap2 = self.cap_text("And that's when the fire begins.", 29)
        # Fire: the freed droplet is burned for energy.
        fl = flame(scale=1.1, pos=droplet.get_center() + UP * 0.2)
        add_flicker(fl[1]); add_flicker(fl[2])
        cap = self.swap(cap, cap2, FadeIn(fl, scale=0.4),
                        droplet.animate.scale(0.75), run_time=1.8)
        self.mito = mito
        self.droplet = droplet
        self.flame = fl
        self._cap = cap

    # ----------------------------------------------------------------
    def switch_and_chorus(self):
        # Pre-chorus: nature's switch. Clear the fire, set up store<->burn.
        self.wait_until(73.0)
        cap = self.cap_text("Nature don't waste nothing.", 29)
        cap = self.enter_cap(cap, FadeOut(self.flame),
                             self.mito.animate.move_to(RIGHT * 3.2 + UP * 0.6)
                             .set_opacity(0.0),
                             self.droplet.animate.scale(1.1).move_to(ORIGIN),
                             run_time=2.2)
        droplet = self.droplet

        self.wait_until(79.0)
        cap2 = self.cap_text("She's got a switch for every season.", 28)
        # A cycle arrow around the droplet: store <-> burn, round and round.
        cycle = Circle(radius=1.7, color=MEMBRANE, stroke_width=2.5,
                       stroke_opacity=0.5).move_to(droplet)
        save_lbl = Text("save", font_size=20, color=FAT).next_to(cycle, LEFT)
        burn_lbl = Text("burn", font_size=20, color=FIRE).next_to(cycle, RIGHT)
        marker = Dot(radius=0.1, color=CA).move_to(cycle.point_from_proportion(0))
        cap = self.swap(cap, cap2, Create(cycle), FadeIn(save_lbl),
                        FadeIn(burn_lbl), FadeIn(marker), run_time=2.0)
        marker.add_updater(lambda m: None)

        def spin_marker(alpha_end, rt):
            self.play_t(MoveAlongPath(marker, cycle), run_time=rt,
                        rate_func=linear)

        # Chorus -- the store<->burn dance. Marker rides the cycle; the droplet
        # breathes bigger (save) and smaller with a flame lick (burn).
        self.wait_until(84.0)
        cap = self.swap(cap, self.cap_text("The fat knows when...  the fat knows how...", 28),
                        run_time=1.4)
        self.play_t(MoveAlongPath(marker, cycle), droplet.animate.scale(1.15),
                    run_time=2.5, rate_func=linear)

        self.wait_until(89.0)
        cap = self.swap(cap, self.cap_text("Every cell's been listening all along somehow.", 26),
                        run_time=1.4)
        lick = flame(scale=0.7, pos=droplet.get_top() + UP * 0.1)
        add_flicker(lick[1]); add_flicker(lick[2])
        self.play_t(MoveAlongPath(marker, cycle), FadeIn(lick),
                    droplet.animate.scale(0.87), run_time=2.6, rate_func=linear)

        self.wait_until(94.0)
        cap = self.swap(cap, self.cap_text("Hold it close...  turn it free...", 28),
                        FadeOut(lick), run_time=1.4)
        self.play_t(MoveAlongPath(marker, cycle), droplet.animate.scale(1.15),
                    run_time=2.0, rate_func=linear)

        self.wait_until(98.5)
        cap = self.swap(cap, self.cap_text("Every heartbeat's chemistry.", 29),
                        run_time=1.3)
        # A heartbeat pulse through the whole cycle.
        for _ in range(2):
            self.play_t(droplet.animate.scale(1.08), run_time=0.35,
                        rate_func=rush_into)
            self.play_t(droplet.animate.scale(1 / 1.08), run_time=0.55,
                        rate_func=rush_from)

        self.wait_until(103.0)
        cap = self.swap(cap, self.cap_text("Burn a little...  save a little...", 28),
                        run_time=1.3)
        lick2 = flame(scale=0.7, pos=droplet.get_top() + UP * 0.1)
        add_flicker(lick2[1]); add_flicker(lick2[2])
        self.play_t(FadeIn(lick2), droplet.animate.scale(0.88), run_time=1.5)
        self.play_t(FadeOut(lick2), droplet.animate.scale(1 / 0.88), run_time=1.5)

        self.wait_until(107.5)
        cap = self.swap(cap, self.cap_text("Life keeps dancing right down the middle.", 26),
                        run_time=1.4)
        self.play_t(MoveAlongPath(marker, cycle), run_time=2.0, rate_func=linear)

        self.wait_until(111.0)
        cap = self.swap(cap, self.cap_text("The fat knows when...  the fat knows now.", 28),
                        run_time=1.4)
        # End this fade exactly on the 114.0 anchor the next (confirmed-timing)
        # section opens on, so the traffic-light sequence stays tight.
        self.wait_until(112.5)
        marker.clear_updaters()
        self.play_t(FadeOut(cycle), FadeOut(save_lbl), FadeOut(burn_lbl),
                    FadeOut(marker), droplet.animate.scale(0.9).move_to(LEFT * 2.6),
                    run_time=1.5)
        self.droplet = droplet
        self._cap = cap

    # ----------------------------------------------------------------
    def calcium_traffic(self):
        droplet = self.droplet
        # The mechanism scene. Bring back the engine, feed it calcium.
        mito = mitochondrion(w=2.1, h=1.15, pos=RIGHT * 1.4)
        add_breathe(mito, amp=0.02, speed=1.0)
        link = tether(droplet.get_right(), mito.get_left())
        cap = self.cap_text("Turns out calcium ain't just for bones.", 28)
        self.wait_until(114.0)
        cap = self.enter_cap(cap, FadeIn(mito, scale=0.8), Create(link),
                             run_time=1.8)
        # A faint bone glyph fades out -- "not just for bones".
        bone = Text("\U0001f9b4", font_size=40).set_opacity(0.5).to_corner(DR,
                                                                          buff=1.0)
        self.play_t(FadeIn(bone), run_time=0.6)
        self.play_t(FadeOut(bone, shift=DOWN * 0.5), run_time=0.8)

        self.wait_until(118.0)
        cap2 = self.cap_text("It's whispering inside those engines.", 27)
        # Calcium ions stream into the mitochondrion.
        ions = VGroup(*[calcium_dot(mito.get_center()
                                    + RIGHT * 3.5 + UP * random.uniform(-1, 1))
                        for _ in range(6)])
        cap = self.swap(cap, cap2, run_time=1.3)
        self.play_t(LaggedStart(*[
            ion.animate.move_to(mito.get_center()
                                + np.array([random.uniform(-0.5, 0.5),
                                            random.uniform(-0.3, 0.3), 0]))
            for ion in ions], lag_ratio=0.15), run_time=2.0)

        self.wait_until(121.7)
        cap2 = self.cap_text("Telling them: “Stay close.”", 29)
        # Low calcium read: stay tethered (a green-ish steady bond).
        cap = self.swap(cap, cap2, mito.animate.move_to(RIGHT * 1.15),
                        link.animate.set_stroke(opacity=1.0, color=MEMBRANE),
                        run_time=1.6)

        self.wait_until(123.9)
        cap2 = self.cap_text("Or: “Turn loose.”", 29)
        # High calcium: mito reshapes and detaches.
        cap = self.swap(cap, cap2, ions.animate.set_color(FIRE_HOT),
                        Uncreate(link),
                        mito.animate.stretch(1.15, 0).move_to(RIGHT * 2.2),
                        run_time=1.5)

        self.wait_until(125.5)
        cap2 = self.cap_text("Like a traffic light for yesterday's dinner.", 26)
        tl, red, green = traffic_light(pos=LEFT * 4.3 + UP * 0.3, scale=1.2)
        cap = self.swap(cap, cap2, FadeIn(tl, scale=0.6), run_time=1.6)
        self.traffic = (tl, red, green)

        self.wait_until(128.8)
        cap2 = self.cap_text("Green means: let the fuel roll.", 28)
        # Green -> detach, droplet released and burned.
        fl = flame(scale=1.0, pos=droplet.get_center() + UP * 0.2)
        add_flicker(fl[1]); add_flicker(fl[2])
        cap = self.swap(cap, cap2, green.animate.set_fill(opacity=1.0),
                        red.animate.set_fill(opacity=0.12),
                        mito.animate.move_to(RIGHT * 3.0 + UP * 0.4),
                        run_time=1.5)
        self.play_t(FadeIn(fl, scale=0.4), droplet.animate.scale(0.82),
                    run_time=1.0)

        self.wait_until(131.9)
        cap2 = self.cap_text("Red means: wait a little longer.", 28)
        # Red -> re-tether, fire out, fuel held.
        relink = tether(droplet.get_right(), RIGHT * 1.15 + LEFT * 0.05)
        cap = self.swap(cap, cap2, red.animate.set_fill(opacity=1.0),
                        green.animate.set_fill(opacity=0.12),
                        FadeOut(fl), mito.animate.move_to(RIGHT * 1.15),
                        droplet.animate.scale(1 / 0.82), run_time=1.6)
        self.play_t(Create(relink), run_time=1.0)
        self.mito = mito
        self.droplet = droplet
        self.link = relink
        self.ions = ions
        self._cap = cap

    # ----------------------------------------------------------------
    def the_conversation(self):
        mito, droplet, link = self.mito, self.droplet, self.link
        self.wait_until(136.1)
        cap = self.cap_text("Now here's the beautiful part...", 30)
        tl = self.traffic[0]
        cap = self.enter_cap(cap, FadeOut(tl), FadeOut(self.ions),
                             run_time=1.8)

        self.wait_until(139.3)
        cap = self.swap(cap, self.cap_text("Scientists found it ain't just the fat,", 27),
                        Indicate(droplet, color=FAT, scale_factor=1.15),
                        run_time=1.5)
        self.wait_until(141.5)
        cap = self.swap(cap, self.cap_text("it ain't just the engine—", 28),
                        Indicate(mito, color=MITO, scale_factor=1.12),
                        run_time=1.4)

        self.wait_until(144.3)
        cap2 = self.cap_text("it's the conversation between the two.", 27)
        # Highlight the tether itself as the "conversation".
        conv_glow = soft_blob(link.get_center(), 0.9, MEMBRANE, peak=0.1,
                              layers=12)
        cap = self.swap(cap, cap2, FadeIn(conv_glow),
                        link.animate.set_stroke(width=4, opacity=1.0),
                        run_time=1.6)

        self.wait_until(146.4)
        cap2 = self.cap_text("One little signal...", 30)
        signal = calcium_dot(droplet.get_center(), r=0.09)
        cap = self.swap(cap, cap2, FadeIn(signal, scale=0.3), run_time=1.0)
        self.wait_until(147.9)
        cap2 = self.cap_text("changes everything.", 30)
        # The one ion travels the tether to the mito and lands.
        cap = self.swap(cap, cap2, run_time=0.8)
        self.play_t(signal.animate.move_to(mito.get_center()),
                    Flash(mito.get_center(), color=CA, line_length=0.3),
                    run_time=1.4)

        self.wait_until(150.1)
        cap2 = self.cap_text("A protein says, “Hold on.”", 28)
        # Two proteins at the contact: one holds (NCLX active), one lets go.
        hold = VGroup(
            RoundedRectangle(width=0.5, height=0.28, corner_radius=0.1,
                             color=MEMBRANE, fill_opacity=0.85, stroke_width=0),
            Text("hold on", font_size=15, color=BLACK),
        )
        hold[1].move_to(hold[0])
        hold.next_to(link, UP, buff=0.35)
        let = VGroup(
            RoundedRectangle(width=0.5, height=0.28, corner_radius=0.1,
                             color=FIRE, fill_opacity=0.85, stroke_width=0),
            Text("let go", font_size=15, color=BLACK),
        )
        let[1].move_to(let[0])
        let.next_to(link, DOWN, buff=0.35)
        cap = self.swap(cap, cap2, FadeIn(hold, shift=DOWN * 0.2),
                        Indicate(hold, color=MEMBRANE), run_time=1.6)

        self.wait_until(152.8)
        cap2 = self.cap_text("Another says, “Let go.”", 28)
        cap = self.swap(cap, cap2, FadeIn(let, shift=UP * 0.2),
                        Indicate(let, color=FIRE), run_time=1.6)

        self.wait_until(155.6)
        cap = self.swap(cap, self.cap_text("And suddenly,", 30), run_time=1.0)
        self.wait_until(156.6)
        cap2 = self.cap_text("the body's writing a whole new story.", 27)
        cap = self.swap(cap, cap2, FadeOut(hold), FadeOut(let),
                        FadeOut(conv_glow), FadeOut(signal), run_time=1.6)

        self.wait_until(160.0)
        cap2 = self.cap_text("Alright...  alright...  alright...", 30)
        cap = self.swap(cap, cap2, run_time=1.4)
        self.mito = mito
        self.droplet = droplet
        self.link = link
        self._cap = cap

    # ----------------------------------------------------------------
    def more_than_calories(self):
        self.wait_until(166.0)
        cap = self.cap_text("Maybe that's why we're more than calories.", 27)
        # Zoom out: the single pair becomes many across a tissue.
        cap = self.enter_cap(cap,
                             self.mito.animate.scale(0.4).move_to(RIGHT * 0.4
                                                                  + UP * 0.2),
                             self.droplet.animate.scale(0.4).move_to(LEFT * 0.2
                                                                     + UP * 0.2),
                             FadeOut(self.link), run_time=2.0)

        pairs = VGroup()
        for _ in range(9):
            c = np.array([random.uniform(-5.2, 5.2),
                          random.uniform(-3.0, 2.2), 0])
            d = lipid_droplet(radius=0.32, pos=c, glow=False)
            m = mitochondrion(w=0.66, h=0.38, pos=c + RIGHT * 0.7
                              + UP * random.uniform(-0.2, 0.2), glow=False)
            ln = tether(d.get_right(), m.get_left())
            pairs.add(VGroup(d, ln, m))

        self.wait_until(172.0)
        cap2 = self.cap_text("We're timing...  signals...  conversations...", 27)
        cap = self.swap(cap, cap2, LaggedStartMap(FadeIn, pairs, lag_ratio=0.12,
                                                  scale=0.5), run_time=2.2)

        self.wait_until(179.0)
        cap2 = self.cap_text("A billion tiny decisions made every second,", 26)
        # Signals blink across the field.
        blinks = VGroup(*[calcium_dot(p.get_center(), r=0.05) for p in pairs])
        cap = self.swap(cap, cap2, LaggedStart(*[
            Broadcast(m, focal_point=m.get_center(), n_mobs=2) for m in blinks],
            lag_ratio=0.1), run_time=2.4)

        self.wait_until(185.1)
        cap = self.swap(cap, self.cap_text("without us ever knowing.", 28),
                        run_time=1.4)
        self.wait_until(187.5)
        cap = self.swap(cap, self.cap_text("That's life.", 32), run_time=1.2)
        self.wait_until(190.0)
        self.play_t(FadeOut(pairs), FadeOut(self.mito), FadeOut(self.droplet),
                    run_time=1.5)
        self._cap = cap

    # ----------------------------------------------------------------
    def symphony(self):
        self.wait_until(192.0)
        cap = self.cap_text("The fat knows when...  the fat knows why...", 28)
        # A ring of pulsing organelles -- the cell as an orchestra.
        ring = VGroup()
        n = 10
        for i in range(n):
            a = i / n * TAU
            p = 2.6 * np.array([np.cos(a), np.sin(a) * 0.8, 0])
            if i % 2 == 0:
                node = lipid_droplet(radius=0.34, pos=p, glow=False)
            else:
                node = mitochondrion(w=0.7, h=0.4, pos=p, glow=False)
            ring.add(node)
        strings = VGroup(*[
            Line(ring[i].get_center(), ring[(i + 1) % n].get_center(),
                 color=MEMBRANE, stroke_width=1.5, stroke_opacity=0.4)
            for i in range(n)
        ])
        cap = self.enter_cap(cap, FadeIn(strings), LaggedStartMap(
            FadeIn, ring, lag_ratio=0.08, scale=0.6), run_time=2.4)

        self.wait_until(198.0)
        cap = self.swap(cap, self.cap_text("Nothing in this body ever stands nearby.", 26),
                        run_time=1.4)
        # A pulse travels the ring, node to node.
        self.play_t(LaggedStart(*[
            Indicate(m, color=FIRE_HOT, scale_factor=1.3) for m in ring],
            lag_ratio=0.12), run_time=3.0)

        self.wait_until(203.0)
        cap = self.swap(cap, self.cap_text("Every cell's a working band, every note a helping hand.", 24),
                        run_time=1.5)
        core = soft_blob(ORIGIN, 1.4, FIRE_HOT, peak=0.09, layers=16)
        self.play_t(FadeIn(core), run_time=2.0)

        self.wait_until(208.0)
        cap = self.swap(cap, self.cap_text("We're not machines...  we're symphonies...", 26),
                        run_time=1.5)
        add_breathe(ring, amp=0.04, speed=2.0)
        self.play_t(ring.animate.set_color(FIRE_HOT).set_opacity(0.9),
                    run_time=2.0)

        self.wait_until(213.0)
        cap = self.swap(cap, self.cap_text("playing songs called energy.", 28),
                        Flash(ORIGIN, color=FIRE_HOT, line_length=0.6,
                              num_lines=18, flash_radius=2.8), run_time=1.6)

        self.wait_until(216.5)
        cap = self.swap(cap, self.cap_text("The fat knows when—and now, so do we.", 26),
                        run_time=1.5)
        # Land this fade on the outro's 220.8 anchor.
        self.wait_until(219.2)
        ring.clear_updaters()
        self.play_t(FadeOut(ring), FadeOut(strings), FadeOut(core), run_time=1.6)
        self._cap = cap

    # ----------------------------------------------------------------
    def closing(self):
        # Outro (spoken) -- one droplet, listening, then becoming fuel.
        droplet = lipid_droplet(radius=1.05, pos=ORIGIN)
        add_breathe(droplet, amp=0.03, speed=0.9)
        self.wait_until(220.8)
        cap = self.cap_text("Funny thing...", 30)
        cap = self.enter_cap(cap, FadeIn(droplet, scale=0.7), run_time=1.5)

        self.wait_until(223.0)
        cap = self.swap(cap, self.cap_text("We thought fat was just storage.", 28),
                        run_time=1.4)
        self.wait_until(228.0)
        # "It's listening": a listening pulse ripples inward.
        ear = Circle(radius=1.6, color=CA, stroke_width=2).move_to(droplet)
        cap = self.swap(cap, self.cap_text("Turns out... it's listening.", 29),
                        run_time=1.4)
        self.play_t(ear.animate.scale(0.1).set_stroke(opacity=0), run_time=1.6)

        self.wait_until(230.5)
        cap = self.swap(cap, self.cap_text("Waiting for exactly the right moment,", 27),
                        run_time=1.5)
        self.wait_until(236.0)
        cap2 = self.cap_text("to become tomorrow's fuel.", 29)
        fl = flame(scale=1.3, pos=droplet.get_center() + UP * 0.3)
        add_flicker(fl[1]); add_flicker(fl[2])
        cap = self.swap(cap, cap2, FadeIn(fl, scale=0.3),
                        droplet.animate.scale(0.7), run_time=2.0)

        # Instrumental tail (~240-267): settle into the citation card.
        self.wait_until(241.0)
        self.play_t(FadeOut(cap), FadeOut(fl), FadeOut(droplet), run_time=2.0)

        backdrop = VGroup(
            lipid_droplet(radius=0.5, pos=LEFT * 2.2 + DOWN * 0.2, glow=False),
            mitochondrion(w=1.0, h=0.55, pos=RIGHT * 2.2 + DOWN * 0.2, glow=False),
        ).set_opacity(0.18)
        title = Text("The Fat Knows When", font_size=44, gradient=(FAT, MITO))
        cite = Text("Acín Pérez, Assali, Veliova et al.", font_size=20,
                    color=CALM).next_to(title, DOWN, buff=0.5)
        cite2 = Text("The EMBO Journal (2026)  ·  CNIC & UCLA", font_size=18,
                     color=DIM).next_to(cite, DOWN, buff=0.2)
        self.play_t(FadeIn(backdrop), Write(title), run_time=2.5)
        self.play_t(FadeIn(cite, shift=UP * 0.2), FadeIn(cite2, shift=UP * 0.2),
                    run_time=2.0)
        add_breathe(title, amp=0.012, speed=0.7)
        self.wait_until(265.0)
        title.clear_updaters()
        self.play_t(FadeOut(title), FadeOut(cite), FadeOut(cite2),
                    FadeOut(backdrop), run_time=1.8)
