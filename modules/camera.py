import streamlit as st
import cv2
import numpy as np

def run():
    # **1️⃣ Status Kamera & Deteksi Api**
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="text-align: center; background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd;">
                <h4>Camera Status:</h4>
                <h3 style="color: green;">On</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/1042/1042264.png" width="50">
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div style="text-align: center; background-color: white; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 10px #ddd;">
                <h4>Fire Detected:</h4>
                <h3 style="color: red;">False</h3>
                <img src="https://cdn-icons-png.flaticon.com/512/482/482895.png" width="50">
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # **2️⃣ Streaming Kamera**
    st.markdown("<h3 style='text-align: center;'>Live Camera</h3>", unsafe_allow_html=True)

    # **Gunakan session_state untuk menyimpan status kamera**
    if "camera_active" not in st.session_state:
        st.session_state.camera_active = False

    # **Tombol untuk mengaktifkan kamera**
    if not st.session_state.camera_active:
        if st.button("Start Camera", key="start_cam"):
            st.session_state.camera_active = True

    # **Tombol untuk menghentikan kamera**
    else:
        if st.button("Stop Camera", key="stop_cam"):
            st.session_state.camera_active = False

    # **Menampilkan stream jika kamera aktif**
    if st.session_state.camera_active:
        frame_placeholder = st.empty()
        cap = cv2.VideoCapture(0)

        while st.session_state.camera_active:
            ret, frame = cap.read()
            if not ret:
                st.error("Failed to capture frame.")
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame, channels="RGB", use_container_width=True)

        cap.release()

if __name__ == "__main__":
    run()
