import sys
import os
import shlex
import subprocess
import json
import base64
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QPushButton, QLineEdit, QSlider, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QFileDialog, QScrollArea,
    QFrame, QSplitter, QTextEdit, QGroupBox, QToolButton, QSizePolicy,
    QStatusBar, QMessageBox, QTabWidget, QCompleter
)
from PyQt6.QtCore import (
    Qt, QProcess, QThread, pyqtSignal, QStringListModel,
    QPropertyAnimation, QEasingCurve, QTimer, QSize
)
from PyQt6.QtGui import (
    QFont, QFontDatabase, QPalette, QColor, QIcon, QPixmap,
    QPainter, QTextCursor, QSyntaxHighlighter, QTextCharFormat
)

# ─── THEMES ────────────────────────────────────────────────────────────────────

DARK = {
    "name": "dark",
    "bg":         "#0e0f11",
    "surface":    "#16181c",
    "surface2":   "#1e2027",
    "border":     "#2a2d36",
    "accent":     "#5b6aff",
    "accent2":    "#40e0a0",
    "danger":     "#ff5f6d",
    "text":       "#e8eaf0",
    "text_dim":   "#6b7280",
    "text_muted": "#3d4147",
}

LIGHT = {
    "name": "light",
    "bg":         "#f8f9fa",
    "surface":    "#ffffff",
    "surface2":   "#f1f3f5",
    "border":     "#dee2e6",
    "accent":     "#5b6aff",
    "accent2":    "#099268",
    "danger":     "#e03131",
    "text":       "#212529",
    "text_dim":   "#495057",
    "text_muted": "#adb5bd",
}

_RAW_SVG = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>'
_B64_CHECK_ICON = base64.b64encode(_RAW_SVG.encode('utf-8')).decode('utf-8')

def get_qss(theme):
    check_icon_url = f"url(data:image/svg+xml;base64,{_B64_CHECK_ICON})"

    return f"""
    QMainWindow, QWidget {{ background: {theme['bg']}; color: {theme['text']}; }}

    /* Scrollbars */
    QScrollBar:vertical {{ background: {theme['surface']}; width: 6px; border-radius: 3px; }}
    QScrollBar::handle:vertical {{ background: {theme['border']}; border-radius: 3px; min-height: 30px; }}
    QScrollBar::handle:vertical:hover {{ background: {theme['accent']}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ background: {theme['surface']}; height: 6px; }}
    QScrollBar::handle:horizontal {{ background: {theme['border']}; border-radius: 3px; }}

    /* LineEdits */
    QLineEdit {{
        background: {theme['surface']}; border: 1px solid {theme['border']};
        border-radius: 6px; padding: 7px 12px; color: {theme['text']};
        font-size: 13px; selection-background-color: {theme['accent']};
    }}
    QLineEdit:focus {{ border: 1px solid {theme['accent']}; }}
    QLineEdit:hover {{ border: 1px solid #3d4455; }}
    QLineEdit:disabled {{ background: {theme['bg']}; color: {theme['text_muted']}; }}

    /* SpinBoxes */
    QSpinBox, QDoubleSpinBox {{
        background: {theme['surface']}; border: 1px solid {theme['border']};
        border-radius: 6px; padding: 6px 10px; color: {theme['text']}; font-size: 13px;
    }}
    QSpinBox:focus, QDoubleSpinBox:focus {{ border: 1px solid {theme['accent']}; }}
    QSpinBox::up-button, QSpinBox::down-button,
    QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
        background: {theme['surface2']}; border: none; width: 16px;
    }}
    QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
    QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
        background: {theme['border']};
    }}
    QSpinBox:disabled, QDoubleSpinBox:disabled {{
        background: {theme['bg']}; color: {theme['text_muted']};
        border: 1px solid {theme['text_muted']};
    }}

    /* ComboBox */
    QComboBox {{
        background: {theme['surface']}; border: 1px solid {theme['border']};
        border-radius: 6px; padding: 7px 12px; color: {theme['text']}; font-size: 13px;
        min-width: 80px;
    }}
    QComboBox:focus {{ border: 1px solid {theme['accent']}; }}
    QComboBox::drop-down {{ border: none; width: 24px; }}
    QComboBox QAbstractItemView {{
        background: {theme['surface2']}; border: 1px solid {theme['border']};
        color: {theme['text']}; selection-background-color: {theme['accent']};
        outline: none;
    }}
    QComboBox:disabled {{
        background: {theme['bg']}; color: {theme['text_muted']};
        border: 1px solid {theme['text_muted']};
    }}

    /* Checkboxes */
    QCheckBox {{
        color: {theme['text']}; spacing: 8px; font-size: 13px;
    }}
    QCheckBox::indicator {{
        width: 18px; height: 18px; border-radius: 4px;
        border: 1px solid {theme['border']}; background: {theme['surface']};
    }}
    QCheckBox::indicator:hover {{
        border-color: {theme['accent']}; background: {theme['surface2']};
    }}
    QCheckBox::indicator:checked {{
        background: {theme['accent']};
        border-color: {theme['accent']};
        image: {check_icon_url};
    }}
    QCheckBox::indicator:disabled {{
        background: {theme['bg']};
        border-color: {theme['text_muted']};
    }}
    QCheckBox:disabled {{ color: {theme['text_muted']}; }}

    /* Labels */
    QLabel {{ color: {theme['text']}; font-size: 13px; }}
    QLabel#paramLabel {{ color: {theme['text_dim']}; }}
    QLabel:disabled {{ color: {theme['text_muted']}; }}

    /* Buttons */
    QPushButton {{
        background: {theme['surface2']}; border: 1px solid {theme['border']};
        border-radius: 6px; padding: 7px 16px; color: {theme['text']};
        font-size: 13px; font-weight: 500;
    }}
    QPushButton:hover {{ background: {theme['border']}; border-color: #3d4455; }}
    QPushButton:pressed {{ background: {theme['accent']}; border-color: {theme['accent']}; }}

    QPushButton#primary {{
        background: {theme['accent']}; border-color: {theme['accent']}; color: white;
        font-weight: 600; font-size: 14px; padding: 10px 28px; border-radius: 8px;
    }}
    QPushButton#primary:hover {{ background: #6b7aff; border-color: #6b7aff; }}
    QPushButton#primary:disabled {{ background: {theme['surface2']}; border-color: {theme['border']}; color: {theme['text_dim']}; }}

    QPushButton#danger {{
        background: {theme['danger']}; border-color: {theme['danger']}; color: white;
        font-weight: 600; font-size: 14px; padding: 10px 28px; border-radius: 8px;
    }}
    QPushButton#danger:hover {{ background: #ff7a85; }}

    QPushButton#browse {{
        padding: 7px 12px; min-width: 32px; max-width: 36px;
        background: {theme['surface2']}; font-size: 13px;
    }}

    /* GroupBox */
    QGroupBox {{
        border: 1px solid {theme['border']}; border-radius: 8px;
        margin-top: 10px; padding: 12px 10px 8px 10px;
        font-size: 12px; font-weight: 600; color: {theme['text_dim']};
    }}
    QGroupBox::title {{
        subcontrol-origin: margin; left: 10px; padding: 0 4px;
        color: {theme['text_dim']}; text-transform: uppercase; letter-spacing: 1px;
    }}

    /* TextEdit (log & cmd) */
    QTextEdit {{
        background: {theme['bg']}; border: 1px solid {theme['border']};
        border-radius: 6px; color: {theme['accent2']}; font-family: 'Cascadia Code', 'Fira Code', monospace;
        font-size: 12px; padding: 8px;
        selection-background-color: {theme['accent']};
    }}

    /* TabWidget */
    QTabWidget::pane {{ border: 1px solid {theme['border']}; border-radius: 8px; background: {theme['surface']}; }}
    QTabBar::tab {{
        background: {theme['surface']}; color: {theme['text_dim']}; padding: 8px 18px;
        border: 1px solid {theme['border']}; border-bottom: none;
        border-radius: 6px 6px 0 0; font-size: 12px; margin-right: 2px;
    }}
    QTabBar::tab:selected {{ background: {theme['surface2']}; color: {theme['text']}; border-bottom: 2px solid {theme['accent']}; }}
    QTabBar::tab:hover {{ color: {theme['text']}; }}

    QFrame[frameShape="4"], QFrame[frameShape="5"] {{ color: {theme['border']}; }}

    QToolButton#collapsible {{
        background: {theme['surface2']}; border: 1px solid {theme['border']};
        border-radius: 6px; padding: 6px 12px; color: {theme['text']};
        font-size: 12px; font-weight: 600; text-align: left;
    }}
    QToolButton#collapsible:hover {{ background: {theme['border']}; }}
    QToolButton#collapsible:checked {{ border-color: {theme['accent']}; color: {theme['accent']}; }}

    QStatusBar {{ background: {theme['surface']}; color: {theme['text_dim']}; font-size: 11px; border-top: 1px solid {theme['border']}; }}
    QStatusBar::item {{ border: none; }}

    QSlider::groove:horizontal {{
        background: {theme['border']}; height: 4px; border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {theme['accent']}; width: 14px; height: 14px;
        border-radius: 7px; margin: -5px 0;
    }}
    QSlider::sub-page:horizontal {{ background: {theme['accent']}; border-radius: 2px; }}
    """

