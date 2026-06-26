import streamlit as st

def aplicar_estilo():

    st.markdown("""
    <style>

    .stApp{
        background: linear-gradient(180deg,#fffdfd,#fff7fb);
    }

    .main .block-container{
        max-width:1200px;
        padding-top:1rem;
    }

    h1{
        color:#b56b8b;
        font-weight:800;
        letter-spacing:0.5px;
    }

    h2,h3{
        color:#b56b8b;
    }

    p{
        color:#666666;
    }

    hr{
        border:none;
        border-top:1px solid #f3dce7;
    }

    div[data-testid="stMetric"]{
        background:white;
        border-radius:20px;
        padding:18px;
        border:1px solid #f4d7e3;
        box-shadow:0 8px 20px rgba(0,0,0,.04);
    }

    div[data-testid="stMetric"]:hover{
        transform:translateY(-2px);
        transition:.25s;
    }

    .stButton>button{
        border-radius:999px;
        border:1px solid #efbfd0;
        background:white;
        color:#b56b8b;
        font-weight:600;
        padding:.55rem 1.3rem;
    }

    .stButton>button:hover{
        background:#fdeef4;
        color:#a25378;
        border:1px solid #eaaac2;
    }

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stDateInput input,
    textarea{

        border-radius:16px !important;
        border:1px solid #efd2dd !important;

    }

    .stTabs [data-baseweb="tab"]{
        border-radius:999px;
        background:white;
        border:1px solid #efd2dd;
        margin-right:8px;
    }

    .stTabs [aria-selected="true"]{
        background:#fdeef4;
        color:#b56b8b;
    }

    .bloque{

        background:white;
        border-radius:24px;
        padding:28px;
        border:1px solid #f3d8e3;
        box-shadow:0 10px 30px rgba(0,0,0,.05);
        margin-bottom:18px;

    }

    </style>
    """, unsafe_allow_html=True)
