# ============================================================
#
#                                         /\
#                                        / /\
#                                       / /  \
#                                      /_/____\
#                                    _/____[]_/
#                                  _/___||||_/
#                     ____________/____||||/
#                    /__________________/ /
#                   /__   __   __   __ / /
#                  /__/__/  \_/  \_/  / /
#                 /__________________/ /
#                / []  []   WA   [] / /
#               /__________________/ /
#              /____   _________  / /
#              \____\_/________/ / /
#               \    \_________/ /
#                \_____________/
#                 |##|   |##|  \
#                 |##|   |##|   \
#                 |##|   |##|    \
#                 \__/   \__/    /
#                  \/     \/    /
#                 /\/\   /\/\  /
#
#                WAYWARD ATLAS STUDIO
#                    (c) 2026
#                  ONE STEP OF MANY
#
# ============================================================


"""Generate original, synthetic vowel-like mumble samples for a Godot prototype."""

# WAYWARD ATLAS CUSTOM:

from pathlib import Path
import argparse
import sys
import wave
import zipfile
import numpy as np
from scipy.signal import butter, sosfilt


# WAYWARD ATLAS CUSTOM:
# Locate the project folder in source mode,
# or the executable folder in standalone mode.
if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
else:
    ROOT = Path(__file__).resolve().parent.parent


# Store generated audio in the project's output folder.
# The output folder is configured after selecting a voice preset.
OUT = None

RATE = 44100
RNG = np.random.default_rng(20261107)

# Overall voice pitch multiplier.
# 1.0 = original pitch
# Below 1.0 = deeper voice
# Above 1.0 = higher voice
VOICE_PITCH_MULTIPLIER = 1.00

# Overall mumble duration multiplier.
# 1.0 = original duration
# Below 1.0 = shorter sounds
# Above 1.0 = longer sounds
VOICE_DURATION_MULTIPLIER = 1.00

# Overall generated audio volume.
# 1.0 = original volume
# 0.5 = half the original amplitude
# 0.0 = silence
VOICE_VOLUME_MULTIPLIER = 1.00

# Available voice presets.
VOICE_PRESETS = {
    "neutral": {
        "pitch": 1.0,
        "duration": 1.0,
        "volume": 1.0
    },

    "tiny_creature": {
        "pitch": 1.5,
        "duration": 0.75,
        "volume": 0.8
    },

    "deep_voice": {
        "pitch": 0.7,
        "duration": 1.25,
        "volume": 1.0
    },

    "robot": {
        "pitch": 0.9,
        "duration": 1.0,
        "volume": 0.9
    }
}


# Allow voice presets to be selected from the terminal.
parser = argparse.ArgumentParser(
    description="Wayward Atlas Studio Mumble Generator"
)


parser.add_argument(
    "--preset",
    type=str,
    default="neutral",
    choices=VOICE_PRESETS.keys(),
    help="Select the voice preset to generate."
)


# Allow manual pitch adjustment from the terminal.
parser.add_argument(
    "--pitch",
    type=float,
    default=1.0,
    help="Pitch multiplier (0.5 to 2.0). Default: 1.0"
)


# Allow manual duration adjustment from the terminal.
parser.add_argument(
    "--duration",
    type=float,
    default=1.0,
    help="Duration multiplier (0.5 to 2.0). Default: 1.0"
)


# Allow manual volume adjustment from the terminal.
parser.add_argument(
    "--volume",
    type=float,
    default=1.0,
    help="Volume multiplier (0.0 to 1.0). Default: 1.0"
)


# Allow users to name custom voice variations.
parser.add_argument(
    "--variant",
    type=str,
    default="",
    help="Optional name for a custom voice variation."
)


# Preview cleanup candidates without deleting files.
parser.add_argument(
    "--clean",
    action="store_true",
    help="Preview extra WAV files in the selected output folder."
)

# Reserve explicit confirmation for safe cleanup.
parser.add_argument(
    "--confirm-clean",
    action="store_true",
    help="Confirm cleanup when safe deletion is implemented."
)



# Read the command-line arguments.
args = parser.parse_args()


# Cleanup confirmation requires cleanup mode.
if args.confirm_clean and not args.clean:
    parser.error("--confirm-clean requires --clean")


# Validate optional variant names for safe filenames.
variant_name = args.variant.strip().lower()

