import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, ArrowStyle
import shutil

OUTPUT_DIRS = [
    r"E:\Project\AUDIO-SIGN\isl-overlay-app\report_figures",
    r"C:\Users\rohan\.gemini\antigravity\brain\f5eee7a6-4d76-4570-b9d3-0c7e846b8169\report_figures"
]

def save_fig(fig, filename):
    for out_dir in OUTPUT_DIRS:
        os.makedirs(out_dir, exist_ok=True)
        dest = os.path.join(out_dir, filename)
        fig.savefig(dest, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Generated: {filename}")

# Set overall plot aesthetics
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

# ==========================================
# Figure 2.1: Project Gantt Chart
# ==========================================
def generate_fig_2_1():
    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')
    
    tasks = [
        "1. Problem Formulation & Feasibility Study",
        "2. WASAPI Loopback Audio Capture & VAD",
        "3. Real-Time Streaming ASR (Vosk & Whisper)",
        "4. ISL Syntactic NLP (SVO-to-SOV + NMM)",
        "5. SQLite Lexicon & Fingerspelling Engine",
        "6. 3D Avatar Reverse-Engineering (Hugo & Maya)",
        "7. Three.js Rigify Rig & SLERP Coarticulation",
        "8. Electron Glassmorphic Overlay UI",
        "9. System Integration & Pytest Verification",
        "10. Latency Benchmarking & Performance Tuning"
    ]
    
    start_weeks = [1, 2, 4, 5, 7, 6, 8, 9, 11, 12]
    duration_weeks = [3, 3, 4, 4, 3, 4, 4, 3, 3, 2]
    colors = ['#0284c7', '#0369a1', '#0d9488', '#059669', '#16a34a', '#6366f1', '#4f46e5', '#8b5cf6', '#d97706', '#dc2626']
    
    y_pos = np.arange(len(tasks))
    
    for i in range(len(tasks)):
        ax.barh(y_pos[i], duration_weeks[i], left=start_weeks[i], height=0.55, 
                color=colors[i], edgecolor='#1e293b', linewidth=0.8, alpha=0.9, zorder=3)
        ax.text(start_weeks[i] + duration_weeks[i] + 0.2, y_pos[i], f"W{start_weeks[i]}-W{start_weeks[i]+duration_weeks[i]}", 
                va='center', ha='left', fontsize=8.5, fontweight='bold', color='#334155')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(tasks, fontsize=9.5, fontweight='bold', color='#1e293b')
    ax.invert_yaxis()
    ax.set_xlabel("Project Timeline (Academic Calendar Weeks)", fontsize=10, fontweight='bold', color='#0f172a', labelpad=10)
    ax.set_xlim(0, 16)
    ax.set_xticks(np.arange(1, 16, 1))
    ax.set_xticklabels([f"W{w}" for w in range(1, 16)], fontsize=9, color='#475569')
    ax.grid(axis='x', linestyle='--', alpha=0.6, zorder=0)
    ax.set_title("Figure 2.1: Project Implementation Schedule & Milestone Gantt Chart", fontsize=12, fontweight='bold', color='#0f172a', pad=14)
    
    save_fig(fig, "fig_2_1_project_gantt.png")

# ==========================================
# Figure 3.1: WASAPI Loopback Capture Architecture
# ==========================================
def generate_fig_3_1():
    fig, ax = plt.subplots(figsize=(10.5, 5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axis('off')
    
    # Draw blocks
    def draw_box(x, y, w, h, title, subtitle, color, text_color='#ffffff'):
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08", 
                             facecolor=color, edgecolor='#0f172a', linewidth=1.2, zorder=3)
        ax.add_patch(box)
        ax.text(x + w/2, y + h*0.62, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color=text_color, zorder=4)
        ax.text(x + w/2, y + h*0.32, subtitle, ha='center', va='center', fontsize=8, color=text_color, zorder=4)

    def draw_arrow(x1, y1, x2, y2, label=""):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor='#0284c7', edgecolor='#0284c7', width=1.5, headwidth=7, headlength=7), zorder=5)
        if label:
            ax.text((x1+x2)/2, (y1+y2)/2 + 0.04, label, ha='center', va='bottom', fontsize=7.5, fontweight='bold', color='#0369a1')

    # Layer 1: OS & Hardware
    draw_box(0.05, 0.55, 0.22, 0.32, "Host Audio Driver", "Realtek / WASAPI Core Audio\nEndpoint Output Stream", '#1e293b')
    draw_arrow(0.27, 0.71, 0.35, 0.71, "Loopback Tap")
    
    # Layer 2: In-Memory Ring Buffer & Capture Engine
    draw_box(0.35, 0.55, 0.26, 0.32, "AudioCaptureEngine", "16 kHz Mono Float32 PCM\n100ms Chunks (1,600 samples)\nZero Disk I/O", '#0284c7')
    draw_arrow(0.61, 0.71, 0.70, 0.71, "100ms Frames")
    
    # Layer 3: VAD
    draw_box(0.70, 0.55, 0.25, 0.32, "Energy-Based VAD", "RMS Energy Calculation\nFloor Threshold: 0.003\nSpeech vs Silence Tagging", '#0d9488')
    
    # Lower Layer: Dual Path
    draw_arrow(0.82, 0.55, 0.82, 0.38, "")
    draw_box(0.68, 0.12, 0.28, 0.26, "Downstream ASR Stream", "Continuous Acoustic Feeding\nor 300ms Silence Commit", '#059669')

    draw_arrow(0.48, 0.55, 0.48, 0.38, "")
    draw_box(0.35, 0.12, 0.26, 0.26, "In-Memory Ring Buffer", "Circular Deque (Max 30 frames)\n3.0-Second Audio Retention", '#475569')

    ax.text(0.5, 0.96, "Figure 3.1: Windows Core Audio WASAPI Loopback Capture & VAD Architecture", 
            ha='center', va='center', fontsize=11, fontweight='bold', color='#0f172a')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig_3_1_wasapi_capture.png")

