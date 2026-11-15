# ============================================================
#
#                           /\
#                          /  \
#                         / /\ \
#                        / /  \ \
#                       / /_[]_\ \
#                      /___|  |___\
#                   __/    |WA|    \__
#                 _/  \____|__|____/  \_
#               _/____/    |  |    \____\_
#              /_____/\____|__|____/\_____\
#             /_____/  \   |  |   /  \_____\
#                /_/    \__|  |__/    \_\
#                 |     /__|  |__\     |
#                 |_____|  |  |  |_____|
#                       |__|  |__|
#                       /  |  |  \
#                      /___|__|___\
#                       |#|    |#|
#                       |#|    |#|
#                       \_/    \_/
#                      /\/\    /\/\
#
#                   WAYWARD ATLAS STUDIO
#                       (c) 2026
#                     ONE STEP OF MANY
#
# ============================================================

# WAYWARD ATLAS CUSTOM:
# Cat contribution #001
# 0

"""Graphical interface for the Wayward Atlas Studio Mumble Generator."""

# WAYWARD ATLAS CUSTOM:


import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

import os
import platform
import threading
import queue
import subprocess
import sys
from pathlib import Path
import shutil
import webbrowser
import json

# WAYWARD ATLAS CUSTOM:
# Shared project directory for source and standalone execution.
if getattr(sys, "frozen", False):
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

# WAYWARD ATLAS CUSTOM:
# Import Windows audio support only on Windows.
if platform.system() == "Windows":
    import winsound
else:
    winsound = None


# WAYWARD ATLAS CUSTOM:
# Central application version information.
APP_NAME = "Wayward Atlas Mumble Generator"
APP_VERSION = "1.0.0"
STUDIO_NAME = "Wayward Atlas Studio"


# WAYWARD ATLAS CUSTOM:
# Project links can be customized by developers.
# Leave a URL empty until the destination is available.
PROJECT_LINKS = {
    "github": "https://github.com/WaywardAtlasStudio/WaywardAtlas-MumbleGenerator",
    "donate": "https://www.paypal.com/biz/profile/waywardatlasstudio",
}

# WAYWARD ATLAS CUSTOM:
# Application appearance preferences.
APPEARANCE_OPTIONS = (
    "System Default",
    "Light",
    "Dark",
)

# WAYWARD ATLAS CUSTOM:
# Store application preferences outside the project folder.
SETTINGS_PATH = (
    Path.home()
    / ".wayward_atlas_mumble_generator"
    / "settings.json"
)

# Define custom colors for light and dark appearances.
APPEARANCE_COLORS = {
    "Light": {
        "background": "#F2F4F8",
        "surface": "#FFFFFF",
        "foreground": "#172033",
        "accent": "#1674D1",
    },
    "Dark": {
        "background": "#171B24",
        "surface": "#252B36",
        "foreground": "#F2F4F8",
        "accent": "#63B3FF",
    },
}

# WAYWARD ATLAS CUSTOM:
# Initial voice presets available in the GUI.
VOICE_PRESETS = (
    "neutral",
    "tiny_creature",
    "deep_voice",
    "robot",
)


# WAYWARD ATLAS CUSTOM:
# Match the voice preset multipliers in make_mumble_pack.py.
PRESET_SETTINGS = {
    "neutral": {"pitch": 1.0, "duration": 1.0, "volume": 1.0},
    "tiny_creature": {"pitch": 1.5, "duration": 0.75, "volume": 0.8},
    "deep_voice": {"pitch": 0.7, "duration": 1.25, "volume": 1.0},
    "robot": {"pitch": 0.9, "duration": 1.0, "volume": 0.9},
}


