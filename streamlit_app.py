import streamlit as st
from PIL import Image
import importlib

st.set_page_config(page_title="Bombatronic", page_icon="🔥", layout="wide")

logo = Image.open("assets/logo.png")

# Konfigurasi menu navigasi
menu = {
    "📊 Dashboard": "dashboard",
    "💬 Chatbot": "chatbot",
    "📷 Camera": "camera",
    "ℹ️ About": "about"
}

# Baca halaman dari query params
query_params = st.query_params
current_page = query_params.get("page", "dashboard")

def switch_page(page):
    st.query_params.update(page=page)
    st.rerun()  

with st.sidebar:
    st.image(logo, use_container_width=True)
    st.markdown("<h1 style='text-align: center; color: white; font-size: 30px;'>Bombatronic</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 12px; color: white;'>presented by SymbIoT</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
        <style>

            /* Warna background utama */
            body, [data-testid="stAppViewContainer"] {
                background-color: #ffffff;  /* Warna utama */
                color: black;  /* Warna teks */
            }

            /* Warna sidebar */
            [data-testid="stSidebar"] {
                background-color: #244475 !important;  /* Warna sidebar */
                color :white;
            }
            
            [data-testid="stSidebar"] image {
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
            } 
            
            /* Mengubah tampilan button navigasi di sidebar */
            [data-testid="stSidebar"] button {
                background-color: transparent !important;
                color: white !important;
                border: none !important;
                padding: 10px !important;
                font-weight: bold !important;
                text-align: left !important;
                width: 100% !important;
            }

            /* Hover effect */
            [data-testid="stSidebar"] button:hover {
                background-color: #1e3a5f !important; /* Warna hover */
            }

            /* Tombol aktif */
            [data-testid="stSidebar"] button:focus {
                background-color: #1b2e4b !important; /* Warna untuk tombol aktif */
            }

        </style>
    """, unsafe_allow_html=True)

    # Tampilkan menu sidebar dengan status aktif
    for label, page in menu.items():
        button_class = "active" if current_page == page else ""
        if st.button(label, key=page, use_container_width=True):
            switch_page(page)  # Navigasi langsung saat diklik

# Load halaman berdasarkan query params
try:
    module = importlib.import_module(f"modules.{current_page}")
    module.run()  # Jalankan fungsi `run()` di masing-masing file
except ModuleNotFoundError:
    st.error("Halaman tidak ditemukan!")
