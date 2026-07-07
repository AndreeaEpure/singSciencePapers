"""Visuals for "One Water, Two Souls" (4:08 song, timed to the vocals).

Based on: Li, L., & Zeng, X. C. (2026). Evidence for the generic existence
of two local structures in liquid water. Nature Physics.

Render (from the manim/ directory):
    manim -pql scenes/one_water_two_souls.py OneWaterTwoSouls   # fast preview
    manim -pqh scenes/one_water_two_souls.py OneWaterTwoSouls   # final 1080p60

Uses Text only (no LaTeX required). If songs/one-water-two-souls/song.mp3
exists it is baked into the rendered video.

Section timestamps come from a Whisper transcription of the actual track:
    0:09  Verse 1 vocals    0:57  "One crowd packed in tight"
    0:44  Verse 2           1:06  Pre-chorus -> Chorus
    1:51  Verse 3 (HDL/LDL) 2:11  Bridge (spoken)
    2:41  Verse 4           3:02  Final chorus (approx.)
    3:36  Outro (spoken)    4:08  end
"""

import random
from pathlib import Path

import numpy as np
from manim import *

# If the Suno MP3 has been downloaded into the song folder, it gets baked
# into the rendered video automatically.
SONG_MP3 = Path(__file__).resolve().parents[2] / "songs" / "one-water-two-souls" / "song.mp3"

OXYGEN = "#4fc3f7"
OXYGEN_DARK = "#1976a8"
HYDROGEN = "#e8ecf1"
LDL_COLOR = "#7aa2f7"   # low-density liquid: open, ordered
HDL_COLOR = "#f7768e"   # high-density liquid: dense, disordered
BOND_COLOR = "#3a4456"
random.seed(7)


def water_molecule(scale=1.0, angle=0.0):
    """A stylized H2O with a highlight for a hint of depth."""
    o = Circle(radius=0.28 * scale, color=OXYGEN, fill_opacity=1,
               stroke_color=OXYGEN_DARK, stroke_width=1.5 * scale)
    shine = Circle(radius=0.09 * scale, color=WHITE, fill_opacity=0.45,
                   stroke_width=0).move_to(o.get_center()
                                           + 0.11 * scale * (UP + LEFT))
    mol = VGroup(o)
    for sign in (-1, 1):
        theta = angle + sign * (104.5 / 2) * DEGREES + 90 * DEGREES
        offset = 0.42 * scale * np.array([np.cos(theta), np.sin(theta), 0])
        bond = Line(o.get_center(), o.get_center() + offset,
                    stroke_width=3 * scale, color=GREY_C)
        h = Circle(radius=0.13 * scale, color=HYDROGEN, fill_opacity=1,
                   stroke_width=0).move_to(o.get_center() + offset)
        mol.add(bond, h)
    mol.add(shine)
    return mol


def molecule_cluster(positions, scale=0.5, bond_pairs=None):
    """Molecules plus dashed hydrogen bonds between the given index pairs."""
    cluster = VGroup()
    bonds = VGroup()
    if bond_pairs:
        for i, j in bond_pairs:
            bonds.add(DashedLine(positions[i], positions[j],
                                 stroke_width=1.6, color=BOND_COLOR,
                                 dash_length=0.08))
    cluster.add(bonds)
    for p in positions:
        cluster.add(water_molecule(scale=scale,
                                   angle=random.uniform(0, TAU)).move_to(p))
    return cluster


def ldl_positions(center, n_ring=6, r=1.1):
    """Open, ordered: hexagonal ring plus center — ice-like tetrahedral order."""
    pts = [center]
    for k in range(n_ring):
        theta = k * TAU / n_ring
        pts.append(center + r * np.array([np.cos(theta), np.sin(theta), 0]))
    return pts


def ldl_bond_pairs(n_ring=6):
    """Center to every ring molecule, plus ring neighbours: an ordered net."""
    pairs = [(0, k) for k in range(1, n_ring + 1)]
    pairs += [(k, k % n_ring + 1) for k in range(1, n_ring + 1)]
    return pairs


def hdl_positions(center, n=7, spread=0.75):
    """Dense, disordered: randomly packed close together."""
    return [
        center + np.array([random.uniform(-spread, spread),
                           random.uniform(-spread, spread), 0])
        for _ in range(n)
    ]


def hdl_bond_pairs(n=7, k=5):
    """A few tangled random bonds: disorder."""
    pairs = set()
    while len(pairs) < k:
        i, j = random.sample(range(n), 2)
        pairs.add((min(i, j), max(i, j)))
    return list(pairs)


