import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import math
import base64
import json
import os
import streamlit.components.v1 as components

# --- COMPONENT SETUP ---
parent_dir = os.path.dirname(os.path.abspath(__file__))
build_dir = os.path.join(parent_dir, "ghost_component")
_ghost_canvas = components.declare_component("ghost_canvas", path=build_dir)

# --- SAYFA YAPILANDIRMASI (Antigravity Theme) ---
st.set_page_config(page_title="GHOST GRID", page_icon="💠", layout="wide")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
        
        /* Global Reset */
        .stApp {
            background-color: #0d1117;
            background-image: radial-gradient(circle at 50% 50%, #1a1f26 0%, #0d1117 100%);
            color: #e6edf3;
            font-family: 'Inter', sans-serif;
        }

        /* Glassmorphism Sidebar */
        [data-testid="stSidebar"] {
            background: rgba(22, 27, 34, 0.7);
            backdrop-filter: blur(12px);
            border-right: 1px solid rgba(88, 166, 255, 0.2);
            padding: 2rem 1rem;
        }

        /* Tactical Headers */
        h1, h2, h3 {
            font-family: 'Orbitron', sans-serif !important;
            letter-spacing: 2px;
            color: #58a6ff;
            text-shadow: 0 0 10px rgba(88, 166, 255, 0.3);
        }

        /* Glass Cards */
        div.stButton > button {
            background: rgba(88, 166, 255, 0.1);
            color: #58a6ff;
            border: 1px solid rgba(88, 166, 255, 0.4);
            border-radius: 8px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.8rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            width: 100%;
            text-transform: uppercase;
        }
        div.stButton > button:hover {
            background: #58a6ff;
            color: #0d1117;
            box-shadow: 0 0 20px rgba(88, 166, 255, 0.6);
            border: 1px solid #58a6ff;
        }

        /* Input Styling */
        .stTextInput > div > div > input, .stSelectbox > div > div > div {
            background: rgba(13, 17, 23, 0.6) !important;
            border: 1px solid rgba(88, 166, 255, 0.2) !important;
            color: #e6edf3 !important;
            border-radius: 6px !important;
        }

        /* File Uploader Customization */
        [data-testid="stFileUploader"] {
            background: rgba(22, 27, 34, 0.5);
            border: 1px dashed rgba(88, 166, 255, 0.3);
            border-radius: 12px;
            padding: 1rem;
        }

        /* HUD Status Bar */
        .hud-bar {
            height: 2px;
            background: linear-gradient(90deg, transparent, #58a6ff, transparent);
            margin: 1rem 0;
            opacity: 0.5;
        }
                /* Workspace Centering Fix */
        .stCustomComponentV1 {
            display: flex;
            justify-content: center;
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

# --- CORE LOGIC ---
def smart_process(images, image_settings, pW_cm, pH_cm):
    # 1. DYNAMIC PAPER SETTINGS (300 DPI)
    DPI = 300
    PAPER_W = int((pW_cm / 2.54) * DPI)
    PAPER_H = int((pH_cm / 2.54) * DPI)
    
    paper = Image.new('RGB', (PAPER_W, PAPER_H), 'white')
    
    # 2. YERLEŞTİRME (FREEFORM)
    sorted_indices = sorted(range(len(images)), key=lambda i: image_settings.get(i, {}).get("layer", 0))
    for i in sorted_indices:
        uploaded_file = images[i]
        settings = image_settings.get(i, {"x": 0.5, "y": 0.5, "w": 0.3, "h": 0.3, "rotation": 0})
        
        img = Image.open(uploaded_file).convert("RGBA")
        img = ImageOps.exif_transpose(img)
        
        target_w = int(PAPER_W * settings["w"])
        target_h = int(PAPER_H * settings["h"])
        
        img_resized = img.resize((max(10, target_w), max(10, target_h)), Image.Resampling.LANCZOS)
        img_rotated = img_resized.rotate(settings.get("rotation", 0), expand=True, resample=Image.Resampling.BICUBIC)
        
        pos_x = int((PAPER_W * settings["x"]) - (img_rotated.width // 2))
        pos_y = int((PAPER_H * settings["y"]) - (img_rotated.height // 2))
        
        paper.paste(img_rotated, (pos_x, pos_y), img_rotated)
    return paper.convert("RGB")

# --- EXECUTION ---
# login_system() removed for immediate access

st.sidebar.subheader("📏 PAPER SIZE (cm)")
pW_cm = st.sidebar.slider("Width", 5, 200, 28)
pH_cm = st.sidebar.slider("Height", 5, 200, 28)

st.title("💠 GHOST GRID // COLLAGE")
files = st.file_uploader(" ", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

if files:
    img_bufs = []
    b64_images = []
    aspect_ratios = []
    for f in files:
        buf = io.BytesIO(f.read())
        img_bufs.append(buf)
        buf.seek(0)
        pimg = Image.open(buf)
        aspect_ratios.append(pimg.size[0] / pimg.size[1])
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode()
        b64_images.append(f"data:image/jpeg;base64,{encoded}")

    if "last_file_count" not in st.session_state or st.session_state.last_file_count != len(files):
        st.session_state.last_file_count = len(files)
        st.session_state.canvas_state = [
            {
                "x": 100 + (i % 3 * 180), 
                "y": 100 + (i // 3 * 180), 
                "w": 150, 
                "h": 150 / aspect_ratios[i], 
                "rot": 0, 
                "id": i, 
                "ratio": aspect_ratios[i]
            } 
            for i in range(len(files))
        ]

    st.markdown("<div class='hud-bar'></div>", unsafe_allow_html=True)
    st.markdown(f"### 🎨 {pW_cm}x{pH_cm}cm PRECISION WORKSPACE")
    st.info("💡 Her kare **1cm**'yi temsil eder. Resimleri **üste getirmek** için üzerlerine tıkla.")
    
    # Render Custom Component with Dynamic Paper Size
    new_state = _ghost_canvas(
        state=st.session_state.canvas_state, 
        images=b64_images, 
        paperWidth=pW_cm,
        paperHeight=pH_cm,
        key="ghost_canvas_v1"
    )
    st.markdown("<div class='hud-bar'></div>", unsafe_allow_html=True)
    
    if new_state is not None:
        st.session_state.canvas_state = new_state

    # Mapping logic: coordinates are relative to the interactive container size
    # which we now calculate based on the aspect ratio in the JS side (max 600px)
    max_px = 600
    if pW_cm >= pH_cm:
        container_w = max_px
        container_h = max_px * (pH_cm / pW_cm)
    else:
        container_h = max_px
        container_w = max_px * (pW_cm / pH_cm)

    image_settings = {}
    for i, s in enumerate(st.session_state.canvas_state):
        image_settings[s["id"]] = {
            "x": s["x"] / container_w,
            "y": s["y"] / container_h,
            "w": s["w"] / container_w,
            "h": s["h"] / container_h,
            "rotation": s.get("rot", 0),
            "layer": i 
        }

    with st.spinner("Synthesizing collage..."):
        st.sidebar.markdown("---")
        st.sidebar.subheader("⚙️ EXPORT SETTINGS")
        
        export_format = st.sidebar.selectbox(
            "Select Output Format",
            options=["JPEG", "TIFF", "PDF", "PNG", "WebP"],
            index=0,
            help="JPEG/PNG: Standart. TIFF: Kayıpsız Baskı. PDF: Matbaa belgesi. WebP: Yeni nesil yüksek sıkıştırma."
        )
        
        final_img = smart_process(files, image_settings, pW_cm, pH_cm)
        
        # Save based on format
        buf = io.BytesIO()
        mime_type = "image/jpeg"
        file_ext = "jpg"
        
        if export_format == "JPEG":
            final_img.save(buf, format="JPEG", quality=95, dpi=(300, 300))
        elif export_format == "TIFF":
            final_img.save(buf, format="TIFF", compression="tiff_adobe", dpi=(300, 300))
            mime_type = "image/tiff"
            file_ext = "tiff"
        elif export_format == "PDF":
            final_img.save(buf, format="PDF", resolution=300.0)
            mime_type = "application/pdf"
            file_ext = "pdf"
        elif export_format == "PNG":
            final_img.save(buf, format="PNG", dpi=(300, 300))
            mime_type = "image/png"
            file_ext = "png"
        elif export_format == "WebP":
            final_img.save(buf, format="WebP", quality=95, lossless=True)
            mime_type = "image/webp"
            file_ext = "webp"
        
        byte_im = buf.getvalue()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("💾 EXPORT PANEL")
        st.sidebar.download_button(
            label=f"⬇️ DOWNLOAD {pW_cm}x{pH_cm}cm {export_format}",
            data=byte_im,
            file_name=f"ghost_grid_{pW_cm}x{pH_cm}.{file_ext}",
            mime=mime_type,
            help=f"Baskı için yüksek çözünürlüklü {export_format} dosyasını indir."
        )
        

        st.image(byte_im, caption=f"High-Res Result Preview ({export_format})", use_container_width=True)