# ─── PARAMETER DEFINITIONS ────────────────────────────────────────────────────

PARAMS = {
    "Core": [
        ("--ctx-size",      "Context Size",         "spin",   {"min": 0, "max": 1048576, "default": 0,    "step": 512,  "tip": "Size of prompt context (0 = from model)"}),
        ("--n-predict",     "Max Tokens",           "spin",   {"min": -1, "max": 1048576, "default": -1,  "step": 256,  "tip": "Max tokens to predict (-1 = infinity)"}),
        ("--threads",       "CPU Threads",          "spin",   {"min": -1, "max": 512, "default": -1,      "step": 1,    "tip": "CPU threads for generation (-1 = auto)"}),
        ("--threads-batch", "Batch Threads",        "spin",   {"min": -1, "max": 512, "default": -1,      "step": 1,    "tip": "Threads for batch/prompt processing"}),
        ("--batch-size",    "Batch Size",           "spin",   {"min": 1, "max": 65536, "default": 2048,   "step": 256,  "tip": "Logical max batch size"}),
        ("--ubatch-size",   "Micro-Batch Size",     "spin",   {"min": 1, "max": 65536, "default": 512,    "step": 128,  "tip": "Physical max batch size"}),
        ("--n-gpu-layers",  "GPU Layers",           "text",   {"default": "auto",                                       "tip": "Layers to store in VRAM: number, 'auto', or 'all'"}),
        ("--keep",          "Keep Tokens",          "spin",   {"min": -1, "max": 65536, "default": 0,     "step": 64,   "tip": "Tokens to keep from initial prompt (-1 = all)"}),
    ],
    "Sampling": [
        ("--temp",              "Temperature",      "dspin",  {"min": 0.0, "max": 5.0,  "default": 0.8,   "step": 0.05, "tip": "Sampling temperature"}),
        ("--top-k",             "Top-K",            "spin",   {"min": 0,   "max": 1000, "default": 40,    "step": 5,    "tip": "Top-K sampling (0 = disabled)"}),
        ("--top-p",             "Top-P",            "dspin",  {"min": 0.0, "max": 1.0,  "default": 0.95,  "step": 0.01, "tip": "Nucleus sampling (1.0 = disabled)"}),
        ("--min-p",             "Min-P",            "dspin",  {"min": 0.0, "max": 1.0,  "default": 0.05,  "step": 0.01, "tip": "Min-P sampling (0.0 = disabled)"}),
        ("--repeat-penalty",    "Repeat Penalty",   "dspin",  {"min": 0.0, "max": 2.0,  "default": 1.0,   "step": 0.05, "tip": "Penalize repeated tokens (1.0 = disabled)"}),
        ("--repeat-last-n",     "Repeat Last N",    "spin",   {"min": -1,  "max": 4096, "default": 64,    "step": 16,   "tip": "Tokens to consider for repeat penalty (-1 = ctx)"}),
        ("--presence-penalty",  "Presence Penalty", "dspin",  {"min": 0.0, "max": 2.0,  "default": 0.0,   "step": 0.05, "tip": "Presence penalty (0.0 = disabled)"}),
        ("--frequency-penalty", "Frequency Penalty","dspin",  {"min": 0.0, "max": 2.0,  "default": 0.0,   "step": 0.05, "tip": "Frequency penalty (0.0 = disabled)"}),
        ("--seed",              "RNG Seed",         "spin",   {"min": -1,  "max": 999999999, "default": -1,"step": 1,   "tip": "Random seed (-1 = random)"}),
        ("--dynatemp-range",    "DynaTemp Range",   "dspin",  {"min": 0.0, "max": 5.0,  "default": 0.0,   "step": 0.1,  "tip": "Dynamic temperature range (0.0 = disabled)"}),
        ("--mirostat",          "Mirostat",         "combo",  {"choices": ["0 (off)", "1", "2"],           "default": 0, "tip": "Mirostat sampling (0=off, 1=v1, 2=v2)"}),
        ("--mirostat-lr",       "Mirostat LR",      "dspin",  {"min": 0.0, "max": 1.0,  "default": 0.1,   "step": 0.01, "tip": "Mirostat learning rate (eta)"}),
        ("--mirostat-ent",      "Mirostat Entropy", "dspin",  {"min": 0.0, "max": 10.0, "default": 5.0,   "step": 0.5,  "tip": "Mirostat target entropy (tau)"}),
        ("--dry-multiplier",    "DRY Multiplier",   "dspin",  {"min": 0.0, "max": 5.0,  "default": 0.0,   "step": 0.05, "tip": "DRY sampling multiplier (0 = disabled)"}),
        ("--xtc-probability",   "XTC Probability",  "dspin",  {"min": 0.0, "max": 1.0,  "default": 0.0,   "step": 0.05, "tip": "XTC probability (0.0 = disabled)"}),
        ("--ignore-eos",        "Ignore EOS",       "check",  {"default": False,                                        "tip": "Ignore end-of-stream token"}),
    ],
    "Server": [
        ("--host",              "Host",             "text",   {"default": "127.0.0.1",                                  "tip": "IP address to listen on"}),
        ("--port",              "Port",             "spin",   {"min": 1,   "max": 65535, "default": 8080, "step": 1,    "tip": "Port to listen on"}),
        ("--parallel",          "Parallel Slots",   "spin",   {"min": -1,  "max": 256,  "default": -1,   "step": 1,    "tip": "Number of server slots (-1 = auto)"}),
        ("--timeout",           "Timeout (sec)",    "spin",   {"min": 0,   "max": 86400,"default": 600,  "step": 60,   "tip": "Server read/write timeout in seconds"}),
        ("--threads-http",      "HTTP Threads",     "spin",   {"min": -1,  "max": 256,  "default": -1,   "step": 1,    "tip": "Threads for HTTP request processing"}),
        ("--api-key",           "API Key",          "text",   {"default": "",                                           "tip": "API key(s) for auth (comma-separated)"}),
        ("--api-prefix",        "API Prefix",       "text",   {"default": "",                                           "tip": "Prefix path for the server API"}),
        ("--cont-batching",     "Cont. Batching",   "check",  {"default": True,                                         "tip": "Enable continuous/dynamic batching"}),
        ("--embeddings",        "Embeddings Only",  "check",  {"default": False,                                        "tip": "Restrict to embedding use case only"}),
        ("--reranking",         "Reranking",        "check",  {"default": False,                                        "tip": "Enable reranking endpoint"}),
        ("--metrics",           "Prometheus Metrics","check", {"default": False,                                        "tip": "Enable /metrics endpoint"}),
        ("--slots",             "Slots Endpoint",   "check",  {"default": True,                                         "tip": "Expose slots monitoring endpoint"}),
        ("--props",             "Props Endpoint",   "check",  {"default": False,                                        "tip": "Enable POST /props for global properties"}),
        ("--no-webui",          "Disable Web UI",   "check",  {"default": False,                                        "tip": "Disable built-in Web UI"}),
        ("--cache-prompt",      "Cache Prompt",     "check",  {"default": True,                                         "tip": "Enable prompt caching"}),
        ("--cache-reuse",       "Cache Reuse Min",  "spin",   {"min": 0,   "max": 65536,"default": 0,    "step": 64,   "tip": "Min chunk size for KV cache reuse"}),
        ("--sleep-idle-seconds","Idle Sleep (sec)", "spin",   {"min": -1,  "max": 86400,"default": -1,   "step": 30,   "tip": "Sleep after N seconds idle (-1 = disabled)"}),
    ],
    "Performance": [
        ("--flash-attn",     "Flash Attention",     "combo",  {"choices": ["auto", "on", "off"],           "default": 0, "tip": "Flash Attention use"}),
        ("--cache-type-k",   "KV Cache Type K",     "combo",  {"choices": ["f16","f32","bf16","q8_0","q4_0","q4_1","q5_0","q5_1","iq4_nl"], "default": 0, "tip": "KV cache data type for K"}),
        ("--cache-type-v",   "KV Cache Type V",     "combo",  {"choices": ["f16","f32","bf16","q8_0","q4_0","q4_1","q5_0","q5_1","iq4_nl"], "default": 0, "tip": "KV cache data type for V"}),
        ("--split-mode",     "GPU Split Mode",      "combo",  {"choices": ["layer", "none", "row"],        "default": 0, "tip": "How to split model across multiple GPUs"}),
        ("--main-gpu",       "Main GPU Index",      "spin",   {"min": 0, "max": 16, "default": 0,         "step": 1,    "tip": "Primary GPU for model/intermediate results"}),
        ("--mlock",          "Force mlock",         "check",  {"default": False,                                        "tip": "Force system to keep model in RAM"}),
        ("--no-mmap",        "Disable mmap",        "check",  {"default": False,                                        "tip": "Disable memory-mapping model files"}),
        ("--swa-full",       "Full SWA Cache",      "check",  {"default": False,                                        "tip": "Use full-size Sliding Window Attention cache"}),
        ("--kv-offload",     "KV Cache Offload",    "check",  {"default": True,                                         "tip": "Enable KV cache GPU offloading"}),
        ("--repack",         "Weight Repack",       "check",  {"default": True,                                         "tip": "Enable weight repacking for performance"}),
        ("--op-offload",     "Op Offload",          "check",  {"default": True,                                         "tip": "Offload host tensor operations to device"}),
        ("--kv-unified",     "Unified KV Buffer",   "check",  {"default": True,                                         "tip": "Use single unified KV buffer across sequences"}),
        ("--context-shift",  "Context Shift",       "check",  {"default": False,                                        "tip": "Enable context shifting for infinite generation"}),
        ("--fit",            "Auto-Fit to VRAM",    "combo",  {"choices": ["on", "off"],                   "default": 0, "tip": "Auto-adjust params to fit device memory"}),
        ("--numa",           "NUMA Mode",           "combo",  {"choices": ["none", "distribute", "isolate", "numactl"], "default": 0, "tip": "NUMA optimization mode"}),
        ("--prio",           "Thread Priority",     "combo",  {"choices": ["normal (0)", "low (-1)", "medium (1)", "high (2)", "realtime (3)"], "default": 0, "tip": "Process/thread priority"}),
        ("--poll",           "Poll Level",          "spin",   {"min": 0, "max": 100, "default": 50,       "step": 10,   "tip": "Polling level for work waiting (0=no polling)"}),
    ],
    "RoPE / Context Extension": [
        ("--rope-scaling",   "RoPE Scaling",        "combo",  {"choices": ["default", "none", "linear", "yarn"], "default": 0, "tip": "RoPE frequency scaling method"}),
        ("--rope-scale",     "RoPE Scale",          "dspin",  {"min": 0.0, "max": 32.0, "default": 0.0,  "step": 0.5,  "tip": "RoPE context scaling factor (0 = disabled)"}),
        ("--rope-freq-base", "RoPE Freq Base",      "dspin",  {"min": 0.0, "max": 5000000.0, "default":0.0,"step": 1000,"tip": "RoPE base frequency (0 = from model)"}),
        ("--yarn-orig-ctx",  "YaRN Orig Context",   "spin",   {"min": 0, "max": 1048576, "default": 0,   "step": 1024, "tip": "YaRN original context size (0 = training ctx)"}),
        ("--yarn-ext-factor","YaRN Ext Factor",     "dspin",  {"min": -1.0, "max": 4.0, "default": -1.0, "step": 0.1,  "tip": "YaRN extrapolation mix factor"}),
        ("--yarn-attn-factor","YaRN Attn Factor",   "dspin",  {"min": -1.0, "max": 4.0, "default": -1.0, "step": 0.1,  "tip": "YaRN attention magnitude scale"}),
    ],
    "Speculative Decoding": [
        ("--draft",          "Draft Tokens",        "spin",   {"min": 0, "max": 128, "default": 16,      "step": 4,    "tip": "Tokens to draft for speculative decoding"}),
        ("--draft-min",      "Min Draft Tokens",    "spin",   {"min": 0, "max": 64,  "default": 0,       "step": 1,    "tip": "Minimum draft tokens to use"}),
        ("--draft-p-min",    "Draft Min Prob",      "dspin",  {"min": 0.0, "max": 1.0, "default": 0.75,  "step": 0.05, "tip": "Minimum speculative decoding probability"}),
        ("--ctx-size-draft", "Draft Context Size",  "spin",   {"min": 0, "max": 1048576, "default": 0,   "step": 512,  "tip": "Prompt context size for draft model (0 = from model)"}),
        ("--gpu-layers-draft","Draft GPU Layers",   "text",   {"default": "auto",                                       "tip": "Draft model layers to store in VRAM"}),
        ("--threads-draft",  "Draft Threads",       "spin",   {"min": -1, "max": 512, "default": -1,     "step": 1,    "tip": "Threads for draft model generation"}),
        ("--spec-type",      "Spec Type",           "combo",  {"choices": ["none","ngram-cache","ngram-simple","ngram-map-k","ngram-map-k4v","ngram-mod"], "default": 0, "tip": "Speculative decoding type (no draft model)"}),
    ],
    "Reasoning": [
        ("--reasoning",         "Reasoning Mode",   "combo",  {"choices": ["auto", "on", "off"],          "default": 0, "tip": "Use reasoning/thinking in chat"}),
        ("--reasoning-format",  "Reasoning Format", "combo",  {"choices": ["auto", "none", "deepseek", "deepseek-legacy"], "default": 0, "tip": "How thought tags are returned"}),
        ("--reasoning-budget",  "Reasoning Budget", "spin",   {"min": -1, "max": 100000, "default": -1,  "step": 1000, "tip": "Token budget for thinking (-1 = unlimited, 0 = off)"}),
    ],
    "Chat Template": [
        ("--jinja",          "Use Jinja",           "check",  {"default": True,                                         "tip": "Use Jinja template engine for chat"}),
        ("--chat-template",  "Chat Template",       "combo",  {"choices": [
            "(from model)", "chatml", "llama3", "llama2", "mistral-v3", "mistral-v7",
            "deepseek", "deepseek2", "deepseek3", "gemma", "phi3", "phi4", "command-r",
            "vicuna", "zephyr", "openchat", "granite", "grok-2", "falcon3",
        ], "default": 0, "tip": "Jinja chat template"}),
        ("--prefill-assistant", "Prefill Assistant","check",  {"default": True,                                         "tip": "Prefill assistant response if last msg is assistant"}),
        ("--skip-chat-parsing", "Skip Chat Parse",  "check",  {"default": False,                                        "tip": "Force pure content parser (no tool/reasoning extract)"}),
    ],
    "Logging": [
        ("--log-disable",    "Disable Logging",     "check",  {"default": False,                                        "tip": "Disable all logging"}),
        ("--log-verbosity",  "Log Verbosity",       "combo",  {"choices": ["3 (info)", "0 (generic)", "1 (error)", "2 (warning)", "4 (debug)"], "default": 0, "tip": "Logging verbosity level"}),
        ("--log-colors",     "Log Colors",          "combo",  {"choices": ["auto", "on", "off"],          "default": 0, "tip": "Colored log output"}),
        ("--log-prefix",     "Log Prefix",          "check",  {"default": False,                                        "tip": "Enable prefix in log messages"}),
        ("--log-timestamps", "Log Timestamps",      "check",  {"default": False,                                        "tip": "Enable timestamps in log messages"}),
        ("--verbose-prompt", "Verbose Prompt",      "check",  {"default": False,                                        "tip": "Print verbose prompt before generation"}),
    ],
    "Multimodal": [
        ("--mmproj-offload",  "mmproj GPU Offload", "check",  {"default": True,                                         "tip": "GPU offloading for multimodal projector"}),
        ("--image-min-tokens","Image Min Tokens",   "spin",   {"min": 0, "max": 65536, "default": 0,     "step": 64,    "tip": "Min tokens per image (0 = from model)"}),
        ("--image-max-tokens","Image Max Tokens",   "spin",   {"min": 0, "max": 65536, "default": 0,     "step": 64,    "tip": "Max tokens per image (0 = from model)"}),
    ],
}