if variant_name and (
    not variant_name.isascii()
    or not all(
        char.islower() or char.isdigit() or char == "_"
        for char in variant_name
    )
):
    parser.error(
        "--variant must contain only letters a-z, numbers 0-9, or underscores"
    )

# Combine preset and variant names.
OUTPUT_NAME = (
    f"{args.preset}_{variant_name}"
    if variant_name
    else args.preset
)


# Select the requested voice preset.
ACTIVE_VOICE_PRESET = args.preset

# Validate and apply the requested pitch.
if not 0.5 <= args.pitch <= 2.0:
    parser.error("--pitch must be between 0.5 and 2.0")

VOICE_PITCH_MULTIPLIER = args.pitch

# Validate and apply the requested duration.
if not 0.5 <= args.duration <= 2.0:
    parser.error("--duration must be between 0.5 and 2.0")

VOICE_DURATION_MULTIPLIER = args.duration

# Validate and apply the requested volume.
if not 0.0 <= args.volume <= 1.0:
    parser.error("--volume must be between 0.0 and 1.0")

VOICE_VOLUME_MULTIPLIER = args.volume

# Validate the selected voice preset.
if ACTIVE_VOICE_PRESET not in VOICE_PRESETS:
    raise ValueError(
        f"Unknown voice preset: {ACTIVE_VOICE_PRESET}"
    )

selected_preset = VOICE_PRESETS[ACTIVE_VOICE_PRESET]

# Give each voice preset its own output folder.
OUT = ROOT / "output" / OUTPUT_NAME
OUT.mkdir(parents=True, exist_ok=True)

# Combine the selected preset with manual adjustments.
effective_pitch = (
    selected_preset["pitch"] * VOICE_PITCH_MULTIPLIER
)

effective_duration = (
    selected_preset["duration"] * VOICE_DURATION_MULTIPLIER
)

effective_volume = (
    selected_preset["volume"] * VOICE_VOLUME_MULTIPLIER
)


# Display the final voice settings after applying
# the selected preset and manual adjustments.
print(f"Voice preset: {ACTIVE_VOICE_PRESET}")
print(f"Effective pitch: {effective_pitch:.2f}x")
print(f"Effective duration: {effective_duration:.2f}x")
print(f"Effective volume: {effective_volume:.2f}x")


def syllable(name, pitch, vowel, duration, seed):
    rng = np.random.default_rng(seed)
    n = int(RATE * duration)
    t = np.arange(n) / RATE
    # Subtle rising/falling inflection; a smooth integrated phase avoids clicks.
    f0 = pitch * (1 + 0.05 * np.sin(2 * np.pi * t / duration + 0.5))
    phase = 2 * np.pi * np.cumsum(f0) / RATE
    # Harmonic source with formant-like spectral peaks, plus soft breath/noise.
    formants = {
        "ah": (800, 1180), "oh": (520, 950), "ee": (350, 2180),
        "uh": (610, 1330), "eh": (600, 1840), "oo": (330, 920),
    }
    f1, f2 = formants[vowel]
    src = np.zeros(n)
    for h in range(1, 27):
        freq = pitch * h
        band1 = np.exp(-0.5 * ((freq - f1) / 280) ** 2)
        band2 = np.exp(-0.5 * ((freq - f2) / 410) ** 2)
        gain = (0.10 + 1.8 * band1 + 1.4 * band2) / h ** 1.08
        src += gain * np.sin(h * phase + 0.03 * h)
    noise = rng.standard_normal(n)
    sos = butter(2, [420, 2800], btype="bandpass", fs=RATE, output="sos")
    src += 0.012 * sosfilt(sos, noise)
    # Attack and release have a raised-cosine contour.
    attack = max(1, int(.012 * RATE))
    release = max(1, int(.026 * RATE))
    envelope = np.ones(n)
    envelope[:attack] = np.sin(np.linspace(0, np.pi / 2, attack)) ** 2
    envelope[-release:] = np.cos(np.linspace(0, np.pi / 2, release)) ** 2
    envelope *= (0.91 + 0.09 * np.sin(np.pi * t / duration))
    src *= envelope
    src /= max(np.max(np.abs(src)), 1e-8)

    # Apply the generated voice volume.
    src *= 0.52 * effective_volume
    data = (np.clip(src, -1, 1) * 32767).astype("<i2")
    write_wav(OUT / name, data)
    return data


def write_wav(path, samples):
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(RATE)
        wav.writeframes(samples.tobytes())


