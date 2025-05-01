import streamlit as st
import cv2
import numpy as np
import urllib.request
import time

def run():
    st.title("Camera Streaming")

    ip_snapshot_url = st.text_input("IP Camera Snapshot URL", "https://68ae-2404-c0-9aa0-00-2331-24e8.ngrok-free.app/cam-hi.jpg")
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False

    # Custom style button agar teksnya putih
    button_style = """
        <style>
        div.stButton > button:first-child {
            color: white !important;
            background-color: #2E86C1;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
        }
        </style>
    """
    st.markdown(button_style, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])  # Tengahin tombol
    with col2:
        if not st.session_state.camera_active:
            if st.button("Start Snapshot Stream"):
                st.session_state.camera_active = True
                st.session_state.snapshot_url = ip_snapshot_url
        else:
            if st.button("Stop Snapshot Stream"):
                st.session_state.camera_active = False

    # Tengahin gambar
    if st.session_state.camera_active:
        outer_col1, outer_col2, outer_col3 = st.columns([1, 2, 1])
        with outer_col2:
            img_placeholder = st.empty()

            while st.session_state.camera_active:
                try:
                    resp = urllib.request.urlopen(st.session_state.snapshot_url)
                    img_array = np.asarray(bytearray(resp.read()), dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    img_placeholder.image(frame, channels="RGB", width=750)

                    time.sleep(0.1)
                except Exception as e:
                    st.error(f"Gagal mengambil gambar: {e}")
                    break

if __name__ == "__main__":
    run()