# WAYWARD ATLAS CUSTOM:
# Reusable rounded gradient button for the Mumble Generator.
class GradientButton(tk.Canvas):

    def __init__(
        self,
        parent,
        text,
        command,
        height=60,
        **kwargs
    ):
        super().__init__(
            parent,
            height=height,
            highlightthickness=0,
            takefocus=True,
            cursor="hand2",
            borderwidth=0,
            **kwargs
        )

        self.button_text = text
        self.button_command = command
        self.button_height = height

        self.enabled = True
        self.hovered = False
        self.pressed = False
        self.focused = False

        self.bind("<Configure>", self.redraw)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

        self.bind("<Return>", self.on_keyboard_activate)
        self.bind("<space>", self.on_keyboard_activate)

    def set_enabled(self, enabled):
        self.enabled = bool(enabled)
        self.configure(
            cursor="hand2" if self.enabled else "arrow"
        )
        self.redraw()

    def on_enter(self, _event):
        self.hovered = True
        self.redraw()

    def on_leave(self, _event):
        self.hovered = False
        self.pressed = False
        self.redraw()

    def on_press(self, _event):
        if self.enabled:
            self.focus_set()
            self.pressed = True
            self.redraw()

    def on_release(self, event):
        was_pressed = self.pressed
        self.pressed = False
        self.redraw()

        if (
            self.enabled
            and was_pressed
            and 0 <= event.x < self.winfo_width()
            and 0 <= event.y < self.winfo_height()
        ):
            self.button_command()

    def on_focus_in(self, _event):
        self.focused = True
        self.redraw()

    def on_focus_out(self, _event):
        self.focused = False
        self.pressed = False
        self.redraw()

    def on_keyboard_activate(self, _event):
        if self.enabled:
            self.button_command()
        return "break"

    def redraw(self, _event=None):
        import math
        import tkinter.font as tkfont

        # Match the canvas background to its parent frame.
        # This makes the rounded corners blend into the theme.
        frame_background = (
            ttk.Style(self).lookup("TFrame", "background")
            or self.master.winfo_toplevel().cget("background")
        )

        self.configure(background=frame_background)

        self.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()

        if width < 20 or height < 20:
            return

        radius = 16

        if not self.enabled:
            top_color = (86, 108, 137)
            bottom_color = (60, 76, 98)
        elif self.pressed:
            top_color = (5, 60, 132)
            bottom_color = (5, 92, 178)
        elif self.hovered:
            top_color = (38, 160, 255)
            bottom_color = (8, 105, 201)
        else:
            top_color = (15, 137, 239)
            bottom_color = (5, 83, 174)

        
        # WAYWARD ATLAS CUSTOM:
        # Draw the gradient inside a padded rounded rectangle.
        margin = 4
        left = margin
        right = width - margin - 1
        top = margin
        bottom = height - margin - 1

        radius = min(16, (bottom - top) // 2)

        for y in range(top, bottom + 1):
            ratio = (y - top) / max(1, bottom - top)

            rgb = tuple(
                round(
                    top_color[i] * (1 - ratio)
                    + bottom_color[i] * ratio
                )
                for i in range(3)
            )

            color = "#{:02x}{:02x}{:02x}".format(*rgb)

            local_y = y - top
            inset = 0

            if local_y < radius:
                distance = radius - local_y - 0.5
                inset = radius - math.sqrt(
                    max(0, radius ** 2 - distance ** 2)
                )

            elif y > bottom - radius:
                distance = y - (bottom - radius) - 0.5
                inset = radius - math.sqrt(
                    max(0, radius ** 2 - distance ** 2)
                )

            self.create_line(
                left + inset,
                y,
                right - inset,
                y,
                fill=color
            )

        text_color = "#FFFFFF" if self.enabled else "#D7E0EC"

        font = tkfont.Font(
            family="Segoe UI",
            size=13,
            weight="bold"
        )

        center_x = width / 2
        center_y = height / 2
        text_width = font.measure(self.button_text)

        # Center waveform and text as one group.
        icon_width = 32
        gap = 14
        group_width = icon_width + gap + text_width
        group_start = center_x - group_width / 2

        bars = (8, 15, 25, 15, 8)

        for index, bar_height in enumerate(bars):
            x = group_start + index * 7

            self.create_line(
                x,
                center_y - bar_height / 2,
                x,
                center_y + bar_height / 2,
                fill=text_color,
                width=3,
                capstyle="round"
            )

        self.create_text(
            group_start + icon_width + gap,
            center_y,
            text=self.button_text,
            font=font,
            fill=text_color,
            anchor="w"
        )
        
        # WAYWARD ATLAS CUSTOM:
        # Show keyboard focus without square corner outlines.
        if self.focused:
            self.create_line(
                22,
                height - 10,
                width - 22,
                height - 10,
                fill="#FFFFFF",
                dash=(4, 3),
                width=1
            )



def main():
    root = tk.Tk()

    root.title(f"{APP_NAME} - v{APP_VERSION}")

    # WAYWARD ATLAS CUSTOM:
    # Apply the studio's custom application icon.
    icon_path = (
        PROJECT_ROOT
        / "assets"
        / "icons"
        / "app_icon_small.png"
    )


    if icon_path.is_file():
        app_icon = tk.PhotoImage(file=str(icon_path))
        root.iconphoto(True, app_icon)
    else:
        print(f"Application icon not found: {icon_path}")

    root.geometry("550x710")
    root.minsize(450, 400)

    # Create a scrollable application area.
    scroll_container = ttk.Frame(root)
    scroll_container.pack(fill="both", expand=True)

    canvas = tk.Canvas(
        scroll_container,
        highlightthickness=0,
        borderwidth=0
    )
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(
        scroll_container,
        orient="vertical",
        command=canvas.yview
    )
    scrollbar.pack(side="right", fill="y")

    canvas.configure(
        yscrollcommand=scrollbar.set
    )

    # WAYWARD ATLAS CUSTOM:
    # Keep all existing GUI controls inside this frame.
    main_frame = ttk.Frame(canvas, padding=24)

    canvas_window = canvas.create_window(
        (0, 0),
        window=main_frame,
        anchor="nw"
    )


    # WAYWARD ATLAS CUSTOM:
    # Update scroll limits whenever content changes size.
    def update_scroll_region(_event=None):
        canvas.configure(
            scrollregion=canvas.bbox("all")
        )

    main_frame.bind(
        "<Configure>",
        update_scroll_region
    )


    # WAYWARD ATLAS CUSTOM:
    # Keep the content width aligned with the window.
    def resize_content(event):
        canvas.itemconfigure(
            canvas_window,
            width=event.width
        )

    canvas.bind(
        "<Configure>",
        resize_content
    )


    # WAYWARD ATLAS CUSTOM:
    # Scroll the interface using the mouse wheel.
    def on_mousewheel(event):
        # Ignore scrolling inside secondary windows.
        if event.widget.winfo_toplevel() is not root:
            return

        # Only scroll when content exceeds the visible area.

        scroll_region = canvas.bbox("all")

        if scroll_region is None:
            return

        content_height = scroll_region[3] - scroll_region[1]

        if content_height <= canvas.winfo_height():
            return

        # WAYWARD ATLAS CUSTOM:
        # Support mouse-wheel events with different delta sizes.
        if event.delta > 0:
            canvas.yview_scroll(-1, "units")

        elif event.delta < 0:
            canvas.yview_scroll(1, "units")


    # WAYWARD ATLAS CUSTOM:
    # Windows mouse-wheel support.
    canvas.bind_all(
        "<MouseWheel>",
        on_mousewheel
    )


    # WAYWARD ATLAS CUSTOM:
    # Linux/X11 mouse-wheel support.
    def on_linux_mousewheel(event):
        # Ignore scrolling inside secondary windows.
        if event.widget.winfo_toplevel() is not root:
            return

        scroll_region = canvas.bbox("all")


        if scroll_region is None:
            return

        content_height = scroll_region[3] - scroll_region[1]

        if content_height <= canvas.winfo_height():
            return

        if event.num == 4:
            canvas.yview_scroll(-1, "units")

        elif event.num == 5:
            canvas.yview_scroll(1, "units")

    if platform.system() == "Linux":
        canvas.bind_all("<Button-4>", on_linux_mousewheel)
        canvas.bind_all("<Button-5>", on_linux_mousewheel)

    # WAYWARD ATLAS CUSTOM:
    # Compact appearance selector above the application branding.
    # Load the previously selected appearance.
    def load_appearance_preference():
        try:
            settings = json.loads(
                SETTINGS_PATH.read_text(encoding="utf-8")
            )

            saved_appearance = settings.get(
                "appearance",
                "System Default"
            )

            if saved_appearance in APPEARANCE_OPTIONS:
                return saved_appearance

        except (OSError, ValueError, TypeError, AttributeError):
            pass

        return "System Default"

    appearance_var = tk.StringVar(
        value=load_appearance_preference()
    )

    appearance_frame = ttk.Frame(main_frame)
    appearance_frame.pack(
        fill="x",
        pady=(0, 12)
    )

    ttk.Label(
        appearance_frame,
        text="Theme:"
    ).pack(
        side="left",
        padx=(0, 6)
    )

    appearance_dropdown = ttk.Combobox(
        appearance_frame,
        textvariable=appearance_var,
        values=APPEARANCE_OPTIONS,
        state="readonly",
        width=15
    )
    appearance_dropdown.pack(
        side="left"
    )


    # WAYWARD ATLAS CUSTOM:
    # Preserve the operating system's original Tkinter appearance.
    app_style = ttk.Style(root)

    system_theme = app_style.theme_use()
    system_background = root.cget("background")
    system_canvas_background = canvas.cget("background")

    # WAYWARD ATLAS CUSTOM:
    # Apply the selected appearance without restarting the GUI.
    def apply_appearance(_event=None):
        selected = appearance_var.get()

        if selected == "System Default":
            # Restore the original operating system theme.
            app_style.theme_use(system_theme)
            root.configure(background=system_background)
            canvas.configure(
                background=system_canvas_background
            )
            return

        colors = APPEARANCE_COLORS.get(selected)

        if colors is None:
            return

        background = colors["background"]
        surface = colors["surface"]
        foreground = colors["foreground"]
        accent = colors["accent"]

        # Use a theme that allows custom widget colors.
        app_style.theme_use("clam")

        # Main application widgets.
        app_style.configure(
            "TFrame",
            background=background
        )
        app_style.configure(
            "TLabel",
            background=background,
            foreground=foreground
        )
        app_style.configure(
            "TLabelframe",
            background=background,
            foreground=foreground
        )
        app_style.configure(
            "TLabelframe.Label",
            background=background,
            foreground=foreground
        )

        # Buttons.
        app_style.configure(
            "TButton",
            background=surface,
            foreground=foreground,
            padding=6
        )
        app_style.map(
            "TButton",
            background=[
                ("active", accent),
                ("pressed", accent)
            ]
        )

        # Text entry fields.
        app_style.configure(
            "TEntry",
            fieldbackground=surface,
            foreground=foreground
        )

        # Dropdown menus.
        app_style.configure(
            "TCombobox",
            fieldbackground=surface,
            background=surface,
            foreground=foreground,
            arrowcolor=foreground
        )
        app_style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", surface)
            ],
            foreground=[
                ("readonly", foreground)
            ]
        )

        # Scrollbars and sliders.
        app_style.configure(
            "TScrollbar",
            background=surface,
            troughcolor=background
        )
        app_style.configure(
            "TScale",
            background=background,
            troughcolor=surface
        )

        # Non-ttk widgets need their colors set directly.
        root.configure(background=background)
        canvas.configure(background=background)

   
    # WAYWARD ATLAS CUSTOM:
    # Save the chosen appearance after applying it.
    def on_appearance_changed(_event=None):
        apply_appearance()
        generate_button.redraw()
        
        try:
            SETTINGS_PATH.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            SETTINGS_PATH.write_text(
                json.dumps(
                    {"appearance": appearance_var.get()},
                    indent=4
                ),
                encoding="utf-8"
            )

        except OSError as error:
            print(f"Unable to save appearance: {error}")

    appearance_dropdown.bind(
        "<<ComboboxSelected>>",
        on_appearance_changed
    )

    # Apply the stored appearance when the GUI starts.
    apply_appearance()
    
    # WAYWARD ATLAS CUSTOM:
    # Display the high-quality studio application logo.
    large_logo_path = (
        PROJECT_ROOT
        / "assets"
        / "icons"
        / "app_logo_128_rounded.png"
    )

    if large_logo_path.is_file():
        large_logo_image = tk.PhotoImage(
            file=str(large_logo_path)
        )

        logo_label = ttk.Label(
            main_frame,
            image=large_logo_image
        )

        # Keep the image reference alive.
        logo_label.image = large_logo_image

        logo_label.pack(pady=(0, 12))


    title = ttk.Label(
        main_frame,
        text="Wayward Atlas Mumble Generator",
        font=("Segoe UI", 18, "bold")
    )
    title.pack(pady=(0, 12))

    subtitle = ttk.Label(
        main_frame,
        text="Create original character mumble voices."
    )
    subtitle.pack(pady=(0, 24))


    # WAYWARD ATLAS CUSTOM:
    # Store the selected voice preset.
    preset_var = tk.StringVar(value="neutral")

    ttk.Label(
        main_frame,
        text="Voice Preset:"
    ).pack(anchor="w")

    preset_dropdown = ttk.Combobox(
        main_frame,
        textvariable=preset_var,
        values=VOICE_PRESETS,
        state="readonly"
    )
    preset_dropdown.pack(fill="x", pady=(4, 16))

    # WAYWARD ATLAS CUSTOM:
    # Allow users to name their custom voice variant.
    variant_var = tk.StringVar()

    ttk.Label(
        main_frame,
        text="Custom Variant Name (Optional):"
    ).pack(anchor="w")

    variant_entry = ttk.Entry(
        main_frame,
        textvariable=variant_var
    )
    variant_entry.pack(fill="x", pady=(4, 16))

    # WAYWARD ATLAS CUSTOM:
    # Display the current voice selection.
    selection_label = ttk.Label(main_frame)
    selection_label.pack(pady=(8, 16))

    # WAYWARD ATLAS CUSTOM:
    # Validate variant names and preview the output identity.
    def update_selection(*_args):
        variant = variant_var.get().strip().lower()
        output_name = preset_var.get()

        valid_variant = (
            not variant
            or (
                variant.isascii()
                and all(
                    char.islower()
                    or char.isdigit()
                    or char == "_"
                    for char in variant
                )
            )
        )

        if not valid_variant:
            selection_label.config(
                text="Invalid variant: use a-z, 0-9, or underscores.",
                foreground="red"
            )
            return

        if variant:
            output_name += f"_{variant}"

        selection_label.config(
            text=f"Selected Voice: {output_name}",
            foreground="green"
        )


    # WAYWARD ATLAS CUSTOM:
    # Update the display whenever either input changes.
    preset_var.trace_add("write", update_selection)
    variant_var.trace_add("write", update_selection)

    update_selection()

    # Voice adjustment controls.
    pitch_var = tk.DoubleVar(value=1.0)
    duration_var = tk.DoubleVar(value=1.0)
    volume_var = tk.DoubleVar(value=1.0)

    settings_frame = ttk.LabelFrame(
        main_frame,
        text="Voice Adjustments",
        padding=12
    )
    settings_frame.pack(fill="x", pady=(0, 12))

    # WAYWARD ATLAS CUSTOM:
    # Track sliders so their ranges can follow preset limits.
    slider_controls = {}

    def add_slider(label, variable, minimum, maximum):
        row = ttk.Frame(settings_frame)
        row.pack(fill="x", pady=5)

        ttk.Label(
            row,
            text=label,
            width=10
        ).pack(side="left")

        value_label = ttk.Label(row, width=7)
        value_label.pack(side="right")

        def update_value(*_args):
            value_label.config(
                text=f"{variable.get():.2f}x"
            )
            update_effective_settings()

        slider = ttk.Scale(
            row,
            from_=minimum,
            to=maximum,
            variable=variable,
            command=lambda _value: update_value()
        )
        slider.pack(
            side="left",
            fill="x",
            expand=True,
            padx=8
        )

        slider_controls[label.lower()] = slider

        variable.trace_add("write", update_value)
        update_value()


    effective_label = ttk.Label(settings_frame)
    effective_label.pack(side="bottom", pady=(12, 0))

    def update_effective_settings(*_args):

        # WAYWARD ATLAS CUSTOM:
        # Sliders now represent the actual effective voice values.
        pitch = pitch_var.get()
        duration = duration_var.get()
        volume = volume_var.get()

        effective_label.config(
            text=(
                f"Effective: Pitch {pitch:.2f}x  |  "
                f"Duration {duration:.2f}x  |  "
                f"Volume {volume:.2f}x"
            )
        )


    # WAYWARD ATLAS CUSTOM:
    # Apply each preset's effective adjustment limits.
    def load_preset_settings(*_args):
        preset = PRESET_SETTINGS[preset_var.get()]

        for setting in ("pitch", "duration", "volume"):
            base_value = preset[setting]
            slider = slider_controls[setting]

            minimum = 0.0 if setting == "volume" else 0.5
            maximum = 1.0 if setting == "volume" else 2.0

            slider.configure(
                from_=base_value * minimum,
                to=base_value * maximum
            )

        pitch_var.set(preset["pitch"])
        duration_var.set(preset["duration"])
        volume_var.set(preset["volume"])

        update_effective_settings()



    add_slider("Pitch", pitch_var, 0.5, 2.0)
    add_slider("Duration", duration_var, 0.5, 2.0)
    add_slider("Volume", volume_var, 0.0, 1.0)

    # WAYWARD ATLAS CUSTOM:
    # Update all sliders when the voice preset changes.
    preset_var.trace_add("write", load_preset_settings)

    # WAYWARD ATLAS CUSTOM:
    # Load the initial preset values.
    load_preset_settings()

    # WAYWARD ATLAS CUSTOM:
    # Restore the selected preset's original voice settings.
    reset_button = ttk.Button(
        settings_frame,
        text="Reset to Preset Defaults",
        command=load_preset_settings
    )
    reset_button.pack(
        side="bottom",
        fill="x",
        pady=(12, 0)
    )


    # WAYWARD ATLAS CUSTOM:
    # Track whether the preview matches the current settings.
    last_generated_settings = [None]

    preview_status = ttk.Label(
        main_frame,
        text="Preview not verified. Generate a voice pack.",
        foreground="blue"
    )
    preview_status.pack(pady=(0, 12))


    # WAYWARD ATLAS CUSTOM:
    # Discover previously generated voice packs.
    def discover_saved_voices():
        output_root = PROJECT_ROOT / "output"

        if not output_root.is_dir():
            return []

        saved_voices = []

        for folder in output_root.iterdir():
            if not folder.is_dir():
                continue

            output_name = folder.name

            # Only include folders containing a usable preview.
            preview_path = (
                folder
                / f"{output_name}_speech_preview.wav"
            )

            if not preview_path.is_file():
                continue

            # Reuse our existing README settings reader.
            settings = read_saved_voice_settings(output_name)

            if settings is None:
                continue

            saved_voices.append(output_name)

        return sorted(saved_voices)


    # WAYWARD ATLAS CUSTOM:
    # Read saved voice settings from an existing voice pack.
    def read_saved_voice_settings(output_name):
        readme_path = (
            PROJECT_ROOT
            / "output"
            / output_name
            / "README.txt"
        )

        if not readme_path.is_file():
            return None

        try:
            content = readme_path.read_text(
                encoding="utf-8"
            )

            saved = {}

            for line in content.splitlines():
                if ":" not in line:
                    continue

                key, value = line.split(":", 1)
                saved[key.strip()] = value.strip()

            
            preset = saved["Voice Preset"]
            variant = saved.get("Voice Variant", "")

            # Base presets store "Default" in the README.
            # Convert that label to an empty variant name.
            if variant == "Default":
                variant = ""

            output = saved["Output Name"]


            pitch = float(
                saved["Effective Pitch"].removesuffix("x")
            )
            duration = float(
                saved["Effective Duration"].removesuffix("x")
            )
            volume = float(
                saved["Effective Volume"].removesuffix("x")
            )

            expected_name = (
                f"{preset}_{variant}" if variant else preset
            )

            if output != output_name or expected_name != output_name:
                return None

            if preset not in VOICE_PRESETS:
                return None

            return (
                preset,
                variant,
                round(pitch, 6),
                round(duration, 6),
                round(volume, 6)
            )

        except (OSError, KeyError, ValueError, UnicodeError):
            return None


    def current_voice_settings():
        return (
            preset_var.get(),
            variant_var.get().strip().lower(),
            round(pitch_var.get(), 6),
            round(duration_var.get(), 6),
            round(volume_var.get(), 6)
        )


    # WAYWARD ATLAS CUSTOM:
    # Verify previews using current-session settings or
    # settings saved in an existing voice pack's README.
    def update_preview_status(*_args):
        current = current_voice_settings()

        preset_name = current[0]
        variant_name = current[1]

        output_name = (
            f"{preset_name}_{variant_name}"
            if variant_name
            else preset_name
        )
        
        preview_path = (
            PROJECT_ROOT
            / "output"
            / output_name
            / f"{output_name}_speech_preview.wav"
        )

        if not preview_path.is_file():
            preview_status.config(
                text="No preview found. Generate this voice first.",
                foreground="blue"
            )
            return

        saved = read_saved_voice_settings(output_name)

        # Exact match from the current application session.
        session_matches = (
            last_generated_settings[0] == current
        )

        # The current README format saves two decimal places.
        saved_matches = (
            saved is not None
            and saved[:2] == current[:2]
            and all(
                round(a, 2) == round(b, 2)
                for a, b in zip(saved[2:], current[2:])
            )
        )

        if session_matches or saved_matches:
            preview_status.config(
                text="Preview matches current settings.",
                foreground="green"
            )
        else:
            preview_status.config(
                text="Preview unverified or settings changed!",
                foreground="red"
            )


    # WAYWARD ATLAS CUSTOM:
    # Watch for changes to the voice configuration.
    for variable in (
        preset_var,
        variant_var,
        pitch_var,
        duration_var,
        volume_var
    ):
        variable.trace_add("write", update_preview_status)

    # WAYWARD ATLAS CUSTOM:
    # Verify the selected voice when the GUI first opens.
    update_preview_status()


    # WAYWARD ATLAS CUSTOM:
    # Display previously generated voice packs.
    saved_voices_frame = ttk.LabelFrame(
        main_frame,
        text="Saved Voices",
        padding=12
    )
    saved_voices_frame.pack(fill="x", pady=(0, 12))

    saved_voice_var = tk.StringVar()

    # Prevent automatic changes during voice loading
    # from clearing the Saved Voices selection.
    loading_saved_voice = [False]

    saved_voice_dropdown = ttk.Combobox(
        saved_voices_frame,
        textvariable=saved_voice_var,
        state="readonly"
    )
    saved_voice_dropdown.pack(
        fill="x",
        pady=(0, 8)
    )

    # WAYWARD ATLAS CUSTOM:
    # Refresh the list of previously generated voices.
    def refresh_saved_voices():
        
        voices = discover_saved_voices()

        saved_voice_dropdown.configure(values=voices)

        if saved_voice_var.get() not in voices:
            saved_voice_var.set("")

        if voices:
            print(f"Found {len(voices)} saved voice(s).")
        else:
            print("No saved voices found.")

    refresh_button = ttk.Button(
        saved_voices_frame,
        text="Refresh Saved Voices",
        command=refresh_saved_voices
    )
    refresh_button.pack(fill="x")


    # WAYWARD ATLAS CUSTOM:
    # Restore saved voice settings without clearing the
    # Saved Voices selection during automatic updates.
    def load_saved_voice(_event=None):
        output_name = saved_voice_var.get()

        if not output_name:
            return

        settings = read_saved_voice_settings(output_name)

        if settings is None:
            messagebox.showwarning(
                "Saved Voice Unavailable",
                "The saved voice settings could not be read.",
                parent=root
            )
            return

        preset, variant, pitch, duration, volume = settings

        loading_saved_voice[0] = True

        try:
            # Changing the preset also updates slider ranges.
            preset_var.set(preset)
            variant_var.set(variant)

            # Restore saved effective values.
            pitch_var.set(pitch)
            duration_var.set(duration)
            volume_var.set(volume)

        finally:
            loading_saved_voice[0] = False

        update_effective_settings()
        update_preview_status()

    # WAYWARD ATLAS CUSTOM:
    # Load a saved voice when selected from the dropdown.
    saved_voice_dropdown.bind(
        "<<ComboboxSelected>>",
        load_saved_voice
    )


    # WAYWARD ATLAS CUSTOM:
    # Clear the library selection when settings are edited.
    def clear_saved_voice_selection(*_args):
        if loading_saved_voice[0]:
            return

        if saved_voice_var.get():
            saved_voice_var.set("")

    for variable in (
        preset_var,
        variant_var,
        pitch_var,
        duration_var,
        volume_var
    ):
        variable.trace_add(
            "write",
            clear_saved_voice_selection
        )


    # WAYWARD ATLAS CUSTOM:
    # Start a new voice without modifying saved voice packs.
    def create_new_voice():
        # Clear the selected saved voice.
        saved_voice_var.set("")

        # Start with the neutral preset.
        preset_var.set("neutral")

        # Remove the previous custom variant name.
        variant_var.set("")

        # Restore the default voice adjustments.
        load_preset_settings()

        # Refresh the voice information.
        update_selection()
        update_preview_status()

    # WAYWARD ATLAS CUSTOM:
    # Provide an easy way to begin creating a new voice.
    new_voice_button = ttk.Button(
        saved_voices_frame,
        text="New Voice / Clear Selection",
        command=create_new_voice
    )

    new_voice_button.pack(
        fill="x",
        pady=(8, 0)
    )


    refresh_saved_voices()


    # WAYWARD ATLAS CUSTOM:
    # Prepare the settings for the audio generator.
    # This checkpoint previews the command without running it.
    def prepare_generation():
        preset_name = preset_var.get()
        variant_name = variant_var.get().strip().lower()
        preset = PRESET_SETTINGS[preset_name]

        # Capture the exact settings used for this generation.
        generation_settings = current_voice_settings()


        # Validate the variant name before generating.
        if variant_name and (
            not variant_name.isascii()
            or not all(
                char.islower() or char.isdigit() or char == "_"
                for char in variant_name
            )
        ):
            status.config(
                text="Invalid variant name. Please correct it.",
                foreground="red"
            )
            return

        # WAYWARD ATLAS CUSTOM:
        # Convert effective GUI values into CLI multipliers.
        pitch_multiplier = pitch_var.get() / preset["pitch"]
        duration_multiplier = duration_var.get() / preset["duration"]
        volume_multiplier = volume_var.get() / preset["volume"]

        # Respect the existing generator's accepted ranges.
        if not (
            0.5 <= pitch_multiplier <= 2.0
            and 0.5 <= duration_multiplier <= 2.0
            and 0.0 <= volume_multiplier <= 1.0
        ):
            status.config(
                text="Settings exceed the generator's current limits.",
                foreground="red"
            )
            return

        command = [
            "--preset", preset_name,
            "--pitch", str(pitch_multiplier),
            "--duration", str(duration_multiplier),
            "--volume", str(volume_multiplier),
        ]

        if variant_name:
            command.extend(["--variant", variant_name])

        # Protect existing voice packs from accidental overwrites.
        output_name = (
            f"{preset_name}_{variant_name}"
            if variant_name
            else preset_name
        )
        
        # WAYWARD ATLAS CUSTOM:
        # Use the shared project directory for generated audio.
        output_root = PROJECT_ROOT / "output"

        voice_folder = output_root / output_name

        voice_zip = (
            output_root
            / f"WaywardAtlas_Mumble_{output_name}.zip"
        )

        # WAYWARD ATLAS CUSTOM:
        # Check for either an existing voice folder or ZIP.
        if voice_folder.exists() or voice_zip.exists():
            overwrite = messagebox.askyesno(
                "Existing Voice Pack",
                f"A voice pack named '{output_name}' "
                "already exists.\n\n"
                "Generating again may overwrite its "
                "existing audio and ZIP files.\n\n"
                "Do you want to continue?",
                icon="warning",
                parent=root
            )

            if not overwrite:
                status.config(
                    text="Generation cancelled. Existing files preserved.",
                    foreground="blue"
                )
                return


        # WAYWARD ATLAS CUSTOM:
        # Generate audio without freezing the GUI.
        generator_script = (
            Path(__file__).resolve().parent / "make_mumble_pack.py"
        )

        
        # WAYWARD ATLAS CUSTOM:
        # Support source execution and future standalone builds.
        if getattr(sys, "frozen", False):
            # In a packaged build, launch the companion
            # audio-generation executable.
            engine_name = (
                "WaywardAtlas_MumbleEngine.exe"
                if platform.system() == "Windows"
                else "WaywardAtlas_MumbleEngine"
            )

            engine_path = (
                Path(sys.executable).resolve().parent
                / engine_name
            )

            generator_command = [
                str(engine_path),
                *command
            ]

        else:
            # In source mode, use the active Python interpreter.
            generator_command = [
                sys.executable,
                str(generator_script),
                *command
            ]


        result_queue = queue.Queue()

        status.config(
            text="Generating voice pack...",
            foreground="blue"
        )

        generate_button.set_enabled(False)

        def run_generator():
            # Worker thread: never update Tkinter widgets here.
            try:
                
                # WAYWARD ATLAS CUSTOM:
                # Hide the engine console window on Windows.
                # Continue capturing output and error messages.
                startup_flags = (
                    subprocess.CREATE_NO_WINDOW
                    if platform.system() == "Windows"
                    else 0
                )

                result = subprocess.run(
                    generator_command,
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=startup_flags
                )

                result_queue.put(("success", result.stdout))

            except subprocess.CalledProcessError as error:
                result_queue.put(("error", error.stderr))

            except Exception as error:
                result_queue.put(("error", str(error)))

        def check_generation():
            try:
                result_type, message = result_queue.get_nowait()

            except queue.Empty:
                root.after(100, check_generation)
                return

            generate_button.set_enabled(True)
            
            if result_type == "success":
                print(message)

                # Remember the settings used for this generation.
                last_generated_settings[0] = generation_settings
                update_preview_status()

                # Refresh the saved voice library after generation.
                refresh_saved_voices()

                status.config(
                    text="Voice pack generated successfully!",
                    foreground="green"
                )
            
            else:
                # Display generation errors inside the GUI.
                print("Generator error:", message)

                status.config(
                    text="Voice pack generation failed.",
                    foreground="red"
                )

                error_details = (
                    message.strip()
                    if message and message.strip()
                    else "The generator did not provide error details."
                )

                messagebox.showerror(
                    "Mumble Generator - Error",
                    "Unable to generate the voice pack.\n\n"
                    f"Details:\n{error_details}",
                    parent=root
                )


        worker = threading.Thread(
            target=run_generator,
            daemon=True
        )

        worker.start()
        root.after(100, check_generation)

    
    # WAYWARD ATLAS CUSTOM:
    # Rounded gradient Generate Voice Pack button.
    generate_button = GradientButton(
        main_frame,
        text="Generate Voice Pack",
        command=prepare_generation,
        height=64
    )

    generate_button.pack(
        fill="x",
        pady=(8, 12)
    )


    # WAYWARD ATLAS CUSTOM:
    # Open the output folder on Windows, Linux, and macOS.
    def open_output_folder():
        output_folder = PROJECT_ROOT / "output"

        output_folder.mkdir(parents=True, exist_ok=True)

        try:
            operating_system = platform.system()

            if operating_system == "Windows":
                os.startfile(str(output_folder))

            elif operating_system == "Darwin":
                subprocess.Popen(
                    ["open", str(output_folder)]
                )

            elif operating_system == "Linux":
                subprocess.Popen(
                    ["xdg-open", str(output_folder)]
                )

            else:
                raise OSError(
                    f"Unsupported operating system: {operating_system}"
                )

        except (OSError, FileNotFoundError) as error:
            print(f"Unable to open output folder: {error}")

            status.config(
                text="Could not open the output folder.",
                foreground="red"
            )


    open_folder_button = ttk.Button(
        main_frame,
        text="Open Output Folder",
        command=open_output_folder
    )
    open_folder_button.pack(fill="x", pady=(0, 12))


    # WAYWARD ATLAS CUSTOM:
    # Cross-platform audio playback engine.
    # Linux and macOS use an external audio player.
    # Windows continues using its built-in winsound library.
    preview_process = None

    def start_audio_playback(preview_path):
        nonlocal preview_process

        operating_system = platform.system()

        if operating_system == "Windows":
            winsound.PlaySound(
                str(preview_path),
                winsound.SND_FILENAME | winsound.SND_ASYNC
            )
            return

        # Stop any previous external playback process.
        if preview_process is not None:
            if preview_process.poll() is None:
                preview_process.terminate()

            preview_process = None

        if operating_system == "Darwin":
            player = shutil.which("afplay")

        elif operating_system == "Linux":
            player = (
                shutil.which("pw-play")
                or shutil.which("paplay")
                or shutil.which("aplay")
            )

        else:
            raise RuntimeError(
                f"Unsupported operating system: {operating_system}"
            )

        if player is None:
            raise RuntimeError(
                "No supported audio playback application found."
            )

        preview_process = subprocess.Popen(
            [player, str(preview_path)]
        )

    def stop_audio_playback():
        nonlocal preview_process

        if platform.system() == "Windows":
            winsound.PlaySound(None, 0)
            return

        if preview_process is not None:
            if preview_process.poll() is None:
                preview_process.terminate()

            preview_process = None


    # WAYWARD ATLAS CUSTOM:
    # Play the selected voice pack's generated speech preview.
    def play_voice_preview():
        preset_name = preset_var.get()
        variant_name = variant_var.get().strip().lower()
        generation_settings = current_voice_settings()

        # Apply the same variant naming rules as the generator.
        if variant_name and (
            not variant_name.isascii()
            or not all(
                char.islower() or char.isdigit() or char == "_"
                for char in variant_name
            )
        ):
            status.config(
                text="Invalid variant name.",
                foreground="red"
            )
            return

        output_name = (
            f"{preset_name}_{variant_name}"
            if variant_name
            else preset_name
        )

        output_folder = (
            PROJECT_ROOT
            / "output"
            / output_name
        )

        preview_path = (
            output_folder
            / f"{output_name}_speech_preview.wav"
        )

        if not preview_path.is_file():
            status.config(
                text="No preview found. Generate this voice first.",
                foreground="red"
            )
            return

        # WAYWARD ATLAS CUSTOM:
        # Warn when the current settings are not verified
        # against the existing audio preview.
        if (
            current_voice_settings() != last_generated_settings[0]
            and not (
                (saved := read_saved_voice_settings(output_name)) is not None
                and saved[:2] == current_voice_settings()[:2]
                and all(
                    round(a, 2) == round(b, 2)
                    for a, b in zip(saved[2:], current_voice_settings()[2:])
                )
            )
        ):
            play_anyway = messagebox.askyesno(
                "Preview May Be Outdated",
                "This preview has not been verified against "
                "the current voice settings.\n\n"
                "It may contain previously generated audio.\n\n"
                "Play the existing preview anyway?",
                parent=root
            )

            if not play_anyway:
                return


        try:

            # WAYWARD ATLAS CUSTOM:
            # Play previews using the appropriate operating system.
            start_audio_playback(preview_path)

            status.config(
                text=f"Playing preview: {output_name}",
                foreground="green"
            )

        except (RuntimeError, OSError) as error:
            print(f"Audio playback error: {error}")

            status.config(
                text="Unable to play audio preview.",
                foreground="red"
            )


    # WAYWARD ATLAS CUSTOM:
    # Stop preview audio on all supported platforms.
    def stop_voice_preview():
        try:
            stop_audio_playback()

            status.config(
                text="Audio preview stopped.",
                foreground="blue"
            )

        except (RuntimeError, OSError) as error:
            print(f"Unable to stop audio: {error}")

            status.config(
                text="Unable to stop audio preview.",
                foreground="red"
            )


    preview_frame = ttk.Frame(main_frame)
    preview_frame.pack(fill="x", pady=(0, 12))

    play_button = ttk.Button(
        preview_frame,
        text="Play Preview",
        command=play_voice_preview
    )
    play_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 6)
    )

    stop_button = ttk.Button(
        preview_frame,
        text="Stop Preview",
        command=stop_voice_preview
    )
    stop_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(6, 0)
    )


    status = ttk.Label(
        main_frame,
        text="GUI initialized successfully.",
        foreground="green"
    )
    status.pack(pady=12)

    # WAYWARD ATLAS CUSTOM:
    # Display application version and studio branding.
    version_label = ttk.Label(
        main_frame,
        text=f"{APP_NAME} | v{APP_VERSION}",
        foreground="gray"
    )
    version_label.pack(pady=(12, 4))

    studio_label = ttk.Label(
        main_frame,
        text=f"Created by {STUDIO_NAME}",
        foreground="gray"
    )
    studio_label.pack(pady=(0, 12))

    
    # WAYWARD ATLAS CUSTOM:
    # Reusable viewer for bundled legal and attribution documents.
    def show_document(filename, document_title):
        document_path = PROJECT_ROOT / filename

        try:
            document_text = document_path.read_text(
                encoding="utf-8"
            )
        except (OSError, UnicodeError) as error:
            messagebox.showerror(
                "Document Error",
                f"Unable to open {document_title}:\n\n{error}",
                parent=root
            )
            return

        document_window = tk.Toplevel(root)
        document_window.title(
            f"{APP_NAME} - {document_title}"
        )
        document_window.geometry("700x550")
        document_window.minsize(400, 300)

        # WAYWARD ATLAS CUSTOM:
        # Match the document viewer to the selected appearance.
        selected_appearance = appearance_var.get()

        if selected_appearance in APPEARANCE_COLORS:
            document_colors = APPEARANCE_COLORS[
                selected_appearance
            ]

            document_background = document_colors["background"]
            document_surface = document_colors["surface"]
            document_foreground = document_colors["foreground"]
        else:
            # Use Tkinter's native colors for System Default.
            document_background = system_background
            document_surface = "white"
            document_foreground = "black"

        document_window.configure(
            background=document_background
        )

        document_display = scrolledtext.ScrolledText(
            document_window,
            wrap="word",
            padx=12,
            pady=12,
            background=document_surface,
            foreground=document_foreground,
            insertbackground=document_foreground,
            selectbackground="#3678B8" if selected_appearance == "Dark" else "#A9CEF4",
            selectforeground="#FFFFFF" if selected_appearance == "Dark" else "#172033"
        )

        document_display.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=12
        )

        document_display.insert("1.0", document_text)
        document_display.configure(state="disabled")

        ttk.Button(
            document_window,
            text="Close",
            command=document_window.destroy
        ).pack(pady=(0, 12))


    # WAYWARD ATLAS CUSTOM:
    # Open the Apache 2.0 software license.
    license_button = ttk.Button(
        main_frame,
        text="View Software License",
        command=lambda: show_document(
            "LICENSE",
            "Software License"
        )
    )
    license_button.pack(
        fill="x",
        pady=(0, 12)
    )

    # WAYWARD ATLAS CUSTOM:
    # Open generated audio usage permissions.
    audio_license_button = ttk.Button(
        main_frame,
        text="View Generated Audio Permissions",
        command=lambda: show_document(
            "GENERATED_AUDIO_LICENSE.txt",
            "Generated Audio Permissions"
        )
    )
    audio_license_button.pack(
        fill="x",
        pady=(0, 12)
    )

    # WAYWARD ATLAS CUSTOM:
    # Open the original project attribution notice.
    notice_button = ttk.Button(
        main_frame,
        text="View Original Project Attribution",
        command=lambda: show_document(
            "NOTICE",
            "Original Project Attribution"
        )
    )
    notice_button.pack(
        fill="x",
        pady=(0, 12)
    )


    # WAYWARD ATLAS CUSTOM:
    # Open configured project links in the default browser.
    def open_project_link(link_name):
        url = PROJECT_LINKS.get(link_name, "").strip()

        if not url:
            return

        if not url.startswith(("https://", "http://")):
            messagebox.showerror(
                "Invalid Project Link",
                "Project links must begin with https:// or http://",
                parent=root
            )
            return

        try:
            if not webbrowser.open(url, new=2):
                raise RuntimeError(
                    "The operating system could not open a browser."
                )
        except Exception as error:
            messagebox.showerror(
                "Unable to Open Link",
                f"Could not open the project link:\n\n{error}",
                parent=root
            )

    # WAYWARD ATLAS CUSTOM:
    # Keep project links together in the application footer.
    links_frame = ttk.Frame(main_frame)
    links_frame.pack(fill="x", pady=(0, 12))

    github_url = PROJECT_LINKS.get("github", "").strip()
    donate_url = PROJECT_LINKS.get("donate", "").strip()

    github_button = ttk.Button(
        links_frame,
        text="GitHub",
        command=lambda: open_project_link("github"),
        state="normal" if github_url else "disabled"
    )
    github_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 6)
    )

    donate_button = ttk.Button(
        links_frame,
        text="Donate",
        command=lambda: open_project_link("donate"),
        state="normal" if donate_url else "disabled"
    )
    donate_button.pack(
        side="left",
        fill="x",
        expand=True,
        padx=(6, 0)
    )


    # WAYWARD ATLAS CUSTOM:
    # Stop active audio playback when closing the GUI.
    def on_window_close():
        try:
            stop_audio_playback()
        except (OSError, RuntimeError) as error:
            print(f"Audio cleanup warning: {error}")
        finally:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_window_close)


    # Temporary saved-voice discovery test.
    print("Discovered saved voices:")

    for voice_name in discover_saved_voices():
        print(f"  - {voice_name}")



    root.mainloop()


if __name__ == "__main__":
    main()
