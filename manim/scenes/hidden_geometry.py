"""Visuals for "Hidden Geometry" (2:32 song, timed to the vocals).

Based on: Sala, Mercaldo, Domi, Gariglio, Cuoco, Ortix & Caviglia,
"The quantum metric of electrons with spin-momentum locking",
Science 389, 822-825 (2025). University of Geneva.

The paper shows that spin-momentum locking (spin direction tied to
momentum direction) at spin-orbit-coupled interfaces produces a
measurable "quantum metric" -- a geometric curvature of the electron's
quantum state, previously only theoretical, now directly detected via
nonlinear magnetoresistance in ordinary oxide interfaces (not just
exotic topological materials).

Render (from the manim/ directory):
    manim -pql scenes/hidden_geometry.py HiddenGeometry   # fast preview
    manim -pqh scenes/hidden_geometry.py HiddenGeometry   # final 1080p60

Uses Text only (no LaTeX required). If songs/hidden-geometry/song.mp3
exists it is baked into the rendered video.

Timestamps 0-58s are confirmed by two independent Whisper passes.
58s-152s is estimated (Whisper couldn't parse that stretch -- likely
heavier reverb/quieter mix), paced evenly between the last solid
anchor and the end of the track.

Caption changes always crossfade (FadeOut old + FadeIn new) rather than
Transform -- Transform between two different text strings morphs
individual glyph shapes into each other, which is unreadable mid-flight
whenever the strings differ and the animation runs more than a beat.
"""

import random
from pathlib import Path

import numpy as np
from manim import *

SONG_MP3 = Path(__file__).resolve().parents[2] / "songs" / "hidden-geometry" / "song.mp3"

GEO_A = "#a78bfa"      # violet
GEO_B = "#2dd4bf"      # teal
ATOM_A = "#f4a261"     # warm amber (e.g. LaAlO3 layer)
ATOM_B = "#457b9d"     # steel blue (e.g. SrTiO3 layer)
BOND_COLOR = "#3a4456"
CHALK = "#c9c9c9"
ELECTRON = "#ffe66d"
random.seed(11)


# --------------------------------------------------------------------------
# Shared building blocks
# --------------------------------------------------------------------------

def crystal_lattice(rows=3, cols=5, spacing=0.85, color_a=ATOM_A, color_b=ATOM_B):
    """A small bilayer crystal: two rows of atoms per layer, alternating colors,
    connected by a bond lattice."""
    atoms = VGroup()
    positions = {}
    for r in range(rows):
        for c in range(cols):
            p = np.array([(c - (cols - 1) / 2) * spacing,
                          (r - (rows - 1) / 2) * spacing, 0])
            color = color_a if r < rows / 2 else color_b
            dot = Circle(radius=0.15, color=color, fill_opacity=1,
                        stroke_width=0).move_to(p)
            atoms.add(dot)
            positions[(r, c)] = p
    bonds = VGroup()
    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                bonds.add(Line(positions[(r, c)], positions[(r, c + 1)],
                               stroke_width=1.5, color=BOND_COLOR))
            if r + 1 < rows:
                bonds.add(Line(positions[(r, c)], positions[(r + 1, c)],
                               stroke_width=1.5, color=BOND_COLOR))
    return VGroup(bonds, atoms)


def landscape(bumps, x_range=(-4, 4), color=GEO_A, stroke_width=3.5):
    """A hills-and-valleys curve: bumps = [(center_x, height, width), ...]."""
    def f(x):
        return sum(h * np.exp(-((x - cx) ** 2) / (2 * w ** 2))
                   for cx, h, w in bumps)
    return FunctionGraph(f, x_range=list(x_range), color=color,
                         stroke_width=stroke_width), f


def dashed(mobject, num_dashes=24, color=None):
    d = DashedVMobject(mobject, num_dashes=num_dashes, dashed_ratio=0.55)
    if color:
        d.set_color(color)
    return d