def make_ldl_cluster(center):
    return molecule_cluster(ldl_positions(center), bond_pairs=ldl_bond_pairs())


def make_hdl_cluster(center):
    return molecule_cluster(hdl_positions(center), bond_pairs=hdl_bond_pairs())


def droplet(scale=1.0, color=OXYGEN):
    """A stylized water drop."""
    body = Circle(radius=0.5 * scale, color=color, fill_opacity=0.45,
                  stroke_width=3).shift(DOWN * 0.12 * scale)
    tip = Polygon(LEFT * 0.3 * scale + UP * 0.18 * scale,
                  RIGHT * 0.3 * scale + UP * 0.18 * scale,
                  UP * 0.95 * scale,
                  color=color, fill_color=color, fill_opacity=0.45,
                  stroke_width=3)
    return VGroup(body, tip)


def snowflake(scale=0.35, color=WHITE):
    """A six-fold ice crystal built from lines."""
    spoke = VGroup(Line(ORIGIN, UP * scale, stroke_width=2, color=color))
    for frac, side in ((0.55, 0.3), (0.8, 0.18)):
        base = UP * scale * frac
        for ang in (40 * DEGREES, -40 * DEGREES):
            tip = base + rotate_vector(UP * scale * side, ang)
            spoke.add(Line(base, tip, stroke_width=1.5, color=color))
    flake = VGroup(*[spoke.copy().rotate(k * TAU / 6, about_point=ORIGIN)
                     for k in range(6)])
    return flake


def add_bob(mob, amp=0.06, speed=1.4):
    """Gentle floating motion so clusters never sit frozen."""
    mob.bob_t = random.uniform(0, TAU)
    mob.bob_prev = np.zeros(3)

    def upd(m, dt):
        m.bob_t += dt
        off = np.array([0.6 * np.sin(0.7 * speed * m.bob_t),
                        np.sin(speed * m.bob_t), 0]) * amp
        m.shift(off - m.bob_prev)
        m.bob_prev = off

    mob.add_updater(upd)


def remove_bob(mob):
    mob.clear_updaters()
    if hasattr(mob, "bob_prev"):
        mob.shift(-mob.bob_prev)
        mob.bob_prev = np.zeros(3)


