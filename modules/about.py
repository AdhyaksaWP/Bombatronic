import streamlit as st

# Konfigurasi halaman

def run():
    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        st.image("assets/logo2.png", use_container_width=False, width=250)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style='text-align: center; font-size: 20px;'>
            Bombatronic is a product by SymbIoT team consisted of four highly ambitious individuals passionate about technology, IoT, and AI. 
            Driven by innovation, they aim to reduce fire-related tragedies across Indonesia by developing a cost-efficient 
            IoT prototype that is both accessible and widely applicable for all. 
            <br><br>
            All of this research was possible because of the IoT and AI bootcamp named <b>“Samsung Innovation Campus”</b> provided by Samsung and Hacktiv8.
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    # **2️⃣ Tech Stacks**
    st.markdown("<h3 style='text-align: center; font-size: 40px;'>Tech Stacks :</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1.5, 1, 0.5])

    with col1:
        st.image("assets/flask.png", width=200)

    with col2:
        st.image("assets/opencv.png", width=100)

    with col3:
        st.image("assets/streamlit.png", width=200)

    with col4:
        st.image("assets/tensorflow.png", width=100)

    with col5:
        st.image("assets/mongodb.png", width=100)

if __name__ == "__main__":
    run()
