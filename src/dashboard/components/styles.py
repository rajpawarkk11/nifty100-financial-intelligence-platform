import streamlit as st

def load_css():

    st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html,body,[class*="css"]{
font-family:'Inter',sans-serif;
}

.stApp{

background:
radial-gradient(circle at top,#111827,#0b1220 55%,#070b13);

}

section[data-testid="stSidebar"]{

background:#08111F;

border-right:1px solid rgba(255,255,255,.08);

}

.block-container{

padding-top:1rem;

padding-left:2rem;

padding-right:2rem;

padding-bottom:1rem;

}

.metric-card{

background:rgba(18,24,38,.88);

border:1px solid rgba(255,255,255,.08);

border-radius:20px;

padding:22px;

transition:.25s;

backdrop-filter:blur(12px);

box-shadow:
0 10px 30px rgba(0,0,0,.35);

}

.metric-card:hover{

transform:translateY(-4px);

border:1px solid #7c3aed;

box-shadow:

0 18px 35px rgba(124,58,237,.35);

}

.metric-title{

font-size:14px;

color:#9CA3AF;

}

.metric-value{

font-size:36px;

font-weight:700;

color:white;

}

.section-title{

font-size:30px;

font-weight:700;

color:white;

margin-bottom:15px;

}
                .metric-top{

display:flex;

justify-content:space-between;

align-items:center;

}

.metric-icon{

width:60px;

height:60px;

border-radius:18px;

display:flex;

justify-content:center;

align-items:center;

font-size:28px;

color:white;

box-shadow:

0 10px 25px rgba(0,0,0,.35);

}
                .header-box{

padding:5px 0 15px 0;

}

.header-title{

font-size:38px;

font-weight:800;

background:linear-gradient(90deg,#A855F7,#60A5FA);

-webkit-background-clip:text;

-webkit-text-fill-color:transparent;

}

.header-subtitle{

font-size:16px;

color:#9CA3AF;

margin-top:8px;

}

.header-stat{

background:rgba(18,24,38,.90);

border:1px solid rgba(255,255,255,.08);

padding:18px;

border-radius:18px;

text-align:center;

box-shadow:0 8px 25px rgba(0,0,0,.30);

}

.stat-label{

font-size:12px;

color:#9CA3AF;

letter-spacing:1px;

}

.stat-value{

margin-top:8px;

font-size:22px;

font-weight:700;

color:white;

}

</style>
""",unsafe_allow_html=True)
    