"""Four deterministic, seekable scenes with persistent Matplotlib artists."""
from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from matplotlib.patches import Rectangle, ConnectionPatch, FancyArrowPatch
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection
from mpl_toolkits.mplot3d import proj3d
from sklearn.decomposition import PCA

from .config import Labels
from .graphics import (DeviceRoom, MatrixDisplay, SignalStrip, direction_segment,
                       set_line_3d, set_scatter_3d, style_2d, style_3d)
from .model import (SceneData, cross_correlation, make_scene_data, normalize_columns,
                    direction_angle)
from .timeline import ramp, smooth, scene2_phase, SCENE2
from .projection import flatten_points, projection_guides, mixing_coordinates


class BaseScene:
    scene_id = "0"

    def __init__(self, figure: Figure, config: dict, data: SceneData | None = None) -> None:
        self.figure, self.config = figure, config
        self.settings = config["scenes"][self.scene_id]
        self.labels = Labels(config.get("language", "en"))
        self.style = config["style"]
        self.colors = self.style["source_colors"]
        self.data = make_scene_data(config, self.scene_id) if data is None else data
        self.figure.clear()
        self.figure.set_facecolor(self.style["background"])
        self.figure.text(0.947, 0.945, self.labels("chapter", number=self.scene_id),
                         fontsize=10, color=self.style["muted"], ha="right")
        self.figure.text(0.055, 0.923, self.labels(f"scene{self.scene_id}_title"),
                         fontsize=26, weight="bold", color=self.style["foreground"])
        self.phase = self.figure.text(0.057, 0.855, "", fontsize=12,
                                      color=self.colors[0])
        self.strip = SignalStrip(figure, config, self.labels, self.data.time, self.data.sources,
                                 show_variance=self.scene_id == "3")
        self.progress_bg = Rectangle((0.057, 0.025), 0.89, 0.0025, transform=figure.transFigure,
                                     color=self.style["grid"], linewidth=0)
        self.progress_bar = Rectangle((0.057, 0.025), 0.001, 0.0025, transform=figure.transFigure,
                                      color=self.colors[0], linewidth=0)
        figure.patches.extend([self.progress_bg, self.progress_bar])
        self.fade = Rectangle((0, 0), 1, 1, transform=figure.transFigure,
                              color=self.style["background"], linewidth=0, zorder=1000, alpha=0)
        figure.patches.append(self.fade)

    def text(self, x, y, value="", size=12, color=None, **kwargs):
        return self.figure.text(x, y, value, fontsize=size, color=color or self.style["foreground"], **kwargs)

    def finish(self, progress: float, fade: bool = False) -> None:
        self.progress_bar.set_width(0.89 * np.clip(progress, 0, 1))
        if fade:
            edge = min(0.04, self.config["render"]["fade_seconds"] / self.settings["duration"])
            opacity = 1 - min(smooth(progress, 0, edge), 1 - smooth(progress, 1 - edge, 1))
            self.fade.set_alpha(opacity)
        else:
            self.fade.set_alpha(0)

    def update(self, progress: float, fade: bool = False) -> None:
        raise NotImplementedError


