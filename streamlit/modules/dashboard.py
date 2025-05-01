import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from pymongo import MongoClient
from datetime import datetime

# Koneksi MongoDB
MONGO_URI = "mongodb+srv://symbiot:horehore@sensor.hh6drjg.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["sensor"]
collection = db["data_sensor"]

# Fungsi untuk mengambil data terbaru dari MongoDB

def get_latest_data(limit=10):
    cursor = collection.find().sort("_id", -1).limit(limit)
    df = pd.DataFrame(cursor)

    # Jika belum ada kolom 'timestamp', buat dari _id (ObjectId mengandung waktu)
    if "timestamp" not in df.columns:
        if "_id" in df.columns:
            df["timestamp"] = df["_id"].apply(lambda x: x.generation_time)
        else:
            df["timestamp"] = datetime.utcnow()

    # Ubah ke datetime dan urutkan
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    return df

# Fungsi untuk membuat grafik
def plot_graph(title, x, y, color):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', line=dict(color=color)))
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title=title)
    return fig

# Fungsi utama untuk menjalankan dashboard
def run():
    st.markdown("<h1 style='text-align: center;'>DASHBOARD BOMBATRONIC </h1>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    df = get_latest_data()

    latest_status = "0"
    if not df.empty and "status" in df.columns:
        latest_status = str(df["status"].iloc[-1])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3><b>System Status:</b> <span style='color: green;'>On</span></h3>", unsafe_allow_html=True)
    with col2:
        if latest_status == "1":
            fire_html = "<h3><b>Fire Detected:</b> <span style='color: red;'>On</span></h3>"
        else:
            fire_html = "<h3><b>Fire Detected:</b> <span style='color: green;'>Off</span></h3>"
        st.markdown(fire_html, unsafe_allow_html=True)

    # Tombol untuk refresh data
    if st.button("Refresh Data", key="refresh_button", help="Klik untuk refresh data", use_container_width=True):
        df = get_latest_data()

        if df.empty:
            st.warning("Belum ada data tersedia.")
        else:
            x = df['timestamp'].dt.strftime("%H:%M:%S") if 'timestamp' in df.columns else list(range(len(df)))
            y1 = df["MQ7"] if "MQ7" in df else [0]*len(x)
            y2 = df["MQ135"] if "MQ135" in df else [0]*len(x)
            y3 = df["Temp"] if "Temp" in df else [0]*len(x)
            y4 = df["Hum"] if "Hum" in df else [0]*len(x)

            col1, col2 = st.columns(2)
            col1.plotly_chart(plot_graph("CO (MQ7)", x, y1, "blue"), use_container_width=True)
            col2.plotly_chart(plot_graph("CO2 (MQ135)", x, y2, "orange"), use_container_width=True)

            col1, col2 = st.columns(2)
            col1.plotly_chart(plot_graph("Temperature", x, y3, "green"), use_container_width=True)
            col2.plotly_chart(plot_graph("Humidity", x, y4, "red"), use_container_width=True)

            st.markdown("<h3>Recent Readings</h3>", unsafe_allow_html=True)
            st.dataframe(df[["MQ7", "MQ135", "Temp", "Hum", "status", "timestamp"]])

# Styling untuk tombol Refresh
st.markdown("""
    <style>
    .stButton>button {
        background-color: red;
        color: white;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 5px;
        border: none;
        transition: background-color 0.3s;
    }

    .stButton>button:hover {
        background-color: darkred;
    }
    </style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    run()
