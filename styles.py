import streamlit as st

def aplicar_estilo():
    st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;700&family=Poppins:wght@300;400;500;600&display=swap');

html, body, [class*="css"]{
    font-family:'Poppins',sans-serif;
}

.stApp{
    background:linear-gradient(135deg,#FFF8F7,#FDF8F2,#F5FBFA);
}

.main .block-container{
    max-width:1350px;
    padding-top:2rem;
}

h1,h2,h3{
    font-family:'Cormorant Garamond',serif !important;
    color:#b56b8b;
}

.stTabs [data-baseweb="tab"]{
    border-radius:999px;
    background:white;
    border:1px solid #ead5dd;
    padding:10px 22px;
}

.stTabs [aria-selected="true"]{
    background:#fbeef4;
    color:#b56b8b;
}

div[data-testid="stMetric"]{
    background:white;
    border-radius:22px;
    border:1px solid #efd9e2;
    box-shadow:0 10px 25px rgba(0,0,0,.05);
    padding:20px;
}

.stButton>button{
    border-radius:999px;
    background:white;
    border:1px solid #e6c6d4;
    color:#b56b8b;
    font-weight:600;
}

.stButton>button:hover{
    background:#fdeef4;
}

.stTextInput input,
textarea,
.stSelectbox div[data-baseweb="select"]{
    border-radius:16px !important;
    border:1px solid #edd4dd !important;
}

</style>
""", unsafe_allow_html=True)