voices = [
    ("neutral_01_ah.wav", 186, "ah", .110),
    ("neutral_02_oh.wav", 202, "oh", .125),
    ("neutral_03_ee.wav", 224, "ee", .090),
    ("neutral_04_uh.wav", 193, "uh", .105),
    ("neutral_05_eh.wav", 216, "eh", .115),
    ("neutral_06_oo.wav", 178, "oo", .130),
]


# Generate samples with preset-specific filenames.
samples = [
    syllable(
    name.replace(
        "neutral_",
        f"{OUTPUT_NAME}_",
        1
    ),
        pitch * effective_pitch,
        vowel,
        duration * effective_duration,
        1000 + idx
    )
    for idx, (name, pitch, vowel, duration) in enumerate(voices)
]

# A deliberate rhythm preview, not a real language or a transcript.
sequence = [0, 3, 1, 4, 2, 5, 1, 0, 4, 3, 2, 5, 0, 1, 3]
parts = []
for i, sample_idx in enumerate(sequence):
    parts.append(samples[sample_idx])
    pause = .17 if i in (5, 11) else (.055 if i % 3 else .075)
    parts.append(np.zeros(int(pause * RATE), dtype="<i2"))

# Give each preview its preset's name.
preview_filename = f"{OUTPUT_NAME}_speech_preview.wav"

write_wav(
    OUT / preview_filename,
    np.concatenate(parts)
)

(OUT / "README.txt").write_text(
    "Wayward Atlas Studio - Hybrid Mumble Prototype V1\n"

    # Record the voice preset and effective settings.
    
    f"\nVoice Preset: {ACTIVE_VOICE_PRESET}\n"
    f"Voice Variant: {variant_name if variant_name else 'Default'}\n"
    f"Output Name: {OUTPUT_NAME}\n"
    f"Effective Pitch: {effective_pitch:.2f}x\n"
    f"Effective Duration: {effective_duration:.2f}x\n"
    f"Effective Volume: {effective_volume:.2f}x\n"


    "Six ORIGINAL procedurally synthesized neutral syllables plus rhythm preview.\n\n"
    "Audio: WAV, PCM signed 16-bit, mono, 44,100 Hz.\n"
    "Each sample: approximately 90-130 ms.\n"
    "All sounds were generated from code, not derived from a game or recording.\n"
    "The generator source is included when available in source mode.\n\n"
    "Godot use (later): randomize samples per dialogue character reveal,\n"
    "then expose per-character pitch, volume, and frequency controls.\n"
    "These are design prototypes: listen and adjust before final integration.\n"
    "No spoken words or copyrighted audio assets are included.\n"
)


# Save each voice variant in its own ZIP archive.
archive = ROOT / "output" / f"WaywardAtlas_Mumble_{OUTPUT_NAME}.zip"

with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:

    
    # Package only the six expected syllables and
    # the current voice preview.
    expected_wavs = [
        OUT / name.replace(
            "neutral_",
            f"{OUTPUT_NAME}_",
            1
        )
        for name, _, _, _ in voices
    ]

    expected_wavs.append(OUT / preview_filename)

    # Preview leftover WAV files before cleanup.
    # This step never deletes files.
    if args.clean:
        expected_names = {
            path.name for path in expected_wavs
        }

        cleanup_candidates = [
            path for path in sorted(OUT.glob("*.wav"))
            if path.name not in expected_names
        ]

        print("\nCleanup preview:")

        if cleanup_candidates:
            for path in cleanup_candidates:
                print(f"  Candidate: {path.name}")
        else:
            print("  No extra WAV files found.")

        
        print(
            "  Preview only: no files were deleted. "
            "Extra WAV files may contain custom audio."
        )



    for path in expected_wavs:
        if not path.is_file():
            raise FileNotFoundError(
                f"Expected generated audio is missing: {path}"
            )

        z.write(
            path,
            arcname=f"{OUTPUT_NAME}/{path.name}"
        )


    # Include generated documentation.
    readme_path = OUT / "README.txt"

    if readme_path.exists():
        z.write(
            readme_path,
            arcname=f"{OUTPUT_NAME}/README.txt"
        )

    
    # WAYWARD ATLAS CUSTOM:
    # Include the original Python source in source mode.
    # Standalone builds do not require this source file.
    if not getattr(sys, "frozen", False):
        source_script = Path(__file__).resolve()

        if source_script.is_file():
            z.write(
                source_script,
                arcname=f"{OUTPUT_NAME}/make_mumble_pack.py"
            )


print(archive)

