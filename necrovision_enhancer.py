#!/usr/bin/env python3
"""
NECROVISION // Deep-Frame Resurrection Engine
=============================================
A next-generation Hollywood horror/sci-fi post-production tool.

Somewhere between a VFX pipeline and a haunted machine, NECROVISION
exhumes low-resolution HEIF images and resurrects them at 4x scale,
then passes them through 7 experimental enhancement modules recovered
from a decommissioned studio render farm. Studio legend says the
original colorist never logged out.

FOR INTERNAL USE ONLY — BLACKLIGHT PICTURES, POST-PRODUCTION DIVISION
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
import json

import cv2
import numpy as np
from PIL import Image
import torch
from torch import nn
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk
from tkinter import Canvas, Label, Frame, StringVar, DoubleVar, Scale
import threading
from datetime import datetime


# ============================================================================
# THE ENGINE — Resurrection Core and Anomaly Modules
# ============================================================================

class ResurrectionUpscaler:
    """4x frame resurrection core. Exhumes detail from dead pixels."""

    def __init__(self, scale_factor: int = 4):
        self.scale_factor = scale_factor
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    def upscale(self, image: np.ndarray) -> np.ndarray:
        """Resurrect the frame at 4x scale using cubic reconstruction."""
        try:
            height, width = image.shape[:2]
            new_height = height * self.scale_factor
            new_width = width * self.scale_factor
            upscaled = cv2.resize(image, (new_width, new_height),
                                  interpolation=cv2.INTER_CUBIC)
            return upscaled
        except Exception as e:
            print(f"[RESURRECTION FAILURE] {e}")
            return image


class AnomalyEffectsProcessor:
    """7 experimental enhancement modules. Handle with gloves."""

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    # Module 1: NECRO GRADE — horror color science
    def necro_grade(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Horror-grade color science: sickly green-teal shadows, cold sterile
        highlights, crushed contrast. The palette of every abandoned
        laboratory and derelict starship in modern cinema.
        """
        image_float = image.astype(np.float32) / 255.0

        # Convert to LAB color space for surgical color manipulation
        image_bgr = cv2.cvtColor((image_float * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        image_lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

        # Crush the luminance — horror lives in the dark
        L = image_lab[:, :, 0]
        mean_L = np.mean(L)
        L = mean_L + (L - mean_L) * (1 + intensity * 0.35)
        L = L - intensity * 8  # pull the whole frame toward the void
        L = np.clip(L, 0, 255)
        image_lab[:, :, 0] = L

        # Sickly green-teal shadows, cold blue highlights
        A = image_lab[:, :, 1]
        B = image_lab[:, :, 2]

        shadow_mask = np.clip(1 - (L / 128), 0, 1)
        highlight_mask = np.clip((L - 128) / 128, 0, 1)

        # Negative A = green shift, negative B = blue shift
        A = A - (12 * intensity * shadow_mask) - (4 * intensity * highlight_mask)
        B = B - (6 * intensity * shadow_mask) - (10 * intensity * highlight_mask)

        image_lab[:, :, 1] = np.clip(A, 0, 255)
        image_lab[:, :, 2] = np.clip(B, 0, 255)

        result = cv2.cvtColor(image_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        return result

    # Module 2: EVENT HORIZON — HDR tone collapse
    def event_horizon_hdr(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Gravitational tone mapping. Dynamic range is stretched until the
        highlights scream and the shadows swallow light whole — the
        Uncharted 2 filmic curve, pushed past its safety rating.
        """
        image_float = image.astype(np.float32) / 255.0

        # Filmic tone curve coefficients (do not ask what F stands for)
        A = 0.15 * intensity
        B = 0.50 * intensity
        C = 0.10
        D = 0.20
        E = 0.02
        F = 0.30

        def tonemap(x):
            return ((x * (A * x + C * B) + D * E) /
                    (x * (A * x + B) + D * F)) - E / F

        result = tonemap(image_float) / tonemap(np.array([11.2]))
        result = np.clip(result * 255, 0, 255).astype(np.uint8)
        return result

    # Module 3: SIGNAL EXORCISM — noise purge
    def signal_exorcism(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Edge-aware bilateral purge. Removes the static — the whispers in
        the grain — while leaving the subject's edges intact. Whatever was
        in the noise, it isn't there afterward.
        """
        image_uint8 = image.astype(np.uint8)

        radius = int(5 + intensity * 10)
        sigma_color = 50 + intensity * 50
        sigma_space = 50 + intensity * 50

        purged = cv2.bilateralFilter(image_uint8, radius, sigma_color, sigma_space)

        # Blend with the original — never purge a frame completely
        alpha = intensity * 0.6
        result = cv2.addWeighted(image_uint8, 1 - alpha, purged, alpha, 0)
        return result

    # Module 4: XENO-DETAIL — forensic sharpening
    def xeno_detail(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Multi-scale forensic sharpening. Resolves micro-detail the camera
        never consciously recorded: pores, fibers, the texture of things
        moving at the edge of frame.
        """
        image_float = image.astype(np.float32)

        # Separate the frame into detail strata
        blur1 = cv2.GaussianBlur(image_float, (5, 5), 1.0)
        blur2 = cv2.GaussianBlur(image_float, (15, 15), 3.0)

        detail_layer = image_float - blur1
        micro_detail = blur1 - blur2

        strength = intensity * 2.0
        result = image_float + (detail_layer * strength * 0.5) + (micro_detail * strength * 0.3)
        result = np.clip(result, 0, 255).astype(np.uint8)
        return result

    # Module 5: RETINAL RECONSTRUCTION — edge-guided super resolution
    def retinal_reconstruction(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Edge-guided perceptual reconstruction. Traces every contour with
        Canny detection and rebuilds high-frequency detail along the
        edges — the way an eye reconstructs a shape in a dark hallway.
        """
        image_float = image.astype(np.float32) / 255.0

        # Contour extraction
        image_gray = cv2.cvtColor((image_float * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(image_gray, 100, 200).astype(np.float32) / 255.0

        # Let the edges grow
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges_dilated = cv2.dilate(edges, kernel, iterations=2)

        image_uint8 = (image_float * 255).astype(np.uint8)
        blurred = cv2.GaussianBlur(image_uint8, (3, 3), 1.0)

        # Selective sharpening along the contours
        edge_mask = np.stack([edges_dilated] * 3, axis=2)
        sharpened = image_uint8.astype(np.float32) + (
            (image_uint8.astype(np.float32) - blurred.astype(np.float32)) *
            edge_mask * intensity
        )
        result = np.clip(sharpened, 0, 255).astype(np.uint8)
        return result

    # Module 6: BIOLUMINESCENCE — otherworldly saturation
    def bioluminescence(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Content-aware vibrance with an unnatural glow. Colors saturate as
        if lit from within, while skin tones stay just human enough to be
        unsettling.
        """
        image_hsv = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)

        saturation = image_hsv[:, :, 1]
        value = image_hsv[:, :, 2]

        # Skin tones live roughly at H: 0-25 or 335-360 — keep them (mostly) human
        hue = image_hsv[:, :, 0]
        skin_mask = ((hue < 25) | (hue > 335)).astype(np.float32)

        # Everything non-human glows harder
        saturation_boost = intensity * 30 * (1 + skin_mask * 0.3)
        saturation = np.clip(saturation + saturation_boost, 0, 255)

        image_hsv[:, :, 1] = saturation
        result = cv2.cvtColor(image_hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
        return result

    # Module 7: SPECTRAL DRIFT — dreamlike smoothing
    def spectral_drift(self, image: np.ndarray, intensity: float = 0.7) -> np.ndarray:
        """
        Edge-preserving domain-transform smoothing, applied in passes.
        Each pass makes the frame a little too smooth, a little too calm —
        the visual language of a dream you can't wake from.
        """
        image_uint8 = image.astype(np.uint8)

        sigma_spatial = 5 + intensity * 15
        sigma_range = 0.1 + intensity * 0.2

        for _ in range(int(intensity * 2) + 1):
            if hasattr(cv2, 'ximgproc'):
                drifted = cv2.ximgproc.dtFilter(image_uint8, image_uint8,
                                                sigma_spatial, sigma_range)
            else:
                # Contrib build not installed — fall back to bilateral drift
                drifted = cv2.bilateralFilter(image_uint8, 9,
                                              sigma_range * 255, sigma_spatial)
            image_uint8 = drifted

        return image_uint8


# ============================================================================
# HEIF Containment Unit
# ============================================================================

class HEIFContainmentUnit:
    """Safely opens sealed HEIF/HEIC containers recovered from set."""

    @staticmethod
    def open_heif(file_path: str) -> Optional[Image.Image]:
        """Break the seal on a HEIF/HEIC container."""
        try:
            # Pillow 10.0+ has HEIF support
            image = Image.open(file_path)
            return image
        except Exception as e:
            print(f"[CONTAINMENT BREACH] {e}")
            return None

    @staticmethod
    def to_numpy(pil_image: Image.Image) -> np.ndarray:
        """Convert PIL Image to numpy array (RGB)."""
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        return np.array(pil_image)

    @staticmethod
    def from_numpy(array: np.ndarray) -> Image.Image:
        """Convert numpy array back into a PIL Image."""
        array_uint8 = np.clip(array, 0, 255).astype(np.uint8)
        return Image.fromarray(array_uint8, 'RGB')


# ============================================================================
# CONTROL DECK — Main GUI (Apple dark-mode design language)
# ============================================================================

# macOS / iOS dark system palette
BG = '#1c1c1e'            # system background
CARD = '#2c2c2e'          # secondary background (cards)
CARD_2 = '#3a3a3c'        # tertiary fill (controls)
SEPARATOR = '#38383a'
TEXT_PRIMARY = '#f5f5f7'
TEXT_SECONDARY = '#98989d'
BLUE = '#0a84ff'          # system blue (accent)
GREEN = '#30d158'         # system green
RED = '#ff453a'           # system red
ORANGE = '#ff9f0a'        # system orange
VIEWER_BG = '#000000'     # photo viewer stays true black

UI_FONT = 'Helvetica Neue'


class AppleButton(tk.Canvas):
    """Pill-shaped iOS-style button. Drawn on a Canvas because macOS Tk
    renders native Aqua buttons and ignores their background colors."""

    STYLES = {
        'primary':     {'fill': BLUE,   'hover': '#2b95ff', 'press': '#0774e0', 'text': '#ffffff'},
        'secondary':   {'fill': CARD_2, 'hover': '#48484a', 'press': '#2c2c2e', 'text': TEXT_PRIMARY},
        'destructive': {'fill': RED,    'hover': '#ff5d52', 'press': '#e03a30', 'text': '#ffffff'},
    }

    def __init__(self, parent, text, command, kind='secondary',
                 font_size=13, bold=True, padx=20, height=34):
        self.style = self.STYLES[kind]
        self.command = command
        font = (UI_FONT, font_size, 'bold' if bold else 'normal')
        measured = tkfont.Font(font=font).measure(text)
        width = measured + padx * 2
        super().__init__(parent, width=width, height=height,
                         bg=parent['bg'], highlightthickness=0, cursor='hand2')
        radius = height // 2
        self.shape = self._rounded_rect(1, 1, width - 1, height - 1, radius,
                                        fill=self.style['fill'], outline='')
        self.create_text(width // 2, height // 2, text=text,
                         fill=self.style['text'], font=font)
        self.bind('<Enter>', lambda e: self.itemconfig(self.shape, fill=self.style['hover']))
        self.bind('<Leave>', lambda e: self.itemconfig(self.shape, fill=self.style['fill']))
        self.bind('<ButtonPress-1>', lambda e: self.itemconfig(self.shape, fill=self.style['press']))
        self.bind('<ButtonRelease-1>', self._on_release)

    def _on_release(self, event):
        self.itemconfig(self.shape, fill=self.style['hover'])
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self.command()

    def _rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
                  x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
                  x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.create_polygon(points, smooth=True, **kwargs)


class NecrovisionDeck:
    """NECROVISION operator console. Do not leave a frame rendering overnight.

    Threading rule: Tkinter is NOT thread-safe (especially on macOS).
    Worker threads only compute; every UI update is marshaled back to the
    main thread with self.root.after(0, ...).
    """

    # Display names for the progress readout
    MODULE_NAMES = {
        'exorcism': 'Signal Exorcism',
        'necro': 'Necro Grade',
        'horizon': 'Event Horizon HDR',
        'xeno': 'Xeno-Detail',
        'retinal': 'Retinal Reconstruction',
        'biolume': 'Bioluminescence',
        'drift': 'Spectral Drift',
    }

    def __init__(self, root):
        self.root = root
        self.root.title("NECROVISION — Deep-Frame Resurrection Engine")
        self.root.geometry("1400x900")
        self.root.configure(bg=BG)

        # Initialize the engine
        self.upscaler = ResurrectionUpscaler(scale_factor=4)
        self.effects = AnomalyEffectsProcessor()
        self.containment = HEIFContainmentUnit()

        # Session state
        self.current_image = None
        self.original_image = None
        self.processed_image = None
        self.image_path = StringVar(value="No specimen loaded")

        # Task coordination
        self.busy = False               # a heavy task is running
        self._preview_job = None        # pending debounced preview
        self._preview_running = False   # a preview thread is active

        self.effect_intensities = {
            'necro': DoubleVar(value=0.5),
            'horizon': DoubleVar(value=0.5),
            'exorcism': DoubleVar(value=0.5),
            'xeno': DoubleVar(value=0.5),
            'retinal': DoubleVar(value=0.5),
            'biolume': DoubleVar(value=0.5),
            'drift': DoubleVar(value=0.5),
        }

        self.enabled_effects = {
            'necro': tk.BooleanVar(value=True),
            'horizon': tk.BooleanVar(value=False),
            'exorcism': tk.BooleanVar(value=True),
            'xeno': tk.BooleanVar(value=True),
            'retinal': tk.BooleanVar(value=False),
            'biolume': tk.BooleanVar(value=False),
            'drift': tk.BooleanVar(value=False),
        }

        self.setup_ui()

    # ------------------------------------------------------------------
    # Thread-safe UI helpers
    # ------------------------------------------------------------------

    def ui(self, fn, *args, **kwargs):
        """Run a UI update on the main thread (safe from any thread)."""
        self.root.after(0, lambda: fn(*args, **kwargs))

    def task_begin(self, message: str, determinate: bool = True):
        """Start a task: set status and arm the progress bar."""
        self.busy = True
        self.status_var.set(message)
        self.progress.stop()
        if determinate:
            self.progress.configure(mode='determinate', value=0, maximum=100)
        else:
            self.progress.configure(mode='indeterminate')
            self.progress.start(12)

    def task_progress(self, percent: float, message: str = None):
        """Update the progress bar (0–100) and optionally the status text."""
        if str(self.progress.cget('mode')) != 'determinate':
            self.progress.stop()
            self.progress.configure(mode='determinate', maximum=100)
        self.progress.configure(value=percent)
        if message:
            self.status_var.set(message)

    def task_end(self, message: str):
        """Finish a task: fill the bar, then reset it after a beat."""
        self.busy = False
        self.progress.stop()
        self.progress.configure(mode='determinate', value=100)
        self.status_var.set(message)
        self.root.after(1200, lambda: self.progress.configure(value=0))

    def task_failed(self, title: str, detail: str, status: str):
        """Report a failed task on the main thread."""
        self.busy = False
        self.progress.stop()
        self.progress.configure(mode='determinate', value=0)
        self.status_var.set(status)
        messagebox.showerror(title, detail)

    def reveal_in_file_browser(self, file_path: str):
        """Open the enclosing folder with the file selected."""
        try:
            if sys.platform == 'darwin':
                subprocess.run(['open', '-R', file_path], check=False)
            elif os.name == 'nt':
                subprocess.run(['explorer', '/select,', file_path], check=False)
            else:
                subprocess.run(['xdg-open', str(Path(file_path).parent)], check=False)
        except Exception as e:
            print(f"[REVEAL FAILED] {e}")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _card(self, parent, **pack_kwargs):
        """A flat, Apple-style card container."""
        card = Frame(parent, bg=CARD, bd=0, relief=tk.FLAT,
                     highlightbackground=SEPARATOR, highlightthickness=1)
        card.pack(**pack_kwargs)
        return card

    def setup_ui(self):
        """Assemble the control deck."""
        # Dark progress-bar styling (clam theme allows custom colors)
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass
        style.configure('Necro.Horizontal.TProgressbar',
                        troughcolor=CARD_2, background=BLUE,
                        bordercolor=BG, lightcolor=BLUE, darkcolor=BLUE)
        style.configure('Necro.Vertical.TScrollbar',
                        troughcolor=CARD, background=CARD_2,
                        bordercolor=CARD, arrowcolor=TEXT_SECONDARY)

        main_frame = Frame(self.root, bg=BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Title bar
        header = Frame(main_frame, bg=BG)
        header.pack(fill=tk.X, pady=(0, 12))
        Label(header, text="NECROVISION", bg=BG, fg=TEXT_PRIMARY,
              font=(UI_FONT, 22, 'bold')).pack(side=tk.LEFT)
        Label(header, text="  Deep-Frame Resurrection Engine · Blacklight Pictures",
              bg=BG, fg=TEXT_SECONDARY, font=(UI_FONT, 13)).pack(side=tk.LEFT, pady=(6, 0))

        # Top panel: specimen intake
        self.setup_file_panel(main_frame)

        # Middle: the viewing chamber
        preview_card = self._card(main_frame, fill=tk.BOTH, expand=True, pady=12)

        Label(preview_card, text="VIEWING CHAMBER — LIVE FEED", bg=CARD, fg=TEXT_SECONDARY,
              font=(UI_FONT, 11, 'bold')).pack(anchor='nw', padx=14, pady=(10, 4))

        self.canvas = Canvas(preview_card, bg=VIEWER_BG, width=500, height=400,
                             highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 14))

        # Bottom: anomaly modules
        self.setup_effects_panel(main_frame)

        # Status readout + progress bar
        bottom_bar = Frame(self.root, bg=BG)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_var = StringVar(value="System nominal. Awaiting specimen.")
        Label(bottom_bar, textvariable=self.status_var, bg=BG,
              fg=TEXT_SECONDARY, anchor='w', padx=16, pady=8,
              font=(UI_FONT, 11)).pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.progress = ttk.Progressbar(bottom_bar, style='Necro.Horizontal.TProgressbar',
                                        orient=tk.HORIZONTAL, mode='determinate',
                                        maximum=100, value=0, length=280)
        self.progress.pack(side=tk.RIGHT, padx=16, pady=8)

    def setup_file_panel(self, parent):
        """Specimen intake panel."""
        file_card = self._card(parent, fill=tk.X, pady=(0, 4))
        inner = Frame(file_card, bg=CARD)
        inner.pack(fill=tk.X, padx=14, pady=10)

        Label(inner, text="Specimen", bg=CARD, fg=TEXT_SECONDARY,
              font=(UI_FONT, 12)).pack(side=tk.LEFT, padx=(0, 10))

        path_field = Frame(inner, bg=CARD_2)
        path_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 12))
        Label(path_field, textvariable=self.image_path, bg=CARD_2, fg=TEXT_PRIMARY,
              anchor='w', padx=10, pady=6, font=(UI_FONT, 12)).pack(fill=tk.X)

        AppleButton(inner, "Acquire Specimen", self.open_image,
                    kind='primary').pack(side=tk.LEFT, padx=4)
        AppleButton(inner, "Resurrect 4×", self.upscale_image,
                    kind='secondary').pack(side=tk.LEFT, padx=4)
        AppleButton(inner, "Seal & Archive", self.save_image,
                    kind='secondary').pack(side=tk.LEFT, padx=4)

    def setup_effects_panel(self, parent):
        """Anomaly module rack — 7 experimental effects."""
        effects_card = self._card(parent, fill=tk.X, pady=(8, 0))

        rack_header = Frame(effects_card, bg=CARD)
        rack_header.pack(fill=tk.X, padx=14, pady=(10, 4))
        Label(rack_header, text="ANOMALY MODULE RACK", bg=CARD, fg=TEXT_PRIMARY,
              font=(UI_FONT, 13, 'bold')).pack(side=tk.LEFT)
        Label(rack_header, text="  7 units online · Clearance level Omega",
              bg=CARD, fg=TEXT_SECONDARY, font=(UI_FONT, 11)).pack(side=tk.LEFT, pady=(2, 0))
        AppleButton(rack_header, "Engage All Modules", self.apply_effects,
                    kind='primary').pack(side=tk.RIGHT)

        # Scrollable module rack
        canvas_effects = Canvas(effects_card, bg=CARD, highlightthickness=0, height=220)
        scrollbar = ttk.Scrollbar(effects_card, orient=tk.VERTICAL,
                                  style='Necro.Vertical.TScrollbar',
                                  command=canvas_effects.yview)
        scrollable_frame = Frame(canvas_effects, bg=CARD)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_effects.configure(scrollregion=canvas_effects.bbox("all"))
        )

        window_id = canvas_effects.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_effects.bind(
            "<Configure>",
            lambda e: canvas_effects.itemconfig(window_id, width=e.width)
        )
        canvas_effects.configure(yscrollcommand=scrollbar.set)

        # Module manifest
        effects_config = [
            ('necro', '🩸 Necro Grade', 'Sickly shadows, sterile highlights — abandoned-lab color science'),
            ('horizon', '🕳 Event Horizon HDR', 'Tone collapse past the filmic safety rating'),
            ('exorcism', '📡 Signal Exorcism', 'Purges the whispers hiding in the grain'),
            ('xeno', '🧬 Xeno-Detail', 'Resolves what the camera never consciously recorded'),
            ('retinal', '👁 Retinal Reconstruction', 'Rebuilds edges like an eye in a dark hallway'),
            ('biolume', '☢ Bioluminescence', 'Colors that glow as if lit from within'),
            ('drift', '🌫 Spectral Drift', 'Too smooth, too calm — the dream you can\'t wake from'),
        ]

        for key, title, description in effects_config:
            self.create_effect_control(scrollable_frame, key, title, description)

        canvas_effects.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=14, pady=(4, 14))
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 4), pady=(4, 14))

    def create_effect_control(self, parent, effect_key, title, description):
        """Wire up a single anomaly module's controls — an iOS settings row."""
        row = Frame(parent, bg=CARD_2, bd=0)
        row.pack(fill=tk.X, padx=2, pady=3)

        header_frame = Frame(row, bg=CARD_2)
        header_frame.pack(fill=tk.X, padx=12, pady=(8, 0))

        # Module arm/disarm switch
        check = tk.Checkbutton(header_frame, text=title, variable=self.enabled_effects[effect_key],
                               bg=CARD_2, fg=TEXT_PRIMARY, selectcolor=CARD,
                               font=(UI_FONT, 12, 'bold'), activebackground=CARD_2,
                               activeforeground=BLUE, bd=0, highlightthickness=0)
        check.pack(side=tk.LEFT)

        Label(header_frame, text=description, bg=CARD_2, fg=TEXT_SECONDARY,
              font=(UI_FONT, 11)).pack(side=tk.LEFT, padx=10)

        # Dread level dial
        slider_frame = Frame(row, bg=CARD_2)
        slider_frame.pack(fill=tk.X, padx=12, pady=(0, 8))

        Label(slider_frame, text="Dread level", bg=CARD_2, fg=TEXT_SECONDARY,
              font=(UI_FONT, 11)).pack(side=tk.LEFT)

        scale = Scale(slider_frame, from_=0, to=1, resolution=0.05, orient=tk.HORIZONTAL,
                      variable=self.effect_intensities[effect_key], bg=CARD_2,
                      fg=TEXT_SECONDARY, troughcolor='#48484a', highlightthickness=0,
                      bd=0, showvalue=False, sliderrelief=tk.FLAT,
                      activebackground=BLUE,
                      command=lambda v: self.preview_effects())
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        intensity_label = Label(slider_frame, text="0.50", bg=CARD_2, fg=BLUE,
                                width=5, font=(UI_FONT, 11, 'bold'))
        intensity_label.pack(side=tk.LEFT)

        # Update readout when the dial turns
        def update_intensity_label(v, label=intensity_label):
            label.config(text=f"{float(v):.2f}")

        self.effect_intensities[effect_key].trace_add('write', lambda *args, update=update_intensity_label: update(self.effect_intensities[effect_key].get()))

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def open_image(self):
        """Acquire a specimen from disk."""
        if self.busy:
            self.status_var.set("Engine busy — wait for the current task to finish")
            return

        file_types = [
            ("Image Files", "*.jpg *.jpeg *.png *.heif *.heic *.bmp *.webp"),
            ("HEIF/HEIC", "*.heif *.heic"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("All Files", "*.*")
        ]

        file_path = filedialog.askopenfilename(filetypes=file_types)
        if not file_path:
            return

        self.image_path.set(file_path)
        self.load_image(file_path)

    def load_image(self, file_path: str):
        """Bring the specimen into containment (fast — runs on main thread)."""
        self.task_begin(f"Acquiring specimen: {Path(file_path).name}…")
        self.root.update_idletasks()

        try:
            self.task_progress(30)
            # Sealed HEIF/HEIC containers go through the containment unit
            if file_path.lower().endswith(('.heif', '.heic')):
                pil_image = self.containment.open_heif(file_path)
                if pil_image is None:
                    self.task_failed("Containment Breach", "The HEIF container refused to open.",
                                     "Containment breach — specimen lost")
                    return
                self.current_image = self.containment.to_numpy(pil_image)
            else:
                self.current_image = cv2.imread(file_path)
                if self.current_image is None:
                    self.task_failed("Containment Breach", "The specimen could not be read.",
                                     "Containment breach — specimen lost")
                    return
                self.current_image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)

            self.task_progress(70)
            self.original_image = self.current_image.copy()
            self.processed_image = self.current_image.copy()
            self.display_image(self.current_image)
            self.task_end(
                f"Specimen contained: {Path(file_path).name} "
                f"({self.current_image.shape[1]}×{self.current_image.shape[0]}) — vitals stable"
            )

        except Exception as e:
            self.task_failed("Containment Breach", f"Acquisition failed: {str(e)}",
                             f"Anomaly detected: {str(e)}")

    def display_image(self, image: np.ndarray):
        """Project the specimen into the viewing chamber (main thread only)."""
        try:
            pil_image = Image.fromarray(image.astype(np.uint8))

            # Fit the feed to the chamber
            canvas_width = self.canvas.winfo_width() if self.canvas.winfo_width() > 1 else 600
            canvas_height = self.canvas.winfo_height() if self.canvas.winfo_height() > 1 else 400

            pil_image.thumbnail((canvas_width - 10, canvas_height - 10), Image.Resampling.LANCZOS)

            from PIL import ImageTk
            self.photo_image = ImageTk.PhotoImage(pil_image)
            self.canvas.delete('all')
            self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.photo_image)

        except Exception as e:
            print(f"[FEED INTERRUPTED] {e}")

    def upscale_image(self):
        """Run the resurrection sequence."""
        if self.current_image is None:
            messagebox.showwarning("No Specimen", "Acquire a specimen before attempting resurrection.")
            return
        if self.busy:
            self.status_var.set("Engine busy — wait for the current task to finish")
            return

        self.task_begin("Resurrection in progress (4×)… do not look away from the feed",
                        determinate=False)
        source = self.current_image

        def upscale_thread():
            try:
                upscaled = self.upscaler.upscale(source)

                def done():
                    self.current_image = upscaled
                    self.processed_image = upscaled.copy()
                    self.display_image(upscaled)
                    self.task_end(
                        f"Resurrection complete — specimen now "
                        f"{upscaled.shape[1]}×{upscaled.shape[0]}. It looks… sharper."
                    )
                self.ui(done)
            except Exception as e:
                self.ui(self.task_failed, "Resurrection Failure",
                        f"The sequence collapsed: {e}",
                        "Resurrection failure — specimen unchanged")

        threading.Thread(target=upscale_thread, daemon=True).start()

    def preview_effects(self):
        """Debounced low-resolution live preview of the module chain."""
        if self.current_image is None or self.busy:
            return

        # Debounce: sliders fire on every tick; only preview once they settle
        if self._preview_job is not None:
            self.root.after_cancel(self._preview_job)
        self._preview_job = self.root.after(250, self._run_preview)

    def _run_preview(self):
        self._preview_job = None
        if self._preview_running or self.busy or self.current_image is None:
            return

        self._preview_running = True
        self.status_var.set("Projecting preview…")
        source = self.current_image.copy()

        def preview_thread():
            try:
                preview = self.apply_effects_to_image(source, use_low_res=True)

                def done():
                    self._preview_running = False
                    self.display_image(preview)
                    self.status_var.set("Preview stable — for now")
                self.ui(done)
            except Exception as e:
                print(f"[PREVIEW ANOMALY] {e}")
                self.ui(lambda: setattr(self, '_preview_running', False))

        threading.Thread(target=preview_thread, daemon=True).start()

    def apply_effects_to_image(self, image: np.ndarray, use_low_res: bool = False,
                               progress_cb=None) -> np.ndarray:
        """Route the specimen through every armed anomaly module, in order.

        progress_cb(done, total, module_name) is called after each module
        (from the worker thread — the callback must marshal to the UI itself).
        """
        result = image.copy()

        # Preview mode runs at reduced resolution to keep the feed responsive
        if use_low_res and image.shape[0] > 800:
            scale_factor = 800 / image.shape[0]
            result = cv2.resize(result, (int(result.shape[1] * scale_factor), 800))

        # Module firing order matters — exorcise the signal before grading it
        effects_order = [
            ('exorcism', self.effects.signal_exorcism),
            ('necro', self.effects.necro_grade),
            ('horizon', self.effects.event_horizon_hdr),
            ('xeno', self.effects.xeno_detail),
            ('retinal', self.effects.retinal_reconstruction),
            ('biolume', self.effects.bioluminescence),
            ('drift', self.effects.spectral_drift),
        ]

        armed = [(key, fn) for key, fn in effects_order if self.enabled_effects[key].get()]
        total = len(armed)

        for i, (effect_key, effect_fn) in enumerate(armed, start=1):
            intensity = self.effect_intensities[effect_key].get()
            result = effect_fn(result, intensity=intensity)
            if progress_cb:
                progress_cb(i, total, self.MODULE_NAMES[effect_key])

        # Restore full resolution after a preview pass
        if use_low_res and image.shape[0] > 800:
            result = cv2.resize(result, (image.shape[1], image.shape[0]))

        return result

    def apply_effects(self):
        """Engage every armed module at full resolution, with per-module progress."""
        if self.current_image is None:
            messagebox.showwarning("No Specimen", "Acquire a specimen before engaging the modules.")
            return
        if self.busy:
            self.status_var.set("Engine busy — wait for the current task to finish")
            return
        if not any(v.get() for v in self.enabled_effects.values()):
            messagebox.showwarning("No Modules Armed", "Arm at least one anomaly module first.")
            return

        self.task_begin("Engaging modules…")
        source = self.current_image

        def on_module_done(done, total, name):
            percent = done / total * 100
            self.ui(self.task_progress, percent,
                    f"Module {done}/{total} complete: {name}")

        def apply_thread():
            try:
                processed = self.apply_effects_to_image(source, progress_cb=on_module_done)

                def done():
                    self.processed_image = processed
                    self.display_image(processed)
                    self.task_end("Process complete. The frame is different now. Better. Probably better.")
                self.ui(done)
            except Exception as e:
                self.ui(self.task_failed, "Module Failure",
                        f"An anomaly module misfired: {e}",
                        "Module failure — chain aborted")

        threading.Thread(target=apply_thread, daemon=True).start()

    def save_image(self):
        """Seal the processed specimen, then reveal it in the file browser."""
        if self.processed_image is None:
            messagebox.showwarning("Nothing to Seal", "There is no processed specimen to archive.")
            return
        if self.busy:
            self.status_var.set("Engine busy — wait for the current task to finish")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg"),
                ("HEIF", "*.heif"),
                ("All Files", "*.*")
            ]
        )

        if not file_path:
            return

        self.task_begin("Sealing specimen…")
        image_to_save = self.processed_image

        def save_thread():
            try:
                pil_image = Image.fromarray(np.clip(image_to_save, 0, 255).astype(np.uint8))
                pil_image.save(file_path, quality=95)

                def done():
                    self.task_end(f"Specimen sealed: {Path(file_path).name} — archive integrity 100%")
                    self.reveal_in_file_browser(file_path)
                self.ui(done)
            except Exception as e:
                self.ui(self.task_failed, "Seal Failure",
                        f"The archive rejected the specimen: {e}",
                        "Seal failure — specimen still loose")

        threading.Thread(target=save_thread, daemon=True).start()


def main():
    """Power up the deck."""
    root = tk.Tk()
    app = NecrovisionDeck(root)
    root.mainloop()


if __name__ == "__main__":
    main()