# Sentinel object for --no-cont-batching
_CONT_BATCHING_OFF = object()

# ─── COLLAPSIBLE SECTION ──────────────────────────────────────────────────────

class CollapsibleSection(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self._expanded = False
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.toggle_btn = QToolButton()
        self.toggle_btn.setObjectName("collapsible")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(False)
        self.toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.toggle_btn.setText(f"  ▶  {title.upper()}")
        self.toggle_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.toggle_btn.setMinimumHeight(34)
        self.toggle_btn.clicked.connect(self._toggle)
        layout.addWidget(self.toggle_btn)

        self.content = QWidget()
        self.content.setVisible(False)
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(4, 4, 4, 8)
        content_layout.setSpacing(6)
        layout.addWidget(self.content)

    def _toggle(self, checked):
        self._expanded = checked
        self.content.setVisible(checked)
        arrow = "▼" if checked else "▶"
        name = self.toggle_btn.text().split("  ", 2)[-1]
        self.toggle_btn.setText(f"  {arrow}  {name}")

    def add_widget(self, w):
        self.content.layout().addWidget(w)


# ─── PARAM ROW ────────────────────────────────────────────────────────────────

class ParamRow(QWidget):
    def __init__(self, flag, label, ptype, opts, parent=None):
        super().__init__(parent)
        self.flag = flag
        self.ptype = ptype
        self.opts = opts
        self._active = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self.enable_cb = QCheckBox()
        self.enable_cb.setFixedWidth(20)
        self.enable_cb.setToolTip(f"Enable {flag}")
        self.enable_cb.stateChanged.connect(self._on_enable)
        layout.addWidget(self.enable_cb)

        lbl = QLabel(label)
        lbl.setFixedWidth(148)
        lbl.setToolTip(opts.get("tip", ""))
        lbl.setObjectName("paramLabel")
        layout.addWidget(lbl)

        self.input = self._make_input()
        self.input.setEnabled(False)
        layout.addWidget(self.input, 1)

        self.browse_btn = None
        if ptype in ("file", "dir"):
            self.browse_btn = QPushButton("…")
            self.browse_btn.setObjectName("browse")
            self.browse_btn.setFixedSize(32, 32)
            self.browse_btn.setEnabled(False)
            self.browse_btn.clicked.connect(self._browse)
            layout.addWidget(self.browse_btn)

        self.enable_cb.stateChanged.connect(lambda s: self._update_enabled(s == 2))

    def _make_input(self):
        opts = self.opts
        if self.ptype == "spin":
            w = QSpinBox()
            w.setMinimum(opts.get("min", 0))
            w.setMaximum(opts.get("max", 99999))
            w.setSingleStep(opts.get("step", 1))
            w.setValue(opts.get("default", 0))
            return w
        elif self.ptype == "dspin":
            w = QDoubleSpinBox()
            w.setMinimum(opts.get("min", 0.0))
            w.setMaximum(opts.get("max", 1.0))
            w.setSingleStep(opts.get("step", 0.01))
            w.setDecimals(3)
            w.setValue(opts.get("default", 0.0))
            return w
        elif self.ptype == "combo":
            w = QComboBox()
            for c in opts.get("choices", []):
                w.addItem(str(c))
            w.setCurrentIndex(opts.get("default", 0))
            return w
        elif self.ptype == "check":
            w = QCheckBox("Enabled")
            w.setChecked(opts.get("default", False))
            return w
        else:
            w = QLineEdit()
            w.setText(str(opts.get("default", "")))
            w.setPlaceholderText(opts.get("placeholder", ""))
            return w

    def _update_enabled(self, enabled):
        self.input.setEnabled(enabled)
        if self.browse_btn:
            self.browse_btn.setEnabled(enabled)

    def _on_enable(self, state):
        enabled = state == 2
        self.input.setEnabled(enabled)
        if self.browse_btn:
            self.browse_btn.setEnabled(enabled)

    def _browse(self):
        if self.ptype == "dir":
            path = QFileDialog.getExistingDirectory(self, f"Select directory for {self.flag}")
        else:
            path, _ = QFileDialog.getOpenFileName(self, f"Select file for {self.flag}", "", "All Files (*)")
        if path:
            self.input.setText(path)

    def reset(self):
        self.enable_cb.setChecked(False)
        default = self.opts.get("default")
        if self.ptype == "spin":
            self.input.setValue(default if default is not None else 0)
        elif self.ptype == "dspin":
            self.input.setValue(default if default is not None else 0.0)
        elif self.ptype == "combo":
            self.input.setCurrentIndex(default if default is not None else 0)
        elif self.ptype == "check":
            self.input.setChecked(default if default is not None else False)
        elif self.ptype == "text":
            self.input.setText(str(default if default is not None else ""))

    def is_active(self):
        return self.enable_cb.isChecked()

    def get_flag_args(self):
        """Return list of CLI args for this param, or empty if not active."""
        if not self.enable_cb.isChecked():
            return []
        flag = self.flag

        if self.ptype == "spin":
            val = self.input.value()
        elif self.ptype == "dspin":
            val = self.input.value()
        elif self.ptype == "combo":
            raw = self.input.currentText()
            val = raw.split(" ")[0]
        elif self.ptype == "check":
            checked = self.input.isChecked()
            if flag.startswith("--no-") or flag in ("--log-disable",):
                return [flag] if checked else []
            else:
                return [flag] if checked else []
        else:
            val = self.input.text().strip()
            if not val:
                return []

        if self.ptype == "check":
            return []
        return [flag, str(val)]

    def matches_search(self, query):
        q = query.lower()
        return (q in self.flag.lower() or
                any(q in lbl.lower() for lbl in [self.opts.get("tip", "")]))


# ─── FILE PICKER ROW ─────────────────────────────────────────────────────────

class FilePickerRow(QWidget):
    def __init__(self, flag, label, file_filter="All Files (*)", parent=None):
        super().__init__(parent)
        self.flag = flag
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.enable_cb = QCheckBox()
        self.enable_cb.setFixedWidth(20)
        self.enable_cb.stateChanged.connect(self._on_enable)
        layout.addWidget(self.enable_cb)

        lbl = QLabel(label)
        lbl.setFixedWidth(148)
        lbl.setObjectName("paramLabel")
        layout.addWidget(lbl)

        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select file…")
        self.path_edit.setEnabled(False)
        layout.addWidget(self.path_edit, 1)

        self.browse_btn = QPushButton("…")
        self.browse_btn.setObjectName("browse")
        self.browse_btn.setFixedSize(32, 32)
        self.browse_btn.setEnabled(False)
        self.browse_btn.clicked.connect(lambda: self._browse(file_filter))
        layout.addWidget(self.browse_btn)

        self.enable_cb.stateChanged.connect(
            lambda s: (self.path_edit.setEnabled(s == 2),
                       self.browse_btn.setEnabled(s == 2))
        )

    def _on_enable(self, state):
        enabled = state == 2
        self.path_edit.setEnabled(enabled)
        self.browse_btn.setEnabled(enabled)

    def _browse(self, filt):
        path, _ = QFileDialog.getOpenFileName(self, f"Select {self.flag}", "", filt)
        if path:
            self.path_edit.setText(path)

    def reset(self):
        self.enable_cb.setChecked(False)
        self.path_edit.clear()

    def get_flag_args(self):
        if not self.enable_cb.isChecked():
            return []
        val = self.path_edit.text().strip()
        if not val:
            return []
        return [self.flag, val]


# ─── MAIN WINDOW ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("llama-server Launcher")
        self.resize(1100, 780)

        self._current_theme = DARK
        self.setStyleSheet(get_qss(self._current_theme))

        self._process = None
        self._param_rows: list[ParamRow] = []
        self._settings_path = Path.home() / ".llamalauncher_settings.json"

        # Quick setting checkbox references
        self._qs_cbs = {}

        self._build_ui()
        self._load_settings()
        self._update_cmd_preview()

    # ── HELPERS ───────────────────────────────────────────────────────────────

    def _make_qs_cell(self, label_text, input_widget):
        """Create a quick-settings cell: [enable_cb] [label] [input]."""
        cell = QWidget()
        h = QHBoxLayout(cell)
        h.setContentsMargins(0, 2, 0, 2)
        h.setSpacing(4)

        cb = QCheckBox()
        cb.setChecked(True)
        cb.setFixedWidth(18)
        cb.setToolTip(f"Include {label_text} in command")

        lbl = QLabel(label_text)
        lbl.setObjectName("paramLabel")

        h.addWidget(cb)
        h.addWidget(lbl)
        h.addWidget(input_widget, 1)

        # Toggle input + label enabled state when checkbox changes
        def _toggle(enabled):
            input_widget.setEnabled(enabled)
            lbl.setEnabled(enabled)

        cb.stateChanged.connect(lambda s: _toggle(s == 2))
        return cell, cb

    @staticmethod
    def _qs_spin(default, mn, mx, step):
        w = QSpinBox()
        w.setRange(mn, mx)
        w.setSingleStep(step)
        w.setValue(default)
        return w

    @staticmethod
    def _qs_dspin(default, mn, mx, step):
        w = QDoubleSpinBox()
        w.setRange(mn, mx)
        w.setSingleStep(step)
        w.setDecimals(2)
        w.setValue(default)
        return w

    # ── BUILD UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(16, 12, 16, 12)
        root.setSpacing(10)

        root.addWidget(self._build_top_bar())

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet(f"color: {self._current_theme['border']};")
        root.addWidget(sep)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet(f"QSplitter::handle {{ background: {self._current_theme['border']}; }}")
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([420, 680])
        root.addWidget(splitter, 1)

        root.addWidget(self._build_cmd_bar())

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._set_status("Ready", "idle")

    def _build_top_bar(self):
        w = QWidget()
        layout = QHBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        title = QLabel("⚡ llama-server")
        title.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {self._current_theme['accent']}; font-family: monospace;")
        layout.addWidget(title)

        layout.addStretch()

        self.theme_btn = QPushButton("💡 Theme")
        self.theme_btn.setToolTip("Toggle Light/Dark Mode")
        self.theme_btn.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_btn)

        layout.addSpacing(10)

        exe_lbl = QLabel("Executable:")
        exe_lbl.setStyleSheet(f"color: {self._current_theme['text_dim']}; font-size: 12px;")
        layout.addWidget(exe_lbl)

        self.exe_edit = QLineEdit()
        self.exe_edit.setPlaceholderText("Path to llama-server or llama-server.exe …")
        self.exe_edit.setMinimumWidth(320)
        self.exe_edit.textChanged.connect(self._update_cmd_preview)
        layout.addWidget(self.exe_edit, 1)

        browse_exe = QPushButton("Browse")
        browse_exe.clicked.connect(self._browse_exe)
        layout.addWidget(browse_exe)

        detect_btn = QPushButton("Auto-detect")
        detect_btn.setToolTip("Search PATH for llama-server")
        detect_btn.clicked.connect(self._auto_detect_exe)
        layout.addWidget(detect_btn)

        return w

    def _build_left_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 6, 0)
        layout.setSpacing(8)

        search_row = QHBoxLayout()
        search_icon = QLabel("🔍")
        search_row.addWidget(search_icon)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search parameters…")
        self.search_edit.textChanged.connect(self._filter_params)
        search_row.addWidget(self.search_edit)
        clear_btn = QPushButton("✕")
        clear_btn.setFixedSize(28, 28)
        clear_btn.setStyleSheet(f"background: transparent; border: none; color: {self._current_theme['text_dim']}; font-size: 14px;")
        clear_btn.clicked.connect(lambda: self.search_edit.clear())
        search_row.addWidget(clear_btn)
        layout.addLayout(search_row)

        layout.addWidget(self._build_model_files_section())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_w = QWidget()
        self.params_layout = QVBoxLayout(scroll_w)
        self.params_layout.setContentsMargins(0, 0, 0, 0)
        self.params_layout.setSpacing(4)

        self._sections: dict[str, CollapsibleSection] = {}
        for category, params in PARAMS.items():
            section = CollapsibleSection(category)
            grid = QWidget()
            gl = QVBoxLayout(grid)
            gl.setContentsMargins(0, 0, 0, 0)
            gl.setSpacing(2)
            for flag, label, ptype, opts in params:
                row = ParamRow(flag, label, ptype, opts)
                row.enable_cb.stateChanged.connect(self._update_cmd_preview)
                if hasattr(row.input, "valueChanged"):
                    row.input.valueChanged.connect(self._update_cmd_preview)
                if hasattr(row.input, "currentTextChanged"):
                    row.input.currentTextChanged.connect(self._update_cmd_preview)
                if hasattr(row.input, "textChanged"):
                    row.input.textChanged.connect(self._update_cmd_preview)
                if hasattr(row.input, "stateChanged"):
                    row.input.stateChanged.connect(self._update_cmd_preview)
                gl.addWidget(row)
                self._param_rows.append(row)
            section.add_widget(grid)
            self._sections[category] = section
            self.params_layout.addWidget(section)

        self.params_layout.addStretch()
        scroll.setWidget(scroll_w)
        layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        exp_btn = QPushButton("Expand All")
        exp_btn.clicked.connect(lambda: self._set_all_sections(True))
        col_btn = QPushButton("Collapse All")
        col_btn.clicked.connect(lambda: self._set_all_sections(False))
        btn_row.addWidget(exp_btn)
        btn_row.addWidget(col_btn)
        layout.addLayout(btn_row)

        return w

    def _build_model_files_section(self):
        box = QGroupBox("MODEL FILES")
        layout = QVBoxLayout(box)
        layout.setSpacing(6)

        model_row = QHBoxLayout()
        model_lbl = QLabel("Model  *")
        model_lbl.setFixedWidth(100)
        model_lbl.setStyleSheet(f"color: {self._current_theme['accent2']}; font-size: 12px; font-weight: 600;")
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("Path to .gguf model file…")
        self.model_edit.textChanged.connect(self._update_cmd_preview)
        model_browse = QPushButton("…")
        model_browse.setObjectName("browse")
        model_browse.setFixedSize(32, 32)
        model_browse.clicked.connect(lambda: self._browse_file(self.model_edit, "GGUF Models (*.gguf);;All Files (*)"))
        model_row.addWidget(model_lbl)
        model_row.addWidget(self.model_edit, 1)
        model_row.addWidget(model_browse)
        layout.addLayout(model_row)

        self.mmproj_row = FilePickerRow("--mmproj", "mmproj", "GGUF Files (*.gguf);;All Files (*)")
        self.mmproj_row.path_edit.textChanged.connect(self._update_cmd_preview)
        self.mmproj_row.enable_cb.stateChanged.connect(self._update_cmd_preview)
        layout.addWidget(self.mmproj_row)

        self.draft_model_row = FilePickerRow("--model-draft", "Draft Model", "GGUF Files (*.gguf);;All Files (*)")
        self.draft_model_row.path_edit.textChanged.connect(self._update_cmd_preview)
        self.draft_model_row.enable_cb.stateChanged.connect(self._update_cmd_preview)
        layout.addWidget(self.draft_model_row)

        self.vocoder_row = FilePickerRow("--model-vocoder", "Vocoder", "GGUF Files (*.gguf);;All Files (*)")
        self.vocoder_row.path_edit.textChanged.connect(self._update_cmd_preview)
        self.vocoder_row.enable_cb.stateChanged.connect(self._update_cmd_preview)
        layout.addWidget(self.vocoder_row)

        self.lora_row = FilePickerRow("--lora", "LoRA Adapter", "All Files (*)")
        self.lora_row.path_edit.textChanged.connect(self._update_cmd_preview)
        self.lora_row.enable_cb.stateChanged.connect(self._update_cmd_preview)
        layout.addWidget(self.lora_row)

        log_row = QHBoxLayout()
        log_lbl = QLabel("Log File")
        log_lbl.setFixedWidth(100)
        log_lbl.setObjectName("paramLabel")
        self.log_file_cb = QCheckBox()
        self.log_file_cb.setFixedWidth(20)
        self.log_file_cb.stateChanged.connect(self._update_cmd_preview)
        self.log_file_edit = QLineEdit()
        self.log_file_edit.setPlaceholderText("Optional log file path…")
        self.log_file_edit.setEnabled(False)
        self.log_file_edit.textChanged.connect(self._update_cmd_preview)
        self.log_file_cb.stateChanged.connect(lambda s: self.log_file_edit.setEnabled(s == 2))
        log_row.addWidget(self.log_file_cb)
        log_row.addWidget(log_lbl)
        log_row.addWidget(self.log_file_edit, 1)
        layout.addLayout(log_row)

        return box

    def _build_right_panel(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(6, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._build_quick_settings())

        log_label = QLabel("SERVER LOG")
        log_label.setStyleSheet(f"color: {self._current_theme['text_dim']}; font-size: 11px; font-weight: 600; letter-spacing: 1px;")
        layout.addWidget(log_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        layout.addWidget(self.log_output, 1)

        log_ctrl = QHBoxLayout()
        clear_log = QPushButton("Clear Log")
        clear_log.clicked.connect(self.log_output.clear)
        save_log = QPushButton("Save Log…")
        save_log.clicked.connect(self._save_log)
        log_ctrl.addWidget(clear_log)
        log_ctrl.addWidget(save_log)
        log_ctrl.addStretch()
        layout.addLayout(log_ctrl)

        return w

    def _build_quick_settings(self):
        box = QGroupBox("QUICK SETTINGS")
        layout = QGridLayout(box)
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(6)

        # ── Row 0: Context, GPU Layers, Batch ─────────────────────────────────
        self.qs_ctx = self._qs_spin(4096, 0, 1048576, 512)
        c0, cb0 = self._make_qs_cell("Context", self.qs_ctx)
        self._qs_cbs["ctx"] = cb0
        layout.addWidget(c0, 0, 0, 1, 2)

        self.qs_gpu = self._qs_spin(99, 0, 999, 1)
        c1, cb1 = self._make_qs_cell("GPU Layers", self.qs_gpu)
        self._qs_cbs["gpu"] = cb1
        layout.addWidget(c1, 0, 2, 1, 2)

        self.qs_batch = self._qs_spin(2048, 1, 65536, 256)
        c2, cb2 = self._make_qs_cell("Batch", self.qs_batch)
        self._qs_cbs["batch"] = cb2
        layout.addWidget(c2, 0, 4, 1, 2)

        # ── Row 1: Threads, Parallel, Port ────────────────────────────────────
        self.qs_threads = self._qs_spin(-1, -1, 512, 1)
        c3, cb3 = self._make_qs_cell("Threads", self.qs_threads)
        self._qs_cbs["threads"] = cb3
        layout.addWidget(c3, 1, 0, 1, 2)

        self.qs_parallel = self._qs_spin(1, -1, 256, 1)
        c4, cb4 = self._make_qs_cell("Parallel", self.qs_parallel)
        self._qs_cbs["parallel"] = cb4
        layout.addWidget(c4, 1, 2, 1, 2)

        self.qs_port = self._qs_spin(8080, 1, 65535, 1)
        c5, cb5 = self._make_qs_cell("Port", self.qs_port)
        self._qs_cbs["port"] = cb5
        layout.addWidget(c5, 1, 4, 1, 2)

        # ── Row 2: Temperature, Top-P, Host ───────────────────────────────────
        self.qs_temp = self._qs_dspin(0.8, 0.0, 5.0, 0.05)
        c6, cb6 = self._make_qs_cell("Temp", self.qs_temp)
        self._qs_cbs["temp"] = cb6
        layout.addWidget(c6, 2, 0, 1, 2)

        self.qs_topp = self._qs_dspin(0.95, 0.0, 1.0, 0.01)
        c7, cb7 = self._make_qs_cell("Top-P", self.qs_topp)
        self._qs_cbs["topp"] = cb7
        layout.addWidget(c7, 2, 2, 1, 2)

        self.qs_host = QLineEdit("127.0.0.1")
        c8, cb8 = self._make_qs_cell("Host", self.qs_host)
        self._qs_cbs["host"] = cb8
        layout.addWidget(c8, 2, 4, 1, 2)

        # ── Row 3: Flash Attn, Cont Batch, KV Cache ───────────────────────────
        self.qs_fa = QComboBox()
        for x in ["auto", "on", "off"]:
            self.qs_fa.addItem(x)
        c9, cb9 = self._make_qs_cell("Flash Attn", self.qs_fa)
        self._qs_cbs["fa"] = cb9
        layout.addWidget(c9, 3, 0, 1, 2)

        self.qs_cb = QCheckBox()
        self.qs_cb.setChecked(True)
        c10, cb10 = self._make_qs_cell("Cont Batch", self.qs_cb)
        self._qs_cbs["cb"] = cb10
        layout.addWidget(c10, 3, 2, 1, 2)

        self.qs_kv = QComboBox()
        for x in ["f16", "q8_0", "q4_0", "f32", "bf16"]:
            self.qs_kv.addItem(x)
        c11, cb11 = self._make_qs_cell("KV Cache", self.qs_kv)
        self._qs_cbs["kv"] = cb11
        layout.addWidget(c11, 3, 4, 1, 2)

        # ── Connect all signals to command preview ────────────────────────────
        for w in [self.qs_ctx, self.qs_gpu, self.qs_batch, self.qs_threads,
                  self.qs_parallel, self.qs_port, self.qs_temp, self.qs_topp]:
            w.valueChanged.connect(self._update_cmd_preview)
        self.qs_host.textChanged.connect(self._update_cmd_preview)
        for w in [self.qs_fa, self.qs_kv]:
            w.currentTextChanged.connect(self._update_cmd_preview)
        self.qs_cb.stateChanged.connect(self._update_cmd_preview)
        for cb in self._qs_cbs.values():
            cb.stateChanged.connect(self._update_cmd_preview)

        # ── Row 4: Buttons ────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("▶  Launch Server")
        self.start_btn.setObjectName("primary")
        self.start_btn.clicked.connect(self._launch_server)
        self.stop_btn = QPushButton("■  Stop Server")
        self.stop_btn.setObjectName("danger")
        self.stop_btn.clicked.connect(self._stop_server)
        self.stop_btn.setEnabled(False)

        self.save_btn = QPushButton("💾 Save")
        self.save_btn.clicked.connect(self._save_settings)
        self.load_btn = QPushButton("📂 Load")
        self.load_btn.clicked.connect(self._load_settings_dialog)

        self.reset_btn = QPushButton("↺ Reset")
        self.reset_btn.setToolTip("Reset all settings to defaults")
        self.reset_btn.clicked.connect(self._reset_settings)

        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.load_btn)
        layout.addLayout(btn_row, 4, 0, 1, 6)

        return box

    def _build_cmd_bar(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        header = QHBoxLayout()
        cmd_lbl = QLabel("COMMAND PREVIEW")
        cmd_lbl.setStyleSheet(f"color: {self._current_theme['text_dim']}; font-size: 11px; font-weight: 600; letter-spacing: 1px;")
        header.addWidget(cmd_lbl)

        copy_btn = QPushButton("Copy")
        copy_btn.setFixedWidth(60)
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(self.cmd_preview.toPlainText()))
        header.addStretch()
        header.addWidget(copy_btn)
        layout.addLayout(header)

        self.cmd_preview = QTextEdit()
        self.cmd_preview.setReadOnly(True)
        self.cmd_preview.setMaximumHeight(100)
        self._refresh_cmd_style()
        layout.addWidget(self.cmd_preview)
        return w

    def _refresh_cmd_style(self):
        self.cmd_preview.setStyleSheet(f"""
            QTextEdit {{
                background: {self._current_theme['bg']}; color: {self._current_theme['accent2']};
                font-family: 'Cascadia Code', 'Fira Code', monospace;
                font-size: 12px; border: 1px solid {self._current_theme['border']}; border-radius: 4px;
                padding: 4px;
            }}
        """)

    # ── THEME LOGIC ───────────────────────────────────────────────────────────

    def _toggle_theme(self):
        if self._current_theme["name"] == "dark":
            self._current_theme = LIGHT
        else:
            self._current_theme = DARK
        self.setStyleSheet(get_qss(self._current_theme))
        self._refresh_cmd_style()
        self._save_settings()

    # ── PARAM SEARCH ──────────────────────────────────────────────────────────

    def _filter_params(self, query):
        if not query:
            for section in self._sections.values():
                section.setVisible(True)
                for i in range(section.content.layout().count()):
                    item = section.content.layout().itemAt(i)
                    if item and item.widget():
                        grid_widget = item.widget()
                        for j in range(grid_widget.layout().count()):
                            row_item = grid_widget.layout().itemAt(j)
                            if row_item and isinstance(row_item.widget(), ParamRow):
                                row_item.widget().setVisible(True)
            return

        q = query.lower()
        for cat, section in self._sections.items():
            any_visible = False
            for i in range(section.content.layout().count()):
                item = section.content.layout().itemAt(i)
                if item and item.widget():
                    grid_widget = item.widget()
                    for j in range(grid_widget.layout().count()):
                        row_item = grid_widget.layout().itemAt(j)
                        if row_item and isinstance(row_item.widget(), ParamRow):
                            row = row_item.widget()
                            visible = (q in row.flag.lower() or
                                       q in cat.lower() or
                                       q in row.opts.get("tip", "").lower())
                            row.setVisible(visible)
                            if visible:
                                any_visible = True
            section.setVisible(any_visible)
            if any_visible and not section._expanded:
                section.toggle_btn.setChecked(True)
                section._toggle(True)

    # ── COMMAND BUILDING ──────────────────────────────────────────────────────
    #
    # Uses an ordered dict so that later entries OVERRIDE earlier ones with the
    # same flag key.  Quick-settings are inserted first; advanced params are
    # inserted second and therefore win when the same flag appears in both.

    def _build_args(self):
        """Return (exe, structured_args) where structured_args is a list of
        (flag, value_or_None) tuples.  Use _flatten_args() to get a plain
        string list suitable for QProcess.start()."""

        args_map = {}  # flag_string -> value (None for flag-only)

        # Model
        model = self.model_edit.text().strip()
        if model:
            args_map["-m"] = model

        # ── Quick settings (only when their enable-checkbox is on) ────────────
        if self._qs_cbs["ctx"].isChecked():
            args_map["--ctx-size"] = str(self.qs_ctx.value())

        if self._qs_cbs["gpu"].isChecked():
            args_map["--n-gpu-layers"] = str(self.qs_gpu.value())

        if self._qs_cbs["batch"].isChecked():
            args_map["--batch-size"] = str(self.qs_batch.value())

        if self._qs_cbs["threads"].isChecked() and self.qs_threads.value() != -1:
            args_map["--threads"] = str(self.qs_threads.value())

        if self._qs_cbs["parallel"].isChecked() and self.qs_parallel.value() != -1:
            args_map["--parallel"] = str(self.qs_parallel.value())

        if self._qs_cbs["port"].isChecked():
            args_map["--port"] = str(self.qs_port.value())

        if self._qs_cbs["host"].isChecked():
            args_map["--host"] = self.qs_host.text().strip() or "127.0.0.1"

        if self._qs_cbs["temp"].isChecked():
            args_map["--temp"] = f"{self.qs_temp.value():.2f}"

        if self._qs_cbs["topp"].isChecked():
            args_map["--top-p"] = f"{self.qs_topp.value():.3f}"

        if self._qs_cbs["fa"].isChecked():
            args_map["--flash-attn"] = self.qs_fa.currentText()

        # Cont-batching: when QS enabled + inner checkbox unchecked → --no-cont-batching
        if self._qs_cbs["cb"].isChecked():
            if not self.qs_cb.isChecked():
                args_map["--cont-batching"] = _CONT_BATCHING_OFF
            # If inner is checked, default behaviour – don't add anything

        if self._qs_cbs["kv"].isChecked():
            kv_val = self.qs_kv.currentText()
            if kv_val != "f16":
                args_map["--cache-type-k"] = kv_val

        # ── File pickers ──────────────────────────────────────────────────────
        for row in [self.mmproj_row, self.draft_model_row, self.vocoder_row, self.lora_row]:
            fa = row.get_flag_args()
            if fa:
                args_map[fa[0]] = fa[1] if len(fa) > 1 else None

        # Log file
        if self.log_file_cb.isChecked() and self.log_file_edit.text().strip():
            args_map["--log-file"] = self.log_file_edit.text().strip()

        # ── Advanced params — these OVERRIDE any quick-setting with the same flag
        for row in self._param_rows:
            fa = row.get_flag_args()
            if fa:
                flag = fa[0]
                val = fa[1] if len(fa) > 1 else None
                args_map[flag] = val  # <-- override

        # ── Convert dict → list of (flag, value) tuples ───────────────────────
        structured = []
        for flag, val in args_map.items():
            if flag == "--cont-batching" and val is _CONT_BATCHING_OFF:
                structured.append(("--no-cont-batching", None))
            else:
                structured.append((flag, val))

        exe = self.exe_edit.text().strip()
        return exe, structured

    @staticmethod
    def _flatten_args(structured):
        """Convert [(flag, val), …] → [flag, val, flag, val, …] for QProcess."""
        flat = []
        for flag, val in structured:
            flat.append(flag)
            if val is not None:
                flat.append(str(val))
        return flat

    def _update_cmd_preview(self):
        exe, structured = self._build_args()
        exe_display = exe or "llama-server"

        lines = [exe_display]
        for flag, val in structured:
            if val is not None:
                lines.append(f"  {flag} {shlex.quote(str(val))}")
            else:
                lines.append(f"  {flag}")

        self.cmd_preview.setPlainText("\n".join(lines))

    # ── SERVER CONTROL ────────────────────────────────────────────────────────

    def _launch_server(self):
        exe, structured = self._build_args()
        args = self._flatten_args(structured)

        if not exe:
            QMessageBox.warning(self, "No Executable",
                                "Please select the llama-server executable first.")
            return
        if not Path(exe).exists():
            QMessageBox.warning(self, "Executable Not Found",
                                f"Cannot find:\n{exe}\n\nPlease check the path.")
            return

        model = self.model_edit.text().strip()
        if not model:
            reply = QMessageBox.question(self, "No Model Selected",
                                         "No model file selected. Launch anyway?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.No:
                return

        self._process = QProcess(self)
        self._process.readyReadStandardOutput.connect(self._on_stdout)
        self._process.readyReadStandardError.connect(self._on_stderr)
        self._process.finished.connect(self._on_process_finished)
        self._process.errorOccurred.connect(self._on_process_error)

        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._set_status(f"Starting server at {self.qs_host.text()}:{self.qs_port.value()}...", "idle")
        self._append_log(f"[Launcher] Starting: {exe} ...\n", self._current_theme['accent2'])

        self._process.start(exe, args)

    def _stop_server(self):
        if self._process and self._process.state() != QProcess.ProcessState.NotRunning:
            self._process.terminate()
            if not self._process.waitForFinished(3000):
                self._process.kill()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_status("Server stopped", "idle")
        self._append_log("[Launcher] Server stopped.\n", self._current_theme['danger'])

    def _on_stdout(self):
        data = self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self._append_log(data)

    def _on_stderr(self):
        data = self._process.readAllStandardError().data().decode("utf-8", errors="replace")
        self._append_log(data, "#ffd080")

    def _on_process_finished(self, code, status):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_status(f"Server exited (code {code})", "idle")
        self._append_log(f"[Launcher] Process finished with code {code}\n", self._current_theme['text_dim'])

    def _on_process_error(self, error):
        self._append_log(f"[Launcher] Process error: {error}\n", self._current_theme['danger'])
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_status("Error starting server", "error")

    def _append_log(self, text, color=None):
        cursor = self.log_output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        if color:
            fmt = QTextCharFormat()
            fmt.setForeground(QColor(color))
            cursor.setCharFormat(fmt)
        cursor.insertText(text)
        self.log_output.setTextCursor(cursor)
        self.log_output.ensureCursorVisible()

    # ── FILE BROWSING ─────────────────────────────────────────────────────────

    def _browse_exe(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select llama-server Executable", "",
                                              "Executables (*.exe llama-server llama-server.*);;All Files (*)")
        if path:
            self.exe_edit.setText(path)

    def _auto_detect_exe(self):
        import shutil
        for name in ["llama-server", "llama-server.exe", "server", "server.exe"]:
            found = shutil.which(name)
            if found:
                self.exe_edit.setText(found)
                self._set_status(f"Auto-detected: {found}", "idle")
                return
        self._set_status("llama-server not found in PATH", "error")
        QMessageBox.information(self, "Not Found",
                                "Could not auto-detect llama-server in PATH.\nPlease browse to its location manually.")

    def _browse_file(self, edit: QLineEdit, filt: str):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", filt)
        if path:
            edit.setText(path)

    # ── SETTINGS ─────────────────────────────────────────────────────────────

    def _save_settings(self):
        data = {
            "theme": self._current_theme["name"],
            "exe": self.exe_edit.text(),
            "model": self.model_edit.text(),
            # Quick-setting values
            "qs_ctx": self.qs_ctx.value(),
            "qs_gpu": self.qs_gpu.value(),
            "qs_batch": self.qs_batch.value(),
            "qs_threads": self.qs_threads.value(),
            "qs_parallel": self.qs_parallel.value(),
            "qs_port": self.qs_port.value(),
            "qs_host": self.qs_host.text(),
            "qs_temp": self.qs_temp.value(),
            "qs_topp": self.qs_topp.value(),
            "qs_fa": self.qs_fa.currentText(),
            "qs_cb": self.qs_cb.isChecked(),
            "qs_kv": self.qs_kv.currentText(),
            # Quick-setting enable checkboxes
            "qs_ctx_on": self._qs_cbs["ctx"].isChecked(),
            "qs_gpu_on": self._qs_cbs["gpu"].isChecked(),
            "qs_batch_on": self._qs_cbs["batch"].isChecked(),
            "qs_threads_on": self._qs_cbs["threads"].isChecked(),
            "qs_parallel_on": self._qs_cbs["parallel"].isChecked(),
            "qs_port_on": self._qs_cbs["port"].isChecked(),
            "qs_host_on": self._qs_cbs["host"].isChecked(),
            "qs_temp_on": self._qs_cbs["temp"].isChecked(),
            "qs_topp_on": self._qs_cbs["topp"].isChecked(),
            "qs_fa_on": self._qs_cbs["fa"].isChecked(),
            "qs_cb_on": self._qs_cbs["cb"].isChecked(),
            "qs_kv_on": self._qs_cbs["kv"].isChecked(),
        }
        try:
            with open(self._settings_path, "w") as f:
                json.dump(data, f, indent=2)
            self._set_status(f"Settings saved to {self._settings_path}", "idle")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _load_settings(self):
        if not self._settings_path.exists():
            return
        try:
            with open(self._settings_path) as f:
                data = json.load(f)

            if data.get("theme") == "light":
                self._current_theme = LIGHT
                self.setStyleSheet(get_qss(self._current_theme))
                self._refresh_cmd_style()

            self.exe_edit.setText(data.get("exe", ""))
            self.model_edit.setText(data.get("model", ""))

            # Quick-setting values
            self.qs_ctx.setValue(data.get("qs_ctx", 4096))
            self.qs_gpu.setValue(data.get("qs_gpu", 99))
            self.qs_batch.setValue(data.get("qs_batch", 2048))
            self.qs_threads.setValue(data.get("qs_threads", -1))
            self.qs_parallel.setValue(data.get("qs_parallel", 1))
            self.qs_port.setValue(data.get("qs_port", 8080))
            self.qs_host.setText(data.get("qs_host", "127.0.0.1"))
            self.qs_temp.setValue(data.get("qs_temp", 0.8))
            self.qs_topp.setValue(data.get("qs_topp", 0.95))
            idx = self.qs_fa.findText(data.get("qs_fa", "auto"))
            if idx >= 0:
                self.qs_fa.setCurrentIndex(idx)
            self.qs_cb.setChecked(data.get("qs_cb", True))
            idx = self.qs_kv.findText(data.get("qs_kv", "f16"))
            if idx >= 0:
                self.qs_kv.setCurrentIndex(idx)

            # Quick-setting enable checkboxes
            self._qs_cbs["ctx"].setChecked(data.get("qs_ctx_on", True))
            self._qs_cbs["gpu"].setChecked(data.get("qs_gpu_on", True))
            self._qs_cbs["batch"].setChecked(data.get("qs_batch_on", True))
            self._qs_cbs["threads"].setChecked(data.get("qs_threads_on", True))
            self._qs_cbs["parallel"].setChecked(data.get("qs_parallel_on", True))
            self._qs_cbs["port"].setChecked(data.get("qs_port_on", True))
            self._qs_cbs["host"].setChecked(data.get("qs_host_on", True))
            self._qs_cbs["temp"].setChecked(data.get("qs_temp_on", True))
            self._qs_cbs["topp"].setChecked(data.get("qs_topp_on", True))
            self._qs_cbs["fa"].setChecked(data.get("qs_fa_on", True))
            self._qs_cbs["cb"].setChecked(data.get("qs_cb_on", True))
            self._qs_cbs["kv"].setChecked(data.get("qs_kv_on", True))

        except Exception:
            pass

    def _load_settings_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Settings", "", "JSON Files (*.json)")
        if path:
            self._settings_path = Path(path)
            self._load_settings()

    def _reset_settings(self):
        self.model_edit.clear()
        self.exe_edit.clear()

        # Reset quick-setting values to defaults
        self.qs_ctx.setValue(4096)
        self.qs_gpu.setValue(99)
        self.qs_batch.setValue(2048)
        self.qs_threads.setValue(-1)
        self.qs_parallel.setValue(1)
        self.qs_port.setValue(8080)
        self.qs_host.setText("127.0.0.1")
        self.qs_temp.setValue(0.8)
        self.qs_topp.setValue(0.95)
        self.qs_fa.setCurrentIndex(0)
        self.qs_cb.setChecked(True)
        self.qs_kv.setCurrentIndex(0)

        # Re-enable all quick-setting checkboxes
        for cb in self._qs_cbs.values():
            cb.setChecked(True)

        # Reset file pickers
        for row in [self.mmproj_row, self.draft_model_row, self.vocoder_row, self.lora_row]:
            row.reset()

        # Reset advanced params
        for row in self._param_rows:
            row.reset()

        self._set_status("Settings reset to defaults", "idle")

    # ── MISC ──────────────────────────────────────────────────────────────────

    def _save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Log", "llama_server.log",
                                              "Log Files (*.log);;Text Files (*.txt);;All Files (*)")
        if path:
            with open(path, "w") as f:
                f.write(self.log_output.toPlainText())

    def _set_all_sections(self, expand: bool):
        for section in self._sections.values():
            if section._expanded != expand:
                section.toggle_btn.setChecked(expand)
                section._toggle(expand)

    def _set_status(self, msg, state="idle"):
        colors = {"idle": self._current_theme['text_dim'], "running": self._current_theme['accent2'],
                  "error": self._current_theme['danger']}
        self.statusBar().showMessage(msg)

    def closeEvent(self, event):
        self._stop_server()
        self._save_settings()
        event.accept()


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("llama-server Launcher")
    app.setOrganizationName("llama.cpp")

    QFontDatabase.addApplicationFont(":/fonts/JetBrainsMono.ttf")
    font = QFont("Segoe UI", 9)
    font.setHintingPreference(QFont.HintingPreference.PreferFullHinting)
    app.setFont(font)

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()