class OneWaterTwoSouls(Scene):
    # --- timing helpers: self.t tracks elapsed scene time -------------
    def play_t(self, *anims, run_time=1.0, **kwargs):
        self.play(*anims, run_time=run_time, **kwargs)
        self.t += run_time

    def wait_until(self, t):
        if t > self.t:
            self.wait(t - self.t)
            self.t = t

    # -------------------------------------------------------------------
    def construct(self):
        if SONG_MP3.exists():
            self.add_sound(str(SONG_MP3))
        self.t = 0.0
        self.add_ambient_background()
        self.title_card()          # 0:00 - 0:38   intro + Verse 1
        self.one_molecule()        # 0:38 - 0:57   Verse 2
        self.crowds_intro()        # 0:57 - 1:06   the two crowds
        self.chorus_interchange()  # 1:06 - 1:51   Pre-chorus + Chorus 1
        self.verse3_labels()       # 1:51 - 2:11   Verse 3 (HDL / LDL)
        self.ai_discovery()        # 2:11 - 2:41   Bridge (spoken)
        self.density_anomaly()     # 2:41 - 3:02   Verse 4
        self.finale()              # 3:02 - 3:36   Final chorus
        self.closing()             # 3:36 - 4:08   Outro (spoken)

    def add_ambient_background(self):
        """Faint water molecules drifting up the whole video."""
        ambient = VGroup()
        for _ in range(20):
            m = water_molecule(scale=random.uniform(0.15, 0.35),
                               angle=random.uniform(0, TAU))
            m.set_opacity(random.uniform(0.06, 0.14))
            m.move_to([random.uniform(-7, 7), random.uniform(-4.2, 4.2), 0])
            m.drift = np.array([random.uniform(-0.08, 0.08),
                                random.uniform(0.03, 0.12), 0])
            m.spin = random.uniform(-0.3, 0.3)

            def upd(mob, dt):
                mob.shift(mob.drift * dt)
                mob.rotate(mob.spin * dt)
                if mob.get_center()[1] > 4.6:
                    mob.shift(DOWN * 9.2)

            m.add_updater(upd)
            ambient.add(m)
        self.add(ambient)

    def title_card(self):
        title = Text("One Water, Two Souls", font_size=60,
                     gradient=(LDL_COLOR, HDL_COLOR))
        # A swarm of molecules rushes together and becomes the title.
        swarm = VGroup(*[
            water_molecule(scale=random.uniform(0.25, 0.5),
                           angle=random.uniform(0, TAU)).move_to(
                [random.uniform(-7, 7), random.uniform(-4, 4), 0])
            for _ in range(18)
        ])
        self.add(swarm)
        self.play_t(*[m.animate.move_to(title.get_center()
                                        + np.array([random.uniform(-2.5, 2.5),
                                                    random.uniform(-0.4, 0.4), 0]))
                      for m in swarm], run_time=2.5)
        self.play_t(Write(title), FadeOut(swarm, scale=0.2), run_time=2.5)
        underline = Line(title.get_corner(DL) + DOWN * 0.25,
                         title.get_corner(DR) + DOWN * 0.25,
                         stroke_width=2).set_color_by_gradient(LDL_COLOR,
                                                               HDL_COLOR)
        self.play_t(Create(underline), run_time=1)

        # The roadside bottle, filling with water and rising bubbles.
        store = Text("I picked up a bottle at a roadside store...",
                     font_size=26, color=GREY_B).next_to(underline, DOWN,
                                                         buff=0.5)
        sub1 = Text("Thought I knew what water was.", font_size=26,
                    color=GREY_B).next_to(store, DOWN, buff=0.25)
        sub2 = Text("Clear. Simple. One thing.", font_size=26,
                    color=GREY_B).next_to(sub1, DOWN, buff=0.25)

        body = RoundedRectangle(width=1.5, height=2.4, corner_radius=0.25,
                                stroke_color=GREY_B, stroke_width=3)
        neck = Rectangle(width=0.55, height=0.45, stroke_color=GREY_B,
                         stroke_width=3).next_to(body, UP, buff=0)
        cap = Rectangle(width=0.72, height=0.2, fill_color=GREY_B,
                        fill_opacity=1, stroke_width=0).next_to(neck, UP,
                                                                buff=0)
        bottle = VGroup(body, neck, cap).move_to(LEFT * 5.1 + DOWN * 1.1)
        inner_bottom = body.get_bottom() + UP * 0.08
        water = Rectangle(width=1.3, height=0.02, fill_color=OXYGEN,
                          fill_opacity=0.35, stroke_width=0)
        water.move_to(inner_bottom + UP * 0.01)

        self.wait_until(8.7)
        self.play_t(FadeIn(store, shift=UP * 0.3), Create(bottle), run_time=2)
        self.play_t(water.animate.stretch_to_fit_height(1.7).move_to(
            inner_bottom + UP * 0.85), run_time=1.5)

        bubbles = VGroup()
        for _ in range(3):
            b = Circle(radius=random.uniform(0.04, 0.07), stroke_width=1.5,
                       color=HYDROGEN)
            b.move_to(inner_bottom + UP * random.uniform(0.2, 1.4)
                      + RIGHT * random.uniform(-0.4, 0.4))

            def bub(mob, dt):
                mob.shift(UP * 0.25 * dt)
                if mob.get_center()[1] > inner_bottom[1] + 1.55:
                    mob.shift(DOWN * 1.4)

            b.add_updater(bub)
            bubbles.add(b)
        self.add(bubbles)

        self.wait_until(31.5)
        for b in bubbles:
            b.clear_updaters()
        drop = droplet(scale=1.1).move_to(bottle.get_center())
        self.play_t(FadeIn(sub1, shift=UP * 0.3),
                    Transform(VGroup(bottle, water, bubbles), drop),
                    run_time=1.5)
        self.play_t(Broadcast(Circle(radius=1.6, stroke_color=OXYGEN,
                                     stroke_width=3),
                              focal_point=drop.get_center()), run_time=1.5)
        self.wait_until(34.5)
        # Foreshadowing: the one drop is secretly two.
        drop2 = droplet(scale=1.1, color=HDL_COLOR).move_to(drop.get_center())
        bottle_drop = VGroup(bottle, water, bubbles)
        self.play_t(FadeIn(sub2, shift=UP * 0.3),
                    bottle_drop.animate.shift(LEFT * 0.9),
                    FadeIn(drop2, shift=RIGHT * 0.9), run_time=1.5)
        self.wait_until(36.7)
        self.play_t(FadeOut(title), FadeOut(underline), FadeOut(store),
                    FadeOut(sub1), FadeOut(sub2), FadeOut(bottle_drop),
                    FadeOut(drop2), run_time=1.5)

    def one_molecule(self):
        # The molecule sweeps in, roams, then dances with partners.
        mol = water_molecule(scale=2.0).move_to(LEFT * 6 + UP * 1.5)
        label = Text("Funny how the universe likes to hide\nits biggest secrets inside the smallest sip.",
                     font_size=26, color=GREY_B,
                     line_spacing=1).to_edge(DOWN, buff=0.8)
        self.play_t(FadeIn(mol, scale=0.3), Write(label), run_time=1.5)
        entrance = ArcBetweenPoints(mol.get_center(), ORIGIN, angle=PI / 3)
        self.play_t(MoveAlongPath(mol, entrance), run_time=2.5)
        self.play_t(Rotate(mol, angle=TAU / 6), run_time=3)
        self.play_t(mol.animate.scale(1.18).shift(UP * 0.3), run_time=2,
                    rate_func=there_and_back)
        self.wait_until(50.2)

        # "One dance?" — partners waltz around it.
        n1 = water_molecule(scale=1.1, angle=1.0).move_to(LEFT * 3.4 + UP * 1.4)
        n2 = water_molecule(scale=1.1, angle=4.2).move_to(RIGHT * 3.4 + UP * 1.2)
        b1 = DashedLine(n1.get_center(), ORIGIN, stroke_width=2,
                        color=BOND_COLOR, dash_length=0.1)
        b2 = DashedLine(n2.get_center(), ORIGIN, stroke_width=2,
                        color=BOND_COLOR, dash_length=0.1)
        label2 = Text('"What if water ain\'t just one dance?"', font_size=28,
                      color=GREY_B).to_edge(DOWN, buff=1)
        self.play_t(Transform(label, label2),
                    FadeIn(n1, shift=RIGHT * 0.5), FadeIn(n2, shift=LEFT * 0.5),
                    Create(b1), Create(b2), run_time=1.5)
        dance = VGroup(n1, n2, b1, b2)
        self.play_t(Rotate(dance, PI * 2 / 3, about_point=ORIGIN), run_time=2.5)
        self.wait_until(54.2)

        # "Changin' partners" — a stranger cuts in, bonds re-wire.
        n3 = water_molecule(scale=1.1, angle=2.5).move_to(UP * 2.6)
        label3 = Text("What if every drop keeps changin' partners...",
                      font_size=28, color=GREY_B).to_edge(DOWN, buff=1)
        b1_new = DashedLine(n1.get_center(), n3.get_center(), stroke_width=2,
                            color=BOND_COLOR, dash_length=0.1)
        self.play_t(Transform(label, label3), FadeIn(n3, shift=DOWN * 0.5),
                    Transform(b1, b1_new), run_time=1.5)
        self.wait_until(56.0)
        self.play_t(FadeOut(mol), FadeOut(label), FadeOut(dance),
                    FadeOut(n3), run_time=1.4)

    def crowds_intro(self):
        # 57.4 "One crowd packed in tight" / 59.4 "room to breathe"
        self.hdl = make_hdl_cluster(RIGHT * 3.4)
        self.hdl.kind = "hdl"
        self.hdl.side_center = RIGHT * 3.4
        self.ldl = make_ldl_cluster(LEFT * 3.4)
        self.ldl.kind = "ldl"
        self.ldl.side_center = LEFT * 3.4
        self.caption = Text("One crowd packed in tight.",
                            font_size=30).to_edge(UP)
        self.play_t(Write(self.caption), FadeIn(self.hdl), run_time=1.5)
        add_bob(self.hdl)
        self.wait_until(59.4)
        cap2 = Text("One crowd with a little room to breathe.",
                    font_size=30).to_edge(UP)
        self.play_t(Transform(self.caption, cap2), FadeIn(self.ldl),
                    run_time=1.5)
        add_bob(self.ldl)
        self.wait_until(62.4)
        cap3 = Text("And they're switchin' back and forth...",
                    font_size=30).to_edge(UP)
        self.play_t(Transform(self.caption, cap3), run_time=1)
        self.wait_until(64.4)
        cap4 = Text("faster than we ever imagined.", font_size=30).to_edge(UP)
        self.play_t(Transform(self.caption, cap4), run_time=1)

    def chorus_cycle(self, mode, run_time=3):
        """One chorus beat: morph structures, trade places, or zoom."""
        remove_bob(self.ldl)
        remove_bob(self.hdl)
        maker = {"ldl": make_ldl_cluster, "hdl": make_hdl_cluster}
        if mode == "swap":
            # The crowds physically trade places, arcing through the middle.
            cL, cH = self.ldl.side_center, self.hdl.side_center
            self.ldl.side_center, self.hdl.side_center = cH, cL
            self.play_t(self.ldl.animate(path_arc=PI / 1.6).move_to(cH),
                        self.hdl.animate(path_arc=PI / 1.6).move_to(cL),
                        run_time=run_time)
        elif mode in ("zoomL", "zoomR"):
            big, small = ((self.ldl, self.hdl) if mode == "zoomL"
                          else (self.hdl, self.ldl))
            self.play_t(big.animate.scale(1.3), small.animate.scale(0.8),
                        run_time=run_time)
        else:  # morph: each crowd becomes the other kind, with messengers
            for mob in (self.ldl, self.hdl):
                mob.kind = "hdl" if mob.kind == "ldl" else "ldl"
            newL = maker[self.ldl.kind](self.ldl.side_center)
            newH = maker[self.hdl.kind](self.hdl.side_center)
            m1 = water_molecule(scale=0.4).move_to(self.ldl.side_center + UP * 0.4)
            m2 = water_molecule(scale=0.4).move_to(self.hdl.side_center + DOWN * 0.4)
            arc1 = ArcBetweenPoints(m1.get_center(),
                                    self.hdl.side_center + UP * 0.4,
                                    angle=-PI / 2.5)
            arc2 = ArcBetweenPoints(m2.get_center(),
                                    self.ldl.side_center + DOWN * 0.4,
                                    angle=-PI / 2.5)
            self.add(m1, m2)
            self.play_t(Transform(self.ldl, newL), Transform(self.hdl, newH),
                        MoveAlongPath(m1, arc1), MoveAlongPath(m2, arc2),
                        run_time=run_time)
            self.remove(m1, m2)
        add_bob(self.ldl)
        add_bob(self.hdl)

    def chorus_interchange(self):
        # A faint river flows behind the whole chorus: "One river..."
        def make_river(ph=0.0):
            return FunctionGraph(lambda x: 0.4 * np.sin(0.8 * x + ph) - 0.4,
                                 x_range=[-7.6, 7.6], color=OXYGEN,
                                 stroke_width=55,
                                 stroke_opacity=0.07)

        river = make_river()

        def river_upd(m, dt):
            m.ph = getattr(m, "ph", 0.0) + 1.2 * dt
            m.become(make_river(m.ph))

        beats = [
            (66.4, "Not two glasses... One river...", "morph"),
            (70.9, "Learning two different ways to be itself.", "swap"),
            (75.4, "One water... Two souls...", "morph"),
            (80.0, "One runs fast, one slowly rolls.", "zoomL"),
            (85.0, "One stands close, one leaves some space...", "swap"),
            (90.0, "Both keep changing face to face.", "zoomR"),
            (95.0, "Every ocean... every tear...", "morph"),
            (100.0, "Changing songs while we stand here.", "swap"),
            (104.5, "Dancing where nobody goes.", "morph"),
        ]
        first = True
        for when, text, mode in beats:
            self.wait_until(when)
            new_cap = Text(text, font_size=30).to_edge(UP)
            if first:
                self.add(river)
                self.bring_to_back(river)
                river.add_updater(river_upd)
                first = False
            self.play_t(Transform(self.caption, new_cap), run_time=1)
            self.chorus_cycle(mode, run_time=3)
        self.wait_until(108.8)
        remove_bob(self.ldl)
        remove_bob(self.hdl)
        river.clear_updaters()
        self.play_t(FadeOut(self.ldl), FadeOut(self.hdl),
                    FadeOut(self.caption), FadeOut(river), run_time=2)

    def verse3_labels(self):
        # 110.8 "One side's denser" — HDL takes centre stage alone first.
        heading = Text("One side's denser, a little more crowded.",
                       font_size=30).to_edge(UP)
        hdl = make_hdl_cluster(ORIGIN).scale(1.15)
        hdl_box = SurroundingRectangle(hdl, color=HDL_COLOR, buff=0.35,
                                       corner_radius=0.2)
        hdl_label = Text("high-density water", font_size=24,
                         color=HDL_COLOR).next_to(hdl_box, DOWN)
        hdl_group = VGroup(hdl, hdl_box, hdl_label)
        self.play_t(Write(heading), FadeIn(hdl), Create(hdl_box),
                    Write(hdl_label), run_time=2.5)
        add_bob(hdl_group, amp=0.04)

        # 120.2 "old country road" — it steps aside for LDL.
        self.wait_until(120.2)
        remove_bob(hdl_group)
        heading2 = Text("The other opens up like an old country road.",
                        font_size=30).to_edge(UP)
        ldl = make_ldl_cluster(LEFT * 3.4)
        ldl_box = SurroundingRectangle(ldl, color=LDL_COLOR, buff=0.35,
                                       corner_radius=0.2)
        ldl_label = Text("low-density water", font_size=24,
                         color=LDL_COLOR).next_to(ldl_box, DOWN)
        ldl_group = VGroup(ldl, ldl_box, ldl_label)
        self.play_t(Transform(heading, heading2),
                    hdl_group.animate.scale(1 / 1.15).shift(RIGHT * 3.4),
                    FadeIn(ldl_group, shift=RIGHT * 0.8), run_time=2.5)
        add_bob(hdl_group, amp=0.04)
        add_bob(ldl_group, amp=0.04)

        self.wait_until(126.8)
        heading3 = Text("same molecules... different arrangement.",
                        font_size=30).to_edge(UP)
        arrow = DoubleArrow(LEFT * 1.6, RIGHT * 1.6, buff=0.2,
                            stroke_width=3, color=GREY_B,
                            max_tip_length_to_length_ratio=0.08)
        self.play_t(Transform(heading, heading3), GrowFromCenter(arrow),
                    run_time=1.5)
        self.wait_until(129.3)
        remove_bob(hdl_group)
        remove_bob(ldl_group)
        self.play_t(FadeOut(heading), FadeOut(hdl_group), FadeOut(ldl_group),
                    FadeOut(arrow), run_time=1.5)

    def ai_discovery(self):
        # Bridge, spoken: 130.8 - 161
        heading = Text("Now here's the wild part...", font_size=30).to_edge(UP)
        self.play_t(Write(heading), run_time=2)

        self.wait_until(135.0)
        heading2 = Text("They just handed it millions and millions\nof snapshots of water molecules.",
                        font_size=28, line_spacing=1).to_edge(UP)
        dots = VGroup(*[
            Dot([random.uniform(-5.5, 5.5), random.uniform(-2.6, 1.4), 0],
                radius=0.05, color=GREY_B)
            for _ in range(140)
        ])
        self.play_t(Transform(heading, heading2), run_time=1.5)
        self.play_t(LaggedStartMap(FadeIn, dots, lag_ratio=0.015), run_time=3.5)

        # The AI "reads" the data: a scanning beam sweeps the snapshots.
        beam = Rectangle(width=1.0, height=4.6, stroke_width=0,
                         fill_color=LDL_COLOR, fill_opacity=0.18)
        beam.move_to(LEFT * 6.5 + DOWN * 0.6)
        self.add(beam)
        self.play_t(beam.animate.shift(RIGHT * 13), run_time=2.5)
        self.remove(beam)

        self.wait_until(143.0)
        heading3 = Text('No clues. No answer sheet. Just... "Take a look."',
                        font_size=30).to_edge(UP)
        self.play_t(Transform(heading, heading3), run_time=1.5)

        self.wait_until(148.0)
        anims = []
        for i, d in enumerate(dots):
            if i % 2 == 0:
                center, color = LEFT * 3.2 + DOWN * 0.6, HDL_COLOR
                spread = (0.7, 0.5)   # tight: high density
            else:
                center, color = RIGHT * 3.2 + DOWN * 0.6, LDL_COLOR
                spread = (1.2, 0.9)   # open: low density
            target = center + np.array([random.gauss(0, spread[0]),
                                        random.gauss(0, spread[1]), 0])
            anims.append(d.animate.move_to(target).set_color(color))
        label = Text("And that AI found two hidden neighborhoods inside every drop...",
                     font_size=24, color=GREY_B).to_edge(DOWN, buff=0.6)
        self.play_t(*anims, Write(label), run_time=4)

        hull_h = Circle(radius=1.6, color=HDL_COLOR, stroke_width=2)
        hull_h.stretch(0.75, 1).move_to(LEFT * 3.2 + DOWN * 0.6)
        hull_l = Circle(radius=2.0, color=LDL_COLOR, stroke_width=2)
        hull_l.stretch(0.8, 1).move_to(RIGHT * 3.2 + DOWN * 0.6)
        tag_h = Text("HDL", font_size=24, color=HDL_COLOR).next_to(hull_h, UP)
        tag_l = Text("LDL", font_size=24, color=LDL_COLOR).next_to(hull_l, UP)

        self.wait_until(153.0)
        heading4 = Text("like discovering two different heartbeats\ninside the very same song.",
                        font_size=28, line_spacing=1).to_edge(UP)
        self.play_t(Transform(heading, heading4), Create(hull_h),
                    Create(hull_l), FadeIn(tag_h), FadeIn(tag_l), run_time=1.5)
        self.wait_until(159.0)
        self.play_t(FadeOut(dots), FadeOut(heading), FadeOut(label),
                    FadeOut(hull_h), FadeOut(hull_l), FadeOut(tag_h),
                    FadeOut(tag_l), run_time=2)

    def density_anomaly(self):
        # Verse 4, approx. 161 - 182 (Whisper lost the vocals here)
        heading = Text("Maybe that's why water acts so strange.",
                       font_size=30).to_edge(UP)
        axes = Axes(
            x_range=[-8, 20, 4], y_range=[0.9985, 1.0002, 0.0005],
            x_length=9, y_length=4,
            axis_config={"include_numbers": False, "include_tip": False},
        ).shift(DOWN * 0.6)
        x_label = Text("temperature (°C)", font_size=22, color=GREY_B)
        x_label.next_to(axes.x_axis, DOWN, buff=0.45)
        y_label = Text("density", font_size=22, color=GREY_B)
        y_label.rotate(90 * DEGREES).next_to(axes.y_axis, LEFT, buff=0.3)
        ticks = VGroup(*[
            Text(str(x), font_size=16, color=GREY_C).next_to(
                axes.coords_to_point(x, 0.9985), DOWN, buff=0.15)
            for x in (-8, -4, 0, 4, 8, 12, 16, 20)
        ])
        curve = axes.plot(lambda t: 1.0 - 2.2e-6 * (t - 4) ** 2,
                          x_range=[-8, 20], color=OXYGEN)
        # Shade the anomalous side: below 4 C, colder means lighter.
        area = axes.get_area(curve, x_range=(-8, 4), color=LDL_COLOR,
                             opacity=0.15)
        tracer = Dot(color=WHITE, radius=0.06)
        peak = axes.coords_to_point(4, 1.0)
        dot = Dot(peak, color=YELLOW)
        peak_label = Text("heavier until four degrees... then starts pushin' back",
                          font_size=24, color=YELLOW)
        peak_label.next_to(dot, UP, buff=0.3)

        self.play_t(Write(heading), Create(axes), FadeIn(x_label),
                    FadeIn(y_label), FadeIn(ticks), run_time=2.5)
        self.play_t(Create(curve), MoveAlongPath(tracer, curve.copy()),
                    run_time=3)
        self.play_t(FadeIn(dot, scale=2), Write(peak_label), FadeIn(area),
                    FadeOut(tracer), run_time=2)
        self.wait_until(171.5)

        chart = VGroup(axes, x_label, y_label, ticks, curve, area, dot,
                       peak_label)
        note = Text("Why ice floats instead of sinkin'...", font_size=28,
                    color=GREY_B).to_edge(UP)
        self.play_t(FadeOut(chart), Transform(heading, note), run_time=2)

        # Ice bobbing on gently waving water.
        water = Rectangle(width=6, height=1.6, stroke_width=0,
                          fill_color=OXYGEN, fill_opacity=0.3).shift(DOWN * 1.2)
        surface = FunctionGraph(lambda x: 0.06 * np.sin(3 * x),
                                x_range=[-3, 3], color=OXYGEN,
                                stroke_width=3).move_to(water.get_top())

        def wave_upd(m, dt):
            m.ph = getattr(m, "ph", 0.0) + 2.5 * dt
            m.become(FunctionGraph(lambda x: 0.06 * np.sin(3 * x + m.ph),
                                   x_range=[-3, 3], color=OXYGEN,
                                   stroke_width=3).move_to(water.get_top()))

        ice = Square(side_length=0.9, stroke_color=WHITE, stroke_width=2,
                     fill_color=HYDROGEN, fill_opacity=0.8)
        ice.move_to(water.get_top() + UP * 0.15)
        flake = snowflake(scale=0.28, color=GREY_C).move_to(ice.get_center())
        berg = VGroup(ice, flake)
        self.play_t(FadeIn(water), FadeIn(surface),
                    FadeIn(berg, shift=DOWN * 0.5), run_time=2)
        surface.add_updater(wave_upd)
        for angle in (3 * DEGREES, -3 * DEGREES):
            self.play_t(berg.animate.shift(DOWN * 0.12).rotate(angle),
                        run_time=1.5, rate_func=there_and_back)
        self.wait_until(180.0)
        surface.clear_updaters()
        self.play_t(FadeOut(water), FadeOut(surface), FadeOut(berg),
                    FadeOut(heading), run_time=2)

    def finale(self):
        # Final chorus, approx. 182 - 215.5: the two souls are one water.
        left = molecule_cluster(hdl_positions(LEFT * 3.2, n=8), scale=0.45)
        right = molecule_cluster(ldl_positions(RIGHT * 3.2, r=1.0), scale=0.45)
        for group, color in [(left, HDL_COLOR), (right, LDL_COLOR)]:
            for m in group[1:]:
                m[0].set_fill(color).set_stroke(color)
        self.play_t(FadeIn(left), FadeIn(right), run_time=2)

        ring_pts = ldl_positions(ORIGIN, n_ring=14, r=2.2)[1:]
        all_mols = VGroup(*left[1:], *right[1:])
        halo = Circle(radius=2.2, stroke_width=3)
        halo.set_color_by_gradient(LDL_COLOR, HDL_COLOR)

        def halo_upd(m, dt):
            m.ph = getattr(m, "ph", 0.0) + dt
            m.set_stroke(width=3 + 2 * np.sin(2 * m.ph),
                         opacity=0.5 + 0.3 * np.sin(2 * m.ph))

        twinkles = VGroup()
        for _ in range(18):
            s = Dot([random.uniform(-6.5, 6.5), random.uniform(-3.6, 3.6), 0],
                    radius=0.03, color=WHITE)
            s.ph = random.uniform(0, TAU)

            def tw_upd(m, dt):
                m.ph += dt
                m.set_opacity(0.25 + 0.25 * np.sin(3 * m.ph))

            s.add_updater(tw_upd)
            twinkles.add(s)

        anims = [m.animate.move_to(p)
                 for m, p in zip(all_mols, ring_pts + ring_pts)]
        self.play_t(*anims, Create(halo), FadeIn(twinkles), run_time=4)
        halo.add_updater(halo_upd)

        text1 = Text("One water... Two souls...", font_size=40,
                     gradient=(LDL_COLOR, HDL_COLOR))
        self.play_t(Write(text1), Rotate(all_mols, PI / 5, about_point=ORIGIN),
                    run_time=5)
        self.wait_until(196.0)

        text2 = Text("Always new... Changing... So life... can change too.",
                     font_size=28, color=GREY_B).next_to(text1, DOWN, buff=0.5)
        self.play_t(FadeIn(text2, shift=UP * 0.3),
                    Rotate(all_mols, PI / 5, about_point=ORIGIN), run_time=5)
        self.play_t(Rotate(all_mols, PI / 6, about_point=ORIGIN), run_time=5)
        self.play_t(Rotate(all_mols, PI / 6, about_point=ORIGIN), run_time=5)
        self.wait_until(213.5)
        halo.clear_updaters()
        for s in twinkles:
            s.clear_updaters()
        self.play_t(FadeOut(all_mols), FadeOut(halo), FadeOut(twinkles),
                    FadeOut(text1), FadeOut(text2), run_time=2)

    def closing(self):
        # Outro, spoken: 215.5 - 248
        backdrop = water_molecule(scale=3.5).set_opacity(0.07)
        trick = Text("Maybe that's nature's favorite trick...",
                     font_size=30, color=GREY_B).shift(UP * 2)
        line1 = Text("Looking simple...\nwhile carrying more than one truth at the same time.",
                     font_size=30, line_spacing=1.2,
                     gradient=(LDL_COLOR, HDL_COLOR)).next_to(trick, DOWN, buff=0.7)
        line2 = Text("How many other ordinary things are extraordinary...\nonce you finally learn how to look.",
                     font_size=26, color=GREY_B,
                     line_spacing=1.2).next_to(line1, DOWN, buff=0.7)
        cite = Text("Li & Zeng (2026), Nature Physics", font_size=22,
                    color=GREY_C).next_to(line2, DOWN, buff=0.8)
        self.play_t(Write(trick), FadeIn(backdrop), run_time=2)
        self.wait_until(220.3)
        self.play_t(FadeIn(line1, shift=UP * 0.3), run_time=2)
        self.wait_until(228.3)
        self.play_t(FadeIn(line2, shift=UP * 0.3), run_time=2)
        self.wait_until(238.0)
        self.play_t(FadeIn(cite, shift=UP * 0.3), run_time=1.5)
        self.wait_until(245.5)
        self.play_t(FadeOut(trick), FadeOut(line1), FadeOut(line2),
                    FadeOut(cite), FadeOut(backdrop), run_time=2)
        self.wait_until(248.5)