# ==========================================
# Figure 4.1: System Architecture Diagram
# ==========================================
def generate_fig_4_1():
    fig, ax = plt.subplots(figsize=(13, 7.5), facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')
    ax.axis('off')
    
    def box(x, y, w, h, title, items, color, border='#0f172a'):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.05",
                           facecolor=color, edgecolor=border, linewidth=1.2, zorder=3)
        ax.add_patch(p)
        ax.text(x + w/2, y + h - 0.04, title, ha='center', va='top', fontsize=9.5, fontweight='bold', color='#ffffff', zorder=4)
        for idx, item in enumerate(items):
            ax.text(x + 0.02, y + h - 0.08 - idx*0.038, f"• {item}", ha='left', va='top', fontsize=7.8, color='#f1f5f9', zorder=4)

    # Stages 1 to 5
    box(0.03, 0.52, 0.17, 0.38, "1. Audio Ingestion", 
        ["WASAPI Loopback", "16 kHz Mono PCM", "100ms Chunking", "In-Memory Buffer", "VAD (RMS > 0.003)"], '#0f172a')
    
    box(0.23, 0.52, 0.17, 0.38, "2. Streaming ASR", 
        ["Vosk Kaldi Streaming", "vosk-small-en-us", "LocalAgreement-2", "Faster-Whisper INT8", "300ms Micro-Pause"], '#0369a1')
    
    box(0.43, 0.52, 0.17, 0.38, "3. Syntactic NLP", 
        ["spaCy Dependency Tree", "SVO to SOV Order", "Topic-Comment Shift", "Lemmatization", "NMM Marker Tagging"], '#0d9488')
    
    box(0.63, 0.52, 0.17, 0.38, "4. Lexicon Sequencer", 
        ["SQLite Lexicon DB", "3D Bone Keyframes", "2D SVG Card Assets", "OOV Fingerspelling", "Interpreter Feedback"], '#059669')

    box(0.83, 0.52, 0.15, 0.38, "5. WebSocket IPC", 
        ["Async WebSockets", "Port 8765 Loopback", "Telemetry Dispatch", "Zero-Latency Stream", "JSON Action Packet"], '#4f46e5')

    # Presentation Tier
    p_box = FancyBboxPatch((0.15, 0.08), 0.72, 0.34, boxstyle="round,pad=0.03,rounding_size=0.06",
                           facecolor='#1e293b', edgecolor='#06b6d4', linewidth=1.8, zorder=2)
    ax.add_patch(p_box)
    ax.text(0.51, 0.39, "6. Presentation Layer (Electron Frameless Transparent Overlay)", 
            ha='center', va='center', fontsize=10.5, fontweight='bold', color='#38bdf8', zorder=4)

    # Submodules in UI
    def mini_box(x, y, w, h, title, desc, col):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.04", facecolor=col, edgecolor='#cbd5e1', linewidth=0.8, zorder=3)
        ax.add_patch(b)
        ax.text(x + w/2, y + h*0.65, title, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff', zorder=4)
        ax.text(x + w/2, y + h*0.3, desc, ha='center', va='center', fontsize=7.2, color='#cbd5e1', zorder=4)

    mini_box(0.18, 0.12, 0.19, 0.22, "Three.js 3D Engine", "Hugo / Maya glTF 2.0\nRigify 248 Bones\n60 Facial Blendshapes\nSLERP Coarticulation", '#0284c7')
    mini_box(0.41, 0.12, 0.19, 0.22, "2D Visual Cards", "Dynamic SVG Cards\nFingerspelling Ticker\nGloss Ribbon Badges", '#059669')
    mini_box(0.64, 0.12, 0.20, 0.22, "UX & Controls", "Always-On-Top\nClick-Through (Ctrl+Shift+T)\nSpeed / Theme / Opacity\nLatency Telemetry Display", '#7c3aed')

    # Connecting Arrows
    def arrow(x1, y1, x2, y2):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor='#0284c7', edgecolor='#0284c7', width=1.8, headwidth=7, headlength=7), zorder=5)

    arrow(0.20, 0.71, 0.23, 0.71)
    arrow(0.40, 0.71, 0.43, 0.71)
    arrow(0.60, 0.71, 0.63, 0.71)
    arrow(0.80, 0.71, 0.83, 0.71)
    
    # Downward arrow to presentation tier
    ax.annotate('', xy=(0.83, 0.42), xytext=(0.90, 0.52),
                arrowprops=dict(facecolor='#4f46e5', edgecolor='#4f46e5', width=1.8, headwidth=7, headlength=7), zorder=5)

    ax.text(0.5, 0.97, "Figure 4.1: End-to-End System Architecture of the Real-Time ISL Overlay Platform", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    save_fig(fig, "fig_4_1_system_architecture.png")

# ==========================================
# Figure 4.2: Data Flow Diagram (DFD Level 0 & 1)
# ==========================================
def generate_fig_4_2():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.5, 8.5), facecolor='#ffffff')
    for ax in (ax1, ax2):
        ax.set_facecolor('#ffffff')
        ax.axis('off')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    # --- DFD Level 0 (Context Diagram) ---
    ax1.text(0.5, 0.92, "DFD Level 0: Context Diagram", ha='center', va='center', fontsize=11, fontweight='bold', color='#0f172a')
    
    # Entities
    def entity(ax, x, y, w, h, text):
        b = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", facecolor='#f1f5f9', edgecolor='#1e293b', linewidth=1.5, zorder=3)
        ax.add_patch(b)
        ax.text(x + w/2, y + h/2, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#1e293b', zorder=4)

    # Process Circle
    def process_circle(ax, x, y, r, p_num, text):
        c = plt.Circle((x, y), r, facecolor='#0284c7', edgecolor='#0f172a', linewidth=1.5, zorder=3)
        ax.add_patch(c)
        ax.text(x, y + 0.04, f"[{p_num}]", ha='center', va='center', fontsize=8, fontweight='bold', color='#e0f2fe', zorder=4)
        ax.text(x, y - 0.03, text, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff', zorder=4)

    entity(ax1, 0.05, 0.35, 0.18, 0.25, "Operating System\nAudio Streamer\n(YouTube / Teams)")
    process_circle(ax1, 0.50, 0.47, 0.17, "0.0", "ISL Overlay\nSystem Platform")
    entity(ax1, 0.77, 0.52, 0.18, 0.25, "Deaf / Hard of\nHearing User")
    entity(ax1, 0.77, 0.12, 0.18, 0.25, "ISL Interpreter /\nLinguist")

    # Flow arrows
    def flow_arrow(ax, x1, y1, x2, y2, label, offset_y=0.04):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(facecolor='#0369a1', edgecolor='#0369a1', width=1.2, headwidth=6, headlength=6), zorder=5)
        ax.text((x1+x2)/2, (y1+y2)/2 + offset_y, label, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0284c7')

    flow_arrow(ax1, 0.23, 0.47, 0.33, 0.47, "16kHz Loopback PCM")
    flow_arrow(ax1, 0.67, 0.56, 0.77, 0.60, "3D Avatar & Cards")
    flow_arrow(ax1, 0.77, 0.28, 0.65, 0.38, "Missing Sign Flags", -0.04)

    # --- DFD Level 1 (Functional Decomposition) ---
    ax2.text(0.5, 0.95, "DFD Level 1: Functional Decomposition Pipeline", ha='center', va='center', fontsize=11, fontweight='bold', color='#0f172a')
    
    # Processes 1.0 to 4.0
    process_circle(ax2, 0.15, 0.55, 0.11, "1.0", "Capture &\nVAD Filter")
    process_circle(ax2, 0.38, 0.55, 0.11, "2.0", "Streaming\nASR Engine")
    process_circle(ax2, 0.61, 0.55, 0.11, "3.0", "SVO->SOV\nNLP Parser")
    process_circle(ax2, 0.85, 0.55, 0.11, "4.0", "Visual\nSequencer")

    # Data Store
    def datastore(ax, x, y, w, h, id_str, name_str):
        b = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", facecolor='#f8fafc', edgecolor='#0f172a', linewidth=1.2, zorder=3)
        ax.add_patch(b)
        ax.plot([x + 0.04, x + 0.04], [y, y + h], color='#0f172a', linewidth=1.2, zorder=4)
        ax.text(x + 0.02, y + h/2, id_str, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0f172a', zorder=5)
        ax.text(x + 0.05 + (w-0.05)/2, y + h/2, name_str, ha='center', va='center', fontsize=8, fontweight='bold', color='#0f172a', zorder=5)

    datastore(ax2, 0.50, 0.12, 0.22, 0.14, "D1", "sign_lexicon.db\n(Signs & Emojis)")
    datastore(ax2, 0.76, 0.12, 0.20, 0.14, "D2", "interpreter_feedback\n(Missing Signs)")

    # Arrows in Level 1
    flow_arrow(ax2, 0.26, 0.55, 0.27, 0.55, "100ms Chunks")
    flow_arrow(ax2, 0.49, 0.55, 0.50, 0.55, "Committed Text")
    flow_arrow(ax2, 0.72, 0.55, 0.74, 0.55, "ISL Glosses")
    
    # Store lookups
    flow_arrow(ax2, 0.85, 0.44, 0.72, 0.26, "Gloss Query / Keyframe", -0.04)
    flow_arrow(ax2, 0.85, 0.26, 0.85, 0.44, "Keyframe Data", 0.04)

    fig.suptitle("Figure 4.2: Data Flow Diagrams (Level 0 Context Diagram and Level 1 Functional Pipeline)", 
                 fontsize=12, fontweight='bold', color='#0f172a', y=0.99)
    save_fig(fig, "fig_4_2_data_flow_diagram.png")

# ==========================================
# Figure 4.3: UML Use Case Diagram
# ==========================================
def generate_fig_4_3():
    fig, ax = plt.subplots(figsize=(11, 7.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # System boundary box
    sys_box = FancyBboxPatch((0.24, 0.05), 0.52, 0.85, boxstyle="round,pad=0.02,rounding_size=0.04",
                             facecolor='#f8fafc', edgecolor='#0284c7', linewidth=1.8, zorder=2)
    ax.add_patch(sys_box)
    ax.text(0.50, 0.87, "ISL Real-Time 3D Desktop Overlay System", ha='center', va='center', fontsize=11, fontweight='bold', color='#0369a1', zorder=4)

    # Actor drawing helper
    def draw_actor(x, y, name):
        # Head
        c = plt.Circle((x, y + 0.04), 0.025, facecolor='#e2e8f0', edgecolor='#0f172a', linewidth=1.2, zorder=4)
        ax.add_patch(c)
        # Body
        ax.plot([x, x], [y + 0.015, y - 0.035], color='#0f172a', linewidth=1.5, zorder=4)
        # Arms
        ax.plot([x - 0.025, x + 0.025], [y - 0.005, y - 0.005], color='#0f172a', linewidth=1.5, zorder=4)
        # Legs
        ax.plot([x, x - 0.02], [y - 0.035, y - 0.075], color='#0f172a', linewidth=1.5, zorder=4)
        ax.plot([x, x + 0.02], [y - 0.035, y - 0.075], color='#0f172a', linewidth=1.5, zorder=4)
        # Name
        ax.text(x, y - 0.105, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#0f172a', zorder=4)

    draw_actor(0.10, 0.65, "Deaf / Hard-of-Hearing\n(DHH) User")
    draw_actor(0.10, 0.25, "System Audio Driver\n(WASAPI Loopback)")
    draw_actor(0.88, 0.65, "ISL Certified\nInterpreter")
    draw_actor(0.88, 0.25, "System\nAdministrator")

    # Use Cases (Ovals)
    use_cases = [
        ("UC-1: Capture OS Desktop Audio", 0.50, 0.77),
        ("UC-2: Real-Time Speech-to-Text Transcription", 0.50, 0.67),
        ("UC-3: Translate English to ISL SOV Syntax", 0.50, 0.57),
        ("UC-4: Render 3D Avatar Hugo/Maya Animations", 0.50, 0.47),
        ("UC-5: Display 2D Visual Sign Cards & Ticker", 0.50, 0.37),
        ("UC-6: Adjust Speed, Clothing Theme & Opacity", 0.50, 0.27),
        ("UC-7: Flag Missing Sign / Submit Feedback", 0.50, 0.17),
        ("UC-8: Review Logged Feedback & Update Lexicon", 0.50, 0.08)
    ]

    for label, cx, cy in use_cases:
        ellipse = patches.Ellipse((cx, cy), 0.44, 0.07, facecolor='#e0f2fe', edgecolor='#0284c7', linewidth=1.2, zorder=3)
        ax.add_patch(ellipse)
        ax.text(cx, cy, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#0369a1', zorder=4)

    # Actor Connections
    def connect(x1, y1, x2, y2, style='-'):
        ax.plot([x1, x2], [y1, y2], linestyle=style, color='#475569', linewidth=1.1, zorder=3)

    # DHH User connections
    connect(0.13, 0.65, 0.28, 0.47)
    connect(0.13, 0.65, 0.28, 0.37)
    connect(0.13, 0.65, 0.28, 0.27)
    connect(0.13, 0.65, 0.28, 0.17)

    # Audio Driver connections
    connect(0.13, 0.25, 0.28, 0.77)
    connect(0.13, 0.25, 0.28, 0.67)

    # Interpreter connections
    connect(0.85, 0.65, 0.72, 0.17)
    connect(0.85, 0.65, 0.72, 0.08)

    # Admin connections
    connect(0.85, 0.25, 0.72, 0.08)

    ax.text(0.5, 0.96, "Figure 4.3: UML Use Case Diagram of the ISL Overlay Application", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a')
    save_fig(fig, "fig_4_3_use_case_diagram.png")

# ==========================================
# Figure 4.4: UML Class Diagram
# ==========================================
def generate_fig_4_4():
    fig, ax = plt.subplots(figsize=(13.5, 8.5), facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def class_box(x, y, w, h, name, attrs, methods, header_col='#0284c7'):
        # Container
        b = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0", facecolor='#ffffff', edgecolor='#0f172a', linewidth=1.2, zorder=3)
        ax.add_patch(b)
        # Header
        h_h = 0.04
        hb = FancyBboxPatch((x, y + h - h_h), w, h_h, boxstyle="square,pad=0", facecolor=header_col, edgecolor='#0f172a', linewidth=1.2, zorder=4)
        ax.add_patch(hb)
        ax.text(x + w/2, y + h - h_h/2, name, ha='center', va='center', fontsize=8.5, fontweight='bold', color='#ffffff', zorder=5)

        # Dividing lines & text
        cur_y = y + h - h_h - 0.02
        for a in attrs:
            ax.text(x + 0.01, cur_y, f"- {a}", ha='left', va='center', fontsize=7, color='#334155', zorder=5)
            cur_y -= 0.022
        
        ax.plot([x, x + w], [cur_y + 0.01, cur_y + 0.01], color='#cbd5e1', linewidth=0.8, zorder=4)
        cur_y -= 0.012
        for m in methods:
            ax.text(x + 0.01, cur_y, f"+ {m}", ha='left', va='center', fontsize=7, color='#0f172a', zorder=5)
            cur_y -= 0.022

    # Backend Classes
    class_box(0.04, 0.56, 0.28, 0.38, "AudioCaptureEngine", 
              ["chunk_samples: int = 1600", "ring_buffer: deque(30)", "capture_source: str", "running: bool"],
              ["start() -> None", "stop() -> None", "calculate_rms() -> float", "is_speech() -> bool", "_start_soundcard_loopback()"], '#1e293b')

    class_box(0.36, 0.56, 0.28, 0.38, "ASRProcessor",
              ["active_engine: str", "vosk_recognizer: KaldiRecognizer", "whisper_model: WhisperModel", "audio_buffer: List[ndarray]"],
              ["ingest_chunk(chunk, is_speech)", "_ingest_vosk() -> Dict", "_evaluate_rolling_window()", "reset_state() -> None"], '#0369a1')

    class_box(0.68, 0.56, 0.28, 0.38, "ISLTranslator",
              ["nlp: spacy.Language", "IRREGULAR_LEMMAS: Dict", "ISL_STOPWORDS: Set", "WH_WORDS: Set"],
              ["translate(text: str) -> Dict", "detect_nmm(text) -> Tuple", "_translate_spacy(text) -> List", "lemmatize_token(t) -> str"], '#0d9488')

    class_box(0.04, 0.10, 0.28, 0.38, "DatabaseManager",
              ["db_path: Path", "conn: Connection"],
              ["init_db() -> None", "lookup_sign(gloss) -> Dict", "lookup_fingerspelling(char) -> Dict", "record_feedback(gloss, phrase)"], '#059669')

    class_box(0.36, 0.10, 0.28, 0.38, "PipelineOrchestrator",
              ["audio_engine: AudioCaptureEngine", "asr: ASRProcessor", "translator: ISLTranslator", "clients: Set[WebSocket]"],
              ["run_server() -> None", "process_and_broadcast()", "handle_message(ws, msg)", "_on_asr_commit(clause)"], '#4f46e5')

    class_box(0.68, 0.10, 0.28, 0.38, "AvatarEngine (Three.js)",
              ["scene: THREE.Scene", "mixer: AnimationMixer", "nodeMap: Dict[Bone]", "repousoQuaternions: Map", "activeNmm: Dict"],
              ["loadModel(char: str)", "playSequence(keyframe_track)", "applyNmmExpression()", "setSpeed(val)", "update(delta)"], '#7c3aed')

    ax.text(0.5, 0.97, "Figure 4.4: UML Class Diagram of the ISL Real-Time Overlay Architecture", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a')
    save_fig(fig, "fig_4_4_class_diagram.png")

# ==========================================
# Figure 4.5: UML Sequence Diagram
# ==========================================
def generate_fig_4_5():
    fig, ax = plt.subplots(figsize=(12, 7.5), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    lifelines = [
        ("Host Audio", 0.08),
        ("AudioEngine", 0.23),
        ("ASRProcessor", 0.40),
        ("ISLTranslator", 0.57),
        ("Sequencer / DB", 0.74),
        ("Avatar / UI", 0.90)
    ]

    for name, x in lifelines:
        b = FancyBboxPatch((x - 0.06, 0.88), 0.12, 0.05, boxstyle="square,pad=0", facecolor='#1e293b', edgecolor='#0f172a', linewidth=1, zorder=3)
        ax.add_patch(b)
        ax.text(x, 0.905, name, ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=4)
        ax.plot([x, x], [0.88, 0.06], linestyle='--', color='#94a3b8', linewidth=1, zorder=2)

    def seq_msg(y, x1, x2, label, col='#0284c7'):
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(facecolor=col, edgecolor=col, width=1.2, headwidth=6, headlength=6), zorder=5)
        ax.text((x1+x2)/2, y + 0.02, label, ha='center', va='bottom', fontsize=7.2, fontweight='bold', color=col)

    seq_msg(0.81, 0.08, 0.23, "1. 16kHz PCM Output")
    seq_msg(0.72, 0.23, 0.40, "2. 100ms Chunk (VAD Speech)")
    seq_msg(0.63, 0.40, 0.40, "3. Vosk AcceptWaveform()", '#475569')
    seq_msg(0.54, 0.40, 0.90, "4. Partial Subtitle Ticker ('the boy...')", '#d97706')
    seq_msg(0.45, 0.40, 0.57, "5. Commit Clause ('The boy is eating an apple')")
    seq_msg(0.36, 0.57, 0.74, "6. SVO->SOV Glosses ('[BOY, APPLE, EAT, PRESENT]')")
    seq_msg(0.27, 0.74, 0.74, "7. SQLite Lexicon Lookup", '#059669')
    seq_msg(0.18, 0.74, 0.90, "8. WebSocket IPC Payload (Keyframes + Cards)")
    seq_msg(0.09, 0.90, 0.90, "9. Three.js SLERP Coarticulation + Card Flash", '#7c3aed')

    ax.text(0.5, 0.97, "Figure 4.5: UML Sequence Diagram (System Audio Capture to 3D Avatar & Card Synthesis)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a')
    save_fig(fig, "fig_4_5_sequence_diagram.png")

# ==========================================
# Figure 5.1: Dependency Parsing & Syntactic Tree
# ==========================================
def generate_fig_5_1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5), facecolor='#ffffff')
    for ax in (ax1, ax2):
        ax.set_facecolor('#f8fafc')
        ax.axis('off')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    # English SVO Tree
    ax1.text(0.5, 0.92, "Input English Syntax (SVO Tree)", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1e293b')
    ax1.text(0.5, 0.82, '"The boy is eating an apple"', ha='center', va='center', fontsize=9.5, style='italic', color='#0369a1')

    def node(ax, x, y, label, sub, col='#0284c7'):
        b = FancyBboxPatch((x - 0.08, y - 0.04), 0.16, 0.08, boxstyle="round,pad=0.01,rounding_size=0.03", 
                           facecolor=col, edgecolor='#0f172a', linewidth=1, zorder=3)
        ax.add_patch(b)
        ax.text(x, y + 0.015, label, ha='center', va='center', fontsize=8, fontweight='bold', color='#ffffff', zorder=4)
        ax.text(x, y - 0.018, sub, ha='center', va='center', fontsize=6.8, color='#e0f2fe', zorder=4)

    def tree_link(ax, x1, y1, x2, y2, tag):
        ax.plot([x1, x2], [y1, y2], color='#64748b', linewidth=1.2, zorder=2)
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.02, tag, ha='center', va='center', fontsize=6.5, fontweight='bold', color='#334155')

    node(ax1, 0.50, 0.65, "ROOT: eat", "VERB (VBG)", '#0369a1')
    node(ax1, 0.20, 0.35, "boy", "nsubj (NOUN)", '#0284c7')
    node(ax1, 0.50, 0.35, "is", "aux (COP)", '#64748b')
    node(ax1, 0.80, 0.35, "apple", "dobj (NOUN)", '#0284c7')
    
    tree_link(ax1, 0.50, 0.61, 0.20, 0.39, "nsubj")
    tree_link(ax1, 0.50, 0.61, 0.50, 0.39, "aux")
    tree_link(ax1, 0.50, 0.61, 0.80, 0.39, "dobj")

    # Transformed ISL SOV Structure
    ax2.text(0.5, 0.92, "Transformed ISL Syntax (SOV + NMM)", ha='center', va='center', fontsize=10.5, fontweight='bold', color='#1e293b')
    ax2.text(0.5, 0.82, '["BOY", "APPLE", "EAT", "PRESENT"]', ha='center', va='center', fontsize=9.5, fontweight='bold', color='#059669')

    isl_tokens = [
        ("BOY", "Subject Gloss", 0.16, '#0284c7'),
        ("APPLE", "Object Gloss", 0.38, '#0284c7'),
        ("EAT", "Action Verb", 0.61, '#0d9488'),
        ("PRESENT", "Tense Marker", 0.84, '#059669')
    ]

    for tok, desc, x, c in isl_tokens:
        node(ax2, x, 0.55, tok, desc, c)

    # NMM Tagger Ribbon
    nmm_b = FancyBboxPatch((0.08, 0.20), 0.84, 0.18, boxstyle="round,pad=0.02,rounding_size=0.04", 
                           facecolor='#fef3c7', edgecolor='#d97706', linewidth=1.2, zorder=3)
    ax2.add_patch(nmm_b)
    ax2.text(0.50, 0.32, "Non-Manual Marker (NMM) Tagging", ha='center', va='center', fontsize=8.5, fontweight='bold', color='#b45309')
    ax2.text(0.50, 0.24, "Eyebrows: neutral | Head Tilt: 0.0 | Head Shake: False | Mouth: neutral", ha='center', va='center', fontsize=7.2, color='#78350f')

    fig.suptitle("Figure 5.1: spaCy Dependency Parsing & Syntactic Reordering (SVO to SOV + NMM)", 
                 fontsize=12, fontweight='bold', color='#0f172a', y=0.98)
    save_fig(fig, "fig_5_1_nlp_transformation_tree.png")

# ==========================================
# Figure 5.2: Rigify Skeletal Hierarchy
# ==========================================
def generate_fig_5_2():
    fig, ax = plt.subplots(figsize=(11.5, 6), facecolor='#ffffff')
    ax.set_facecolor('#ffffff')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    def rig_box(x, y, w, h, title, items, col):
        b = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.04", facecolor=col, edgecolor='#0f172a', linewidth=1, zorder=3)
        ax.add_patch(b)
        ax.text(x + w/2, y + h - 0.035, title, ha='center', va='top', fontsize=8.5, fontweight='bold', color='#ffffff', zorder=4)
        for i, it in enumerate(items):
            ax.text(x + 0.015, y + h - 0.07 - i*0.032, f"• {it}", ha='left', va='top', fontsize=7, color='#f8fafc', zorder=4)

    # Root & Spine
    rig_box(0.04, 0.48, 0.20, 0.42, "Torso & Spine (18)", 
            ["DEF-hips / ORG-hips", "DEF-spine / ORG-spine", "DEF-ribs / ORG-ribs", "DEF-neck / ORG-neck", "DEF-head / ORG-head"], '#1e293b')

    # Left & Right Arms
    rig_box(0.28, 0.48, 0.22, 0.42, "Arms & Shoulders (24)", 
            ["DEF-shoulderL / R", "DEF-upper_armL01 / 02", "DEF-forearmL01 / 02", "DEF-handL / R", "Kinematic ORG chains"], '#0369a1')

    # Finger Rig (Phalanges)
    rig_box(0.54, 0.48, 0.24, 0.42, "Dual Hands Rig (120)", 
            ["Thumb (01, 02, 03)", "Index (01, 02, 03)", "Middle (01, 02, 03)", "Ring (01, 02, 03)", "Pinky (01, 02, 03)"], '#0d9488')

    # Facial Blendshapes
    rig_box(0.81, 0.48, 0.16, 0.42, "Facial NMM (60)", 
            ["OLHO.PISCA.R/L", "SOBRANCELHA.SOBE", "SOBRANCELHA.DESCE", "BOCA.ABRE / BOCA.O", "LABIO.CANTO.SOBE"], '#7c3aed')

    # Lower Coarticulation & SLERP layer
    slerp_b = FancyBboxPatch((0.15, 0.10), 0.70, 0.28, boxstyle="round,pad=0.02,rounding_size=0.05", facecolor='#f1f5f9', edgecolor='#0284c7', linewidth=1.5, zorder=2)
    ax.add_patch(slerp_b)
    ax.text(0.50, 0.32, "Continuous Quaternion SLERP Coarticulation Engine", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0284c7')
    ax.text(0.50, 0.24, "q(t) = (sin((1-t)θ)/sin(θ)) * q1 + (sin(tθ)/sin(θ)) * q2", ha='center', va='center', fontsize=9, style='italic', color='#0f172a')
    ax.text(0.50, 0.16, "Smooth 200ms boundary blending between consecutive signs with zero resting-pose snapping", ha='center', va='center', fontsize=7.5, color='#475569')

    ax.text(0.5, 0.96, "Figure 5.2: Three.js Rigify Skeletal Joint Hierarchy (248 Bones & 60 Facial Blendshapes)", 
            ha='center', va='center', fontsize=12, fontweight='bold', color='#0f172a')
    save_fig(fig, "fig_5_2_rigify_skeletal_hierarchy.png")

# ==========================================
# Figure 6.2: Dual-Mode Rendering Comparison
# ==========================================
def generate_fig_6_2():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(13, 5), facecolor='#ffffff')
    for ax in (ax1, ax2, ax3):
        ax.set_facecolor('#0f172a')
        ax.axis('off')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

    # 1. 3D Avatar Mode
    ax1.text(0.5, 0.92, "Mode A: 3D Avatar View", ha='center', va='center', fontsize=10, fontweight='bold', color='#38bdf8')
    p1 = FancyBboxPatch((0.15, 0.22), 0.70, 0.60, boxstyle="round,pad=0.02", facecolor='#1e293b', edgecolor='#06b6d4', linewidth=1.5)
    ax1.add_patch(p1)
    ax1.text(0.5, 0.58, "[3D Mesh Rig]\nHugo / Maya Avatar", ha='center', va='center', fontsize=12, fontweight='bold', color='#ffffff')
    ax1.text(0.5, 0.35, "Full Skeletal Motion\nRigify 248 Joints\n60 Blendshapes", ha='center', va='center', fontsize=7.8, color='#94a3b8')
    ax1.text(0.5, 0.10, "Expressive signing for fluent users", ha='center', va='center', fontsize=7.2, color='#cbd5e1')

    # 2. 2D Cards Mode
    ax2.text(0.5, 0.92, "Mode B: 2D Visual Cards", ha='center', va='center', fontsize=10, fontweight='bold', color='#38bdf8')
    p2 = FancyBboxPatch((0.15, 0.22), 0.70, 0.60, boxstyle="round,pad=0.02", facecolor='#1e293b', edgecolor='#10b981', linewidth=1.5)
    ax2.add_patch(p2)
    ax2.text(0.5, 0.60, "[SIGN CARD]\nAPPLE", ha='center', va='center', fontsize=13, fontweight='bold', color='#34d399')
    ax2.text(0.5, 0.35, "Visual Flashcard\n+ Gloss Ticker\nSVG Assets", ha='center', va='center', fontsize=7.8, color='#94a3b8')
    ax2.text(0.5, 0.10, "Zero 3D GPU load / low-end devices", ha='center', va='center', fontsize=7.2, color='#cbd5e1')

    # 3. Hybrid Mode
    ax3.text(0.5, 0.92, "Mode C: Hybrid Overlay (Default)", ha='center', va='center', fontsize=10, fontweight='bold', color='#38bdf8')
    p3 = FancyBboxPatch((0.15, 0.22), 0.70, 0.60, boxstyle="round,pad=0.02", facecolor='#1e293b', edgecolor='#818cf8', linewidth=1.5)
    ax3.add_patch(p3)
    ax3.text(0.35, 0.55, "[3D Rig]\nHugo", ha='center', va='center', fontsize=10, fontweight='bold', color='#ffffff')
    ax3.text(0.68, 0.55, "[CARD]\nAPPLE", ha='center', va='center', fontsize=10, fontweight='bold', color='#818cf8')
    ax3.text(0.5, 0.32, "Simultaneous 3D Signing\n& Synchronized 2D Cards", ha='center', va='center', fontsize=7.8, color='#94a3b8')
    ax3.text(0.5, 0.10, "Maximum accessibility & comprehension", ha='center', va='center', fontsize=7.2, color='#cbd5e1')

    fig.suptitle("Figure 6.2: Dual-Mode Rendering Comparison (3D Avatar vs 2D Cards vs Hybrid Mode)", 
                 fontsize=12, fontweight='bold', color='#0f172a', y=0.98)
    save_fig(fig, "fig_6_2_dual_mode_comparison.png")

# ==========================================
# Figure 6.3: Fingerspelling Decomposition
# ==========================================
def generate_fig_6_3():
    fig, ax = plt.subplots(figsize=(11, 4.5), facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')
    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Input OOV Word
    in_box = FancyBboxPatch((0.05, 0.35), 0.22, 0.35, boxstyle="round,pad=0.02", facecolor='#ef4444', edgecolor='#0f172a', linewidth=1.2)
    ax.add_patch(in_box)
    ax.text(0.16, 0.56, "Out-Of-Vocabulary", ha='center', va='center', fontsize=8, fontweight='bold', color='#fef2f2')
    ax.text(0.16, 0.47, '"VIT"', ha='center', va='center', fontsize=15, fontweight='bold', color='#ffffff')
    ax.text(0.16, 0.39, "Proper Noun / Acronym", ha='center', va='center', fontsize=7, color='#fee2e2')

    # Arrow
    ax.annotate('', xy=(0.35, 0.52), xytext=(0.28, 0.52),
                arrowprops=dict(facecolor='#0284c7', edgecolor='#0284c7', width=1.5, headwidth=7, headlength=7))
    ax.text(0.315, 0.56, "Decompose", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#0284c7')

    # Decomposed Letters
    letters = [
        ("V", "fingerspelling_v.svg", 0.38),
        ("I", "fingerspelling_i.svg", 0.58),
        ("T", "fingerspelling_t.svg", 0.78)
    ]

    for char, svg, x in letters:
        b = FancyBboxPatch((x, 0.30), 0.16, 0.45, boxstyle="round,pad=0.02", facecolor='#1e293b', edgecolor='#38bdf8', linewidth=1.2)
        ax.add_patch(b)
        ax.text(x + 0.08, 0.60, "[HAND SHAPE]", ha='center', va='center', fontsize=7.5, color='#94a3b8')
        ax.text(x + 0.08, 0.48, f"Letter '{char}'", ha='center', va='center', fontsize=11, fontweight='bold', color='#38bdf8')
        ax.text(x + 0.08, 0.38, "Two-Handed ISL", ha='center', va='center', fontsize=7.2, color='#cbd5e1')

    # Connectors
    ax.plot([0.54, 0.58], [0.52, 0.52], color='#0284c7', linewidth=1.5)
    ax.plot([0.74, 0.78], [0.52, 0.52], color='#0284c7', linewidth=1.5)

    ax.text(0.5, 0.92, "Figure 6.3: Two-Handed Fingerspelling Fallback Pipeline for Out-Of-Vocabulary (OOV) Terms", 
            ha='center', va='center', fontsize=11.5, fontweight='bold', color='#0f172a')
    save_fig(fig, "fig_6_3_fingerspelling_pipeline.png")

# ==========================================
# Figure 7.1: Pipeline Latency Breakdown Benchmark
# ==========================================
def generate_fig_7_1():
    fig, ax = plt.subplots(figsize=(10.5, 5), facecolor='#ffffff')
    ax.set_facecolor('#f8fafc')
    
    stages = [
        "Audio Loopback\nCapture (<200ms)",
        "Streaming ASR\nEvaluation (Vosk)",
        "spaCy SOV + NMM\nTranslation (<15ms)",
        "Lexicon Resolution\n& Keyframing",
        "Three.js Avatar\nCoarticulation (60fps)"
    ]
    
    # Measured latency benchmarks in ms
    latencies = [100.0, 18.5, 4.02, 1.25, 16.6]
    target_limits = [200.0, 300.0, 15.0, 20.0, 33.3]
    
    x = np.arange(len(stages))
    width = 0.38

    b1 = ax.bar(x - width/2, latencies, width, label='Measured Benchmark (ms)', color='#0284c7', edgecolor='#0f172a', linewidth=0.8, zorder=3)
    b2 = ax.bar(x + width/2, target_limits, width, label='Maximum Target Limit (ms)', color='#cbd5e1', edgecolor='#64748b', linewidth=0.8, zorder=3)

    for rect in b1:
        h = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., h + 3, f"{h:.1f} ms", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#0369a1')

    ax.set_ylabel("Latency (milliseconds)", fontsize=10, fontweight='bold', color='#0f172a')
    ax.set_xticks(x)
    ax.set_xticklabels(stages, fontsize=8.5, fontweight='bold', color='#334155')
    ax.set_ylim(0, 340)
    ax.grid(axis='y', linestyle='--', alpha=0.6, zorder=0)
    ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#cbd5e1', fontsize=9)
    ax.set_title("Figure 7.1: Pipeline Latency Breakdown Benchmark Across Processing Stages", fontsize=11.5, fontweight='bold', color='#0f172a', pad=12)

    save_fig(fig, "fig_7_1_latency_benchmark.png")

# ==========================================
# Figure 7.2: Comparative ASR Performance
# ==========================================
def generate_fig_7_2():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.8), facecolor='#ffffff')
    for ax in (ax1, ax2):
        ax.set_facecolor('#f8fafc')
        ax.grid(axis='y', linestyle='--', alpha=0.6, zorder=0)

    engines = ['Vosk Kaldi\n(vosk-small-en-us)', 'Faster-Whisper\n(tiny.en INT8)']
    latency_ms = [18.5, 142.0]
    ram_mb = [148.0, 480.0]

    b1 = ax1.bar(engines, latency_ms, color=['#0284c7', '#64748b'], width=0.45, edgecolor='#0f172a', linewidth=0.8, zorder=3)
    ax1.set_ylabel("Step Evaluation Latency (ms)", fontsize=9.5, fontweight='bold', color='#0f172a')
    ax1.set_title("Streaming Step Evaluation Latency", fontsize=10, fontweight='bold', color='#0f172a')
    ax1.set_ylim(0, 180)
    for rect in b1:
        h = rect.get_height()
        ax1.text(rect.get_x() + rect.get_width()/2., h + 3, f"{h:.1f} ms", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#0f172a')

    b2 = ax2.bar(engines, ram_mb, color=['#0d9488', '#94a3b8'], width=0.45, edgecolor='#0f172a', linewidth=0.8, zorder=3)
    ax2.set_ylabel("Memory Footprint (MB RAM)", fontsize=9.5, fontweight='bold', color='#0f172a')
    ax2.set_title("Process Memory Footprint", fontsize=10, fontweight='bold', color='#0f172a')
    ax2.set_ylim(0, 600)
    for rect in b2:
        h = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width()/2., h + 10, f"{h:.0f} MB", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#0f172a')

    fig.suptitle("Figure 7.2: Comparative Streaming Performance (Vosk Kaldi vs Faster-Whisper INT8)", 
                 fontsize=11.5, fontweight='bold', color='#0f172a', y=0.98)
    save_fig(fig, "fig_7_2_asr_comparison.png")

if __name__ == '__main__':
    print("Generating comprehensive technical report diagrams...")
    generate_fig_2_1()
    generate_fig_3_1()
    generate_fig_4_1()
    generate_fig_4_2()
    generate_fig_4_3()
    generate_fig_4_4()
    generate_fig_4_5()
    generate_fig_5_1()
    generate_fig_5_2()
    generate_fig_6_2()
    generate_fig_6_3()
    generate_fig_7_1()
    generate_fig_7_2()
    print("All report figures successfully generated and saved!")
