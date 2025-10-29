import streamlit as st

st.set_page_config(page_title="Test", layout="wide")

st.title("测试页面")
st.write("如果你能看到这个，说明基本功能正常")

# 测试CSS
st.markdown("""
<style>
    .stApp {
        background: #FFF9E6;
    }
</style>
""", unsafe_allow_html=True)

st.success("CSS已加载")
