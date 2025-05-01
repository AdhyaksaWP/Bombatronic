import streamlit as st
import requests

def run():
    st.title("🤖 Chatbot")

    # Tambahkan style untuk jawaban chatbot
    st.markdown("""
        <style>
        .chat-assistant {
            background-color: #f0f0f0;
            color: black;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .chat-user {
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # URL endpoint API LLM
    LLM_API_URL = "https://4c23-140-213-166-26.ngrok-free.app/api/llm"  # Ganti dengan alamat sesuai backend-mu

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Tanyakan sesuatu ke BombaBot...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        try:
            response = requests.post(
                LLM_API_URL,
                json={"input_text": user_input},
                timeout=10
            )
            if response.status_code == 200:
                result = response.json()
                bot_reply = result.get("answer", "Tidak ada jawaban dari server.")
                st.session_state.chat_history.append(("assistant", bot_reply))
            else:
                st.error(f"Gagal mendapatkan respons. Status: {response.status_code}")
        except Exception as e:
            st.error(f"Terjadi error: {e}")

    # Tampilkan riwayat chat
    for role, msg in st.session_state.chat_history:
        with st.chat_message(role):
            if role == "assistant":
                st.markdown(f'<div class="chat-assistant">{msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-user">{msg}</div>', unsafe_allow_html=True)
