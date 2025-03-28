import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def run():
    # Konfigurasi halaman
    st.markdown("<h1 style='text-align: center;'>Hello, Welcome to Our Dashboard 👋</h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    # **1️⃣ Status & Threat Level**
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3><b>System Status:</b> <span style='color: green;'>On</span></h3>", unsafe_allow_html=True)

    with col2:
        st.markdown("<h3><b>Threat Level:</b> <span style='color: green;'>Safe</span></h3>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # **2️⃣ Grafik Monitoring**
    col1, col2 = st.columns(2)

    # Dummy data
    x = [1, 2, 3, 4, 5]
    y1 = [100, 200, 300, 400, 350]  # CO
    y2 = [50, 150, 250, 350, 450]  # CO2
    y3 = [33, 35, 37, 36, 39]  # Temperature
    y4 = [90, 70, 80, 100, 60]  # Humidity

    # Fungsi buat plot
    def plot_graph(title, x, y, color):
        fig, ax = plt.subplots()
        ax.plot(x, y, marker="o", linestyle="-", color=color)
        ax.set_title(title)
        ax.set_xlabel("Time")
        return fig

    with col1:
        st.pyplot(plot_graph("CO", x, y1, "blue"))
    with col2:
        st.pyplot(plot_graph("CO2", x, y2, "orange"))

    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(plot_graph("Temperature", x, y3, "green"))
    with col2:
        st.pyplot(plot_graph("Humidity", x, y4, "black"))

    st.markdown("<br>", unsafe_allow_html=True)

    # **3️⃣ Recent Readings (Tabel)**
    st.markdown("<h3>Recent Readings</h3>", unsafe_allow_html=True)

    # Dummy data tabel
    data = {
        "CO": [100, 100, 100],
        "CO2": [100, 100, 100],
        "Temperature": [38, 38, 38],
        "Humidity": [80, 80, 80],
        "Threat Level": ["Safe", "Safe", "Safe"]
    }
    df = pd.DataFrame(data)

    # Tampilkan tabel dengan styling
    st.dataframe(df.style.set_properties(**{
        "background-color": "#f9f9f9",
        "border": "1px solid #ddd",
        "color": "black"
    }))
# Menjalankan fungsi jika script ini dijalankan langsung
if __name__ == "__main__":
    run()