class MixingScene(BaseScene):
    scene_id = "1"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.room_ax = self.figure.add_axes([0.035, 0.34, 0.52, 0.45])
        self.room = DeviceRoom(self.room_ax, self.config, self.settings)
        self.card_heading = self.text(0.60, 0.754, "", 12, weight="bold")
        self.card_note = self.text(0.60, 0.675, "", 11, self.style["muted"], va="top", linespacing=1.6)
        self.formula1 = self.text(0.60, 0.574, "", 20)
        self.formula2 = self.text(0.60, 0.469, "", 20)
        self.bottom_note = self.text(0.60, 0.352, "", 10, self.style["muted"], va="top", linespacing=1.6)
        self.matrix_ax = self.figure.add_axes([0.61, 0.402, 0.30, 0.235])
        self.matrix_ax.axis("off")
        self.matrix = MatrixDisplay(self.matrix_ax, self.data.mixing, self.colors,
                                    [item["id"] for item in self.settings["microphones"]],
                                    [item["id"] for item in self.settings["speakers"]])
        self.matrix.set_alpha(0)
        self.matrix_label = self.text(0.60, 0.396, self.labels("scene1_matrix"), 9, self.style["muted"])
        self.matrix_label.set_alpha(0)

    def update(self, progress: float, fade: bool = False) -> None:
        p, data = progress, self.data
        self.matrix.set_alpha(0)
        self.matrix_label.set_alpha(0)
        for artist in (self.formula1, self.formula2, self.card_note, self.bottom_note):
            artist.set_alpha(1)
            artist.set_text("")
        self.card_heading.set_text("")
        self.card_heading.set_fontsize(12)
        self.room.update(p * self.settings["duration"], waves=p >= 0.13,
                         highlight_mic=int(p * len(self.settings["microphones"]) * 5) % len(self.settings["microphones"]))
        self.strip.update(data.sources, cursor=(p * 2 % 1) * data.time[-1])
        if p < 0.13:
            self.phase.set_text(self.labels("scene1_room"))
            self.card_note.set_text(self.labels("scene1_intro", sources=len(self.settings["speakers"]),
                                               microphones=len(self.settings["microphones"])))
        elif p < 0.35:
            self.phase.set_text(self.labels("scene1_physics"))
            self.formula1.set_fontsize(23)
            self.formula1.set_text(r"$\mathrm{Intensity}\propto d^{-2}$")
            self.formula2.set_text(r"$\mathrm{Amplitude}\propto d^{-1}$")
        elif p < 0.55:
            self.phase.set_text(self.labels("scene1_coefficients"))
            self.formula1.set_fontsize(20)
            self.formula1.set_text(r"$x_i(t)=\sum_j\frac{d_0}{d_{ij}}\,s_j(t)$")
            self.formula2.set_text(r"$x_i(t)=\sum_j A_{ij}\,s_j(t)$")
            fraction = smooth(p, 0.41, 0.52)
            self.formula1.set_alpha(1 - 0.75 * fraction)
            self.formula2.set_alpha(fraction)
            self.bottom_note.set_text(self.labels("scene1_unknown"))
        elif p < 0.77:
            self.phase.set_text(self.labels("scene1_matrix_phase"))
            self.card_heading.set_text(r"$\mathbf{x}(t)=A\,\mathbf{s}(t)$")
            self.card_heading.set_fontsize(23)
            self.card_note.set_text(r"$A=$")
            self.matrix.set_alpha(smooth(p, 0.55, 0.58))
            self.matrix_label.set_alpha(1)
            self.bottom_note.set_text(self.labels("scene1_unknown"))
        else:
            self.phase.set_text(self.labels("scene1_recovery"))
            self.formula1.set_fontsize(23)
            self.formula1.set_text(r"$\widehat{\mathbf{s}}(t)=W\mathbf{x}(t)$")
            rows, columns = data.mixing.shape
            rank = np.linalg.matrix_rank(data.mixing)
            if rows == columns and rank == columns:
                self.card_note.set_text(self.labels("scene1_inverse"))
                self.formula2.set_text(r"$W_{\mathrm{ideal}}=A^{-1}$")
            elif rows >= columns and rank == columns:
                self.card_note.set_text(self.labels("scene1_pseudoinverse"))
                self.formula2.set_text(r"$W_{\mathrm{ideal}}=A^{+}$")
            else:
                self.card_note.set_text(self.labels("scene1_rank_warning"))
                self.formula2.set_text(r"$\mathrm{rank}(A)<n$")
        self.finish(progress, fade)


