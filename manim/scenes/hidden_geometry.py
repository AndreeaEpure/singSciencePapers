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
    connected by a bond lattice. Each atom carries a soft glow halo and a
    highlight for a beaded, lit look instead of a flat dot."""
    atoms = VGroup()
    positions = {}
    for r in range(rows):
        for c in range(cols):
            p = np.array([(c - (cols - 1) / 2) * spacing,
                          (r - (rows - 1) / 2) * spacing, 0])
            color = color_a if r < rows / 2 else color_b
            glow = Circle(radius=0.27, color=color, fill_opacity=0.16,
                         stroke_width=0).move_to(p)
            dot = Circle(radius=0.15, color=color, fill_opacity=1,
                        stroke_color=WHITE, stroke_width=0.5,
                        stroke_opacity=0.3).move_to(p)
            shine = Circle(radius=0.05, color=WHITE, fill_opacity=0.55,
                          stroke_width=0).move_to(p + 0.055 * (UP + LEFT))
            atoms.add(VGroup(glow, dot, shine))
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
    central mechanism. A fading comet trail follows the electron so the
    continuous rotation reads clearly."""
    ring = Circle(radius=radius, color=GREY_C, stroke_width=1.5).move_to(center)
    ring_glow = Circle(radius=radius, color=color, stroke_width=5,
                       stroke_opacity=0.15).move_to(center)
    theta = ValueTracker(0)

    electron = Dot(color=ELECTRON, radius=0.09)
    spin_arrow = Arrow(ORIGIN, RIGHT * 0.5, buff=0, stroke_width=4,
                       color=color, max_tip_length_to_length_ratio=0.4)
    trail = trail_group(electron, color=ELECTRON, segments=14)

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
    return VGroup(ring_glow, ring, trail, electron, spin_arrow), theta


def trail_group(mob, color=ELECTRON, segments=14, radius=0.045):
    """A fading comet-tail of dots that traces mob's recent path."""
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


def mini_metal(scale=0.4):
    """A tiny 2x2 atom grid: reads as "metal" at a glance."""
    dots = VGroup(*[
        Circle(radius=0.09, color=ATOM_B, fill_opacity=1, stroke_width=0)
        .move_to([x, y, 0])
        for x in (-0.28, 0.28) for y in (-0.22, 0.22)
    ])
    bonds = VGroup(*[
        Line(dots[i].get_center(), dots[j].get_center(), stroke_width=1.2,
            color=BOND_COLOR)
        for i, j in ((0, 1), (0, 2), (1, 3), (2, 3))
    ])
    return VGroup(bonds, dots).scale(scale)


def mini_circuit(scale=0.4):
    """A tiny zigzag trace with contact nodes: reads as "circuit"."""
    pts = [(-0.45, 0), (-0.1, 0), (-0.1, 0.28), (0.15, 0.28),
           (0.15, -0.22), (0.45, -0.22)]
    line = VMobject(color=GEO_B, stroke_width=2.5)
    line.set_points_as_corners([np.array([x, y, 0]) for x, y in pts])
    nodes = VGroup(*[
        Dot(radius=0.05, color=ELECTRON).move_to([x, y, 0])
        for x, y in (pts[0], pts[-1])
    ])
    return VGroup(line, nodes).scale(scale)


def mini_crystal(scale=0.4):
    """A tiny hexagonal lattice: reads as "crystal"."""
    hexagon = RegularPolygon(n=6, color=ATOM_A, stroke_width=2).scale(0.32)
    dots = VGroup(*[
        Dot(radius=0.045, color=ATOM_A, fill_opacity=1).move_to(v)
        for v in hexagon.get_vertices()
    ])
    center_dot = Dot(radius=0.04, color=ATOM_A, fill_opacity=0.7)
    return VGroup(hexagon, dots, center_dot).scale(scale)


def sparkle(pos, size=0.09, color=WHITE):
    """A small 4-point sparkle glyph for a few featured stars."""
    h = Line(LEFT * size, RIGHT * size, stroke_width=1.5, color=color)
    v = Line(UP * size, DOWN * size, stroke_width=1.5, color=color)
    core = Dot(radius=size * 0.28, color=color)
    return VGroup(h, v, core).move_to(pos)


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


