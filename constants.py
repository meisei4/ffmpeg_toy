# constants.py

DEFAULT_TARGET_SIZE_MB = 10
DEFAULT_RESOLUTION = "lowest"
DEFAULT_DENOISE = "med"
DEFAULT_PRESET = "slower"
DEFAULT_MUTE_AUDIO = False
DEFAULT_PREVIEW_DURATION = 0
DEFAULT_SPEED_FACTOR = None

DEFAULT_AUDIO_BITRATE = 64000
DEFAULT_MIN_VIDEO_KBPS = 100
DEFAULT_OVERHEAD = 0.02
DEFAULT_FALLBACK_FPS = "30"

DEFAULT_CROP = {"width": 640, "height": 360, "x": 0, "y": 0}
DEFAULT_FADE = {"type": "in", "duration": 1.0}
DEFAULT_SCALE = {"w": "iw", "h": "ih"}
DEFAULT_ROTATE = {"angle": 0}
DEFAULT_TRANSPOSE = {"dir": 0}
DEFAULT_LENSCORRECTION = {"k1": 0, "k2": 0}
DEFAULT_PERSPECTIVE = {"x0": 0, "y0": 0, "x1": 0, "y1": 0, "x2": 0, "y2": 0, "x3": 0, "y3": 0}

DEFAULT_BOXBLUR = "0:1"
DEFAULT_GBLUR = "sigma=1"
DEFAULT_SMARTBLUR = "lr=1:ls=1"
DEFAULT_EDGEDETECT = "mode=colormix"
DEFAULT_SOBEL = ""
DEFAULT_UNSHARP = "luma_msize_x=7:luma_msize_y=7:luma_amount=1.0"
DEFAULT_DELOGO = {"x": 0, "y": 0, "w": 100, "h": 100, "show": 0}

DEFAULT_OVERLAY = {"x": 0, "y": 0}
DEFAULT_BLEND = {"phase": 1, "cross_params": [], "overrides": {}}
DEFAULT_CHROMAKEY = {"color": "green", "similarity": 0.1, "blend": 0.0}
DEFAULT_COLORKEY = {"color": "black", "similarity": 0.1, "blend": 0.0}
DEFAULT_LUMAKEY = {"threshold": 0.5}

DEFAULT_COLORBALANCE = {"rs": 1, "gs": 1, "bs": 1}
DEFAULT_COLORCHANNELMIXER = {"rr": 1, "rg": 0, "rb": 0, "gr": 0, "gg": 1, "gb": 0, "br": 0, "bg": 0, "bb": 1}
DEFAULT_CURVES = ""
DEFAULT_EQ = {"brightness": 0, "contrast": 1, "gamma": 1, "saturation": 1}
DEFAULT_LUT = ""
DEFAULT_LUT3D = ""
DEFAULT_HALDCLUT = ""

DEFAULT_DRAWTEXT = {
    "text": "",
    "x": "(w-text_w)/2",
    "y": "(h-text_h)/2",
    "fontsize": 24,
    "fontcolor": "white"
}