def spin_orbit_group(center=ORIGIN, radius=1.4, color=GEO_B):
    """A circular momentum-space orbit with a spin arrow locked tangential
    to the electron's momentum direction as it goes around -- the paper's
    central mechanism."""
    ring = Circle(radius=radius, color=GREY_C, stroke_width=1.5).move_to(center)
    theta = ValueTracker(0)

    electron = Dot(color=ELECTRON, radius=0.09)
    spin_arrow = Arrow(ORIGIN, RIGHT * 0.5, buff=0, stroke_width=4,
                       color=color, max_tip_length_to_length_ratio=0.4)

    def upd_electron(m):
        t = theta.get_value()
        m.move_to(center + radius * np.array([np.cos(t), np.sin(t), 0]))

    def upd_spin(m):
        t = theta.get_value()
        pos = center + radius * np.array([np.cos(t), np.sin(t), 0])
        tangent = np.array([-np.sin(t), np.cos(t), 0])
        m.put_start_and_end_on(pos, pos + 0.55 * tangent)

    electron.add_updater(upd_electron)
    spin_arrow.add_updater(upd_spin)
    upd_electron(electron)
    upd_spin(spin_arrow)
    return VGroup(ring, electron, spin_arrow), theta


def add_drift(mob, amp=0.06, speed=1.2):
    mob.drift_t = random.uniform(0, TAU)
    mob.drift_prev = np.zeros(3)

    def upd(m, dt):
        m.drift_t += dt
        off = np.array([0.5 * np.sin(0.6 * speed * m.drift_t),
                        np.sin(speed * m.drift_t), 0]) * amp
        m.shift(off - m.drift_prev)
        m.drift_prev = off

    mob.add_updater(upd)


def remove_drift(mob):
    mob.clear_updaters()
    if hasattr(mob, "drift_prev"):
        mob.shift(-mob.drift_prev)
        mob.drift_prev = np.zeros(3)