def add_breathe(mob, amp=0.025, speed=1.0):
    """A very slight, continuous scale pulse -- keeps a static group alive."""
    mob.breathe_t = random.uniform(0, TAU)
    mob.breathe_prev = 1.0

    def upd(m, dt):
        m.breathe_t += dt
        target = 1 + amp * np.sin(speed * m.breathe_t)
        m.scale(target / m.breathe_prev)
        m.breathe_prev = target

    mob.add_updater(upd)


def add_twinkle(mob, speed=None):
    mob.tw_t = random.uniform(0, TAU)
    sp = speed or random.uniform(1.5, 3.0)
    base = mob.get_stroke_opacity() or 0.7

    def upd(m, dt):
        m.tw_t += sp * dt
        m.set_opacity(max(0.05, base * (0.5 + 0.5 * np.sin(m.tw_t))))

    mob.add_updater(upd)


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

    def enter_cap(self, new_cap, *extra_anims, run_time=1.5):
        """Open a section's first caption. If the previous section handed one
        off via self._cap, crossfade from it (so scenes flow into each other
        instead of cutting to black); otherwise write it fresh."""
        old = getattr(self, "_cap", None)
        if old is not None:
            self.play_t(FadeOut(old, shift=UP * 0.2), FadeIn(new_cap, shift=UP * 0.2),
                        *extra_anims, run_time=run_time)
            self._cap = None
        else:
            self.play_t(Write(new_cap), *extra_anims, run_time=run_time)
        return new_cap

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
        """Faint lattice specks drifting through the whole video, with a
        handful of dim connecting threads so it reads as a diffuse network
        rather than random noise."""
        ambient = VGroup()
        specks = []
        for _ in range(22):
            dot = Circle(radius=random.uniform(0.025, 0.07),
                        color=random.choice([GEO_A, GEO_B, CHALK]),
                        fill_opacity=random.uniform(0.07, 0.15),
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
            specks.append(dot)

        threads = VGroup()
        for a, b in zip(specks, specks[1:]):
            if np.linalg.norm(a.get_center() - b.get_center()) < 3.2:
                line = Line(a.get_center(), b.get_center(), stroke_width=0.6,
                           color=BOND_COLOR, stroke_opacity=0.25)

                def thread_upd(m, dt, a=a, b=b):
                    m.put_start_and_end_on(a.get_center(), b.get_center())

                line.add_updater(thread_upd)
                threads.add(line)
        self.add(threads, ambient)

    # ----------------------------------------------------------------
    def title_and_secret(self):
        title = Text("Hidden Geometry", font_size=58, gradient=(GEO_A, GEO_B))
        halo = Text("Hidden Geometry", font_size=58, color=GEO_B).set_opacity(0.18)
        halo.scale(1.06).move_to(title)
        self.play_t(FadeIn(halo), Write(title), run_time=2.5)
        self.wait_until(1.5)
        line1 = Text("There's a secret world beneath the things we touch,",
                     font_size=27, color=CHALK).to_edge(DOWN, buff=1.1)
        self.play_t(title.animate.scale(0.55).to_edge(UP, buff=0.7),
                    halo.animate.scale(0.55).move_to(title).shift(UP * 0.001),
                    FadeIn(line1, shift=UP * 0.3), run_time=1.5)
        halo.add_updater(lambda m: m.move_to(title))

        # An ordinary flat grid, with pinned nodes at the intersections so it
        # reads as a lattice, not just abstract axes -- nothing special here yet.
        grid = NumberPlane(x_range=[-6, 6, 1], y_range=[-3.2, 3.2, 1],
                           background_line_style={"stroke_color": GREY_D,
                                                  "stroke_width": 1,
                                                  "stroke_opacity": 0.4},
                           axis_config={"stroke_opacity": 0})
        nodes = VGroup(*[
            Dot([x, y, 0], radius=0.02, color=GREY_C, fill_opacity=0.5)
            for x in range(-5, 6) for y in (-2, -1, 0, 1, 2)
        ])
        self.play_t(FadeIn(grid), FadeIn(nodes), run_time=2)

        self.wait_until(20.8)
        line2 = Text("not written in equations alone,", font_size=27,
                     color=CHALK).to_edge(DOWN, buff=1.1)
        # A few faint equation glyphs flicker and dismiss themselves, each
        # nudged off-axis like chalk scrawl.
        glyphs = VGroup(*[
            Text(s, font_size=random.choice([26, 30, 34]), color=GREY_C)
            .rotate(random.uniform(-0.12, 0.12))
            .move_to([random.uniform(-4.5, 4.5), random.uniform(-1.8, 1.8), 0])
            for s in ("E=mc²", "F=ma", "∇×B", "ψ(x,t)", "ħω", "∂S/∂t")
        ]).set_opacity(0.32)
        line1 = self.swap(line1, line2, LaggedStartMap(FadeIn, glyphs,
                                                        lag_ratio=0.15),
                          run_time=1.3)
        self.play_t(FadeOut(glyphs, shift=UP * 0.3), run_time=1.5)

        self.wait_until(24.8)
        line3 = Text("but in the way the universe bends itself,", font_size=27,
                     color=CHALK).to_edge(DOWN, buff=1.1)
        curve, f = landscape([(-2, 0.9, 0.9), (1.5, -0.7, 1.0)],
                             color=GEO_A, stroke_width=3)
        area = Polygon(*[[x, y, 0] for x, y in
                         [(-4, -3.2)] + [(x, f(x)) for x in
                                        np.linspace(-4, 4, 40)] + [(4, -3.2)]],
                       stroke_width=0, fill_color=GEO_A, fill_opacity=0.12)
        # The grid-to-curve morph IS meant to look like a chaotic collapse --
        # keep that Transform, just crossfade the caption and node dust
        # around it, and a marble drops straight into the new valley.
        line1 = self.swap(line1, line3, Transform(grid, curve),
                          FadeOut(nodes), FadeIn(area), run_time=2)
        marble = Dot(color=ELECTRON, radius=0.08).move_to(UP * 2.5)
        self.play_t(marble.animate.move_to([-2, f(-2), 0]), run_time=0.8,
                    rate_func=rush_into)

        self.wait_until(28.9)
        line4 = Text("where no eyes could ever reach.", font_size=27,
                     color=CHALK).to_edge(DOWN, buff=1.1)
        line1 = self.swap(line1, line4, grid.animate.set_opacity(0.25),
                          area.animate.set_opacity(0.05),
                          marble.animate.scale(0.3).set_opacity(0.2),
                          run_time=2)
        self.wait_until(32.3)
        halo.clear_updaters()
        # Keep the hidden valley-curve, its shaded area and the caption alive:
        # the next line is "a geometry folded inside matter," so rather than
        # cut to black we fold this very curve into a crystal lattice.
        self.play_t(FadeOut(marble), FadeOut(title), FadeOut(halo),
                    grid.animate.set_opacity(0.6), run_time=1.0)
        self.bridge_curve = grid
        self.bridge_area = area
        self.bridge_cap = line1

    # ----------------------------------------------------------------
    def folded_in_matter(self):
        cap = Text("A geometry folded inside matter,", font_size=30).to_edge(UP)
        lattice = crystal_lattice().scale(1.1)
        if hasattr(self, "bridge_curve"):
            # The intro's hidden curve folds up into a crystal, the caption
            # rises from the floor to the ceiling, the shading dissolves.
            self.play_t(FadeOut(self.bridge_cap, shift=UP * 1.8),
                        FadeIn(cap, shift=UP * 0.3),
                        ReplacementTransform(self.bridge_curve, lattice),
                        FadeOut(self.bridge_area), run_time=2.5)
            del self.bridge_curve
        else:
            self.play_t(Write(cap), FadeIn(lattice, scale=0.8), run_time=2.5)
        add_drift(lattice, amp=0.03)

        self.wait_until(37.1)
        cap2 = Text("woven through lattices and charges,", font_size=30).to_edge(UP)
        # Charge pulses travel along the bonds rather than just flashing --
        # a literal current threading the lattice.
        bond_sample = list(lattice[0])[:6]
        travelers = VGroup(*[
            Dot(color=ELECTRON, radius=0.05).move_to(b.get_start())
            for b in bond_sample
        ])
        cap = self.swap(cap, cap2, FadeIn(travelers, scale=2), run_time=1.3)
        self.play_t(*[
            MoveAlongPath(d, Line(b.get_start(), b.get_end()))
            for d, b in zip(travelers, bond_sample)
        ], run_time=1.2)
        self.play_t(FadeOut(travelers), run_time=0.8)

        self.wait_until(41.1)
        cap3 = Text("quiet as a law that never needed a witness,",
                    font_size=28).to_edge(UP)
        remove_drift(lattice)
        add_breathe(lattice, amp=0.015, speed=0.8)
        cap = self.swap(cap, cap3, lattice.animate.scale(1.4), run_time=2)

        self.wait_until(45.3)
        cap4 = Text("small enough to live between atoms,", font_size=28).to_edge(UP)
        # Zoom into one gap: a tiny hidden landscape sitting between two atoms,
        # with short radial ticks bending inward like contour lines on a dip.
        gap_center = lattice[1][6].get_center() * 0.5 + lattice[1][7].get_center() * 0.5
        rings = VGroup(*[
            Circle(radius=r, color=GEO_B, stroke_width=2,
                  stroke_opacity=0.85 - 0.22 * i).move_to(gap_center)
            for i, r in enumerate((0.4, 0.28, 0.16))
        ])
        ticks = VGroup(*[
            Line(gap_center + 0.42 * np.array([np.cos(a), np.sin(a), 0]),
                gap_center + 0.5 * np.array([np.cos(a), np.sin(a), 0]),
                stroke_width=1.5, color=GEO_B, stroke_opacity=0.5)
            for a in np.linspace(0, TAU, 10, endpoint=False)
        ])
        gap_visual = VGroup(rings, ticks)
        cap = self.swap(cap, cap4, FadeIn(gap_visual, scale=0.3), run_time=1.5)
        add_breathe(gap_visual, amp=0.06, speed=1.6)

        self.wait_until(50.1)
        cap5 = Text("yet strong enough to steer electrons", font_size=28).to_edge(UP)
        electron = Dot(color=ELECTRON, radius=0.09).move_to(LEFT * 4 + UP * 0.6)
        electron_glow = Circle(radius=0.2, color=ELECTRON, fill_opacity=0.25,
                              stroke_width=0)
        electron_glow.add_updater(lambda m: m.move_to(electron))
        path = VMobject(stroke_width=2.5)
        path.set_points_as_corners([electron.get_center(), electron.get_center()])
        cap = self.swap(cap, cap5, FadeIn(electron), FadeIn(electron_glow),
                        run_time=1)

        def trail_upd(m):
            m.add_points_as_corners([electron.get_center()])
            m.set_color([ELECTRON, GEO_B])

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
        electron_glow.clear_updaters()

        self.wait_until(58.1)
        lattice.clear_updaters()
        gap_visual.clear_updaters()
        self.play_t(FadeOut(lattice), FadeOut(gap_visual), FadeOut(electron),
                    FadeOut(electron_glow), FadeOut(path), run_time=1.5)
        self._cap = cap   # crossfade into the next line, don't cut

    # ----------------------------------------------------------------
    def hills_and_valleys(self):
        cap = Text("They don't just move forward—", font_size=30).to_edge(UP)
        # A lone electron drifts in a straight line -- for this one beat it
        # really is "just moving forward"; the landscape rises under it next.
        drifter = Dot(color=ELECTRON, radius=0.1).move_to(LEFT * 5.5 + UP * 0.2)
        dtrail = trail_group(drifter, color=ELECTRON, segments=14)
        cap = self.enter_cap(cap, FadeIn(drifter), FadeIn(dtrail), run_time=1.5)
        self.play_t(drifter.animate.move_to(LEFT * 1.5 + UP * 0.2), run_time=1.0,
                    rate_func=linear)

        self.wait_until(63.0)
        cap2 = Text("they curve, they hesitate,", font_size=30).to_edge(UP)
        # A faint reference grid sits behind the landscape -- "not quite space,
        # but feels like it."
        ref_grid = NumberPlane(
            x_range=[-6, 6, 1.5], y_range=[-2.4, 2.4, 1.2],
            background_line_style={"stroke_color": GREY_D, "stroke_width": 1,
                                   "stroke_opacity": 0.16},
            axis_config={"stroke_opacity": 0})
        curve, f = landscape([(-2.6, 0.7, 0.7), (-0.5, -0.9, 0.6),
                              (1.3, 0.5, 0.6), (2.8, -0.5, 0.5)])
        area = Polygon(*[[x, y, 0] for x, y in
                         [(-4, -1.6)] + [(x, f(x)) for x in
                                        np.linspace(-4, 4, 40)] + [(4, -1.6)]],
                       stroke_width=0, fill_color=GEO_A, fill_opacity=0.08)
        ticks = VGroup(*[
            Line([x, -1.55, 0], [x, -1.45, 0], stroke_width=1, color=GREY_C)
            for x in np.arange(-4, 4.1, 0.5)
        ])
        ball = Dot(color=ELECTRON, radius=0.1)
        trail = trail_group(ball, color=ELECTRON, segments=16)
        x_tracker = ValueTracker(-3.6)

        def ball_upd(m):
            x = x_tracker.get_value()
            m.move_to([x, f(x), 0])

        ball.add_updater(ball_upd)
        # The drifting electron becomes the ball on the landscape -- same
        # particle, now with ground beneath it.
        dtrail.clear_updaters()
        cap = self.swap(cap, cap2, FadeOut(drifter), FadeOut(dtrail),
                        FadeIn(ref_grid), FadeIn(area), FadeIn(ticks),
                        Create(curve), FadeIn(ball), FadeIn(trail), run_time=1.3)
        self.play_t(x_tracker.animate.set_value(-1.8), run_time=1.5,
                    rate_func=there_and_back)

        self.wait_until(67.0)
        cap3 = Text("they trace invisible hills and valleys", font_size=28).to_edge(UP)
        cap = self.swap(cap, cap3, run_time=1)
        # A second, fainter electron traces its own path in the background --
        # many particles read this landscape, not just one.
        ball_b = Dot(color=GEO_B, radius=0.07, fill_opacity=0.6)
        xb_tracker = ValueTracker(3.2)

        def ball_b_upd(m):
            x = xb_tracker.get_value()
            m.move_to([x, f(x) + 0.02, 0])

        ball_b.add_updater(ball_b_upd)
        self.add(ball_b)
        # Caption settled -- let the ball roll the full landscape on its own.
        self.play_t(x_tracker.animate.set_value(3.6),
                    xb_tracker.animate.set_value(-3.6), run_time=4,
                    rate_func=linear)

        self.wait_until(73.0)
        cap4 = Text("mapped by something that isn't quite space,\nbut feels like it.",
                    font_size=27, line_spacing=1).to_edge(UP)
        ball.clear_updaters()
        ball_b.clear_updaters()
        trail.clear_updaters()
        cap = self.swap(cap, cap4, FadeOut(ball_b), run_time=1.5)
        self.wait_until(79.5)
        ball.clear_updaters()
        trail.clear_updaters()
        self.play_t(FadeOut(ball), FadeOut(trail), FadeOut(area),
                    FadeOut(ticks), FadeOut(ref_grid), run_time=1.3)
        self.hidden_curve_f = f
        # Hand the real curve + caption to the theory scene: it morphs into a
        # chalk rumour there ("once it lived only in theory").
        self.hills_curve = curve
        self._cap = cap

    # ----------------------------------------------------------------
    def theory_to_measured(self):
        # Chalk-era: a faint, uncertain sketch of the idea on a chalkboard.
        cap = Text("Once it lived only in theory,\na rumour in chalk dust,",
                   font_size=28, color=CHALK, line_spacing=1.2).to_edge(UP)
        ghost_curve, _ = landscape([(-2.6, 0.7, 0.7), (-0.5, -0.9, 0.6),
                                    (1.3, 0.5, 0.6), (2.8, -0.5, 0.5)],
                                   color=CHALK)
        ghost = dashed(ghost_curve, color=CHALK)
        ghost.set_opacity(0.5)
        board = RoundedRectangle(width=2.3, height=2.3, corner_radius=0.1,
                                 fill_color="#1c2b22", fill_opacity=0.45,
                                 stroke_color=CHALK, stroke_width=1.5,
                                 stroke_opacity=0.4)
        board.move_to(DOWN * 1.6 + RIGHT * 4.2)
        tensor = VGroup(*[
            Square(0.55, color=CHALK, stroke_width=1.5, stroke_opacity=0.5)
            for _ in range(4)
        ]).arrange_in_grid(2, 2, buff=0.05).move_to(board)
        labels = VGroup(*[
            Text(s, font_size=16, color=CHALK).move_to(sq)
            for s, sq in zip(("gxx", "gxy", "gyx", "gyy"), tensor)
        ]).set_opacity(0.6)
        dust = VGroup(*[
            Dot(radius=random.uniform(0.008, 0.02), color=CHALK,
               fill_opacity=random.uniform(0.2, 0.4))
            .move_to(board.get_center()
                    + np.array([random.uniform(-1.0, 1.0),
                               random.uniform(-1.0, 1.0), 0]))
            for _ in range(14)
        ])
        if hasattr(self, "hills_curve"):
            # The solid, measured curve breaks apart into dashed chalk -- the
            # story rewinds to when this was only a prediction.
            self.play_t(FadeOut(self._cap, shift=UP * 0.2),
                        FadeIn(cap, shift=UP * 0.2),
                        ReplacementTransform(self.hills_curve, ghost),
                        FadeIn(board), FadeIn(tensor), FadeIn(labels),
                        FadeIn(dust), run_time=2.5)
            self._cap = None
            del self.hills_curve
        else:
            self.play_t(Write(cap), Create(ghost), FadeIn(board), FadeIn(tensor),
                        FadeIn(labels), FadeIn(dust), run_time=2.5)

        self.wait_until(87.0)
        cap2 = Text("a prediction waiting for courage.", font_size=28,
                    color=CHALK).to_edge(UP)
        cap = self.swap(cap, cap2, ghost.animate.set_opacity(0.2), run_time=1.5)
        self.play_t(ghost.animate.set_opacity(0.55), run_time=1.5)

        self.wait_until(92.0)
        # The reveal: dashed becomes solid, with a pulse ring marking the
        # instant of confirmation, and spin-momentum locking drives the
        # measurement.
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
        pulse = Circle(radius=0.3, color=GEO_B, stroke_width=3).move_to(
            solid_curve.get_center())
        cap = self.swap(cap, cap3, Transform(ghost, ghost_target),
                        FadeOut(board), FadeOut(tensor), FadeOut(labels),
                        FadeOut(dust), run_time=1.5)
        self.play_t(Transform(ghost, solid_curve), FadeIn(data_pts, scale=1.5),
                    Broadcast(pulse, focal_point=solid_curve.get_center()),
                    run_time=2.5)

        self.wait_until(98.0)
        cap4 = Text("proof that even at the smallest scales\nthere are landscapes, there are fields,",
                   font_size=26, line_spacing=1.2).to_edge(UP)
        orbit, theta = spin_orbit_group(center=UP * 1.3 + LEFT * 4, radius=0.9)
        b_arrow = Arrow(UP * 2.6 + LEFT * 4, UP * 1.9 + LEFT * 4,
                        color=GEO_B, stroke_width=3)
        b_label = Text("B", font_size=20, color=GEO_B).next_to(b_arrow, UP,
                                                               buff=0.1)
        add_breathe(b_arrow, amp=0.05, speed=1.3)
        cap = self.swap(cap, cap4, FadeIn(orbit), FadeIn(b_arrow),
                        FadeIn(b_label), run_time=1.5)
        self.play_t(theta.animate.set_value(TAU * 1.4), run_time=4.5,
                    rate_func=linear)

        self.wait_until(105.0)
        cap5 = Text("there are shapes that tell particles where to go.",
                   font_size=27).to_edge(UP)
        ball2 = Dot(color=ELECTRON, radius=0.1)
        trail2 = trail_group(ball2, color=ELECTRON, segments=16)
        x2 = ValueTracker(-3.6)

        def ball2_upd(m):
            x = x2.get_value()
            m.move_to([x, self.hidden_curve_f(x) - 1.6, 0])

        ball2.add_updater(ball2_upd)
        cap = self.swap(cap, cap5, FadeIn(ball2), FadeIn(trail2), run_time=1)
        self.play_t(x2.animate.set_value(3.6), run_time=4.0, rate_func=linear)

        self.wait_until(111.0)
        orbit.clear_updaters()
        ball2.clear_updaters()
        trail2.clear_updaters()
        b_arrow.clear_updaters()
        self.play_t(FadeOut(ghost), FadeOut(data_pts), FadeOut(orbit),
                    FadeOut(b_arrow), FadeOut(b_label), FadeOut(ball2),
                    FadeOut(trail2), run_time=2)
        self._cap = cap   # crossfade into "So maybe spacetime isn't just..."

    # ----------------------------------------------------------------
    def zoom_to_spacetime(self):
        cap = Text("So maybe spacetime isn't just out there,\nstretching between stars and black holes.",
                   font_size=27, line_spacing=1.2).to_edge(UP)
        lattice = crystal_lattice(rows=3, cols=5, spacing=0.6).scale(0.8)
        cap = self.enter_cap(cap, FadeIn(lattice, scale=0.6), run_time=2)

        stars = VGroup(*[
            Dot([random.uniform(-6.5, 6.5), random.uniform(-3.5, 3.5), 0],
               radius=random.uniform(0.02, 0.045), color=WHITE)
            for _ in range(45)
        ]).set_opacity(0)
        for s in stars:
            add_twinkle(s)
        sparkles = VGroup(*[
            sparkle([random.uniform(-6, 6), random.uniform(-3.2, 3.2), 0],
                   size=random.uniform(0.07, 0.11))
            for _ in range(5)
        ]).set_opacity(0)
        for s in sparkles:
            add_twinkle(s, speed=random.uniform(0.8, 1.4))
        self.play_t(lattice.animate.scale(0.3).set_opacity(0.5),
                    stars.animate.set_opacity(0.7),
                    sparkles.animate.set_opacity(0.8), run_time=2)

        funnel, _ = landscape([(0, -1.6, 1.6)], x_range=(-4, 4),
                              color=GEO_A, stroke_width=4)
        ring_glow = Circle(radius=0.24, color=GEO_B, stroke_width=8,
                          stroke_opacity=0.4).move_to(DOWN * 1.6)
        hole = Circle(radius=0.12, color=BLACK, fill_opacity=1,
                     stroke_color=GEO_B, stroke_width=2).move_to(DOWN * 1.6)
        add_breathe(ring_glow, amp=0.12, speed=1.1)
        # A mote spirals the well, dragging a curved tail -- the curvature is
        # doing something, not just sitting there.
        orbiter = Dot(color=ELECTRON, radius=0.05)
        otrail = trail_group(orbiter, color=GEO_B, segments=20, radius=0.03)
        orbiter.oth = 0.0

        def orb_upd(m, dt):
            m.oth += dt * 1.7
            r = max(0.24, 0.75 - 0.05 * m.oth)
            m.move_to(DOWN * 1.6 + r * np.array([np.cos(m.oth * 2.3),
                                                 np.sin(m.oth * 2.3), 0]))

        orbiter.add_updater(orb_upd)
        self.play_t(Create(funnel), FadeIn(ring_glow), FadeIn(hole, scale=0.3),
                    FadeIn(orbiter), FadeIn(otrail), run_time=2)

        self.wait_until(119.0)
        cap2 = Text("Maybe it's everywhere—hidden in the ordinary,",
                   font_size=27).to_edge(UP)
        ring_glow.clear_updaters()
        orbiter.clear_updaters()
        otrail.clear_updaters()
        cap = self.swap(cap, cap2, FadeOut(funnel), FadeOut(hole),
                        FadeOut(ring_glow), FadeOut(orbiter), FadeOut(otrail),
                        FadeOut(lattice), run_time=1.5)

        icons = VGroup()
        minis = VGroup()
        glows = VGroup()
        makers = (mini_metal, mini_circuit, mini_crystal)
        for i, (cx, maker) in enumerate(zip((-3.6, 0, 3.6), makers)):
            box = RoundedRectangle(width=1.6, height=1.1, corner_radius=0.15,
                                   stroke_color=CHALK, stroke_width=2)
            box.move_to([cx, 0, 0])
            mini = maker().move_to(box.get_center())
            glow, _ = landscape([(0, -0.3, 0.5)], x_range=(-0.7, 0.7),
                                color=GEO_B, stroke_width=2)
            glow.scale(0.6).move_to(box.get_center() + DOWN * 0.05)
            icons.add(box)
            minis.add(mini)
            glows.add(glow)
        tags = VGroup(*[
            Text(s, font_size=20, color=CHALK).next_to(box, DOWN, buff=0.2)
            for s, box in zip(("metal", "circuit", "crystal"), icons)
        ])
        self.play_t(FadeIn(icons), FadeIn(minis), FadeIn(tags), run_time=1.5)

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
        link = DashedLine(small.get_right(), big.get_left(), stroke_width=1.5,
                          color=CHALK, stroke_opacity=0.4)
        cap = self.swap(cap, cap4, FadeOut(icons), FadeOut(minis), FadeOut(tags),
                        FadeOut(glows), run_time=1.3)
        self.play_t(Create(small), Create(big), Create(link), run_time=1.7)

        self.wait_until(139.0)
        cap5 = Text("and always more curved than we imagine.", font_size=27,
                   gradient=(GEO_A, GEO_B)).to_edge(UP)
        cap = self.swap(cap, cap5, run_time=1.2)
        self.play_t(small.animate.set_stroke(width=5, color=GEO_B),
                    big.animate.set_stroke(width=5, color=GEO_A),
                    link.animate.set_stroke(opacity=0.8), run_time=1.8)
        self.wait_until(144.5)
        # The two scales of curvature converge to a single point -- the title
        # of the piece rises out of exactly where they meet.
        self.play_t(FadeOut(cap),
                    small.animate.move_to(ORIGIN).scale(0.2).set_opacity(0),
                    big.animate.move_to(ORIGIN).scale(0.2).set_opacity(0),
                    FadeOut(link), FadeOut(stars), FadeOut(sparkles),
                    run_time=1.5)

    # ----------------------------------------------------------------
    def closing(self):
        backdrop = crystal_lattice(rows=2, cols=3, spacing=1.4).set_opacity(0.08)
        title = Text("Hidden Geometry", font_size=42, gradient=(GEO_A, GEO_B))
        cite = Text("Sala, Mercaldo, Domi, Gariglio, Cuoco, Ortix & Caviglia",
                   font_size=20, color=CHALK).next_to(title, DOWN, buff=0.5)
        cite2 = Text("Science 389, 822-825 (2025) · University of Geneva",
                    font_size=18, color=GREY_C).next_to(cite, DOWN, buff=0.2)
        # Grows from the convergence point of the two landscapes.
        self.play_t(FadeIn(backdrop), FadeIn(title, scale=0.3), run_time=1.5)
        self.play_t(FadeIn(cite, shift=UP * 0.2), FadeIn(cite2, shift=UP * 0.2),
                   run_time=1.5)
        self.wait_until(152.0)
        self.play_t(FadeOut(title), FadeOut(cite), FadeOut(cite2),
                    FadeOut(backdrop), run_time=1.5)