class GeometryScene(BaseScene):
    """Show the same observations, their floor projection, and their mixing lines."""

    scene_id = "2"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        data = self.data
        self.third_is_time = self.settings["third_axis"] == "time"
        self.limit = float(np.max(np.abs(data.observations[:, :2]))) * 1.16
        self.ax3 = self.figure.add_axes([0.008, 0.293, 0.575, 0.530], projection="3d")
        z_limit = ((0, self.config["signals"]["duration"]) if self.third_is_time
                   else (-self.limit, self.limit))
        style_3d(self.ax3, self.config, self.limit, z_limit,
                 self.labels("time_axis") if self.third_is_time else r"$x_3(t)$")
        corners = np.array([[-1, -1, 0], [-1, 1, 0], [1, 1, 0], [1, -1, 0]]) * self.limit
        self.floor_plane = Poly3DCollection([corners], facecolor=self.style["grid"],
                                            edgecolor=self.style["muted"], alpha=0.13,
                                            linewidth=0.7)
        self.ax3.add_collection3d(self.floor_plane)
        for vector in ([1, 0], [0, 1]):
            self.ax3.plot(*direction_segment(vector, self.limit).T,
                          color=self.style["muted"], alpha=0.25, linewidth=0.6)
        self.floor_label = self.ax3.text(-0.94 * self.limit, -0.99 * self.limit, 0,
                                         r"$z=0$", fontsize=9, color=self.style["muted"])
        self.path_lines, self.ghost_lines, self.landing_lines = [], [], []
        self.axes3, self.arrowheads3, self.direction_labels3 = [], [], []
        self.guides, self.moving_markers, self.floor_markers, self.focus_guides = [], [], [], []
        for j in range(2):
            color = self.colors[j]
            self.ghost_lines.append(self.ax3.plot([], [], [], color=color, linewidth=0.8)[0])
            self.path_lines.append(self.ax3.plot([], [], [], color=color, linewidth=1.8)[0])
            self.landing_lines.append(self.ax3.plot([], [], [], color=color, linewidth=2.3)[0])
            self.axes3.append(self.ax3.plot([], [], [], color=color, linewidth=2.3)[0])
            self.arrowheads3.append(self.ax3.plot([], [], [], color=color, linewidth=2.3)[0])
            self.direction_labels3.append(self.ax3.text(0, 0, 0, "", color=color, fontsize=12))
            guide = Line3DCollection([np.zeros((2, 3))], colors=color, linewidths=0.7,
                                      linestyles=(0, (3, 5)), alpha=0.0)
            self.ax3.add_collection3d(guide)
            self.guides.append(guide)
            self.focus_guides.append(self.ax3.plot([], [], [], color=color, linewidth=1.4,
                                                    linestyle=(0, (3, 3)))[0])
            self.moving_markers.append(self.ax3.plot([], [], [], marker="o", markersize=6.0,
                                                      color=color, markeredgecolor="white",
                                                      markeredgewidth=0.8, linestyle="")[0])
            self.floor_markers.append(self.ax3.plot([], [], [], marker="o", markersize=8.5,
                                                     markerfacecolor=self.style["background"],
                                                     markeredgecolor=color, markeredgewidth=1.7,
                                                     linestyle="")[0])
        self.cloud = self.ax3.scatter([], [], [], s=4, color=self.style["combined_color"],
                                      alpha=0.5, depthshade=False)
        self.ghost_cloud = self.ax3.scatter([], [], [], s=2.5, color=self.style["combined_color"],
                                            alpha=0.13, depthshade=False)
        self.joint_guides = Line3DCollection([np.zeros((2, 3))], colors=self.style["muted"], linewidths=0.6,
                                              linestyles=(0, (3, 5)), alpha=0.0)
        self.ax3.add_collection3d(self.joint_guides)
        self.ax2 = self.figure.add_axes([0.616, 0.410, 0.325, 0.363])
        style_2d(self.ax2, self.config, equal=True)
        self.ax2.set_xlim(-self.limit, self.limit)
        self.ax2.set_ylim(-self.limit, self.limit)
        self.ax2.xaxis.set_major_locator(MaxNLocator(3))
        self.ax2.yaxis.set_major_locator(MaxNLocator(3))
        self.ax2.axhline(0, color=self.style["muted"], alpha=0.32, linewidth=0.8)
        self.ax2.axvline(0, color=self.style["muted"], alpha=0.32, linewidth=0.8)
        self.dots2, self.basis2, self.arrows2, self.direction_labels2 = [], [], [], []
        self.focus2, self.links = [], []
        for j in range(2):
            color = self.colors[j]
            self.dots2.append(self.ax2.plot([], [], ".", color=color, markersize=2.6, alpha=0.75)[0])
            self.basis2.append(self.ax2.plot([], [], color=color, linewidth=2.2)[0])
            arrow = FancyArrowPatch((0, 0), (0, 0), color=color, arrowstyle="-|>",
                                    mutation_scale=11, linewidth=1.4)
            self.ax2.add_patch(arrow)
            self.arrows2.append(arrow)
            self.direction_labels2.append(self.ax2.text(0, 0, "", color=color, fontsize=12))
            self.focus2.append(self.ax2.plot([], [], "o", markersize=7,
                                              markeredgecolor="white", markeredgewidth=0.8,
                                              color=color, zorder=12)[0])
            link = ConnectionPatch((0, 0), (0, 0), coordsA="data", coordsB="data",
                                    axesA=self.ax3, axesB=self.ax2, arrowstyle="-|>",
                                    connectionstyle="arc3,rad=-0.12", mutation_scale=11,
                                    linewidth=1.25, linestyle=(0, (4, 5)), color=color,
                                    shrinkA=7, shrinkB=8, clip_on=False, zorder=9)
            self.figure.add_artist(link)
            self.links.append(link)
        self.mix2 = self.ax2.plot([], [], ".", color=self.style["combined_color"],
                                  markersize=2.0, alpha=0.5)[0]
        self.pca2 = [self.ax2.plot([], [], color=self.style["pca_color"],
                                   linestyle=(0, (5, 4)), linewidth=1.7)[0] for _ in range(2)]
        self.pca_projected = PCA().fit(data.observations[:, :2])
        self.floor_heading = self.text(0.621, 0.803, "", 10, weight="bold")
        self.badge = self.text(0.621, 0.359, "", 11)
        self.formula = self.text(0.621, 0.302, "", 18)
        self.note = self.text(0.621, 0.315, "", 10, self.style["muted"])
        self.room_ax = self.figure.add_axes([0.038, 0.345, 0.50, 0.43])
        self.room = DeviceRoom(self.room_ax, self.config, self.config["scenes"]["1"], self.settings)
        self.count_note = self.text(0.621, 0.585, "", 16)
        self.stride = max(1, len(data.time) // self.config["render"]["max_points"])
        self.sample_indices = []
        for j in range(2):
            active = np.flatnonzero(data.alternate_active == j)
            positive = active[data.alternate_sources[active, j] > 0.82 * data.sources[:, j].max()]
            candidates = positive if len(positive) else active
            target = len(data.time) * (0.74 if j == 0 else 0.9)
            self.sample_indices.append(int(candidates[np.argmin(np.abs(candidates - target))]))

    def spatial_points(self, observations: np.ndarray, indices: np.ndarray,
                       projection: float = 0.0) -> np.ndarray:
        z = self.data.time[indices] if self.third_is_time else observations[indices, 2]
        return flatten_points(np.column_stack([observations[indices, :2], z]), projection)

    def _camera(self, progress: float, phase: str) -> float:
        if phase in ("directions", "basis"):
            amount = smooth(progress, SCENE2["top_view_start"], SCENE2["top_view_end"])
        elif phase == "simultaneous":
            amount = 1 - smooth(progress, SCENE2["simultaneous_start"],
                                  SCENE2["simultaneous_start"] + 0.022)
        else:
            amount = 0.0
        elevation = self.config["render"]["camera_elevation"]
        azimuth = self.config["render"]["camera_azimuth"]
        self.ax3.view_init((1 - amount) * elevation + amount * 90,
                          (1 - amount) * azimuth - amount * 90)
        show_height = amount < 0.98
        self.ax3.set_zlabel((self.labels("time_axis") if self.third_is_time else r"$x_3(t)$")
                           if show_height else "")
        height_ticks = (np.linspace(0, self.config["signals"]["duration"], 4)
                        if self.third_is_time else [-self.limit, 0, self.limit])
        self.ax3.set_zticks(height_ticks if show_height else [])
        self.ax3.zaxis.line.set_alpha(1 if show_height else 0)
        return amount

    def _reset(self) -> None:
        for line in (self.path_lines + self.ghost_lines + self.landing_lines + self.axes3
                     + self.arrowheads3 + self.moving_markers + self.floor_markers + self.focus_guides):
            set_line_3d(line, np.empty((0, 3)))
            line.set_alpha(1)
        for line in self.dots2 + self.basis2 + self.pca2 + self.focus2 + [self.mix2]:
            line.set_data([], [])
            line.set_alpha(0.5 if line is self.mix2 else 1.0)
        for scatter in (self.cloud, self.ghost_cloud):
            set_scatter_3d(scatter, np.empty((0, 3)))
        for guide in self.guides + [self.joint_guides]:
            guide.set_segments([])
            guide.set_alpha(0)
        for label in self.direction_labels2 + self.direction_labels3:
            label.set_text("")
        for arrow in self.arrows2:
            arrow.set_visible(False)
        for link in self.links:
            link.set_visible(False)
        for label in (self.formula, self.badge, self.note, self.floor_heading):
            label.set_text("")
        self.formula.set_position((0.621, 0.302))
        self.formula.set_color(self.style["foreground"])
        self.badge.set_position((0.621, 0.359))
        self.badge.set_color(self.style["foreground"])
        self.ax2.set_xlim(-self.limit, self.limit)
        self.ax2.set_ylim(-self.limit, self.limit)
        self.ax2.set_xlabel(r"$x_1(t)$", fontsize=10, labelpad=1)
        self.ax2.set_ylabel(r"$x_2(t)$", fontsize=10, labelpad=1)

    def _draw_direction(self, j: int, vector: np.ndarray, alpha: float = 1.0,
                        transform: np.ndarray | None = None, limit: float | None = None,
                        estimated: bool = False) -> None:
        """Draw the same column direction in both views; only the right may unmix."""
        if alpha <= 0:
            return
        segment = direction_segment(vector[:2], self.limit * 0.98)
        set_line_3d(self.axes3[j], segment)
        self.axes3[j].set_alpha(alpha)
        tip = segment[1]
        unit = tip[:2] / np.linalg.norm(tip[:2])
        perpendicular = np.array([-unit[1], unit[0]])
        wings = np.array([tip[:2] - 0.085 * self.limit * unit + 0.035 * self.limit * perpendicular,
                          tip[:2],
                          tip[:2] - 0.085 * self.limit * unit - 0.035 * self.limit * perpendicular])
        set_line_3d(self.arrowheads3[j], np.column_stack([wings, np.zeros(3)]))
        self.arrowheads3[j].set_alpha(alpha)
        label = rf"$\widehat{{a}}_{j + 1}$" if estimated else rf"$a_{j + 1}$"
        self.direction_labels3[j].set_text(label)
        offset = tip[:2] * 1.05 + self.limit * 0.055 * perpendicular * (-1 if j == 0 else 1)
        self.direction_labels3[j].set_position(tuple(offset))
        self.direction_labels3[j].set_3d_properties(0.0, zdir="z")
        self.direction_labels3[j].set_alpha(alpha)
        plotted = vector[:2] if transform is None else transform @ vector[:2]
        right_limit = self.limit if limit is None else limit
        right_segment = direction_segment(plotted, right_limit * 0.98, dimensions=2)
        self.basis2[j].set_data(right_segment[:, 0], right_segment[:, 1])
        self.basis2[j].set_alpha(alpha)
        self.arrows2[j].set_positions(right_segment[1] * 0.72, right_segment[1])
        self.arrows2[j].set_alpha(alpha)
        self.arrows2[j].set_visible(True)
        offset = right_segment[1] * 0.86
        unit = plotted / np.linalg.norm(plotted)
        perpendicular = np.array([-unit[1], unit[0]])
        offset += perpendicular * right_limit * (0.13 if j == 1 else -0.16)
        self.direction_labels2[j].set_position(tuple(offset))
        if transform is None:
            direction_label = label
        elif np.allclose(transform @ self.data.mixing[:2], np.eye(2), atol=1e-7):
            direction_label = rf"$s_{j + 1}$"
        else:
            direction_label = ""
        self.direction_labels2[j].set_text(direction_label)
        self.direction_labels2[j].set_alpha(alpha)

    def _track_projection(self, j: int, amount: float, camera_amount: float) -> None:
        """Link a real sample to exactly the same floor point in the other view."""
        index = np.array([self.sample_indices[j]])
        original = self.spatial_points(self.data.alternate_observations, index)
        moving = flatten_points(original, amount)
        floor = flatten_points(original, 1)
        set_line_3d(self.moving_markers[j], moving)
        set_line_3d(self.floor_markers[j], floor)
        set_line_3d(self.focus_guides[j], np.vstack([moving, floor]))
        self.focus2[j].set_data(floor[:, 0], floor[:, 1])
        self.focus2[j].set_alpha(1)
        projected_x, projected_y, _ = proj3d.proj_transform(*floor[0], self.ax3.get_proj())
        link = self.links[j]
        link.xy1 = (float(projected_x), float(projected_y))
        link.xy2 = tuple(floor[0, :2])
        link.set_visible(camera_amount < 0.94)
        link.set_alpha(0.9)

    def update(self, progress: float, fade: bool = False) -> None:
        p, data = progress, self.data
        phase = scene2_phase(p)
        self._reset()
        self.phase.set_color(self.colors[0])
        camera_amount = self._camera(p, phase)
        is_transition = phase == "transition"
        self.ax3.set_visible(not is_transition)
        self.ax2.set_visible(phase not in ("transition", "alternate"))
        self.room_ax.set_visible(is_transition)
        self.count_note.set_visible(is_transition)
        self.phase.set_text(self.labels("scene2_" + phase))
        self.floor_heading.set_text(self.labels("scene2_top_view") if self.ax2.get_visible() else "")
        if is_transition:
            self.room.update(p * self.settings["duration"], blend=smooth(p, 0.008, 0.074), waves=False)
            self.count_note.set_text(self.labels("scene2_two" if self.third_is_time else "scene2_three"))
            self.strip.update(data.alternate_sources, cursor=None)
        elif phase in ("alternate", "directions", "basis"):
            end = max(2, min(len(data.time), int(ramp(p, SCENE2["alternate_start"],
                                                         SCENE2["alternate_end"]) * len(data.time))))
            indices = np.arange(end)
            projections = [smooth(p, SCENE2["project_first_start"], SCENE2["project_first_end"]),
                           smooth(p, SCENE2["project_second_start"], SCENE2["project_second_end"])]
            for j in range(2):
                original = self.spatial_points(data.alternate_observations, indices)
                original[data.alternate_active[:end] != j] = np.nan
                moving = flatten_points(original, projections[j])
                set_line_3d(self.path_lines[j], moving)
                self.path_lines[j].set_alpha((0.9 if phase == "alternate" else 0.65)
                                              if projections[j] < 0.999 else 0.0)
                if phase == "directions" and projections[j] < 0.999:
                    focus = 0 if p < SCENE2["project_second_start"] else 1
                    self.path_lines[j].set_alpha(0.93 if j == focus else 0.30)
                if phase != "alternate":
                    set_line_3d(self.ghost_lines[j], original)
                    self.ghost_lines[j].set_alpha(0.23 * projections[j] * (1 - camera_amount))
                    active = indices[data.alternate_active[:end] == j][::self.stride]
                    shadow = self.spatial_points(data.alternate_observations, active, 1)
                    set_line_3d(self.landing_lines[j], shadow)
                    self.landing_lines[j].set_alpha(0.9 * projections[j])
                    self.dots2[j].set_data(shadow[:, 0], shadow[:, 1])
                    self.dots2[j].set_alpha(0.8 * projections[j])
                    guide_indices = active[::max(1, len(active) // 11)]
                    guide_points = self.spatial_points(data.alternate_observations, guide_indices)
                    self.guides[j].set_segments(projection_guides(guide_points))
                    guide_visibility = 0.5 if 0.005 < projections[j] < 0.999 else 0.1 * projections[j]
                    self.guides[j].set_alpha(guide_visibility * (1 - camera_amount))
                    self._draw_direction(j, data.mixing[:, j], smooth(projections[j], 0.76, 1))
            self.strip.update(data.alternate_sources, cursor=data.time[end - 1])
            if phase == "alternate":
                active_source = int(data.alternate_active[end - 1])
                self.badge.set_position((0.621, 0.628))
                self.badge.set_text(self.labels("scene2_one_active", number=active_source + 1))
                self.badge.set_color(self.colors[active_source])
                self.formula.set_position((0.621, 0.540))
                self.formula.set_color(self.colors[active_source])
                self.formula.set_text(rf"$\mathbf{{x}}(t)=a_{active_source+1}\,s_{active_source+1}(t)$")
                last = self.spatial_points(data.alternate_observations, np.array([end - 1]))
                set_line_3d(self.moving_markers[active_source], last)
            elif phase == "directions":
                focus = 0 if p < SCENE2["project_second_start"] else 1
                if p < SCENE2["top_view_start"]:
                    self.phase.set_text(self.labels("scene2_project_source", number=focus + 1))
                    self.phase.set_color(self.colors[focus])
                    self.badge.set_text(self.labels("scene2_column", number=focus + 1))
                    self.badge.set_color(self.colors[focus])
                    self.formula.set_text(rf"$x_2=\frac{{A_{{2{focus+1}}}}}{{A_{{1{focus+1}}}}}\,x_1$")
                    self.formula.set_color(self.colors[focus])
                else:
                    self.formula.set_text(r"$a_j=(A_{1j},\ A_{2j})^{\mathsf{T}}$")
                self._track_projection(focus, projections[focus], camera_amount)
                self.strip.cursors[0].set_visible(False)
                self.strip.cursors[1].set_visible(False)
            else:
                amount = smooth(p, SCENE2["basis_start"] + 0.010, SCENE2["basis_end"] - 0.012)
                transform = mixing_coordinates(data.mixing[:2], amount)
                transformed = data.alternate_observations[:, :2] @ transform.T
                new_limit = (1 - amount) * self.limit + amount * 1.15 * np.max(np.abs(data.sources))
                self.ax2.set_xlim(-new_limit, new_limit)
                self.ax2.set_ylim(-new_limit, new_limit)
                for j in range(2):
                    active = np.flatnonzero(data.alternate_active == j)[::self.stride]
                    self.dots2[j].set_data(transformed[active, 0], transformed[active, 1])
                    self._draw_direction(j, data.mixing[:, j], transform=transform, limit=new_limit)
                self.floor_heading.set_text(self.labels("scene2_source_plane"))
                self.ax2.set_xlabel(r"$s_1(t)$" if amount > 0.999 else r"$u_1$")
                self.ax2.set_ylabel(r"$s_2(t)$" if amount > 0.999 else r"$u_2$")
                self.badge.set_text(r"$W_{\mathrm{ideal}}=A^{-1}$")
                self.formula.set_text(r"$\widehat{\mathbf{s}}=W\mathbf{x}$")
                self.strip.cursors[0].set_visible(False)
                self.strip.cursors[1].set_visible(False)
        else:
            end = max(2, min(len(data.time), int(ramp(p, SCENE2["simultaneous_start"],
                                                         SCENE2["simultaneous_end"]) * len(data.time))))
            indices = np.arange(0, end, self.stride)
            projection = smooth(p, SCENE2["simultaneous_end"], SCENE2["joint_projection_end"])
            original = self.spatial_points(data.observations, indices)
            set_scatter_3d(self.cloud, flatten_points(original, projection))
            self.mix2.set_data(original[:, 0], original[:, 1])
            self.mix2.set_alpha(0.5 * projection)
            if phase == "simultaneous":
                self.ax2.set_visible(False)
                self.floor_heading.set_text("")
                self.formula.set_position((0.621, 0.550))
                self.formula.set_text(r"$\mathbf{x}(t)=a_1s_1(t)+a_2s_2(t)$")
            else:
                set_scatter_3d(self.ghost_cloud, original)
                self.ghost_cloud.set_alpha(0.13 * (1 - smooth(p, 0.884, 0.92)))
                guides = original[::max(1, len(original) // 15)]
                self.joint_guides.set_segments(projection_guides(guides))
                self.joint_guides.set_alpha(0.38 if projection < 0.999 else 0.0)
                if p < SCENE2["joint_projection_end"]:
                    self.phase.set_text(self.labels("scene4_projecting"))
                else:
                    for j in range(2):
                        length = self.limit * (0.92 if j == 0 else 0.60)
                        segment = direction_segment(self.pca_projected.components_[j], length, dimensions=2)
                        self.pca2[j].set_data(segment[:, 0], segment[:, 1])
                        self.pca2[j].set_alpha(0.48 if phase == "ica" else smooth(p, 0.875, 0.89))
                    self.note.set_text(self.labels("scene2_ica_note" if phase == "ica" else "scene2_pca_note"))
                if phase == "ica":
                    for j in range(2):
                        self._draw_direction(j, data.ica.mixing[:, j],
                                              smooth(p, SCENE2["ica_start"], 0.943), estimated=True)
            self.strip.update(data.sources, cursor=data.time[end - 1] if phase == "simultaneous" else None,
                              recovered=data.ica.sources if phase == "ica" else None)
        self.strip.heading.set_text(self.labels("source_reference" if phase == "ica" else "source_signals"))
        self.finish(progress, fade)


class ReducedScene(BaseScene):
    scene_id = "3"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        data = self.data
        self.limit = float(np.max(np.abs(data.observations))) * 1.06
        self.ax3 = self.figure.add_axes([0.008, 0.295, 0.56, 0.50], projection="3d")
        style_3d(self.ax3, self.config, self.limit, (-self.limit, self.limit), r"$x_3$")
        self.ax3.set_xlabel(r"$x_1$")
        self.ax3.set_ylabel(r"$x_2$")
        self.ax3.set_box_aspect((1, 1, 1))
        self.ax3.view_init(self.config["render"]["camera_elevation"], self.config["render"]["camera_azimuth"])
        self.source_clouds = [self.ax3.scatter([], [], [], color=self.colors[j], s=6, alpha=0.8,
                                               depthshade=False) for j in range(3)]
        self.mixture_cloud = self.ax3.scatter([], [], [], color=self.style["combined_color"],
                                              s=3, alpha=0.20, depthshade=False)
        self.true_axes = [self.ax3.plot([], [], [], color=self.colors[j], linewidth=1.0,
                                        linestyle=(0, (3, 4)), alpha=0.8)[0] for j in range(3)]
        self.ica_axes = [self.ax3.plot([], [], [], color=color, linewidth=2.6)[0]
                         for color in (self.colors[0], self.style["residual_color"])]
        first, second = data.pca_directions[:, :2].T
        length = self.limit * 0.82
        vertices = [(sx * first + sy * second) * length for sx, sy in ((-1, -1), (-1, 1), (1, 1), (1, -1))]
        self.plane = Poly3DCollection([vertices], facecolor=self.style["combined_color"],
                                      edgecolor=self.style["muted"], alpha=0)
        self.ax3.add_collection3d(self.plane)
        self.reference_note = self.text(0.057, 0.781, self.labels("scene3_reference"), 8.3,
                                        self.style["muted"], linespacing=1.4)
        self.pipeline = self.text(0.602, 0.786, "", 11, weight="bold")
        self.strong = self.text(0.602, 0.695, "", 11, self.colors[0])
        self.weak = self.text(0.602, 0.646, "", 10.5, self.style["residual_color"], va="top", linespacing=1.5)
        self.inset_title = self.text(0.602, 0.536, self.labels("scene3_inset"), 8.5, self.style["muted"])
        self.inset = self.figure.add_axes([0.606, 0.401, 0.30, 0.12])
        self.inset.axis("off")
        self.inset.set_xlim(-0.15, 1.2)
        self.inset.set_ylim(-0.42, 0.42)
        basis_first = data.mixing[:, 1] / np.linalg.norm(data.mixing[:, 1])
        basis_second = data.mixing[:, 2] - np.dot(data.mixing[:, 2], basis_first) * basis_first
        basis_second /= np.linalg.norm(basis_second)
        projected_vectors = []
        for vector in (data.mixing[:, 1], data.mixing[:, 2], data.ica.mixing[:, 1]):
            vector = vector / np.linalg.norm(vector)
            if np.dot(vector, basis_first) < 0:
                vector = -vector
            projected_vectors.append(np.array([vector @ basis_first, vector @ basis_second]))
        # Center the small angular sector around the horizontal axis.
        half_angle = np.arctan2(projected_vectors[1][1], projected_vectors[1][0]) / 2
        rotation = np.array([[np.cos(half_angle), np.sin(half_angle)], [-np.sin(half_angle), np.cos(half_angle)]])
        self.inset_artists = []
        for vector, color, label in zip(projected_vectors,
                                         [self.colors[1], self.colors[2], self.style["residual_color"]],
                                         [r"$a_2$", r"$a_3$", "ICA 2"]):
            point = rotation @ vector
            line, = self.inset.plot([0, point[0]], [0, point[1]], color=color, linewidth=2)
            text = self.inset.text(point[0] + 0.04, point[1], label, color=color, fontsize=9, va="center")
            self.inset_artists.extend([line, text])
        self.warning = self.text(0.602, 0.367, "", 9.5, self.style["muted"], va="top", linespacing=1.4)
        self.correlations = np.abs(cross_correlation(data.sources, data.ica.sources))
        self.full_correlation = float(np.abs(np.diag(cross_correlation(data.sources, data.full_ica.sources))).min())
        self.indices = np.arange(0, len(data.time), max(1, len(data.time) // 380))
        self.strip.heading.set_text(self.labels("same_scale"))

    def update(self, progress: float, fade: bool = False) -> None:
        p, data = progress, self.data
        count = max(2, int(ramp(p, 0.02, 0.25) * len(self.indices)))
        indices = self.indices[:count]
        for j in range(3):
            contribution = data.sources[indices, j, None] * data.mixing[:, j]
            set_scatter_3d(self.source_clouds[j], contribution)
            segment = direction_segment(data.mixing[:, j], self.limit * 0.87)
            set_line_3d(self.true_axes[j], segment)
            self.true_axes[j].set_alpha(0.6 * smooth(p, 0.13, 0.28))
        self.phase.set_text(self.labels("scene3_clouds"))
        mixture_count = int(ramp(p, 0.25, 0.4) * len(self.indices))
        set_scatter_3d(self.mixture_cloud, data.observations[self.indices[:mixture_count]])
        if p >= 0.25:
            self.phase.set_text(self.labels("scene3_mixtures"))
        plane_alpha = smooth(p, 0.4, 0.55) * 0.12
        self.plane.set_alpha(plane_alpha)
        if p >= 0.4:
            self.phase.set_text(self.labels("scene3_pca"))
        visibility = smooth(p, 0.55, 0.7)
        for j in range(2):
            segment = direction_segment(data.ica.mixing[:, j], self.limit * 0.88 * visibility)
            set_line_3d(self.ica_axes[j], segment)
            self.ica_axes[j].set_alpha(visibility)
        self.pipeline.set_text(self.labels("scene3_pipeline") if p >= 0.4 else "")
        self.strong.set_text(self.labels("scene3_strong") if p >= 0.55 else "")
        self.weak.set_text(self.labels("scene3_weak") if p >= 0.68 else "")
        for item in self.inset_artists:
            item.set_alpha(visibility)
        self.inset_title.set_alpha(visibility)
        self.warning.set_text(self.labels("scene3_warning") if p >= 0.72 else "")
        if p >= 0.55:
            self.phase.set_text(self.labels("scene3_ica"))
        if p >= 0.8:
            self.phase.set_text(self.labels("scene3_conclusion"))
        # Time is intentionally absent from the cloud: all samples are a static dataset.
        self.strip.update(data.sources, cursor=None)
        self.finish(progress, fade)


class IdenticalScene(BaseScene):
    scene_id = "4"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        data = self.data
        self.limit = float(np.max(np.abs(data.observations))) * 1.16
        self.ax3 = self.figure.add_axes([0.012, 0.294, 0.55, 0.51], projection="3d")
        style_3d(self.ax3, self.config, self.limit, (0, self.config["signals"]["duration"]), self.labels("time_axis"))
        self.trajectory = self.ax3.plot([], [], [], color=self.style["foreground"], linewidth=1.5)[0]
        self.common_axis = self.ax3.plot([], [], [], color=self.style["residual_color"], linewidth=2.7)[0]
        self.projection_lines = [self.ax3.plot([], [], [], color=self.style["muted"], linewidth=0.5, alpha=0.3)[0] for _ in range(12)]
        self.ax2 = self.figure.add_axes([0.637, 0.43, 0.282, 0.30])
        style_2d(self.ax2, self.config, equal=True)
        self.ax2.set_xlim(-self.limit, self.limit)
        self.ax2.set_ylim(-self.limit, self.limit)
        self.ax2.set_xlabel(r"$x_1(t)$", fontsize=10, labelpad=1)
        self.ax2.set_ylabel(r"$x_2(t)$", fontsize=10, labelpad=1)
        self.floor_points = self.ax2.plot([], [], ".", color=self.style["foreground"], markersize=3)[0]
        self.floor_axis = self.ax2.plot([], [], color=self.style["residual_color"], linewidth=2.5)[0]
        self.heading = self.text(0.602, 0.79, self.labels("scene4_shared"), 10, weight="bold")
        self.formula = self.text(0.602, 0.75, r"$\mathbf{x}(t)=(a_1+a_2)\,s(t)$", 19)
        self.ranks = self.text(0.602, 0.377, "", 11, self.style["residual_color"])
        self.note = self.text(0.602, 0.342, "", 10, self.style["muted"], va="top", linespacing=1.45)
        self.plot_note = self.text(0.057, 0.3, "", 9, self.style["muted"])
        self.strip.heading.set_text(self.labels("source_signals"))

    def update(self, progress: float, fade: bool = False) -> None:
        p, data = progress, self.data
        end = max(2, int(ramp(p, 0.03, 0.58) * len(data.time)))
        end = min(end, len(data.time))
        collapse = smooth(p, 0.6, 0.84)
        points = np.column_stack([data.observations[:end], data.time[:end] * (1 - collapse)])
        set_line_3d(self.trajectory, points)
        self.floor_points.set_data(data.observations[:end:3, 0], data.observations[:end:3, 1])
        if p < 0.6:
            self.phase.set_text(self.labels("scene4_growing"))
            self.note.set_text(self.labels("scene4_formula_note"))
        elif p < 0.84:
            self.phase.set_text(self.labels("scene4_projecting"))
            self.note.set_text("")
        else:
            self.phase.set_text(self.labels("scene4_rank"))
            self.note.set_text(self.labels("scene4_common"))
        axis = direction_segment(data.mixing.sum(axis=1), self.limit * 1.03)
        set_line_3d(self.common_axis, axis)
        self.common_axis.set_alpha(smooth(p, 0.65, 0.84))
        self.floor_axis.set_data(axis[:, 0], axis[:, 1])
        self.floor_axis.set_alpha(smooth(p, 0.60, 0.75))
        for line, index in zip(self.projection_lines, np.linspace(0, end - 1, 12).astype(int)):
            top = np.r_[data.observations[index], data.time[index] * (1 - collapse)]
            bottom = top.copy()
            bottom[2] = 0
            set_line_3d(line, np.array([top, bottom]))
            line.set_alpha(0.3 if 0.60 <= p <= 0.84 else 0)
        self.ranks.set_text(r"$\mathrm{rank}(X)=1$" if p > 0.58 else r"$s_1(t)=s_2(t)=s(t)$")
        self.heading.set_text(self.labels("scene4_floor" if p > 0.84 else "scene4_shared"))
        self.plot_note.set_text(self.labels("projection") if p > 0.60 else "")
        self.strip.update(data.sources, cursor=data.time[end - 1])
        self.finish(progress, fade)


SCENES = {"1": MixingScene, "2": GeometryScene, "3": ReducedScene, "4": IdenticalScene}