class HiddenGeometry(Scene):
    def play_t(self, *anims, run_time=1.0, **kwargs):
        self.play(*anims, run_time=run_time, **kwargs)
        self.t += run_time

    def wait_until(self, t):
        if t > self.t:
            self.wait(t - self.t)
            self.t = t

    def swap(self, old, new, *extra_anims, run_time=1.2):
        """Crossfade a caption to new text (never Transform dissimilar text --
        it morphs glyph shapes into unreadable mush). Returns the new mobject
        so callers reassign their local variable to it."""
        self.play_t(FadeOut(old), FadeIn(new), *extra_anims, run_time=run_time)
        return new

    # ----------------------------------------------------------------
    def construct(self):
        if SONG_MP3.exists():
            self.add_sound(str(SONG_MP3))
        self.t = 0.0
        self.add_ambient_background()
        self.title_and_secret()      # 0:00 - 0:33   "secret world... no eyes could reach"
        self.folded_in_matter()      # 0:33 - 0:58   "geometry folded... softer language"
        self.hills_and_valleys()     # 0:58 - 1:20   "they curve... feels like it"
        self.theory_to_measured()    # 1:20 - 1:51   "once it lived only in theory... where to go"
        self.zoom_to_spacetime()     # 1:51 - 2:25   "maybe spacetime... more curved than we imagine"
        self.closing()               # 2:25 - 2:32   citation

    def add_ambient_background(self):
        """Faint lattice specks drifting through the whole video."""
        ambient = VGroup()
        for _ in range(16):
            dot = Circle(radius=random.uniform(0.03, 0.07),
                        color=random.choice([GEO_A, GEO_B, CHALK]),
                        fill_opacity=random.uniform(0.08, 0.16),
                        stroke_width=0)
            dot.move_to([random.uniform(-7, 7), random.uniform(-4.2, 4.2), 0])
            dot.drift = np.array([random.uniform(-0.05, 0.05),
                                  random.uniform(0.02, 0.08), 0])

            def upd(m, dt):
                m.shift(m.drift * dt)
                if m.get_center()[1] > 4.6:
                    m.shift(DOWN * 9.2)

            dot.add_updater(upd)
            ambient.add(dot)
        self.add(ambient)

    # ----------------------------------------------------------------
    def title_and_secret(self):
        title = Text("Hidden Geometry", font_size=58, gradient=(GEO_A, GEO_B))
        self.play_t(Write(title), run_time=2.5)
        self.wait_until(1.5)
        line1 = Text("There's a secret world beneath the things we touch,",
                     font_size=27, color=CHALK).to_edge(DOWN, buff=1.1)
        self.play_t(title.animate.scale(0.55).to_edge(UP, buff=0.7),
                    FadeIn(line1, shift=UP * 0.3), run_time=1.5)

        # An ordinary flat grid -- nothing special to see yet.
        grid = NumberPlane(x_range=[-6, 6, 1], y_range=[-3.2, 3.2, 1],
                           background_line_style={"stroke_color": GREY_D,
                                                  "stroke_width": 1,
                                                  "stroke_opacity": 0.4},
                           axis_config={"stroke_opacity": 0})
        self.play_t(FadeIn(grid), run_time=2)

        self.wait_until(20.8)
        line2 = Text("not written in equations alone,", font_size=27,
                     color=CHALK).to_edge(DOWN, buff=1.1)
        # A few faint equation glyphs flicker and dismiss themselves.
        glyphs = VGroup(*[
            Text(s, font_size=30, color=GREY_C).move_to(
                [random.uniform(-4, 4), random.uniform(-1.5, 1.5), 0])
            for s in ("E=mc²", "F=ma", "∇×B", "ψ(x,t)")
        ]).set_opacity(0.35)
        line1 = self.swap(line1, line2, FadeIn(glyphs), run_time=1.3)
        self.play_t(FadeOut(glyphs, shift=UP * 0.3), run_time=1.5)

        self.wait_until(24.8)
        line3 = Text("but in the way the universe bends itself,", font_size=27,
                     color=CHALK).to_edge(DOWN, buff=1.1)
        curve, f = landscape([(-2, 0.9, 0.9), (1.5, -0.7, 1.0)],
                             color=GEO_A, stroke_width=3)
        # The grid-to-curve morph IS meant to look like a chaotic collapse --
        # keep that Transform, just crossfade the caption around it.
        line1 = self.swap(line1, line3, Transform(grid, curve), run_time=2)

        self.wait_until(28.9)
        line4 = Text("where no eyes could ever reach.", font_size=27,
                     color=CHALK).to_edge(DOWN, buff=1.1)
        line1 = self.swap(line1, line4, grid.animate.set_opacity(0.25),
                          run_time=2)
        self.wait_until(32.3)
        self.play_t(FadeOut(grid), FadeOut(line1), FadeOut(title), run_time=1.5)

    # ----------------------------------------------------------------
    def folded_in_matter(self):
        cap = Text("A geometry folded inside matter,", font_size=30).to_edge(UP)
        lattice = crystal_lattice().scale(1.1)
        add_drift(lattice, amp=0.03)
        self.play_t(Write(cap), FadeIn(lattice, scale=0.8), run_time=2.5)

        self.wait_until(37.1)
        cap2 = Text("woven through lattices and charges,", font_size=30).to_edge(UP)
        pulses = VGroup(*[
            Circle(radius=0.05, color=ELECTRON, fill_opacity=0.9,
                  stroke_width=0).move_to(a.get_center())
            for a in lattice[1][::3]
        ])
        cap = self.swap(cap, cap2, FadeIn(pulses, scale=2), run_time=1.3)
        self.play_t(FadeOut(pulses), run_time=1)

        self.wait_until(41.1)
        cap3 = Text("quiet as a law that never needed a witness,",
                    font_size=28).to_edge(UP)
        remove_drift(lattice)
        cap = self.swap(cap, cap3, lattice.animate.scale(1.4), run_time=2)

        self.wait_until(45.3)
        cap4 = Text("small enough to live between atoms,", font_size=28).to_edge(UP)
        # Zoom into one gap: a tiny hidden landscape sitting between two atoms.
        gap_center = lattice[1][6].get_center() * 0.5 + lattice[1][7].get_center() * 0.5
        rings = VGroup(*[
            Circle(radius=r, color=GEO_B, stroke_width=2,
                  stroke_opacity=0.8 - 0.2 * i).move_to(gap_center)
            for i, r in enumerate((0.35, 0.24, 0.13))
        ])
        cap = self.swap(cap, cap4, FadeIn(rings, scale=0.3), run_time=1.5)

        self.wait_until(50.1)
        cap5 = Text("yet strong enough to steer electrons", font_size=28).to_edge(UP)
        electron = Dot(color=ELECTRON, radius=0.09).move_to(LEFT * 4 + UP * 0.6)
        path = VMobject(color=ELECTRON, stroke_width=2)
        path.set_points_as_corners([electron.get_center(), electron.get_center()])
        cap = self.swap(cap, cap5, FadeIn(electron), run_time=1)

        def trail_upd(m):
            m.add_points_as_corners([electron.get_center()])

        path.add_updater(trail_upd)
        self.add(path)

        self.wait_until(54.1)
        cap6 = Text("as if gravity had learned a softer language.",
                    font_size=28).to_edge(UP)
        cap = self.swap(cap, cap6, run_time=1)
        # The electron's path visibly bends as it passes the hidden gap,
        # caption now settled so the motion reads clearly on its own.
        bend_path = ArcBetweenPoints(LEFT * 4 + UP * 0.6, RIGHT * 4 + UP * 0.2,
                                     angle=-PI / 2.2)
        self.play_t(MoveAlongPath(electron, bend_path), run_time=3)
        path.clear_updaters()

        self.wait_until(58.1)
        self.play_t(FadeOut(cap), FadeOut(lattice), FadeOut(rings),
                    FadeOut(electron), FadeOut(path), run_time=1.5)

    # ----------------------------------------------------------------
    def hills_and_valleys(self):
        cap = Text("They don't just move forward—", font_size=30).to_edge(UP)
        self.play_t(Write(cap), run_time=1.5)

        self.wait_until(63.0)
        cap2 = Text("they curve, they hesitate,", font_size=30).to_edge(UP)
        curve, f = landscape([(-2.6, 0.7, 0.7), (-0.5, -0.9, 0.6),
                              (1.3, 0.5, 0.6), (2.8, -0.5, 0.5)])
        ball = Dot(color=ELECTRON, radius=0.1)
        x_tracker = ValueTracker(-3.6)

        def ball_upd(m):
            x = x_tracker.get_value()
            m.move_to([x, f(x), 0])

        ball.add_updater(ball_upd)
        cap = self.swap(cap, cap2, Create(curve), FadeIn(ball), run_time=1.3)
        self.play_t(x_tracker.animate.set_value(-1.8), run_time=1.5,
                    rate_func=there_and_back)

        self.wait_until(67.0)
        cap3 = Text("they trace invisible hills and valleys", font_size=28).to_edge(UP)
        cap = self.swap(cap, cap3, run_time=1)
        # Caption settled -- let the ball roll the full landscape on its own.
        self.play_t(x_tracker.animate.set_value(3.6), run_time=4,
                    rate_func=linear)

        self.wait_until(73.0)
        cap4 = Text("mapped by something that isn't quite space,\nbut feels like it.",
                    font_size=27, line_spacing=1).to_edge(UP)
        ball.clear_updaters()
        cap = self.swap(cap, cap4, run_time=1.5)
        self.wait_until(79.5)
        self.play_t(FadeOut(cap), FadeOut(curve), FadeOut(ball), run_time=1.5)
        self.hidden_curve_f = f

    # ----------------------------------------------------------------
    def theory_to_measured(self):
        # Chalk-era: a faint, uncertain sketch of the idea.
        cap = Text("Once it lived only in theory,\na rumour in chalk dust,",
                   font_size=28, color=CHALK, line_spacing=1.2).to_edge(UP)
        ghost_curve, _ = landscape([(-2.6, 0.7, 0.7), (-0.5, -0.9, 0.6),
                                    (1.3, 0.5, 0.6), (2.8, -0.5, 0.5)],
                                   color=CHALK)
        ghost = dashed(ghost_curve, color=CHALK)
        ghost.set_opacity(0.5)
        tensor = VGroup(*[
            Square(0.55, color=CHALK, stroke_width=1.5, stroke_opacity=0.5)
            for _ in range(4)
        ]).arrange_in_grid(2, 2, buff=0.05).shift(DOWN * 1.6 + RIGHT * 4.2)
        labels = VGroup(*[
            Text(s, font_size=16, color=CHALK).move_to(sq)
            for s, sq in zip(("gxx", "gxy", "gyx", "gyy"), tensor)
        ]).set_opacity(0.6)
        self.play_t(Write(cap), Create(ghost), FadeIn(tensor), FadeIn(labels),
                    run_time=2.5)

        self.wait_until(87.0)
        cap2 = Text("a prediction waiting for courage.", font_size=28,
                    color=CHALK).to_edge(UP)
        cap = self.swap(cap, cap2, ghost.animate.set_opacity(0.2), run_time=1.5)
        self.play_t(ghost.animate.set_opacity(0.55), run_time=1.5)

        self.wait_until(92.0)
        # The reveal: dashed becomes solid, a real crystal interface appears,
        # spin-momentum locking drives the measurement.
        cap3 = Text("Now it's measured, observed, confirmed—",
                    font_size=30, gradient=(GEO_A, GEO_B)).to_edge(UP)
        solid_curve, _ = landscape([(-2.6, 0.7, 0.7), (-0.5, -0.9, 0.6),
                                    (1.3, 0.5, 0.6), (2.8, -0.5, 0.5)],
                                   color=GEO_A, stroke_width=4)
        solid_curve.shift(DOWN * 1.6)
        ghost_target = ghost.copy().shift(DOWN * 1.6)
        data_pts = VGroup(*[
            Dot(solid_curve.point_from_proportion(p), color=ELECTRON,
               radius=0.06)
            for p in np.linspace(0.05, 0.95, 10)
        ])
        cap = self.swap(cap, cap3, Transform(ghost, ghost_target),
                        FadeOut(tensor), FadeOut(labels), run_time=1.5)
        self.play_t(Transform(ghost, solid_curve), FadeIn(data_pts, scale=1.5),
                    run_time=2.5)

        self.wait_until(98.0)
        cap4 = Text("proof that even at the smallest scales\nthere are landscapes, there are fields,",
                   font_size=26, line_spacing=1.2).to_edge(UP)
        orbit, theta = spin_orbit_group(center=UP * 1.3 + LEFT * 4, radius=0.9)
        b_arrow = Arrow(UP * 2.6 + LEFT * 4, UP * 1.9 + LEFT * 4,
                        color=GEO_B, stroke_width=3)
        b_label = Text("B", font_size=20, color=GEO_B).next_to(b_arrow, UP,
                                                               buff=0.1)
        cap = self.swap(cap, cap4, FadeIn(orbit), FadeIn(b_arrow),
                        FadeIn(b_label), run_time=1.5)
        self.play_t(theta.animate.set_value(TAU * 1.4), run_time=4.5,
                    rate_func=linear)

        self.wait_until(105.0)
        cap5 = Text("there are shapes that tell particles where to go.",
                   font_size=27).to_edge(UP)
        ball2 = Dot(color=ELECTRON, radius=0.1)
        x2 = ValueTracker(-3.6)

        def ball2_upd(m):
            x = x2.get_value()
            m.move_to([x, self.hidden_curve_f(x) - 1.6, 0])

        ball2.add_updater(ball2_upd)
        cap = self.swap(cap, cap5, FadeIn(ball2), run_time=1)
        self.play_t(x2.animate.set_value(3.6), run_time=4.5, rate_func=linear)

        self.wait_until(111.0)
        orbit.clear_updaters()
        ball2.clear_updaters()
        self.play_t(FadeOut(cap), FadeOut(ghost), FadeOut(data_pts),
                    FadeOut(orbit), FadeOut(b_arrow), FadeOut(b_label),
                    FadeOut(ball2), run_time=2)

    # ----------------------------------------------------------------
    def zoom_to_spacetime(self):
        cap = Text("So maybe spacetime isn't just out there,\nstretching between stars and black holes.",
                   font_size=27, line_spacing=1.2).to_edge(UP)
        lattice = crystal_lattice(rows=3, cols=5, spacing=0.6).scale(0.8)
        self.play_t(Write(cap), FadeIn(lattice, scale=0.6), run_time=2)

        stars = VGroup(*[
            Dot([random.uniform(-6.5, 6.5), random.uniform(-3.5, 3.5), 0],
               radius=random.uniform(0.02, 0.045), color=WHITE)
            for _ in range(40)
        ]).set_opacity(0)
        self.play_t(lattice.animate.scale(0.3).set_opacity(0.5),
                    stars.animate.set_opacity(0.7), run_time=3)

        funnel, _ = landscape([(0, -1.6, 1.6)], x_range=(-4, 4),
                              color=GEO_A, stroke_width=4)
        hole = Circle(radius=0.12, color=BLACK, fill_opacity=1,
                     stroke_color=GEO_B, stroke_width=2).move_to(DOWN * 1.6)
        self.play_t(Create(funnel), FadeIn(hole, scale=0.3), run_time=2)

        self.wait_until(119.0)
        cap2 = Text("Maybe it's everywhere—hidden in the ordinary,",
                   font_size=27).to_edge(UP)
        cap = self.swap(cap, cap2, FadeOut(funnel), FadeOut(hole),
                        FadeOut(lattice), run_time=1.5)

        icons = VGroup()
        glows = VGroup()
        for i, cx in enumerate((-3.6, 0, 3.6)):
            box = RoundedRectangle(width=1.6, height=1.1, corner_radius=0.15,
                                   stroke_color=CHALK, stroke_width=2)
            box.move_to([cx, 0, 0])
            glow, _ = landscape([(0, -0.3, 0.5)], x_range=(-0.7, 0.7),
                                color=GEO_B, stroke_width=2)
            glow.scale(0.6).move_to(box.get_center() + DOWN * 0.05)
            icons.add(box)
            glows.add(glow)
        tags = VGroup(*[
            Text(s, font_size=20, color=CHALK).next_to(box, DOWN, buff=0.2)
            for s, box in zip(("metal", "circuit", "crystal"), icons)
        ])
        self.play_t(FadeIn(icons), FadeIn(tags), run_time=1.5)

        self.wait_until(125.0)
        cap3 = Text("inside metals, circuits, and crystals,\nbending motion in silence,",
                   font_size=26, line_spacing=1.2).to_edge(UP)
        cap = self.swap(cap, cap3, run_time=1)
        self.play_t(LaggedStartMap(Create, glows, lag_ratio=0.3), run_time=2)

        self.wait_until(132.0)
        cap4 = Text("reminding us that reality is always deeper than it looks,",
                   font_size=25).to_edge(UP)
        small, _ = landscape([(-1, 0.4, 0.5), (1, -0.4, 0.5)], x_range=(-2.2, 2.2),
                             color=GEO_B, stroke_width=3)
        small.scale(0.8).move_to(LEFT * 3 + DOWN * 1.3)
        big, _ = landscape([(0, -1.3, 1.4)], x_range=(-2.6, 2.6),
                           color=GEO_A, stroke_width=3)
        big.move_to(RIGHT * 3 + DOWN * 1.3)
        cap = self.swap(cap, cap4, FadeOut(icons), FadeOut(tags),
                        FadeOut(glows), run_time=1.3)
        self.play_t(Create(small), Create(big), run_time=1.7)

        self.wait_until(139.0)
        cap5 = Text("and always more curved than we imagine.", font_size=27,
                   gradient=(GEO_A, GEO_B)).to_edge(UP)
        cap = self.swap(cap, cap5, run_time=1.2)
        self.play_t(small.animate.set_stroke(width=5),
                    big.animate.set_stroke(width=5), run_time=1.8)
        self.wait_until(144.5)
        self.play_t(FadeOut(cap), FadeOut(small), FadeOut(big),
                    FadeOut(stars), run_time=1.5)

    # ----------------------------------------------------------------
    def closing(self):
        title = Text("Hidden Geometry", font_size=42, gradient=(GEO_A, GEO_B))
        cite = Text("Sala, Mercaldo, Domi, Gariglio, Cuoco, Ortix & Caviglia",
                   font_size=20, color=CHALK).next_to(title, DOWN, buff=0.5)
        cite2 = Text("Science 389, 822-825 (2025) · University of Geneva",
                    font_size=18, color=GREY_C).next_to(cite, DOWN, buff=0.2)
        self.play_t(Write(title), run_time=1.5)
        self.play_t(FadeIn(cite, shift=UP * 0.2), FadeIn(cite2, shift=UP * 0.2),
                   run_time=1.5)
        self.wait_until(152.0)
        self.play_t(FadeOut(title), FadeOut(cite), FadeOut(cite2), run_time=1.5)
