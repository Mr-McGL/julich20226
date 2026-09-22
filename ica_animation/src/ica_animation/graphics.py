"""Reusable vector artwork and plot components. No external image assets."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.patches import Arc, Circle, FancyBboxPatch, Polygon, Rectangle
from matplotlib.transforms import Affine2D
from matplotlib.ticker import MaxNLocator
from .timeline import smooth


def apply_style(config: dict) -> None:
    style = config["style"]
    mpl.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 12,
        "figure.facecolor": style["background"], "axes.facecolor": style["background"],
        "savefig.facecolor": style["background"], "text.color": style["foreground"],
        "axes.labelcolor": style["muted"], "axes.edgecolor": style["grid"],
        "xtick.color": style["muted"], "ytick.color": style["muted"],
        "mathtext.fontset": "dejavusans", "text.usetex": False,
        "axes.unicode_minus": True, "path.simplify": True,
    })


def style_2d(ax: Axes, config: dict, equal: bool = False) -> None:
    style = config["style"]
    ax.set_facecolor(style["background"])
    ax.grid(True, color=style["grid"], linewidth=0.55, alpha=0.6)
    ax.tick_params(labelsize=9, length=0, pad=6)
    ax.spines[["top", "right"]].set_visible(False)
    for name in ("bottom", "left"):
        ax.spines[name].set_color(style["grid"])
    ax.xaxis.set_major_locator(MaxNLocator(4))
    ax.yaxis.set_major_locator(MaxNLocator(3))
    if equal:
        ax.set_aspect("equal", adjustable="box")


def style_3d(ax: Axes, config: dict, limit: float, z_limit: tuple[float, float], z_label: str) -> None:
    style = config["style"]
    ax.set_facecolor(style["background"])
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.set_pane_color((0, 0, 0, 1))
        axis.line.set_color(style["grid"])
        axis._axinfo["grid"].update({"color": style["grid"], "linewidth": 0.55})
        axis.set_major_locator(MaxNLocator(3))
        axis.label.set_color(style["muted"])
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_zlim(*z_limit)
    ax.set_xlabel(r"$x_1(t)$", labelpad=5, fontsize=11)
    ax.set_ylabel(r"$x_2(t)$", labelpad=5, fontsize=11)
    ax.set_zlabel(z_label, labelpad=3, fontsize=10)
    ax.tick_params(labelsize=8, pad=0, colors=style["muted"])
    ax.set_box_aspect((1.05, 1.05, 0.83))
    ax.view_init(config["render"]["camera_elevation"], config["render"]["camera_azimuth"])
    ax.set_proj_type("ortho")


def set_line_3d(line, points: np.ndarray) -> None:
    if len(points) == 0:
        line.set_data_3d([], [], [])
    else:
        line.set_data_3d(points[:, 0], points[:, 1], points[:, 2])


def set_scatter_3d(scatter, points: np.ndarray) -> None:
    if len(points) == 0:
        scatter._offsets3d = ([], [], [])
    else:
        scatter._offsets3d = (points[:, 0], points[:, 1], points[:, 2])


def direction_segment(direction: np.ndarray, length: float, dimensions: int = 3) -> np.ndarray:
    vector = np.asarray(direction, dtype=float)
    vector = vector / max(np.linalg.norm(vector), 1e-14) * length
    if len(vector) < dimensions:
        vector = np.pad(vector, (0, dimensions - len(vector)))
    return np.asarray([-vector, vector])


@dataclass
class DeviceIcon:
    ax: Axes
    kind: str
    name: str
    color: str
    scale: float = 0.34

    def __post_init__(self) -> None:
        if self.kind == "speaker":
            vertices = [(-0.65, -0.25), (-0.23, -0.25), (0.40, -0.70),
                        (0.40, 0.70), (-0.23, 0.25), (-0.65, 0.25)]
            self.parts = [Polygon(vertices, closed=True, fill=False, edgecolor=self.color, linewidth=1.7)]
            for width in (1.55, 2.05):
                self.parts.append(Arc((0.15, 0.0), width, width, theta1=-40, theta2=40,
                                      edgecolor=self.color, linewidth=1.15))
        else:
            self.parts = [FancyBboxPatch((-0.23, -0.12), 0.46, 0.93,
                                         boxstyle="round,pad=0.02,rounding_size=0.22",
                                         fill=False, edgecolor=self.color, linewidth=1.7),
                          Arc((0, 0.24), 0.87, 1.20, theta1=180, theta2=360,
                              edgecolor=self.color, linewidth=1.5)]
            self.parts.append(Polygon([(0, -0.37), (0, -0.85), (-0.38, -0.85),
                                        (0.38, -0.85)], closed=False, fill=False,
                                       edgecolor=self.color, linewidth=1.5))
        for part in self.parts:
            part.set_zorder(8)
            self.ax.add_patch(part)
        self.label = self.ax.text(0, 0, self.name, color=self.color, fontsize=10,
                                   ha="center", va="top", zorder=9)

    def update(self, position, alpha: float = 1.0) -> None:
        transform = Affine2D().scale(self.scale).translate(*position) + self.ax.transData
        for part in self.parts:
            part.set_transform(transform)
            part.set_alpha(alpha)
        self.label.set_position((position[0], position[1] - self.scale * 1.13))
        self.label.set_alpha(alpha)


class DeviceRoom:
    """Animated speaker/microphone layout with distance-attenuated wave ribbons."""

    def __init__(self, ax: Axes, config: dict, scene: dict, target: dict | None = None) -> None:
        self.ax, self.config, self.scene, self.target = ax, config, scene, target or scene
        self.icons, self.positions, self.targets, self.survivors = [], [], [], []
        self.source_indices = []
        self.mic_indices = []
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.axis("off")
        all_points = []
        for kind, key in (("speaker", "speakers"), ("microphone", "microphones")):
            initial = {item["id"]: item for item in scene[key]}
            final = {item["id"]: item for item in self.target[key]}
            names = list(initial) + [name for name in final if name not in initial]
            for index, name in enumerate(names):
                start = initial.get(name, final.get(name))["position"]
                end = final.get(name, initial.get(name))["position"]
                color = config["style"]["source_colors"][index] if kind == "speaker" else config["style"]["microphone_color"]
                icon = DeviceIcon(ax, kind, name, color)
                (self.source_indices if kind == "speaker" else self.mic_indices).append(len(self.icons))
                self.icons.append(icon)
                self.positions.append(np.asarray(start, dtype=float))
                self.targets.append(np.asarray(end, dtype=float))
                self.survivors.append((name in initial, name in final))
                all_points.extend([start, end])
        points = np.asarray(all_points)
        pad = 0.95
        self.ax.set_xlim(points[:, 0].min() - pad, points[:, 0].max() + pad)
        self.ax.set_ylim(points[:, 1].min() - pad, points[:, 1].max() + pad)
        self.ribbons = {}
        for j, source in enumerate(self.source_indices):
            for i, mic in enumerate(self.mic_indices):
                line, = ax.plot([], [], color=config["style"]["source_colors"][j],
                                linewidth=1.0, alpha=0.4, zorder=2)
                self.ribbons[(j, i)] = line
        self.rings = []
        for j in range(len(self.source_indices)):
            rings = []
            for _ in range(3):
                ring = Circle((0, 0), 0.1, fill=False, edgecolor=config["style"]["source_colors"][j],
                              linewidth=0.9, zorder=1)
                ax.add_patch(ring)
                rings.append(ring)
            self.rings.append(rings)

    def update(self, time: float, blend: float = 0.0, activity=None, waves: bool = True,
               alpha: float = 1.0, highlight_mic: int | None = None) -> None:
        positions, alphas = [], []
        for icon, start, end, (was_present, is_present) in zip(self.icons, self.positions, self.targets, self.survivors):
            position = (1 - blend) * start + blend * end
            opacity = alpha * (1.0 if was_present and is_present else ((1 - blend) if was_present else blend))
            icon.update(position, opacity)
            positions.append(position)
            alphas.append(opacity)
        activity = np.ones(len(self.source_indices)) if activity is None else activity
        for (j, i), line in self.ribbons.items():
            source, microphone = self.source_indices[j], self.mic_indices[i]
            start, end = positions[source], positions[microphone]
            delta = end - start
            distance = np.linalg.norm(delta)
            normal = np.asarray([-delta[1], delta[0]]) / max(distance, 1e-8)
            fraction = np.linspace(0.1, 0.90, 100)
            local_distance = fraction * distance
            amplitude = 0.13 / np.maximum(local_distance, 0.5)
            sine = np.sin(2 * np.pi * (fraction * 3.8 - time * (0.8 + j * 0.2)))
            path = start + fraction[:, None] * delta + (amplitude * sine)[:, None] * normal
            line.set_data(path[:, 0], path[:, 1])
            opacity = min(alphas[source], alphas[microphone]) * (activity[j] if j < len(activity) else 0.0)
            line.set_alpha(opacity * (0.7 if highlight_mic == i else 0.33) if waves else 0.0)
        for j, rings in enumerate(self.rings):
            for ring_index, ring in enumerate(rings):
                phase = (time * 0.38 + ring_index / 3) % 1.0
                ring.center = positions[self.source_indices[j]]
                ring.set_radius(0.3 + phase * 2.0)
                enabled = activity[j] if j < len(activity) else 0.0
                ring.set_alpha((1 - phase) * 0.19 * alphas[self.source_indices[j]] * enabled if waves else 0)


class SignalStrip:
    """Persistent source traces with a shared amplitude scale and time cursor."""

    def __init__(self, figure: Figure, config: dict, labels, time: np.ndarray, sources: np.ndarray, show_variance: bool = False) -> None:
        self.figure, self.config, self.time = figure, config, time
        self.axes, self.lines, self.cursors, self.recovered = [], [], [], []
        self.variance_labels = []
        self.heading = figure.text(0.057, 0.255, labels("source_signals"), fontsize=9,
                                   color=config["style"]["muted"], weight="bold")
        count = sources.shape[1]
        limit = float(np.max(np.abs(sources))) * 1.18
        width = 0.875 / count
        for j in range(count):
            ax = figure.add_axes([0.062 + j * (0.91 / count), 0.075, width, 0.135])
            style_2d(ax, config)
            ax.set_xlim(time[0], time[-1])
            ax.set_ylim(-limit, limit)
            ax.set_xticks([0, time[-1] / 2, time[-1]])
            ax.set_xticklabels(["0", f"{time[-1]/2:.0f}", f"{time[-1]:.0f} s"])
            ax.set_yticks([-round(limit / 1.18, 2), 0, round(limit / 1.18, 2)])
            ax.tick_params(labelsize=8)
            color = config["style"]["source_colors"][j]
            ax.text(0, 1.17, rf"$s_{j+1}(t)$" + "  " + labels("source", number=j + 1),
                    color=color, fontsize=10, transform=ax.transAxes)
            variance_label = ax.text(1.0, 1.17, labels("variance", value=sources[:, j].var()),
                                     color=config["style"]["muted"], fontsize=8,
                                     transform=ax.transAxes, ha="right")
            line, = ax.plot(time, sources[:, j], color=color, linewidth=1.3)
            recovered_line, = ax.plot([], [], color=config["style"]["foreground"], linewidth=1.0,
                                      linestyle=(0, (4, 3)), alpha=0.8)
            cursor = ax.axvline(0, color=color, linewidth=0.9, alpha=0.6)
            self.axes.append(ax)
            self.lines.append(line)
            self.cursors.append(cursor)
            self.recovered.append(recovered_line)
            variance_label.set_visible(show_variance)
            self.variance_labels.append(variance_label)
        self.labels = labels

    def update(self, sources: np.ndarray, cursor: float | None = None, recovered: np.ndarray | None = None,
               reveal: float = 1.0) -> None:
        count = max(2, int(len(self.time) * reveal))
        for j, line in enumerate(self.lines):
            line.set_data(self.time[:count], sources[:count, j])
            self.cursors[j].set_visible(cursor is not None)
            if cursor is not None:
                self.cursors[j].set_xdata([cursor, cursor])
            self.variance_labels[j].set_text(self.labels("variance", value=sources[:, j].var()))
            self.recovered[j].set_data((self.time, recovered[:, j]) if recovered is not None else ([], []))


class MatrixDisplay:
    """A compact numeric matrix with column-colored entries and vector brackets."""

    def __init__(self, ax: Axes, matrix: np.ndarray, colors: list[str],
                 row_labels: list[str] | None = None,
                 column_labels: list[str] | None = None) -> None:
        self.artists = []
        rows, columns = matrix.shape
        left, right, bottom, top = 0.06, 0.94, 0.2, 0.80
        dx = (right - left) / columns
        dy = (top - bottom) / rows
        for j, label in enumerate(column_labels or []):
            self.artists.append(ax.text(left + (j + 0.5) * dx, top + 0.10, label,
                                       color=colors[j], fontsize=10, ha="center",
                                       transform=ax.transAxes))
        for i, label in enumerate(row_labels or []):
            self.artists.append(ax.text(left - 0.08, top - (i + 0.5) * dy, label,
                                       color="#929DAF", fontsize=9, ha="right", va="center",
                                       transform=ax.transAxes))
        for i in range(rows):
            for j in range(columns):
                item = ax.text(left + (j + 0.5) * dx, top - (i + 0.5) * dy,
                               f"{matrix[i, j]:.3f}", color=colors[j], ha="center", va="center",
                               fontsize=max(10, 17 - max(0, columns - 3)), transform=ax.transAxes)
                self.artists.append(item)
        for x, sign in ((left - 0.015, 1), (right + 0.015, -1)):
            line, = ax.plot([x + sign * 0.025, x, x, x + sign * 0.025],
                            [top, top, bottom, bottom], color="#F2F4F8", linewidth=1.6,
                            transform=ax.transAxes)
            self.artists.append(line)

    def set_alpha(self, alpha: float) -> None:
        for artist in self.artists:
            artist.set_alpha(alpha)
