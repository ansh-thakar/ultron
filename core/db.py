import streamlit as st
from sqlalchemy import create_engine, URL


@st.cache_resource
def get_engine():
    cfg = st.secrets["mysql"]
    url = URL.create(
        drivername="mysql+mysqlconnector",
        username=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=int(cfg["port"]),
        database=cfg["database"],
    )
    return create_engine(url, pool_pre_ping=True, pool_recycle=3600)