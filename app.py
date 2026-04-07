import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
from anastruct import SystemElements
import streamlit.components.v1 as components
import json

# ============================================================
# PAGINA
# ============================================================
st.set_page_config(
    page_title="BeamFlow",
    layout="wide", page_icon="BF", initial_sidebar_state="expanded"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
header {visibility: hidden;} footer {visibility: hidden;}
.stApp { background-color: #f5f7fa; }
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e1e4e8; }
[data-testid="stSidebar"] * { color: #1a202c !important; }
h1 { color: #1a202c; border-bottom: none; font-weight: 700; font-size: 1.8rem; padding-bottom: 0px; }
h2, h3 { color: #2d3748; font-weight: 600; }
h4 { color: #4a5568; font-weight: 600; font-size: 1.1rem; margin-top: 10px; }
.stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div { background-color: #ffffff !important; border: 1px solid #cbd5e0 !important; border-radius: 6px !important; color: #1a202c !important; box-shadow: none !important; }
.stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus { border-color: #3182ce !important; box-shadow: 0 0 0 1px #3182ce !important; }
button[kind="primary"] { background-color: #3182ce !important; color: white !important; border-radius: 6px !important; border: none !important; font-weight: 600 !important; padding: 0.6rem 1rem !important; transition: background-color 0.2s ease; }
button[kind="primary"]:hover { background-color: #2b6cb0 !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] { background-color: transparent !important; border-radius: 6px !important; padding: 8px 16px !important; font-weight: 500 !important; border: 1px solid transparent !important; }
.stTabs [aria-selected="true"] { background-color: #ffffff !important; color: #3182ce !important; border: 1px solid #e2e8f0 !important; box-shadow: 0 -2px 0 0 #3182ce inset !important; }
div[data-testid="stMetric"] { background: #ffffff; border-radius: 8px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
div[data-testid="stForm"] { border-radius: 8px; border: 1px solid #e2e8f0; background-color: #ffffff; }
</style>
""", unsafe_allow_html=True)
st.markdown("<div style='text-align:right;color:#999;font-size:14px;'>Stud. Pop Rare┼ƒ Darius | BeamFlow v2.0</div>", unsafe_allow_html=True)

# ============================================================
# UTILITARE
# ============================================================
def to_sci(val):
    if val==0: return "0"
    exp=int(np.floor(np.log10(abs(val))))
    coef=val/(10**exp)
    return rf"{coef:.3f} \cdot 10^{{{exp}}}"

def draw_pin(ax,x,y,size=0.25,color='k'):
    pts=np.array([[x,y],[x-size,y-size*1.5],[x+size,y-size*1.5]])
    ax.add_patch(plt.Polygon(pts,closed=True,fc='#ffffcc',ec=color,lw=1.8,zorder=5))
    ax.plot([x-size*1.6,x+size*1.6],[y-size*1.5,y-size*1.5],color=color,lw=1.8,zorder=5)
    for xx in np.linspace(x-size*1.4,x+size*1.4,8):
        ax.plot([xx,xx-size*0.35],[y-size*1.5,y-size*2.1],color=color,lw=1,zorder=4)

def draw_roller(ax,x,y,size=0.25,color='k'):
    pts=np.array([[x,y],[x-size,y-size*1.5],[x+size,y-size*1.5]])
    ax.add_patch(plt.Polygon(pts,closed=True,fc='#ffffcc',ec=color,lw=1.8,zorder=5))
    ax.add_patch(plt.Circle((x,y-size*1.5-size*0.7),size*0.65,fc='white',ec=color,lw=1.8,zorder=5))
    ax.plot([x-size*1.6,x+size*1.6],[y-size*1.5-size*1.4,y-size*1.5-size*1.4],color=color,lw=1.5,zorder=5)

def draw_fixed_bottom(ax,x,y,c_ang=1.0,s_ang=0.0,size=0.35,color='k'):
    # Wall line perpendicular to bar direction
    px,py=-s_ang,c_ang  # perpendicular to bar (rotated 90┬░ CCW)
    ax.plot([x+px*size*1.6,x-px*size*1.6],[y+py*size*1.6,y-py*size*1.6],color=color,lw=3,zorder=5)
    # Hatching going "into wall" (opposite bar direction)
    hx,hy=-c_ang,-s_ang
    for t in np.linspace(-1.3,1.3,9):
        bx=x+px*size*t; by=y+py*size*t
        ax.plot([bx,bx+hx*size*0.55],[by,by+hy*size*0.55],color=color,lw=1,zorder=4)

def draw_fixed_left(ax,x,y_bot,height,size=0.3,color='k'):
    ax.plot([x,x],[y_bot,y_bot+height],color=color,lw=3.5,zorder=5)
    for yy in np.linspace(y_bot,y_bot+height,9):
        ax.plot([x-size*0.9,x],[yy-size*0.35,yy],color=color,lw=1,zorder=4)

def draw_axes(ax,ox,oy,length=0.8,color='gray',fontsize=8):
    hw=length*0.12; hl=length*0.15
    # x-axis arrow
    ax.arrow(ox,oy,length-hl,0,head_width=hw,head_length=hl,fc=color,ec=color,lw=1.3,zorder=8)
    ax.text(ox+length+0.08,oy,'x',color=color,fontsize=fontsize,fontweight='bold',va='center')
    # y-axis arrow
    ax.arrow(ox,oy,0,length-hl,head_width=hw,head_length=hl,fc=color,ec=color,lw=1.3,zorder=8)
    ax.text(ox,oy+length+0.08,'y',color=color,fontsize=fontsize,fontweight='bold',ha='center')
    # origin dot
    ax.plot(ox,oy,'o',color=color,markersize=3,zorder=9)

def draw_force_arrow(ax,x,y,fx,fy,label,color='red',scale=0.8,lw=1.8, txt_offset=(0,0), txt_lx=None, txt_ly=None):
    mag=np.sqrt(fx**2+fy**2)
    if mag<1e-10: return
    ux,uy=fx/mag,fy/mag
    ax.annotate('',xy=(x,y),xytext=(x-ux*scale,y-uy*scale),
                arrowprops=dict(arrowstyle='->',color=color,lw=lw,mutation_scale=14))
    if txt_lx is not None and txt_ly is not None:
        lx, ly = txt_lx, txt_ly
    else:
        perp_x,perp_y=-uy,ux
        lx=x-ux*scale*0.5+perp_x*scale*0.65 + txt_offset[0]
        ly=y-uy*scale*0.5+perp_y*scale*0.65 + txt_offset[1]
    ax.text(lx,ly,label,color=color,fontsize=7.5,fontweight='bold',
            ha='center',va='center',bbox=dict(fc='white',alpha=0.9,ec=color,lw=0.6,boxstyle='round,pad=0.2'))


def draw_distributed_load(ax,x1,x2,y,q,label='q',color='#2255cc',n_arrows=8):
    if x2<=x1: return
    ax.plot([x1,x2],[y,y],color=color,lw=2.2)
    xs=np.linspace(x1,x2,n_arrows)
    arrow_h=max(0.35,abs(q)*0.035+0.25); sign=-1 if q>0 else 1
    for xi in xs:
        ax.annotate('',xy=(xi,y+sign*arrow_h),xytext=(xi,y),
                    arrowprops=dict(arrowstyle='->',color=color,lw=1.3,mutation_scale=10))
    ax.text((x1+x2)/2,y+(-arrow_h-0.3 if sign<0 else arrow_h+0.15),
            f"{label} = {abs(q):.1f} kN/m",color=color,fontsize=9,fontweight='bold',ha='center')

def draw_distributed_load_perp(ax, q_start_s, q_end_s, c_ang, s_ang, q_mag, q_down=True, n=9, color='#2255cc'):
    """Draw distributed load perpendicular to bar, attached to bar surface."""
    if q_end_s<=q_start_s or q_mag<=0: return
    # Normal to bar: rotate bar tangent 90┬░ CCW ΓåÆ upward normal = (-s_ang, c_ang)
    # q_down=True ΓåÆ arrows point from above bar toward bar (local -y)
    # perp direction from bar outward (where arrow tail is)
    # Normal "sus" fa╚¢─â de bar─â = (-s_ang, c_ang). Dac─â qΓåô coada e sus, dac─â qΓåæ coada e jos.
    px = -s_ang if q_down else s_ang
    py =  c_ang if q_down else -c_ang
    arrow_len=max(0.35, q_mag*0.03+0.25)
    xs_s=np.linspace(q_start_s, q_end_s, n)
    for s in xs_s:
        tip_x=s*c_ang; tip_y=s*s_ang
        base_x=tip_x+px*arrow_len; base_y=tip_y+py*arrow_len
        ax.annotate('',xy=(tip_x,tip_y),xytext=(base_x,base_y),
                    arrowprops=dict(arrowstyle='-|>',color=color,lw=1.4,mutation_scale=11))
    # Top line
    bx=[s*c_ang+px*arrow_len for s in xs_s]; by=[s*s_ang+py*arrow_len for s in xs_s]
    ax.plot(bx,by,color=color,lw=2.2)

def draw_moment_arc(ax,x,y,M,r=0.25,color='purple'):
    """Draw moment arc. M>0 = counterclockwise (antiorar), M<0 = clockwise (orar)."""
    if abs(M)<1e-9: return
    if M>0:  # counterclockwise
        t=np.linspace(np.radians(40),np.radians(320),150)
    else:    # clockwise
        t=np.linspace(np.radians(320),np.radians(40),150)
    # Draw arc body up to the tip
    ax.plot(x+r*np.cos(t),y+r*np.sin(t),color=color,lw=2.4,zorder=6,solid_capstyle='round')
    # Manual triangle arrowhead at the exact tip
    tip_x=x+r*np.cos(t[-1]); tip_y=y+r*np.sin(t[-1])
    # Tangent direction at tip
    dx=np.cos(t[-1])-np.cos(t[-3]); dy=np.sin(t[-1])-np.sin(t[-3])
    norm=np.sqrt(dx**2+dy**2)
    if norm<1e-10: return
    dx/=norm; dy/=norm
    # Perpendicular to tangent
    px,py=-dy,dx
    hs=r*0.45  # arrowhead size
    tri=np.array([[tip_x,tip_y],
                  [tip_x-dx*hs+px*hs*0.35, tip_y-dy*hs+py*hs*0.35],
                  [tip_x-dx*hs-px*hs*0.35, tip_y-dy*hs-py*hs*0.35]])
    ax.add_patch(plt.Polygon(tri,closed=True,fc=color,ec=color,lw=0.5,zorder=7))

def _force_xy(f):
    """Return (fx_global, fy_global) from a force dict (new or legacy format)."""
    if "axa" in f:
        axa=f.get("axa","Y"); F=f.get("F",-10.0); al=f.get("alpha",0.0)
        base=0.0 if axa=="X" else 90.0
        return F*np.cos(np.radians(base+al)), F*np.sin(np.radians(base+al))
    return f.get("fx",0.0), f.get("fy",0.0)

def fill_diagram(ax,x,y,color,label,alpha=0.32,sign_labels=True):
    ax.fill_between(x,y,0,color=color,alpha=alpha); ax.plot(x,y,color=color,lw=2.2)
    ax.axhline(0,color='black',lw=1.2); ax.set_ylabel(label,color=color,fontweight='bold',fontsize=10)
    ax.grid(True,alpha=0.18,linestyle='--'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    if sign_labels:
        ymax=np.max(y); ymin=np.min(y)
        x_mid=(x[0]+x[-1])/2
        if ymax>1e-6:
            ax.text(x_mid,ymax*0.5,"+",fontsize=14,color=color,alpha=0.55,fontweight='bold',va='center',ha='center')
        if ymin<-1e-6:
            ax.text(x_mid,ymin*0.5,"ΓêÆ",fontsize=14,color=color,alpha=0.55,fontweight='bold',va='center',ha='center')

def label_extremes(ax,x_arr,y_arr,color='black'):
    shown=set()
    for idx in [int(np.argmax(y_arr)),int(np.argmin(y_arr)),0,len(y_arr)-1]:
        val=y_arr[idx]
        if abs(val)<1e-6: continue
        k=round(val,3)
        if k in shown: continue
        shown.add(k)
        ax.annotate(f'{val:.3f}',xy=(x_arr[idx],val),fontsize=8,color=color,fontweight='bold',
                    ha='center',va='bottom' if val>=0 else 'top',
                    bbox=dict(fc='white',alpha=0.75,ec='none',pad=1.5))

def draw_ntm_on_frame(ax, bars, color, scale, alpha=0.35, label_vals=True):
    """Draw filled N/T/M diagram on arbitrary frame bars.
    bars: list of dicts with keys x1,y1,x2,y2,values (np.array)."""
    for bar in bars:
        x1,y1,x2,y2=bar['x1'],bar['y1'],bar['x2'],bar['y2']
        vals=bar['values']
        n=len(vals)
        dx,dy=x2-x1,y2-y1
        L=np.sqrt(dx**2+dy**2)
        if L<1e-9: continue
        c_b,s_b=dx/L,dy/L
        nx,ny=-s_b,c_b
        t=np.linspace(0,1,n)
        bx=x1+t*dx; by=y1+t*dy
        px=bx+vals*scale*nx; py=by+vals*scale*ny
        ax.plot([x1,x2],[y1,y2],'k-',lw=3.5,zorder=3)
        ax.plot(px,py,color=color,lw=2,zorder=4)
        fill_x=np.concatenate([bx,px[::-1]])
        fill_y=np.concatenate([by,py[::-1]])
        ax.fill(fill_x,fill_y,color=color,alpha=alpha,zorder=2)
        if label_vals:
            for idx in [0,n-1,int(np.argmax(vals)),int(np.argmin(vals))]:
                v=vals[idx]
                if abs(v)<1e-4: continue
                off=scale*0.15 if v>=0 else -scale*0.15
                ax.text(px[idx]+off*nx,py[idx]+off*ny,f'{v:.2f}',
                        color=color,fontsize=7.5,fontweight='bold',ha='center',va='center',
                        bbox=dict(fc='white',alpha=0.85,ec=color,lw=0.5,boxstyle='round,pad=0.15'))

# ============================================================
# NAVIGARE
# ============================================================
st.sidebar.markdown("## BeamFlow")
st.sidebar.markdown("---")
modul=st.sidebar.radio("**Selecteaz─â Modulul**",[
    "Calcul Grinzi simplu",
    "Rezisten╚¢a Materialelor",
    "Statica 1 ΓÇö Static Determinate",
    "Statica 2 ΓÇö Static Nedeterminate",
],key="nav_modul_main")
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#aaa;'>Bazat pe manuale / ├«ndrum─âtoare rom├óne╚Öti</small>",unsafe_allow_html=True)

# ============================================================
# MODUL 1: CALCUL 2D GRINZI
# ============================================================
if modul == "Calcul Grinzi simplu":
    col_panel, col_canvas = st.columns([1.5, 4], gap="large")
    with col_panel:
        st.markdown("<h3 style='margin-top:-10px;'>Panou Control</h3>", unsafe_allow_html=True)
        tab_geom, tab_sup, tab_load = st.tabs(["Material", "Reazeme", "Încărcări"])
        with tab_geom:
            with col_panel:
                st.markdown("<h3 style='margin-top:-10px;'>≡ƒÄ¢∩╕Å Panou Control</h3>", unsafe_allow_html=True)
                tab_geom, tab_sup, tab_load = st.tabs(["Geometrie", "Reazeme", "├Änc─ârc─âri"])

                with tab_geom:
                # --- SIDEBAR: GEOMETRIE + SECTIUNE + MATERIAL ---
                if "gv_L" not in st.session_state: st.session_state.gv_L=6.0
                if "gv_A" not in st.session_state: st.session_state.gv_A=0.0
                def _gL(): st.session_state.gv_L=st.session_state.gv_Lsl
                def _gLn(): st.session_state.gv_L=st.session_state.gv_Lni
                def _gA(): st.session_state.gv_A=float(st.session_state.gv_Asl)
                def _gAn(): st.session_state.gv_A=float(st.session_state.gv_Ani)
                st.markdown("#### 1. Geometrie")
                st.slider("Lungime (m)",0.5,30.0,float(st.session_state.gv_L),0.5,key="gv_Lsl",on_change=_gL)
                L=st.number_input("Lungime (m)",value=float(st.session_state.gv_L),min_value=0.5,key="gv_Lni",on_change=_gLn,label_visibility="visible")
                st.slider("├Änclinare (┬░)",0.0,85.0,float(st.session_state.gv_A),1.0,key="gv_Asl",on_change=_gA)
                theta_deg=st.number_input("Unghi (┬░)",value=float(st.session_state.gv_A),min_value=0.0,max_value=85.0,key="gv_Ani",on_change=_gAn)
                th=np.radians(theta_deg); c_ang,s_ang=np.cos(th),np.sin(th)
                end_x,end_y=L*c_ang,L*s_ang
                st.markdown("#### 2. Sec╚¢iune")
                b_cm=st.number_input("L─â╚¢ime b (cm)",min_value=1.0,value=30.0,key="gv_b")
                h_cm=st.number_input("├Än─âl╚¢ime h (cm)",min_value=1.0,value=50.0,key="gv_h")
                b_m,h_m=b_cm/100,h_cm/100; A_sec=b_m*h_m; I_sec=b_m*h_m**3/12
                st.latex(rf"A={A_sec*1e4:.1f}\text{{cm}}^2,\quad I={to_sci(I_sec)}\text{{m}}^4")
                st.markdown("#### 3. Material")
                mat=st.selectbox("Material",["Beton C20/25","Beton C25/30","Beton C30/37","Beton C35/45","O╚¢el S235","O╚¢el S275","O╚¢el S355"],key="gv_mat")
                E={"Beton C20/25":30e6,"Beton C25/30":31e6,"Beton C30/37":33e6,"Beton C35/45":34e6,"O╚¢el S235":210e6,"O╚¢el S275":210e6,"O╚¢el S355":210e6}[mat]
                # --- REAZEME la distante personalizate ---
                with tab_sup:
                    st.markdown("#### Set─âri Reazeme")
                ro_lbl={0:"Liber",1:"Articula╚¢ie (pin)",2:"Reazem simplu (roller)",3:"├Äncastrare (fixed)"}
                if "gv_sup" not in st.session_state:
                    st.session_state.gv_sup=[{"x":0.0,"tip":1},{"x":float(L),"tip":2}]
                cs_btn=st.columns([1,1,4])
                if cs_btn[0].button("∩╝ï Adaug─â reazem",key="gv_sadd"):
                    st.session_state.gv_sup.append({"x":float(L)/2,"tip":2})
                if cs_btn[1].button("∩╝ì ╚ÿterge ultimul",key="gv_sdel"):
                    if len(st.session_state.gv_sup)>1: st.session_state.gv_sup.pop()
                sup_edited=[]
                n_sup=len(st.session_state.gv_sup)
                sup_cols=st.columns(min(n_sup,4))
                for i,s in enumerate(st.session_state.gv_sup):
                    with sup_cols[i%4]:
                        tip_idx=[0,1,2,3].index(s["tip"]) if s["tip"] in [0,1,2,3] else 1
                        t=st.selectbox(f"Tip reazem {i+1}",[0,1,2,3],index=tip_idx,format_func=lambda x:ro_lbl[x],key=f"gv_st_{i}")
                        xpos=st.number_input(f"Pozi╚¢ie x{i+1} (m)",min_value=0.0,max_value=float(L),value=float(np.clip(s["x"],0,L)),step=0.5,key=f"gv_sx_{i}")
                        sup_edited.append({"x":xpos,"tip":t})
                st.session_state.gv_sup=sup_edited
                # Static determinacy
                total_r=sum([2 if s["tip"]==1 else 1 if s["tip"]==2 else 3 if s["tip"]==3 else 0 for s in st.session_state.gv_sup])
                G_val=total_r-3
                if G_val==0: st.success(f"Structur─â **static determinat─â** (ns=0) ΓÇö {total_r} reac╚¢iuni, 3 ecua╚¢ii")
                elif G_val>0: st.warning(f"**Static nedeterminat─â** ns={G_val} ΓÇö {total_r} reac╚¢iuni")
                else: st.error(f"**MECANISM!** G={G_val} ΓÇö structura instabil─â")
                # --- INCARCARI ---
                with tab_load:
                    st.markdown("#### Distribuite (q)")
                qc1,qc2,qc3,qc4=st.columns(4)
                q_abs=qc1.number_input("q (kN/m)",min_value=0.0,value=0.0,step=1.0,key="gv_qabs")
                q_dir=qc2.selectbox("Direc╚¢ie q",["Γåô Jos (ΓêÆy local)","Γåæ Sus (+y local)"],key="gv_qdir")
                q_down=(q_dir=="Γåô Jos (ΓêÆy local)")
                q_eff=q_abs if q_down else -q_abs   # sign for FEM (positive = down in local y)
                q_start=qc3.number_input("De la x (m)",min_value=0.0,max_value=float(L),value=0.0,step=0.5,key="gv_qx1")
                q_end=qc4.number_input("P├ón─â la x (m)",min_value=0.0,max_value=float(L),value=float(L),step=0.5,key="gv_qx2")
                        st.markdown("#### Concentrate")
                if "gv_forces" not in st.session_state: st.session_state.gv_forces=[]
                fa,fb=st.columns([1,5])
                with fa:
                    if st.button("∩╝ï ├Änc─ârcare",key="gv_fadd"): st.session_state.gv_forces.append({"tip":"F","axa":"Y","F":-10.0,"alpha":0.0,"dist":float(L)/2})
                    if st.button("∩╝ì ╚ÿterge ultima",key="gv_fdel"):
                        if st.session_state.gv_forces: st.session_state.gv_forces.pop()
                f_edited=[]
                if st.session_state.gv_forces:
                    fcols=st.columns(min(len(st.session_state.gv_forces),3))
                    for i,f in enumerate(st.session_state.gv_forces):
                        with fcols[i%3]:
                            st.markdown(f"**├Änc─ârcarea {i+1}**")
                            tip=st.selectbox("Tip",["For╚¢─â","Moment concentrat"],index=0 if f["tip"]=="F" else 1,key=f"gv_ft_{i}")
                            tip_k="F" if tip=="For╚¢─â" else "M"
                            if tip_k=="F":
                                axa_def=f.get("axa","Y")
                                axa=st.selectbox("Ax─â",["X","Y"],index=0 if axa_def=="X" else 1,key=f"gv_faxa_{i}")
                                if axa=="X":
                                    F_val=st.number_input("F (kN)  [ + ΓåÆ dreapta  |  ΓêÆ ΓåÆ st├ónga ]",value=float(f.get("F",10.0) if f.get("axa","Y")=="X" else 10.0),step=1.0,key=f"gv_fF_{i}")
                                else:
                                    F_val=st.number_input("F (kN)  [ + ΓåÆ sus  |  ΓêÆ ΓåÆ jos ]",value=float(f.get("F",-10.0) if f.get("axa","Y")=="Y" else -10.0),step=1.0,key=f"gv_fF_{i}")
                                al=st.number_input("Unghi fa╚¢─â de ax─â ╬▒ (┬░)",value=float(f.get("alpha",0.0)),min_value=-90.0,max_value=90.0,step=5.0,key=f"gv_fal_{i}")
                                d=st.number_input("Pozi╚¢ie x (m)",0.0,float(L),float(np.clip(f.get("dist",L/2),0,L)),step=0.5,key=f"gv_fd_{i}")
                                fx_show,fy_show=_force_xy({"axa":axa,"F":F_val,"alpha":al})
                                st.caption(f"ΓåÆ Fx={fx_show:.2f} kN | Fy={fy_show:.2f} kN")
                                f_edited.append({"tip":"F","axa":axa,"F":F_val,"alpha":al,"dist":d})
                            else:
                                Mval=st.number_input("M (kNm) ΓÇö + antiorar",value=float(f.get("val",5.0)),step=1.0,key=f"gv_fM_{i}")
                                d=st.number_input("Pozi╚¢ie x (m)",0.0,float(L),float(np.clip(f.get("dist",L/2),0,L)),step=0.5,key=f"gv_fd2_{i}")
                                f_edited.append({"tip":"M","val":Mval,"dist":d})
        st.session_state.gv_forces=f_edited
        st.markdown("<br>", unsafe_allow_html=True)
        btn_calc = st.button("▶ Efectuează Calculul", type="primary", use_container_width=True, key="gv_calc")

    canvas_container = col_canvas.container()
    with canvas_container:
        st.title("BeamFlow | Proiectare")
            st.markdown("<br>", unsafe_allow_html=True)
            btn_calc = st.button("Γû╢ Efectueaz─â Calculul", type="primary", use_container_width=True, key="gv_calc")

        canvas_container = col_canvas.container()
        with canvas_container:
            st.markdown("<h3 style='margin-top:-10px;'>Γ£Å∩╕Å Spa╚¢iu de Lucru</h3>", unsafe_allow_html=True)


            # --- SCHI╚Ü─é ---
            ss=max(0.18,L*0.03)
            _dim_drop=max(0.9,L*0.15)   # how far below beam the dimension line sits
            _tick_h=_dim_drop*0.18      # short tick height at dim-line ends

            def _draw_dim_line(ax,x1_g,y1_g,x2_g,y2_g,label,drop,tick_h,color="#555",above=True):
                """Dimension line parallel to beam. above=True ΓåÆ above bar, above=False ΓåÆ below bar."""
                nx,ny=(-s_ang,c_ang) if above else (s_ang,-c_ang)
                ax.plot([x1_g,x1_g+nx*drop],[y1_g,y1_g+ny*drop],color=color,lw=0.7,ls=":",zorder=2)
                ax.plot([x2_g,x2_g+nx*drop],[y2_g,y2_g+ny*drop],color=color,lw=0.7,ls=":",zorder=2)
                ox1=x1_g+nx*drop; oy1=y1_g+ny*drop
                ox2=x2_g+nx*drop; oy2=y2_g+ny*drop
                ax.annotate("",xy=(ox1,oy1),xytext=(ox2,oy2),
                            arrowprops=dict(arrowstyle="<->",color=color,lw=1.0,mutation_scale=10),zorder=3)
                mx=(ox1+ox2)/2+nx*tick_h*1.4; my=(oy1+oy2)/2+ny*tick_h*1.4
                ax.text(mx,my,label,fontsize=8,ha="center",va="center",color=color,fontweight="bold",
                        bbox=dict(fc="white",alpha=0.88,ec="none",pad=1.2))

            fig1,ax1=plt.subplots(figsize=(12,max(4.5,end_y+_dim_drop*2+2.5)),dpi=150)

            # Beam
            ax1.plot([0,end_x],[0,end_y],"k-",lw=7,zorder=3,solid_capstyle="round",
                     path_effects=None)

            # Draw supports + node labels
            node_labels=["A","B","C","D","E","F"]
            sup_xs=sorted(st.session_state.gv_sup,key=lambda s:s["x"])
            for idx,s in enumerate(st.session_state.gv_sup):
                sx_g=s["x"]*c_ang; sy_g=s["x"]*s_ang
                lbl=node_labels[idx] if idx<len(node_labels) else str(idx)
                if s["tip"]==1:
                    draw_pin(ax1,sx_g,sy_g,ss)
                    ax1.text(sx_g-ss*1.2,sy_g-ss*1.5,lbl,fontsize=9.5,fontweight="bold",color="#1a3a5c",
                             ha="right",va="top",bbox=dict(fc="#e8f0fe",ec="#4a6fa5",lw=0.8,boxstyle="round,pad=0.2"))
                elif s["tip"]==2:
                    draw_roller(ax1,sx_g,sy_g,ss)
                    ax1.text(sx_g-ss*1.2,sy_g-ss*2.2,lbl,fontsize=9.5,fontweight="bold",color="#1a3a5c",
                             ha="right",va="top",bbox=dict(fc="#e8f0fe",ec="#4a6fa5",lw=0.8,boxstyle="round,pad=0.2"))
                elif s["tip"]==3:
                    draw_fixed_bottom(ax1,sx_g,sy_g,c_ang,s_ang,ss)
                    ax1.text(sx_g-c_ang*ss*1.2-ss*1.0,sy_g-s_ang*ss*1.2-ss*1.0,lbl,fontsize=9.5,fontweight="bold",color="#1a3a5c",
                             ha="right",va="top",bbox=dict(fc="#e8f0fe",ec="#4a6fa5",lw=0.8,boxstyle="round,pad=0.2"))

            # Draw q perpendicular to bar (no label ΓÇö label goes below beam separately)
            if q_abs>0 and q_end>q_start:
                draw_distributed_load_perp(ax1,q_start,q_end,c_ang,s_ang,q_abs,q_down)

            # Draw forces
            arsc=max(0.55,L*0.1)
            for f in st.session_state.gv_forces:
                d=f.get("dist",0); fp=d*c_ang; fyp=d*s_ang
                if f["tip"]=="F":
                    fx_g,fy_g=_force_xy(f)
                    mag=np.sqrt(fx_g**2+fy_g**2)
                    lbl=f"{abs(f.get('F',mag)):.0f}kN" if "axa" in f else f"{mag:.0f}kN"
                    draw_force_arrow(ax1,fp,fyp,fx_g,fy_g,lbl,color="#c00",scale=arsc)
                else:
                    _Mv=f.get("val",0)
                    draw_moment_arc(ax1,fp,fyp,_Mv,r=ss*1.05,color="purple")
                    ax1.text(fp+ss*2.2,fyp+ss*0.6,f"M={_Mv:.0f}kNm",fontsize=8,color="purple",fontweight="bold",
                             bbox=dict(fc="white",alpha=0.88,ec="purple",lw=0.5,pad=1.2,boxstyle="round,pad=0.2"))

            # ΓöÇΓöÇ COTARE (dimensioning lines) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
            # Build sorted list of key x-positions (supports + ends)
            key_xs=sorted(set([0.0,L]+[s["x"] for s in st.session_state.gv_sup]))

            # q label below beam (between beam and L dimension)
            if q_abs>0 and q_end>q_start:
                _q_lbl_drop=_dim_drop*0.55
                _q_mid=(q_start+q_end)/2
                _q_lx=_q_mid*c_ang+s_ang*_q_lbl_drop; _q_ly=_q_mid*s_ang-c_ang*_q_lbl_drop
                ax1.text(_q_lx,_q_ly,f"q = {q_abs:.1f} kN/m",fontsize=9,fontweight='bold',
                         color='#2255cc',ha='center',va='center',
                         bbox=dict(fc='white',alpha=0.9,ec='#2255cc',lw=0.6,boxstyle='round,pad=0.25'))

            # 1) Overall L ΓÇö jos fa╚¢─â de bar─â (sub label-ul q)
            _q_extra=max(0.8,q_abs*0.035+0.25)*1.3 if q_abs>0 else 0
            _draw_dim_line(ax1,0,0,end_x,end_y,f"L = {L:.2f} m",
                           _dim_drop*1.3+_q_extra,_tick_h,above=False)

            # 2) Segmente ΓÇö sus fa╚¢─â de bar─â
            if len(key_xs)>2:
                for i in range(len(key_xs)-1):
                    xa1=key_xs[i]*c_ang;   ya1=key_xs[i]*s_ang
                    xa2=key_xs[i+1]*c_ang; ya2=key_xs[i+1]*s_ang
                    seg_len=key_xs[i+1]-key_xs[i]
                    _draw_dim_line(ax1,xa1,ya1,xa2,ya2,f"{seg_len:.2f} m",
                                   _dim_drop*0.7,_tick_h,color="#4a6fa5",above=True)

            # Axes system (bottom-left corner)
            draw_axes(ax1,min(0,end_x)-1.2,min(0,end_y)-0.3,length=0.7)

            mg=max(L*0.22,1.5)
            ax1.set_xlim(min(0,end_x)-mg, max(0,end_x)+mg)
            ax1.set_ylim(min(0,end_y)-_dim_drop*1.8-mg*0.3-_q_extra, max(0,end_y)+_dim_drop*1.1+mg*0.5)
            ax1.set_aspect("equal"); ax1.axis("off")
            g_txt="static determinat─â" if G_val==0 else (f"nedeterminat─â ns={G_val}" if G_val>0 else "MECANISM")
            ax1.set_title(f"╬╕ = {theta_deg:.0f}┬░  |  L = {L:.1f} m",
                          fontsize=11,fontweight="bold",pad=8)
            st.pyplot(fig1); plt.close(fig1)

            st.markdown("---")
            if btn_calc:
                if A_sec==0: st.error("Introduce╚¢i sec╚¢iunea.")
                elif G_val<0: st.error("Structura este un mecanism! Adaug─â reazeme.")
                else:
                    try:
                        # Build node list
                        raw_nodes=set([0.0,L])
                        for s in st.session_state.gv_sup: raw_nodes.add(round(s["x"],6))
                        for f in st.session_state.gv_forces: raw_nodes.add(round(f.get("dist",0),6))
                        if q_abs>0: raw_nodes|={round(q_start,6),round(q_end,6)}
                        nodes_s=sorted(raw_nodes); nn=len(nodes_s); ne=nn-1

                        def nidx(xv): return nodes_s.index(round(xv,6))

                        # --- anastruct solver ---
                        ss_fem=SystemElements(EI=E*I_sec, EA=E*A_sec)
                        for i in range(ne):
                            x1=nodes_s[i]; x2=nodes_s[i+1]
                            ss_fem.add_element(location=[[x1*c_ang,x1*s_ang],[x2*c_ang,x2*s_ang]])

                        # Node ID mapping: anastruct node IDs start at 1
                        # node i in nodes_s ΓåÆ anastruct node_id = i+1
                        for s in st.session_state.gv_sup:
                            nid=nidx(s["x"])+1
                            if s["tip"]==1: ss_fem.add_support_hinged(node_id=nid)
                            elif s["tip"]==2: ss_fem.add_support_roll(node_id=nid)
                            elif s["tip"]==3: ss_fem.add_support_fixed(node_id=nid)

                        # Distributed loads ΓÇö gravitational (global y direction)
                        if q_abs>0 and q_end>q_start:
                            for eid in range(1,ne+1):
                                mid=(nodes_s[eid-1]+nodes_s[eid])/2
                                if q_start-1e-6<=mid<=q_end+1e-6:
                                    q_sign=-q_abs if q_down else q_abs
                                    ss_fem.q_load(element_id=eid, q=q_sign, direction='y')

                        # Point loads and moments
                        for f in st.session_state.gv_forces:
                            nid=nidx(f.get("dist",0))+1
                            if f["tip"]=="F":
                                fx_f,fy_f=_force_xy(f)
                                if abs(fx_f)>1e-9: ss_fem.point_load(node_id=nid, Fx=fx_f)
                                if abs(fy_f)>1e-9: ss_fem.point_load(node_id=nid, Fy=fy_f)
                            else:
                                ss_fem.moment_load(node_id=nid, Ty=f.get("val",0))

                        ss_fem.solve()

                        # Build R_g (reactions array) for downstream drawing code
                        R_g=np.zeros(3*nn)
                        for s in st.session_state.gv_sup:
                            ni=nidx(s["x"]); nid=ni+1; base=3*ni
                            r=ss_fem.get_node_results_system(node_id=nid)
                            R_g[base]=r["Fx"]; R_g[base+1]=r["Fy"]; R_g[base+2]=r["Tz"]

                        # Build U_loc (local displacements) for deflection display
                        U_loc=np.zeros(3*nn)
                        for i in range(nn):
                            nid=i+1
                            r=ss_fem.get_node_results_system(node_id=nid)
                            U_loc[3*i]=r["ux"]; U_loc[3*i+1]=r["uy"]; U_loc[3*i+2]=r["phi_z"]

                        # Build diagram arrays from anastruct element results
                        x_pl,N_pl,V_pl,M_pl=[],[],[],[]
                        for i in range(ne):
                            el=ss_fem.element_map[i+1]
                            Le=nodes_s[i+1]-nodes_s[i]
                            npts_el=len(el.bending_moment)
                            xs=np.linspace(nodes_s[i],nodes_s[i+1],npts_el)
                            x_pl.extend(xs)
                            # anastruct: axial force from N_1/N_2 (constant per element)
                            N_arr=np.linspace(el.N_1,el.N_2,npts_el)
                            N_pl.extend(N_arr)
                            V_pl.extend(el.shear_force)
                            M_pl.extend(el.bending_moment)

                        st.success("Calcul finalizat!")
                        xa=np.array(x_pl); Va=np.array(V_pl); Ma=np.array(M_pl); Na=np.array(N_pl)

                        # --- REACTIUNI frumos ---
                        # --- SCHI╚Ü─é CU REAC╚ÜIUNI DESENATE ---
                        st.markdown("### Reac╚¢iuni la Reazeme")
                        _rsc_arr=max(0.5,L*0.10)
                        # Paleta mat─â pentru reac╚¢iuni
                        _cV="#4060a8"   # albastru mat ΓÇö reac╚¢iuni verticale
                        _cH="#3a8060"   # verde-teal mat ΓÇö reac╚¢iuni orizontale
                        _cM="#7050a8"   # violet mat ΓÇö momente reazeme

                        fig_reac,ax_reac=plt.subplots(figsize=(12,max(4.5,end_y+_dim_drop*2+3.0)),dpi=150)
                        ax_reac.plot([0,end_x],[0,end_y],"k-",lw=7,zorder=3,solid_capstyle="round")

                        # Reazeme + etichete noduri (l├óng─â reazem)
                        for idx,s in enumerate(st.session_state.gv_sup):
                            sx_g=s["x"]*c_ang; sy_g=s["x"]*s_ang
                            lbl=node_labels[idx] if idx<len(node_labels) else str(idx)
                            if s["tip"]==1:
                                draw_pin(ax_reac,sx_g,sy_g,ss)
                                ax_reac.text(sx_g-ss*1.2,sy_g-ss*1.5,lbl,fontsize=9.5,fontweight="bold",color="#1a3a5c",
                                             ha="right",va="top",bbox=dict(fc="#e8f0fe",ec="#4a6fa5",lw=0.7,boxstyle="round,pad=0.2"))
                            elif s["tip"]==2:
                                draw_roller(ax_reac,sx_g,sy_g,ss)
                                ax_reac.text(sx_g-ss*1.2,sy_g-ss*2.2,lbl,fontsize=9.5,fontweight="bold",color="#1a3a5c",
                                             ha="right",va="top",bbox=dict(fc="#e8f0fe",ec="#4a6fa5",lw=0.7,boxstyle="round,pad=0.2"))
                            elif s["tip"]==3:
                                draw_fixed_bottom(ax_reac,sx_g,sy_g,c_ang,s_ang,ss*0.75)
                                ax_reac.text(sx_g-c_ang*ss*1.2-ss*1.0,sy_g-s_ang*ss*1.2-ss*1.0,lbl,fontsize=9.5,fontweight="bold",color="#1a3a5c",
                                             ha="right",va="top",bbox=dict(fc="#e8f0fe",ec="#4a6fa5",lw=0.7,boxstyle="round,pad=0.2"))

                        # ├Änc─ârc─âri aplicate ΓÇö q f─âr─â label (R va ar─âta valoarea)
                        if q_abs>0 and q_end>q_start:
                            _qpx=-s_ang if q_down else s_ang
                            _qpy= c_ang if q_down else -c_ang
                            _qlen=max(0.35,q_abs*0.03+0.25)
                            _qs=np.linspace(q_start,q_end,9)
                            for _s in _qs:
                                _tx=_s*c_ang; _ty=_s*s_ang
                                ax_reac.annotate("",xy=(_tx,_ty),xytext=(_tx+_qpx*_qlen,_ty+_qpy*_qlen),
                                                 arrowprops=dict(arrowstyle="-|>",color="#2255cc",lw=1.3,mutation_scale=10))
                            _bx=[_s*c_ang+_qpx*_qlen for _s in _qs]
                            _by=[_s*s_ang+_qpy*_qlen for _s in _qs]
                            ax_reac.plot(_bx,_by,color="#2255cc",lw=2.0)

                        # For╚¢e concentrate utilizator
                        for f in st.session_state.gv_forces:
                            d=f.get("dist",0); fp=d*c_ang; fyp=d*s_ang
                            if f["tip"]=="F":
                                fx_g,fy_g=_force_xy(f)
                                mag=np.sqrt(fx_g**2+fy_g**2)
                                lbl=f"{abs(f.get('F',mag)):.0f}kN" if "axa" in f else f"{mag:.0f}kN"
                                draw_force_arrow(ax_reac,fp,fyp,fx_g,fy_g,lbl,color="#c00",scale=_rsc_arr)
                            else:
                                _Mv=f.get("val",0)
                                draw_moment_arc(ax_reac,fp,fyp,_Mv,r=ss*1.05,color="purple")

                        # ΓöÇΓöÇ Rezultant─â q ΓöÇΓöÇ
                        if q_abs>0 and q_end>q_start:
                            R_q=q_abs*(q_end-q_start)
                            x_R=(q_start+q_end)/2
                            Rg_x=x_R*c_ang; Rg_y=x_R*s_ang
                            Rpx=-s_ang if q_down else s_ang
                            Rpy= c_ang if q_down else -c_ang
                            R_arrow_len=max(0.65,L*0.13)
                            ax_reac.annotate("",xy=(Rg_x,Rg_y),
                                             xytext=(Rg_x+Rpx*R_arrow_len,Rg_y+Rpy*R_arrow_len),
                                             arrowprops=dict(arrowstyle="-|>",color="#1a6e1a",lw=2.5,
                                                             mutation_scale=20))
                            # Label deasupra cozii s─âge╚¢ii, u╚Öor lateral
                            ax_reac.text(Rg_x+Rpx*(R_arrow_len+0.18),Rg_y+Rpy*(R_arrow_len+0.18),
                                         f"R = {R_q:.2f} kN",fontsize=9.5,color="#1a6e1a",fontweight="bold",
                                         ha="center",va="center",
                                         bbox=dict(fc="white",alpha=0.92,ec="#1a6e1a",lw=0.8,
                                                   boxstyle="round,pad=0.35"))
                            # Cotare x ΓÇö jos (sub L total)
                            _draw_dim_line(ax_reac,0,0,Rg_x,Rg_y,
                                           f"x = {x_R:.2f} m",
                                           _dim_drop*0.9,_tick_h,color="#1a6e1a",above=False)

                        # ΓöÇΓöÇ S─âge╚¢i reac╚¢iuni ΓöÇΓöÇ
                        for idx,s in enumerate(st.session_state.gv_sup):
                            ni=nidx(s["x"]); base=3*ni
                            lbl=node_labels[idx] if idx<len(node_labels) else str(idx)
                            sx_g=s["x"]*c_ang; sy_g=s["x"]*s_ang
                            HA_v=R_g[base]   if s["tip"] in [1,3] else 0.0
                            VA_v=R_g[base+1] if s["tip"] in [1,2,3] else 0.0
                            MA_v=R_g[base+2] if s["tip"]==3 else 0.0

                            arr_scale = _rsc_arr * 1.5
                            is_left = (s["x"] <= L/2)

                            # VA: s─âgeat─â mare, text ├«n dreapta
                            if abs(VA_v)>1e-4:
                                if VA_v > 0:
                                    v_tip_y = sy_g - ss*1.0
                                    v_tail_y = v_tip_y - arr_scale
                                else:
                                    v_tip_y = sy_g - ss*1.0 - arr_scale
                                    v_tail_y = sy_g - ss*1.0
                                v_txt_x = sx_g + ss*1.5
                                v_txt_y = (v_tip_y + v_tail_y)/2
                                draw_force_arrow(ax_reac, sx_g, v_tip_y,
                                                 0, VA_v, f"V{lbl}={VA_v:.2f}kN",
                                                 color=_cV, scale=arr_scale, lw=2.2, txt_lx=v_txt_x, txt_ly=v_txt_y)

                            # HA: s─âgeat─â din exterior, text deasupra ei
                            if abs(HA_v)>1e-4:
                                if is_left:
                                    h_tip_x = sx_g - ss*1.2 if HA_v > 0 else sx_g - ss*1.2 - arr_scale
                                    h_tail_x = h_tip_x - arr_scale if HA_v > 0 else h_tip_x + arr_scale
                                else:
                                    h_tip_x = sx_g + ss*1.2 + arr_scale if HA_v > 0 else sx_g + ss*1.2
                                    h_tail_x = h_tip_x - arr_scale if HA_v > 0 else h_tip_x + arr_scale
                                h_txt_x = (h_tip_x + h_tail_x)/2
                                h_txt_y = sy_g + ss*1.4
                                draw_force_arrow(ax_reac, h_tip_x, sy_g,
                                                 HA_v, 0, f"H{lbl}={HA_v:.2f}kN",
                                                 color=_cH, scale=arr_scale, lw=2.2, txt_lx=h_txt_x, txt_ly=h_txt_y)

                            # MA: mic arc
                            if abs(MA_v)>1e-4:
                                draw_moment_arc(ax_reac,sx_g,sy_g,MA_v,r=ss*1.5,color=_cM)
                                m_txt_x = sx_g - ss*1.8 if is_left else sx_g + ss*1.8
                                ax_reac.text(m_txt_x, sy_g+ss*2.5,
                                             f"M{lbl}={MA_v:.2f}kNm",fontsize=7.5,color=_cM,fontweight="bold",
                                             bbox=dict(fc="white",alpha=0.95,ec=_cM,lw=0.6,
                                                       boxstyle="round,pad=0.2"), ha='center', va='center')

                        # Cotare: segmente sus, L jos
                        _draw_dim_line(ax_reac,0,0,end_x,end_y,f"L = {L:.2f} m",
                                       _dim_drop*1.55,_tick_h,above=False)
                        if len(key_xs)>2:
                            for i in range(len(key_xs)-1):
                                xa1r=key_xs[i]*c_ang;   ya1r=key_xs[i]*s_ang
                                xa2r=key_xs[i+1]*c_ang; ya2r=key_xs[i+1]*s_ang
                                _draw_dim_line(ax_reac,xa1r,ya1r,xa2r,ya2r,
                                               f"{key_xs[i+1]-key_xs[i]:.2f} m",
                                               _dim_drop*0.7,_tick_h,color="#4a6fa5",above=True)

                        draw_axes(ax_reac,min(0,end_x)-1.2,min(0,end_y)-0.3,length=0.7)
                        mg=max(L*0.22,1.5)
                        ax_reac.set_xlim(min(0,end_x)-mg,max(0,end_x)+mg)
                        _extra_bot=ss*3.0+abs(s_ang)*ss*2.0+_rsc_arr+0.8
                        ax_reac.set_ylim(min(0,end_y)-_dim_drop*2.2-mg*0.4-_extra_bot,max(0,end_y)+_dim_drop*1.0+mg*0.5)
                        ax_reac.set_aspect("equal"); ax_reac.axis("off")
                        ax_reac.set_title("Schi╚¢─â cu Reac╚¢iuni la Reazeme",fontsize=12,fontweight="bold",pad=10)
                        st.pyplot(fig_reac); plt.close(fig_reac)


                        # Echilibru global
                        Fx_sum=sum(R_g[3*nidx(s["x"])] for s in st.session_state.gv_sup if s["tip"] in [1,3])
                        Fy_sum=sum(R_g[3*nidx(s["x"])+1] for s in st.session_state.gv_sup if s["tip"] in [1,2,3])
                        for f in st.session_state.gv_forces:
                            if f["tip"]=="F":
                                fx_f,fy_f=_force_xy(f)
                                Fx_sum+=fx_f; Fy_sum+=fy_f
                        if q_abs>0: Fy_sum+=(-q_eff)*(q_end-q_start)*c_ang  # global y from perp q

                        eq1,eq2=st.columns(2)
                        _ = eq1.success(f"╬úFx={Fx_sum:.4f} Γëê 0") if abs(Fx_sum)<0.05 else eq1.warning(f"╬úFx={Fx_sum:.4f}")
                        _ = eq2.success(f"╬úFy={Fy_sum:.4f} Γëê 0") if abs(Fy_sum)<0.05 else eq2.warning(f"╬úFy={Fy_sum:.4f}")

                        st.metric("S─âgeat─â maxim─â",f"{np.max(np.abs(U_loc[1::3]))*1000:.4f} mm")

                        # --- DIAGRAME N, T, M ---
                        fig_r,(aN,aV,aM)=plt.subplots(3,1,figsize=(13,11),sharex=True,dpi=180)
                        fill_diagram(aN,xa,Na,"#1a6faf","N (kN)",sign_labels=False); aN.set_title("N(x) ΓÇö Efort axial",fontweight="bold",color="#1a6faf"); label_extremes(aN,xa,Na,"#1a6faf")
                        if np.max(Na)>0.01: aN.text(xa[np.argmax(Na)],Na[np.argmax(Na)]*0.5,"+",ha='center',va='center',fontsize=14,fontweight='bold',color="#1a6faf",alpha=0.75)
                        if np.min(Na)<-0.01: aN.text(xa[np.argmin(Na)],Na[np.argmin(Na)]*0.5,"ΓêÆ",ha='center',va='center',fontsize=14,fontweight='bold',color="#1a6faf",alpha=0.75)
                        fill_diagram(aV,xa,Va,"#2ca02c","T (kN)",sign_labels=False); aV.set_title("T(x) ΓÇö For╚¢─â t─âietoare",fontweight="bold",color="#2ca02c"); label_extremes(aV,xa,Va,"#2ca02c")
                        if np.max(Va)>0.01: aV.text(xa[np.argmax(Va)],Va[np.argmax(Va)]*0.5,"+",ha='center',va='center',fontsize=14,fontweight='bold',color="#2ca02c",alpha=0.75)
                        if np.min(Va)<-0.01: aV.text(xa[np.argmin(Va)],Va[np.argmin(Va)]*0.5,"ΓêÆ",ha='center',va='center',fontsize=14,fontweight='bold',color="#2ca02c",alpha=0.75)
                        # M diagram: conven╚¢ie rom├ón─â + jos (fibra ├«ntins─â jos)
                        aM.fill_between(xa,-Ma,0,color="#d62728",alpha=0.32); aM.plot(xa,-Ma,color="#d62728",lw=2.2)
                        aM.axhline(0,color='black',lw=1.2); aM.set_ylabel("M (kNm)",color="#d62728",fontweight='bold',fontsize=10)
                        aM.grid(True,alpha=0.18,linestyle='--'); aM.spines['top'].set_visible(False); aM.spines['right'].set_visible(False)
                        aM.set_title("M(x) ΓÇö Moment ├«ncovoietor",fontweight="bold",color="#d62728")
                        if np.max(Ma)>0.01: aM.text(xa[np.argmax(Ma)],-Ma[np.argmax(Ma)]*0.5,"+",ha='center',va='center',fontsize=14,fontweight='bold',color="#d62728",alpha=0.75)
                        if np.min(Ma)<-0.01: aM.text(xa[np.argmin(Ma)],-Ma[np.argmin(Ma)]*0.5,"ΓêÆ",ha='center',va='center',fontsize=14,fontweight='bold',color="#d62728",alpha=0.75)
                        _shown=set()
                        for _i in [int(np.argmax(Ma)),int(np.argmin(Ma)),0,len(Ma)-1]:
                            _v=Ma[_i]
                            if abs(_v)<1e-6 or round(_v,3) in _shown: continue
                            _shown.add(round(_v,3))
                            aM.annotate(f'{_v:.3f}',xy=(xa[_i],-_v),fontsize=8,color="#d62728",fontweight='bold',
                                        ha='center',va='bottom' if _v>=0 else 'top',
                                        bbox=dict(fc='white',alpha=0.75,ec='none',pad=1.5))

                        # Mmax unde T=0
                        sign_ch=np.where(np.diff(np.sign(Va)))[0]
                        for sc in sign_ch:
                            dV=Va[sc+1]-Va[sc]
                            if abs(dV)<1e-9: continue
                            x0=xa[sc]-Va[sc]*(xa[sc+1]-xa[sc])/dV
                            m0=float(np.interp(x0,xa,Ma))
                            aV.axvline(x0,color="orange",lw=1.2,ls="--",alpha=0.8)
                            aM.axvline(x0,color="orange",lw=1.2,ls="--",alpha=0.8)
                            aM.annotate(f"M_max\n{m0:.3f}kNm",xy=(x0,-m0),fontsize=8,color="orange",fontweight="bold",
                                        ha="center",va="top",bbox=dict(fc="white",alpha=0.8,ec="orange",pad=2))

                        aM.set_xlabel("x (m)",fontsize=11); plt.tight_layout()
                        fig_r.suptitle(f"Diagrame N, T, M ΓÇö {mat}  EI={E*I_sec/1e3:.0f} MNm┬▓",fontsize=13,fontweight="bold",y=1.01)
                        st.pyplot(fig_r)

                        # Formule Mmax
                        if len(sign_ch)>0:
                            st.markdown("### Formule Moment Maxim (unde T=0)")
                            for sc in sign_ch:
                                dV=Va[sc+1]-Va[sc]
                                if abs(dV)<1e-9: continue
                                x0=xa[sc]-Va[sc]*(xa[sc+1]-xa[sc])/dV
                                m0=float(np.interp(x0,xa,Ma))
                                V0_near=float(Va[max(0,sc-2)])
                                if q_abs>0:
                                    st.latex(rf"T(x_0)=0 \Rightarrow x_0={x0:.3f}\text{{m}},\quad M_{{max}}=M(x_0)={m0:.3f}\text{{kNm}}")
                                else:
                                    st.latex(rf"T\text{{ se anuleaz─â la }}x_0={x0:.3f}\text{{m}},\quad M_{{max}}={m0:.3f}\text{{kNm}}")

                        # Model de calcul
                        with st.expander("Model de calcul (pas cu pas)"):
                            st.markdown(f"""**Structura:** {len(st.session_state.gv_sup)} reazeme, {nn} noduri FEM, {ne} elemente
        **EI** = {E:.2e} kN/m┬▓ ├ù {I_sec:.4e} mΓü┤ = {E*I_sec:.3e} kNm┬▓
        **EA** = {E:.2e} ├ù {A_sec:.4f} = {E*A_sec:.3e} kN
        **Solver:** anastruct (SystemElements)""")
                            st.markdown("**Algoritmul FEM:**")
                            st.latex(r"\mathbf{K}\cdot\mathbf{u}=\mathbf{F}\;\Rightarrow\;\mathbf{u}_{liber}=\mathbf{K}_{ll}^{-1}\cdot\mathbf{F}_{liber}")
                            st.latex(r"\mathbf{R}=\mathbf{K}\cdot\mathbf{u}-\mathbf{F}\quad(\text{reac╚¢iuni})")
                            st.markdown(f"**Noduri FEM:** {[f'{v:.2f}m' for v in nodes_s]}")
                            st.markdown(f"**GDL total:** {3*nn}")
                            st.markdown("**Eforturi ├«n sec╚¢iune prin integrare:**")
                            st.latex(r"N(x)=\text{const./element},\quad T(x)=T_0+q\cdot x,\quad M(x)=M_0+T_0\cdot x+\frac{q x^2}{2}")

                        # ΓöÇΓöÇ PDF cu pa╚Öi detalia╚¢i de calcul ΓöÇΓöÇ
                        def _pdf_text_page(pdf, lines, title="", fontsize=10):
                            """Create a well-spaced text PDF page using matplotlib."""
                            fig_t,ax_t=plt.subplots(figsize=(8.27,11.69),dpi=150)
                            ax_t.axis('off')
                            if title:
                                ax_t.text(0.5,0.96,title,transform=ax_t.transAxes,fontsize=14,fontweight='bold',
                                          ha='center',va='top',color='#0d1b2a')
                                ax_t.plot([0.05,0.95],[0.945,0.945],transform=ax_t.transAxes,color='#E8641A',lw=2)
                            y_pos=0.92 if title else 0.96
                            for line in lines:
                                if y_pos<0.03: break
                                if line.startswith("##"):
                                    y_pos-=0.012
                                    ax_t.text(0.05,y_pos,line[2:].strip(),transform=ax_t.transAxes,fontsize=11.5,
                                              fontweight='bold',color='#1a3a5c',va='top')
                                    y_pos-=0.026
                                elif line=="---":
                                    y_pos-=0.006
                                    ax_t.plot([0.05,0.95],[y_pos,y_pos],transform=ax_t.transAxes,color='#bbb',lw=0.8)
                                    y_pos-=0.012
                                elif line=="":
                                    y_pos-=0.010
                                else:
                                    ax_t.text(0.06,y_pos,line,transform=ax_t.transAxes,fontsize=fontsize,va='top',
                                              color='#222',family='serif')
                                    y_pos-=0.022
                            fig_t.subplots_adjust(left=0.05,right=0.95,top=0.98,bottom=0.02)
                            pdf.savefig(fig_t,bbox_inches="tight"); plt.close(fig_t)

                        def _pdf_text_pages(pdf, lines, title="", fontsize=10):
                            """Split lines across multiple pages if needed."""
                            max_lines_per_page=48
                            for pg in range(0, len(lines), max_lines_per_page):
                                chunk=lines[pg:pg+max_lines_per_page]
                                t=title if pg==0 else f"{title} (cont.)"
                                _pdf_text_page(pdf, chunk, title=t, fontsize=fontsize)

                        buf=BytesIO()
                        with PdfPages(buf) as pdf:
                            # Pagina 1: Schi╚¢a structurii
                            pdf.savefig(fig1,bbox_inches="tight")
                            # Pagina 2: Schi╚¢a cu reac╚¢iuni
                            pdf.savefig(fig_reac,bbox_inches="tight")

                            # Pagina 3: Totul pe un singur flux ΓÇö date, echilibru, eforturi
                            all_lines=[]
                            all_lines.append("## 1. Date de intrare")
                            all_lines.append(f"L = {L:.2f} m,  ╬╕ = {theta_deg:.0f}┬░,  b├ùh = {b_cm:.0f}├ù{h_cm:.0f} cm,  {mat}")
                            all_lines.append(f"A = {A_sec*1e4:.1f} cm┬▓,  I = {I_sec:.3e} mΓü┤,  EI = {E*I_sec:.3e} kNm┬▓")
                            tip_short={0:"Liber",1:"Pin",2:"Roller",3:"├Äncastrare"}
                            sup_strs=[f"{node_labels[i] if i<6 else str(i)}: {tip_short[s['tip']]} x={s['x']:.2f}m" for i,s in enumerate(st.session_state.gv_sup)]
                            all_lines.append(f"Reazeme: {',  '.join(sup_strs)}   (r={total_r}, ns={G_val})")
                            if q_abs>0:
                                Rq_val=q_abs*(q_end-q_start); xRq_val=(q_start+q_end)/2
                                all_lines.append(f"q = {q_abs:.1f} kN/m ({'Γåô' if q_down else 'Γåæ'}) xΓêê[{q_start:.1f},{q_end:.1f}]  ΓåÆ  R_q = {Rq_val:.2f} kN la x_R = {xRq_val:.2f} m")
                            for idx_f,f in enumerate(st.session_state.gv_forces):
                                if f["tip"]=="F":
                                    fx_pdf,fy_pdf=_force_xy(f)
                                    all_lines.append(f"F{idx_f+1}: Fx={fx_pdf:.2f}, Fy={fy_pdf:.2f} kN la x={f.get('dist',0):.2f} m")
                                else:
                                    all_lines.append(f"M{idx_f+1}: {f.get('val',0):.2f} kNm la x={f.get('dist',0):.2f} m")
                            all_lines.append("")

                            # Ecua╚¢ii de echilibru
                            reac_info=[]
                            for idx_s,s in enumerate(st.session_state.gv_sup):
                                ni_s=nidx(s["x"]); base_s=3*ni_s
                                lbl_s=node_labels[idx_s] if idx_s<len(node_labels) else str(idx_s)
                                H_r=R_g[base_s] if s["tip"] in [1,3] else 0.0
                                V_r=R_g[base_s+1] if s["tip"] in [1,2,3] else 0.0
                                M_r=R_g[base_s+2] if s["tip"]==3 else 0.0
                                reac_info.append({"lbl":lbl_s,"x":s["x"],"tip":s["tip"],"H":H_r,"V":V_r,"M":M_r})

                            all_lines.append("## 2. Ecua╚¢ii de echilibru")
                            sfx_parts=[]
                            for r_i in reac_info:
                                if r_i["tip"] in [1,3] and abs(r_i["H"])>1e-6:
                                    sfx_parts.append(f"H{r_i['lbl']}={r_i['H']:+.2f}")
                            for f in st.session_state.gv_forces:
                                if f["tip"]=="F":
                                    fx_p,_=_force_xy(f)
                                    if abs(fx_p)>1e-6: sfx_parts.append(f"Fx={fx_p:+.2f}")
                            all_lines.append("╬úFx = 0:  " + (" + ".join(sfx_parts) + " = 0" if sfx_parts else "(f─âr─â Fx)"))
                            sfy_parts=[]
                            for r_i in reac_info:
                                if r_i["tip"] in [1,2,3] and abs(r_i["V"])>1e-6:
                                    sfy_parts.append(f"V{r_i['lbl']}={r_i['V']:+.2f}")
                            for f in st.session_state.gv_forces:
                                if f["tip"]=="F":
                                    _,fy_p=_force_xy(f)
                                    if abs(fy_p)>1e-6: sfy_parts.append(f"Fy={fy_p:+.2f}")
                            if q_abs>0:
                                Rq_fy=(-q_eff)*(q_end-q_start)*c_ang
                                sfy_parts.append(f"R_q={Rq_fy:+.2f}")
                            all_lines.append("╬úFy = 0:  " + (" + ".join(sfy_parts) + " = 0" if sfy_parts else "(f─âr─â Fy)"))
                            first_sup=reac_info[0] if reac_info else None
                            if first_sup:
                                all_lines.append(f"╬úM{first_sup['lbl']} = 0 (fa╚¢─â de {first_sup['lbl']}, x={first_sup['x']:.2f} m):")
                                for r_i in reac_info:
                                    brat=r_i["x"]-first_sup["x"]
                                    if abs(brat)>1e-6 and abs(r_i["V"])>1e-6:
                                        all_lines.append(f"    V{r_i['lbl']}┬╖{abs(brat):.2f} = {r_i['V']:.2f}┬╖{abs(brat):.2f} = {r_i['V']*brat:+.2f} kNm")
                                    if abs(r_i["M"])>1e-6:
                                        all_lines.append(f"    M{r_i['lbl']} = {r_i['M']:+.2f} kNm")
                                for f in st.session_state.gv_forces:
                                    d_f=f.get("dist",0); brat_f=d_f-first_sup["x"]
                                    if f["tip"]=="F":
                                        _,fy_p=_force_xy(f)
                                        if abs(fy_p)>1e-6 and abs(brat_f)>1e-6:
                                            all_lines.append(f"    Fy┬╖{abs(brat_f):.2f} = {fy_p:.2f}┬╖{abs(brat_f):.2f} = {fy_p*brat_f:+.2f} kNm")
                                    else:
                                        all_lines.append(f"    M_ext = {f.get('val',0):+.2f} kNm")
                                if q_abs>0:
                                    xRq_m=(q_start+q_end)/2; brat_q=xRq_m-first_sup["x"]
                                    Rq_tot=(-q_eff)*(q_end-q_start)
                                    all_lines.append(f"    R_q┬╖{abs(brat_q):.2f} = {Rq_tot:.2f}┬╖{abs(brat_q):.2f} = {Rq_tot*brat_q:+.2f} kNm")
                            all_lines.append("")
                            all_lines.append("## Reac╚¢iuni:")
                            for r_i in reac_info:
                                parts=[]
                                if r_i["tip"] in [1,3]: parts.append(f"H{r_i['lbl']}={r_i['H']:.2f}")
                                if r_i["tip"] in [1,2,3]: parts.append(f"V{r_i['lbl']}={r_i['V']:.2f}")
                                if r_i["tip"]==3: parts.append(f"M{r_i['lbl']}={r_i['M']:.2f}")
                                all_lines.append(f"    {r_i['lbl']}: {',  '.join(parts)} kN")
                            all_lines.append(f"Verif: ╬úFx={Fx_sum:.3f}Γëê0 {'Γ£ô' if abs(Fx_sum)<0.05 else 'Γ£ù'},  ╬úFy={Fy_sum:.3f}Γëê0 {'Γ£ô' if abs(Fy_sum)<0.05 else 'Γ£ù'}")
                            all_lines.append("")

                            # Eforturi sec╚¢ionale
                            all_lines.append("## 3. Eforturi sec╚¢ionale")
                            for i_e in range(ne):
                                Le_e=nodes_s[i_e+1]-nodes_s[i_e]
                                if Le_e<1e-9: continue
                                x_st=nodes_s[i_e]; x_en=nodes_s[i_e+1]
                                el_e=ss_fem.element_map[i_e+1]
                                N_st=el_e.N_1; V_st=el_e.shear_force[0]; V_end=el_e.shear_force[-1]
                                M_st=el_e.bending_moment[0]; M_end=el_e.bending_moment[-1]
                                mid_e=(nodes_s[i_e]+nodes_s[i_e+1])/2
                                hq_e=q_abs>0 and (q_start-1e-6<=mid_e<=q_end+1e-6)

                                hdr=f"Elem.{i_e+1} [{x_st:.2f}ΓÇô{x_en:.2f}]m" + (f"  q={q_abs:.1f}kN/m" if hq_e else "")
                                if hq_e:
                                    all_lines.append(f"  {hdr}:  N={N_st:.2f},  T=[{V_st:.2f}ΓåÆ{V_end:.2f}],  M=[{M_st:.2f}ΓåÆ{M_end:.2f}] kN(m)")
                                else:
                                    all_lines.append(f"  {hdr}:  N={N_st:.2f},  T={V_st:.2f},  M=[{M_st:.2f}ΓåÆ{M_end:.2f}] kN(m)")
                                if hq_e and V_st*V_end<0:
                                    er=el_e.results if hasattr(el_e,'results') else None
                                    M_max_e=max(abs(el_e.bending_moment.min()),abs(el_e.bending_moment.max()))
                                    all_lines.append(f"      ΓåÆ M_max={M_max_e:.2f} kNm")

                            if len(sign_ch)>0:
                                all_lines.append("")
                                all_lines.append("## 4. Moment maxim (T=0)")
                                for sc in sign_ch:
                                    dV_sc=Va[sc+1]-Va[sc]
                                    if abs(dV_sc)<1e-9: continue
                                    x0_sc=xa[sc]-Va[sc]*(xa[sc+1]-xa[sc])/dV_sc
                                    m0_sc=float(np.interp(x0_sc,xa,Ma))
                                    all_lines.append(f"T=0 la xΓéÇ={x0_sc:.3f} m  ΓåÆ  M_max={m0_sc:.2f} kNm")
                            all_lines.append("")
                            all_lines.append(f"S─âgeat─â maxim─â: {np.max(np.abs(U_loc[1::3]))*1000:.3f} mm")
                            _pdf_text_pages(pdf, all_lines, title="BeamFlow ΓÇö Calcul Detaliat")

                            # Ultima pagin─â: Diagrame N, T, M
                            pdf.savefig(fig_r,bbox_inches="tight")

                        st.download_button("Descarc─â PDF",buf.getvalue(),"Grinzi2D.pdf","application/pdf",key="gv_dl")
                        plt.close(fig_r)
                    except np.linalg.LinAlgError:
                        st.error("MECANISM! Matricea de rigiditate e singular─â ΓÇö verific─â reazemele.")
                    except Exception as ex:
                        st.error(f"Eroare: {ex}")

        # ============================================================
        # MODUL 2: REZISTENTA MATERIALELOR
        # ============================================================
        elif modul == "Rezisten╚¢a Materialelor":
            st.title("Rezisten╚¢a Materialelor I")
            st.markdown("Calcule conform *Rezisten╚¢a Materialelor I* (481-0.pdf)")
            st.markdown("---")
            tab1,tab2,tab3,tab4,tab5=st.tabs(["Propriet─â╚¢i Geometrice","Tensiune Axial─â","Invoiere Plan─â","Forfecare & Torsiune","Flambaj Euler"])

            with tab1:
                st.subheader("Propriet─â╚¢i Geometrice")
                with st.expander("Teorie (481-0.pdf, Cap.1)"):
                    st.latex(r"I_x=\frac{bh^3}{12},\; I_x^{cerc}=\frac{\pi d^4}{64},\; W_x=\frac{I_x}{y_{max}},\; i_x=\sqrt{I_x/A}")
                    st.latex(r"\text{Steiner: }I_{x\'} = I_x + A\cdot d^2")
                forma=st.selectbox("Form─â sec╚¢iune",["Dreptunghi plin","Cerc plin","Inel circular","Sec╚¢iune T","Sec╚¢iune I"],key="rm_forma")
                ci,cd=st.columns(2)
                if forma=="Dreptunghi plin":
                    with ci:
                        b_d=st.number_input("L─â╚¢ime b (cm)",min_value=0.1,value=30.0,step=1.0,key="rm_bd")
                        h_d=st.number_input("├Än─âl╚¢ime h (cm)",min_value=0.1,value=50.0,step=1.0,key="rm_hd")
                    A_d=b_d*h_d; Ix=b_d*h_d**3/12; Iy=h_d*b_d**3/12; Wx=Ix/(h_d/2); ix=np.sqrt(Ix/A_d)
                    with ci:
                        st.latex(rf"A={b_d:.1f}\times{h_d:.1f}={A_d:.2f}\text{{ cm}}^2")
                        st.latex(rf"I_x=\frac{{bh^3}}{{12}}={Ix:.2f}\text{{ cm}}^4")
                        st.latex(rf"W_x={Wx:.2f}\text{{ cm}}^3,\; i_x={ix:.3f}\text{{ cm}}")
                    with cd:
                        fig_s,ax_s=plt.subplots(figsize=(4,4),dpi=120)
                        ax_s.add_patch(plt.Rectangle((-b_d/2,-h_d/2),b_d,h_d,fc="#d0e4ff",ec="#1a6faf",lw=2.5))
                        ax_s.axhline(0,color="red",lw=1.5,ls="--",label="$x_c$"); ax_s.axvline(0,color="green",lw=1.5,ls="--",label="$y_c$")
                        ax_s.set_xlim(-b_d*0.9,b_d*1.2); ax_s.set_ylim(-h_d*0.8,h_d*0.8)
                        ax_s.set_aspect("equal"); ax_s.axis("off"); ax_s.legend(fontsize=8); ax_s.set_title("Dreptunghi",fontweight="bold")
                        st.pyplot(fig_s); plt.close(fig_s)
                elif forma=="Cerc plin":
                    with ci: d_c=st.number_input("Diametru d (cm)",min_value=0.1,value=30.0,step=1.0,key="rm_dc")
                    rc=d_c/2; Ac=np.pi*rc**2; Ixc=np.pi*d_c**4/64; Wxc=Ixc/rc; ixc=d_c/4; Ipc=np.pi*d_c**4/32; Wpc=Ipc/rc
                    with ci:
                        st.latex(rf"A=\frac{{\pi d^2}}{{4}}={Ac:.3f}\text{{ cm}}^2")
                        st.latex(rf"I_x=\frac{{\pi d^4}}{{64}}={Ixc:.3f}\text{{ cm}}^4")
                        st.latex(rf"W_x={Wxc:.3f}\text{{ cm}}^3,\; i_x={ixc:.3f}\text{{ cm}}")
                        st.latex(rf"I_p=\frac{{\pi d^4}}{{32}}={Ipc:.3f}\text{{ cm}}^4")
                    with cd:
                        fig_s,ax_s=plt.subplots(figsize=(4,4),dpi=120)
                        ax_s.add_patch(plt.Circle((0,0),rc,fc="#d0e4ff",ec="#1a6faf",lw=2.5))
                        ax_s.axhline(0,color="red",lw=1.2,ls="--"); ax_s.axvline(0,color="green",lw=1.2,ls="--")
                        ax_s.set_xlim(-rc*1.5,rc*1.5); ax_s.set_ylim(-rc*1.5,rc*1.5)
                        ax_s.set_aspect("equal"); ax_s.axis("off"); ax_s.set_title("Cerc",fontweight="bold")
                        st.pyplot(fig_s); plt.close(fig_s)
                elif forma=="Inel circular":
                    with ci:
                        Di=st.number_input("D exterior (cm)",min_value=0.1,value=40.0,key="rm_Di")
                        di=st.number_input("d interior (cm)",min_value=0.0,value=30.0,key="rm_di")
                    if di>=Di: st.error("d < D!")
                    else:
                        Ai=np.pi*(Di**2-di**2)/4; Ixi=np.pi*(Di**4-di**4)/64; Wxi=Ixi/(Di/2)
                        with ci:
                            st.latex(rf"A=\frac{{\pi(D^2-d^2)}}{{4}}={Ai:.3f}\text{{ cm}}^2")
                            st.latex(rf"I_x=\frac{{\pi(D^4-d^4)}}{{64}}={Ixi:.3f}\text{{ cm}}^4")
                            st.latex(rf"W_x={Wxi:.3f}\text{{ cm}}^3")
                elif forma=="Sec╚¢iune T":
                    with ci:
                        bt=st.number_input("L─â╚¢ime talp─â bt (cm)",value=20.0,key="rm_bt")
                        tt=st.number_input("Grosime talp─â tt (cm)",value=3.0,key="rm_tt")
                        bw=st.number_input("L─â╚¢ime inim─â bw (cm)",value=3.0,key="rm_bw")
                        hw=st.number_input("├Än─âl╚¢ime inim─â hw (cm)",value=15.0,key="rm_hw")
                    At=bt*tt; Aw=bw*hw; AT=At+Aw; yt=hw+tt/2; yw=hw/2; yC=(At*yt+Aw*yw)/AT
                    IT=bt*tt**3/12+At*(yt-yC)**2+bw*hw**3/12+Aw*(yw-yC)**2; Wx_T=IT/max(yC,hw+tt-yC)
                    with ci:
                        st.latex(rf"y_C={yC:.3f}\text{{ cm}}")
                        st.latex(rf"I_x={IT:.3f}\text{{ cm}}^4")
                        st.latex(rf"W_x={Wx_T:.3f}\text{{ cm}}^3")
                elif forma=="Sec╚¢iune I":
                    with ci:
                        bf=st.number_input("L─â╚¢ime t─âlpi bf (cm)",value=15.0,key="rm_bf")
                        tf=st.number_input("Grosime t─âlpi tf (cm)",value=1.5,key="rm_tf")
                        hwI=st.number_input("├Än─âl╚¢ime inim─â (cm)",value=20.0,key="rm_hwI")
                        twI=st.number_input("Grosime inim─â (cm)",value=1.0,key="rm_twI")
                    htot=hwI+2*tf; AI=2*bf*tf+hwI*twI; IxI=(bf*htot**3-(bf-twI)*hwI**3)/12; WxI=IxI/(htot/2)
                    with ci:
                        st.latex(rf"A={AI:.3f}\text{{ cm}}^2")
                        st.latex(rf"I_x={IxI:.3f}\text{{ cm}}^4")
                        st.latex(rf"W_x={WxI:.3f}\text{{ cm}}^3")

            with tab2:
                st.subheader("├Äntindere ╚Öi Compresiune Axial─â")
                with st.expander("Teorie (481-0.pdf, Cap.2)"):
                    st.latex(r"\sigma=\frac{N}{A}\leq f_d,\; \varepsilon=\frac{\sigma}{E},\; \Delta l=\frac{NL}{EA}")
                c1,c2=st.columns(2)
                with c1:
                    Ntc=st.number_input("For╚¢─â axial─â N (kN) [+ ├«ntindere]",value=100.0,step=10.0,key="rm_N")
                    Ltc=st.number_input("Lungime L (m)",min_value=0.01,value=3.0,key="rm_L")
                    btc=st.number_input("L─â╚¢ime b (cm)",min_value=0.1,value=20.0,key="rm_btc")
                    htc=st.number_input("├Än─âl╚¢ime h (cm)",min_value=0.1,value=30.0,key="rm_htc")
                with c2:
                    matc=st.selectbox("Material",["Beton C25/30","Beton C30/37","O╚¢el S235","O╚¢el S275","O╚¢el S355"],key="rm_matc")
                    Ecd={"Beton C25/30":31000,"Beton C30/37":33000,"O╚¢el S235":210000,"O╚¢el S275":210000,"O╚¢el S355":210000}
                    fdd={"Beton C25/30":1.67,"Beton C30/37":2.0,"O╚¢el S235":23.5,"O╚¢el S275":27.5,"O╚¢el S355":35.5}
                    Etc=Ecd[matc]; fdtc=fdd[matc]; st.info(f"E={Etc} kN/cm┬▓ | f_d={fdtc} kN/cm┬▓")
                Atc=btc*htc; sigma=Ntc/Atc; eps=sigma/Etc; dl=Ntc*Ltc*100/(Etc*Atc)
                st.latex(rf"A={btc:.1f}\times{htc:.1f}={Atc:.2f}\text{{ cm}}^2")
                st.latex(rf"\sigma=\frac{{N}}{{A}}=\frac{{{Ntc:.2f}}}{{{Atc:.2f}}}={sigma:.4f}\text{{ kN/cm}}^2={sigma*10:.3f}\text{{ MPa}}")
                st.latex(rf"\varepsilon={eps:.2e},\; \Delta l={dl:.4f}\text{{ cm}}")
                if abs(sigma)<=fdtc: st.success(f"VERIFICARE OK: |╧â|={abs(sigma):.4f}Γëñf_d={fdtc}")
                else:
                    st.error(f"DEP─é╚ÿIT─é: |╧â|={abs(sigma):.4f}>f_d={fdtc}")
                    st.warning(f"A_nec={abs(Ntc)/fdtc:.2f} cm┬▓")
                fig_tc,ax_tc=plt.subplots(figsize=(9,3),dpi=120)
                cc="#1a6faf" if Ntc>=0 else "#d62728"
                ax_tc.fill_between([0,Ltc],[Ntc,Ntc],0,color=cc,alpha=0.35); ax_tc.plot([0,Ltc],[Ntc,Ntc],color=cc,lw=3)
                ax_tc.axhline(0,color="k",lw=1.5); ax_tc.set_xlabel("x(m)"); ax_tc.set_ylabel("N(kN)",color=cc)
                ax_tc.set_title(f"Diagram─â N | {'├Äntindere' if Ntc>=0 else 'Compresiune'}",fontweight="bold")
                ax_tc.text(Ltc/2,Ntc*0.7 if abs(Ntc)>0 else 0.5,f"N={Ntc:.2f}kN",ha="center",color=cc,fontsize=11,fontweight="bold")
                plt.tight_layout(); st.pyplot(fig_tc); plt.close(fig_tc)

            with tab3:
                st.subheader("Invoiere Plan─â ΓÇö Formula Navier")
                with st.expander("Teorie (481-0.pdf, Cap.4)"):
                    st.latex(r"\sigma_x(y)=\frac{M}{I_x}\cdot y,\; \sigma_{max}=\frac{M}{W_x},\; W_x=\frac{I_x}{y_{max}}")
                c1,c2=st.columns(2)
                with c1:
                    Mnc=st.number_input("Moment M (kNm)",value=50.0,step=5.0,key="rm_Mnc")
                    bnc=st.number_input("L─â╚¢ime b (cm)",min_value=0.1,value=20.0,key="rm_bnc")
                    hnc=st.number_input("├Än─âl╚¢ime h (cm)",min_value=0.1,value=40.0,key="rm_hnc")
                with c2:
                    matnc=st.selectbox("Material",["Beton C25/30","Beton C30/37","O╚¢el S235","O╚¢el S275","O╚¢el S355"],key="rm_matnc")
                    fdnc={"Beton C25/30":1.67,"Beton C30/37":2.0,"O╚¢el S235":23.5,"O╚¢el S275":27.5,"O╚¢el S355":35.5}[matnc]
                Ixnc=bnc*hnc**3/12; Wxnc=Ixnc/(hnc/2); Mcm=Mnc*100; smax=Mcm/Wxnc
                st.latex(rf"I_x=\frac{{bh^3}}{{12}}={Ixnc:.2f}\text{{ cm}}^4,\; W_x={Wxnc:.2f}\text{{ cm}}^3")
                st.latex(rf"\sigma_{{max}}=\frac{{M}}{{W_x}}=\frac{{{Mcm:.1f}}}{{{Wxnc:.2f}}}={smax:.4f}\text{{ kN/cm}}^2={smax*10:.3f}\text{{ MPa}}")
                if abs(smax)<=fdnc: st.success(f"VERIFICARE OK: ╧â={abs(smax):.4f}Γëñf_d={fdnc}")
                else:
                    st.error(f"DEP─é╚ÿIT─é: ╧â={abs(smax):.4f}>f_d={fdnc}")
                    st.warning(f"W_nec={Mcm/fdnc:.2f} cm┬│")
                fig_nc,ax_nc=plt.subplots(figsize=(5,5),dpi=120)
                ync=np.linspace(-hnc/2,hnc/2,200); snc=Mcm/Ixnc*ync
                ax_nc.fill_betweenx(ync,snc,0,color="#d62728",alpha=0.35); ax_nc.plot(snc,ync,"r-",lw=2.5)
                ax_nc.axvline(0,color="k",lw=1.5); ax_nc.axhline(0,color="gray",ls="--",lw=1,label="Ax─â neutr─â")
                ax_nc.set_xlabel("╧â(kN/cm┬▓)"); ax_nc.set_ylabel("y(cm)"); ax_nc.legend()
                ax_nc.set_title("Distribu╚¢ie tensiuni ╧â(y)",fontweight="bold"); plt.tight_layout(); st.pyplot(fig_nc); plt.close(fig_nc)

            with tab4:
                st.subheader("Forfecare ╚Öi Torsiune")
                sub1,sub2=st.tabs(["Forfecare","Torsiune"])
                with sub1:
                    with st.expander("Teorie"):
                        st.latex(r"\tau=\frac{T S_x^*}{I_x b},\; \tau_{max}^{drept}=\frac{3T}{2A}")
                    c1,c2=st.columns(2)
                    with c1:
                        Tff=st.number_input("For╚¢─â t─âietoare T(kN)",value=80.0,key="rm_Tff")
                        bff=st.number_input("L─â╚¢ime b(cm)",min_value=0.1,value=20.0,key="rm_bff")
                        hff=st.number_input("├Än─âl╚¢ime h(cm)",min_value=0.1,value=40.0,key="rm_hff")
                    Aff=bff*hff; Ixff=bff*hff**3/12; tmx=1.5*Tff/Aff
                    with c2:
                        st.latex(rf"\tau_{{max}}=\frac{{3T}}{{2A}}=\frac{{3\times{Tff:.2f}}}{{2\times{Aff:.2f}}}={tmx:.4f}\text{{ kN/cm}}^2={tmx*10:.3f}\text{{ MPa}}")
                    yarr=np.linspace(-hff/2,hff/2,200); Sarr=bff*(hff**2/8-yarr**2/2); tarr=Tff*Sarr/(Ixff*bff)
                    fig_ff,ax_ff=plt.subplots(figsize=(5,4.5),dpi=120)
                    ax_ff.fill_betweenx(yarr,tarr,0,color="#2ca02c",alpha=0.35); ax_ff.plot(tarr,yarr,"g-",lw=2.5)
                    ax_ff.axvline(0,color="k",lw=1.5); ax_ff.axhline(0,color="gray",ls="--",lw=1)
                    ax_ff.set_xlabel("╧ä(kN/cm┬▓)"); ax_ff.set_ylabel("y(cm)"); ax_ff.set_title("Distribu╚¢ie ╧ä Zhuravski",fontweight="bold")
                    plt.tight_layout(); st.pyplot(fig_ff); plt.close(fig_ff)
                with sub2:
                    with st.expander("Teorie"):
                        st.latex(r"\tau_{tors}=\frac{M_t}{W_p},\; \varphi=\frac{M_t L}{G I_p}")
                    c1,c2=st.columns(2)
                    with c1:
                        Mt=st.number_input("M_t (kNm)",value=10.0,key="rm_Mt"); dt=st.number_input("d(cm)",min_value=0.1,value=10.0,key="rm_dt")
                        Lt=st.number_input("L(m)",min_value=0.01,value=2.0,key="rm_Lt"); Gt=st.number_input("G(kN/cm┬▓)",value=8100.0,key="rm_Gt")
                    Mtcm=Mt*100; Ipt=np.pi*dt**4/32; Wpt=Ipt/(dt/2); taut=Mtcm/Wpt; phit=Mtcm*Lt*100/(Gt*Ipt)
                    with c2:
                        st.latex(rf"I_p=\frac{{\pi d^4}}{{32}}={Ipt:.3f}\text{{ cm}}^4")
                        st.latex(rf"\tau_{{tors}}=\frac{{M_t}}{{W_p}}={taut:.4f}\text{{ kN/cm}}^2={taut*10:.3f}\text{{ MPa}}")
                        st.latex(rf"\varphi={phit:.5f}\text{{ rad}}={np.degrees(phit):.4f}\degree")

            with tab5:
                st.subheader("Flambaj Euler ΓÇö Bare Comprimate")
                with st.expander("Teorie (481-0.pdf, Cap.7)"):
                    st.latex(r"N_{cr}=\frac{\pi^2 E I_{min}}{(\mu L)^2},\; \lambda=\frac{\mu L}{i_{min}},\; \sigma_{cr}=\frac{N_{cr}}{A}")
                    st.markdown("| Rezemare | ╬╝ |\n|---|---|\n| Art-Art | 1.0 |\n| ├Äncast-Liber | 2.0 |\n| ├Äncast-Art | 0.7 |\n| ├Äncast-├Äncast | 0.5 |")
                c1,c2=st.columns(2)
                with c1:
                    Lfl=st.number_input("L(m)",min_value=0.01,value=4.0,key="rm_Lfl"); bfl=st.number_input("b(cm)",min_value=0.1,value=15.0,key="rm_bfl"); hfl=st.number_input("h(cm)",min_value=0.1,value=20.0,key="rm_hfl")
                    cfl=st.selectbox("Rezemare",["Art-Art (╬╝=1.0)","├Äncast-Liber (╬╝=2.0)","├Äncast-Art (╬╝=0.7)","├Äncast-├Äncast (╬╝=0.5)"],key="rm_cfl")
                    mfl=st.selectbox("Material",["O╚¢el S235","O╚¢el S275","O╚¢el S355","Beton C25/30","Beton C30/37"],key="rm_mfl")
                mud={"Art-Art (╬╝=1.0)":1.0,"├Äncast-Liber (╬╝=2.0)":2.0,"├Äncast-Art (╬╝=0.7)":0.7,"├Äncast-├Äncast (╬╝=0.5)":0.5}
                mu=mud[cfl]; Efd={"O╚¢el S235":21000,"O╚¢el S275":21000,"O╚¢el S355":21000,"Beton C25/30":3100,"Beton C30/37":3300}; Efl=Efd[mfl]
                Afl=bfl*hfl; Imin=min(bfl*hfl**3,hfl*bfl**3)/12; imin=np.sqrt(Imin/Afl); Lcm=Lfl*100
                Ncr=np.pi**2*Efl*Imin/(mu*Lcm)**2; lam=mu*Lcm/imin; scr=np.pi**2*Efl/lam**2
                with c2:
                    st.latex(rf"I_{{min}}={Imin:.3f}\text{{ cm}}^4,\; i_{{min}}={imin:.4f}\text{{ cm}}")
                    st.latex(rf"\lambda={lam:.2f},\; N_{{cr}}={Ncr:.2f}\text{{ kN}}")
                    st.latex(rf"\sigma_{{cr}}={scr:.4f}\text{{ kN/cm}}^2={scr*10:.3f}\text{{ MPa}}")
                if lam>100: st.info(f"╬╗={lam:.1f}>100 Euler valabil")
                elif lam>60: st.warning(f"╬╗={lam:.1f} intermediar")
                else: st.success(f"╬╗={lam:.1f}Γëñ60 bar─â scurt─â")
                fig_fl,ax_fl=plt.subplots(figsize=(9,4),dpi=120)
                Lr=np.linspace(0.5,max(Lfl*2,10),200); Ncr_r=np.pi**2*Efl*Imin/(mu*Lr*100)**2
                ax_fl.plot(Lr,Ncr_r,"#d62728",lw=2.5); ax_fl.axvline(Lfl,color="gray",ls="--",lw=1.5,label=f"L={Lfl}m")
                ax_fl.axhline(Ncr,color="orange",ls="--",lw=1.5,label=f"Ncr={Ncr:.2f}kN"); ax_fl.scatter([Lfl],[Ncr],color="red",s=80,zorder=5)
                ax_fl.set_xlabel("L(m)"); ax_fl.set_ylabel("Ncr(kN)"); ax_fl.set_title("Curba Euler",fontweight="bold")
                ax_fl.legend(fontsize=9); ax_fl.grid(True,alpha=0.25); plt.tight_layout(); st.pyplot(fig_fl); plt.close(fig_fl)

        # ============================================================
        # MODUL 3: STATICA 1
        # ============================================================
        elif modul == "Statica 1 ΓÇö Static Determinate":
            st.title("Statica 1 ΓÇö Structuri Static Determinate")
            st.markdown("Calcul conform *Statica ΓÇö Structuri Static Determinate* (975-4.pdf)")
            st.markdown("---")
            tip_struct=st.sidebar.selectbox("Tip Structur─â",["Grind─â Simpl─â","Grind─â Gerber","Cadre 2D","Arc cu 3 Articula╚¢ii","Z─âbrele"],key="s1_tip")

            # ---- GRINDA SIMPLA ----
            if tip_struct=="Grind─â Simpl─â":
                st.header("Grind─â Dreapt─â Static Determinat─â")
                with st.expander("Teorie (975-4.pdf, Cap.1)"):
                    st.markdown("**3 ecua╚¢ii de echilibru:** ╬úFx=0, ╬úFy=0, ╬úMA=0")
                    st.latex(r"V_B=\frac{Q x_Q+P a+M_0}{L},\; V_A=Q+P-V_B")
                    st.latex(r"T(x)=V_A-q(x-x_1)H(x-x_1)-PH(x-a),\; M(x)=V_Ax-\ldots")
                c1,c2=st.columns(2)
                with c1:
                    Ls=st.number_input("Lungime L(m)",min_value=0.1,value=6.0,step=0.5,key="s1_L")
                    qs=st.number_input("q distribuit (kN/m)",value=10.0,step=1.0,key="s1_q")
                    qx1=st.number_input("q de la x1(m)",min_value=0.0,value=0.0,key="s1_qx1")
                    qx2=st.number_input("q pana la x2(m)",min_value=0.0,value=float(Ls),key="s1_qx2")
                with c2:
                    Ps=st.number_input("For╚¢─â P(kN)",value=0.0,step=5.0,key="s1_P")
                    as_=st.number_input("Poz P fa╚¢─â de A(m)",min_value=0.0,value=float(Ls)/2,key="s1_a")
                    M0s=st.number_input("Moment M0(kNm)",value=0.0,step=5.0,key="s1_M0")
                    m0p=st.number_input("Poz M0 fa╚¢─â de A(m)",min_value=0.0,value=float(Ls)/2,key="s1_m0p")
                    tipg=st.selectbox("Rezemare",["Articula╚¢ie A + Reazem simplu B","Consol─â (├Äncastrare A)"],key="s1_tipg")

                # Desen structura
                st.markdown("### Pasul 1 ΓÇö Structura cu ├Änc─ârc─âri")
                fig_s1,ax_s1=plt.subplots(figsize=(12,4.5),dpi=150)
                ax_s1.plot([0,Ls],[0,0],"k-",lw=5.5,zorder=3)
                ss=max(0.22,Ls*0.032)
                if "Articula╚¢ie" in tipg:
                    draw_pin(ax_s1,0,0,ss); draw_roller(ax_s1,Ls,0,ss)
                    ax_s1.text(0,-ss*3.5,"A",fontsize=12,fontweight="bold",ha="center")
                    ax_s1.text(Ls,-ss*3.5,"B",fontsize=12,fontweight="bold",ha="center")
                else:
                    draw_fixed_left(ax_s1,0,-ss*2,ss*4,ss)
                    ax_s1.text(-ss*2.5,0,"A",fontsize=12,fontweight="bold",ha="center")
                if qs>0 and qx2>qx1: draw_distributed_load(ax_s1,qx1,qx2,0.0,qs,f"q={qs}")
                if abs(Ps)>0: draw_force_arrow(ax_s1,as_,0,0,1 if Ps>0 else -1,f"P={abs(Ps)}kN","darkred",scale=ss*4)
                if abs(M0s)>0: draw_moment_arc(ax_s1,m0p,0,M0s,r=ss*1.8,color="purple"); ax_s1.text(m0p+ss*0.3,ss*3.5,f"M0={M0s}kNm",color="purple",fontsize=9)
                ax_s1.annotate("",xy=(Ls,-ss*5.5),xytext=(0,-ss*5.5),arrowprops=dict(arrowstyle="<->",color="#555",lw=1.3))
                ax_s1.text(Ls/2,-ss*6.5,f"L={Ls:.2f} m",ha="center",fontsize=10)
                draw_axes(ax_s1,-ss*4,-ss,length=ss*2.5,color="gray",fontsize=9)
                ax_s1.set_xlim(-ss*7,Ls+ss*7); ax_s1.set_ylim(-ss*10,ss*14)
                ax_s1.set_aspect("equal"); ax_s1.axis("off"); ax_s1.set_title("Structura cu ├Änc─ârc─âri",fontsize=13,fontweight="bold")
                st.pyplot(fig_s1); plt.close(fig_s1)

                # Calcul reactiuni
                Qs=qs*max(0.0,qx2-qx1); xQs=(qx1+qx2)/2 if Qs>0 else 0.0
                if "Articula╚¢ie" in tipg:
                    VBs=(Qs*xQs+Ps*as_+M0s)/Ls; VAs=Qs+Ps-VBs; HAs=0.0; MAs=0.0
                else:
                    VAs=Qs+Ps; HAs=0.0; MAs=Qs*xQs+Ps*as_+M0s; VBs=0.0

                st.markdown("### Pasul 2 ΓÇö Ecua╚¢ii de Echilibru")
                ce1,ce2=st.columns(2)
                with ce1:
                    st.latex(r"\sum F_x=0:\; H_A=0")
                    if "Articula╚¢ie" in tipg:
                        st.latex(r"\sum M_A=0:\; V_B\cdot L=Q x_Q+P a+M_0")
                        st.latex(r"\sum F_y=0:\; V_A+V_B=Q+P")
                    else:
                        st.latex(r"\sum F_y=0:\; V_A=Q+P")
                        st.latex(r"\sum M_A=0:\; M_A=Q x_Q+P a+M_0")
                with ce2:
                    st.latex(rf"Q=q(x_2-x_1)={qs:.2f}\times{max(0,qx2-qx1):.2f}={Qs:.3f}\text{{ kN}}")
                    if "Articula╚¢ie" in tipg:
                        st.latex(rf"V_B=\frac{{{Qs:.2f}\times{xQs:.2f}+{Ps:.2f}\times{as_:.2f}+{M0s:.2f}}}{{{Ls:.2f}}}={VBs:.4f}\text{{ kN}}")
                        st.latex(rf"V_A={VAs:.4f}\text{{ kN}}")
                    else:
                        st.latex(rf"V_A={VAs:.4f}\text{{ kN}},\; M_A={MAs:.4f}\text{{ kNm}}")

                # FBD cu reactiuni
                st.markdown("### Pasul 3 ΓÇö Diagram─â Corp Liber")
                fig_fbd,ax_fbd=plt.subplots(figsize=(12,4.5),dpi=150)
                ax_fbd.plot([0,Ls],[0,0],"k-",lw=5.5,zorder=3)
                sf=max(0.22,Ls*0.032)
                if "Articula╚¢ie" in tipg: draw_pin(ax_fbd,0,0,sf); draw_roller(ax_fbd,Ls,0,sf)
                else: draw_fixed_left(ax_fbd,0,-sf*2,sf*4,sf)
                scr=max(sf*4.5,0.9)
                if abs(VAs)>0.001:
                    ax_fbd.annotate("",xy=(0,0),xytext=(0,-scr if VAs>0 else scr),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=16))
                    ax_fbd.text(-sf*3.5,-scr*0.55 if VAs>0 else scr*0.55,f"VA={VAs:.3f}kN",color="red",fontsize=9,fontweight="bold")
                if abs(VBs)>0.001 and "Articula╚¢ie" in tipg:
                    roller_bot=-sf*2.9  # linia de jos a simbolului reazem simplu
                    if VBs>0:
                        ax_fbd.annotate("",xy=(Ls,roller_bot),xytext=(Ls,roller_bot-scr),
                                        arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=16),zorder=8)
                        ax_fbd.text(Ls+sf*0.5,roller_bot-scr*0.5,f"VB={VBs:.3f}kN",color="red",fontsize=9,fontweight="bold")
                    else:
                        ax_fbd.annotate("",xy=(Ls,0),xytext=(Ls,scr),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=16))
                        ax_fbd.text(Ls+sf*0.5,scr*0.55,f"VB={VBs:.3f}kN",color="red",fontsize=9,fontweight="bold")
                if abs(MAs)>0.001: draw_moment_arc(ax_fbd,0,0,-MAs,r=sf*2.2,color="purple"); ax_fbd.text(-sf*5.5,sf*3,f"MA={MAs:.3f}kNm",color="purple",fontsize=9)
                if qs>0 and qx2>qx1: draw_distributed_load(ax_fbd,qx1,qx2,0.0,qs,f"q={qs}")
                if abs(Ps)>0: draw_force_arrow(ax_fbd,as_,0,0,1 if Ps>0 else -1,f"P={abs(Ps)}kN","darkred",scale=scr)
                ax_fbd.set_xlim(-sf*9,Ls+sf*9); ax_fbd.set_ylim(-sf*12,sf*16)
                ax_fbd.set_aspect("equal"); ax_fbd.axis("off"); ax_fbd.set_title("Diagram─â Corp Liber cu Reac╚¢iuni",fontsize=12,fontweight="bold")
                st.pyplot(fig_fbd); plt.close(fig_fbd)

                # Diagrame NTM
                x_arr=np.linspace(0,Ls,800); T_arr=np.zeros_like(x_arr); M_arr=np.zeros_like(x_arr); N_arr=np.zeros_like(x_arr)
                if "Articula╚¢ie" in tipg:
                    for i,x in enumerate(x_arr):
                        t=VAs
                        if x>qx1 and qs>0: t-=qs*(min(x,qx2)-qx1)
                        if x>as_ and abs(Ps)>0: t-=Ps
                        T_arr[i]=t
                        m=VAs*x
                        if qs>0 and x>qx1: m-=qs/2*(min(x,qx2)-qx1)**2
                        if x>as_ and abs(Ps)>0: m-=Ps*(x-as_)
                        if x>m0p and abs(M0s)>0: m-=M0s
                        M_arr[i]=m
                else:
                    for i,x in enumerate(x_arr):
                        t=0.0; m=0.0
                        if qs>0:
                            xe1=max(x,qx1); xe2=qx2
                            if xe2>xe1: Qr=qs*(xe2-xe1); t+=Qr; m+=Qr*((xe1+xe2)/2-x)
                        if abs(Ps)>0 and x<as_: t+=Ps; m+=Ps*(as_-x)
                        if abs(M0s)>0 and x<m0p: m+=M0s
                        T_arr[i]=t; M_arr[i]=m

                st.markdown("### Pasul 4 ΓÇö Diagrame N, T, M")
                fig_ntm,(axN,axT,axM)=plt.subplots(3,1,figsize=(12,11),dpi=150,sharex=True)
                fill_diagram(axN,x_arr,N_arr,"#1a6faf","N(kN)"); axN.set_title("N(x)",fontweight="bold",color="#1a6faf"); label_extremes(axN,x_arr,N_arr,"#1a6faf")
                if np.max(N_arr)>0.01: axN.text(x_arr[np.argmax(N_arr)],N_arr[np.argmax(N_arr)]*0.5,"+",ha='center',va='center',fontsize=14,fontweight='bold',color="#1a6faf",alpha=0.75)
                if np.min(N_arr)<-0.01: axN.text(x_arr[np.argmin(N_arr)],N_arr[np.argmin(N_arr)]*0.5,"ΓêÆ",ha='center',va='center',fontsize=14,fontweight='bold',color="#1a6faf",alpha=0.75)
                fill_diagram(axT,x_arr,T_arr,"#2ca02c","T(kN)"); axT.set_title("T(x)",fontweight="bold",color="#2ca02c"); label_extremes(axT,x_arr,T_arr,"#2ca02c")
                if np.max(T_arr)>0.01: axT.text(x_arr[np.argmax(T_arr)],T_arr[np.argmax(T_arr)]*0.5,"+",ha='center',va='center',fontsize=14,fontweight='bold',color="#2ca02c",alpha=0.75)
                if np.min(T_arr)<-0.01: axT.text(x_arr[np.argmin(T_arr)],T_arr[np.argmin(T_arr)]*0.5,"ΓêÆ",ha='center',va='center',fontsize=14,fontweight='bold',color="#2ca02c",alpha=0.75)
                fill_diagram(axM,x_arr,M_arr,"#d62728","M(kNm)"); axM.set_title("M(x)",fontweight="bold",color="#d62728"); axM.invert_yaxis(); label_extremes(axM,x_arr,M_arr,"#d62728")
                if np.max(M_arr)>0.01: axM.text(x_arr[np.argmax(M_arr)],M_arr[np.argmax(M_arr)]*0.5,"+",ha='center',va='center',fontsize=14,fontweight='bold',color="#d62728",alpha=0.75)
                if np.min(M_arr)<-0.01: axM.text(x_arr[np.argmin(M_arr)],M_arr[np.argmin(M_arr)]*0.5,"ΓêÆ",ha='center',va='center',fontsize=14,fontweight='bold',color="#d62728",alpha=0.75)
                axM.set_xlabel("x(m)",fontsize=11); plt.tight_layout(); fig_ntm.suptitle("Diagrame N,T,M ΓÇö Grind─â Simpl─â",fontsize=14,fontweight="bold",y=1.01)
                st.pyplot(fig_ntm); plt.close(fig_ntm)

                # Verificare
                st.markdown("### Pasul 5 ΓÇö Verificare Echilibru")
                sFy=VAs+VBs-Qs-Ps
                sMA=VBs*Ls-Qs*xQs-Ps*as_-M0s if "Articula╚¢ie" in tipg else MAs-Qs*xQs-Ps*as_-M0s
                cv1,cv2,cv3=st.columns(3)
                _ = cv1.success(f"╬úFy={sFy:.6f}Γëê0") if abs(sFy)<0.01 else cv1.error(f"╬úFy={sFy:.6f}Γëá0")
                _ = cv2.success(f"╬úMA={sMA:.6f}Γëê0") if abs(sMA)<0.01 else cv2.error(f"╬úMA={sMA:.6f}Γëá0")
                cv3.metric("M max",f"{np.max(np.abs(M_arr)):.4f} kNm")
                with st.expander("Valori Caracteristice"):
                    idx_T0=np.where(np.diff(np.sign(T_arr)))[0]
                    st.metric("T max",f"{np.max(np.abs(T_arr)):.4f} kN")
                    for sc in idx_T0: st.info(f"T=0 la xΓëê{x_arr[sc]:.3f}m ΓåÆ M={M_arr[sc]:.4f}kNm")

            # ---- GRINDA GERBER ----
            elif tip_struct=="Grind─â Gerber":
                st.header("Grind─â Gerber (cu Articula╚¢ii Intermediare)")
                with st.expander("Teorie (975-4.pdf, Cap.2)"):
                    st.markdown("**M=0 ├«n articula╚¢ia intermediar─â.** Calcul GS ΓåÆ GP.")
                    st.latex(r"\text{Verificare: }M_B=0")
                c1,c2,c3=st.columns(3)
                with c1: LGP=st.number_input("L GP(m)",min_value=1.0,value=8.0,step=0.5,key="gerb_LGP"); qGP=st.number_input("q GP(kN/m)",min_value=0.0,value=15.0,step=1.0,key="gerb_qGP")
                with c2: LGS=st.number_input("L GS(m)",min_value=0.5,value=4.0,step=0.5,key="gerb_LGS"); qGS=st.number_input("q GS(kN/m)",min_value=0.0,value=10.0,step=1.0,key="gerb_qGS")
                with c3: PGS=st.number_input("P pe GS(kN)",min_value=0.0,value=0.0,step=5.0,key="gerb_PGS"); aPS=st.number_input("Poz P(m)",min_value=0.0,value=float(LGS)/2,key="gerb_aPS")
                QGS=qGS*LGS; VD=(QGS*LGS/2+PGS*aPS)/LGS; VB_art=QGS+PGS-VD
                xBGP=LGP-LGS; QGP=qGP*LGP; VC=(QGP*LGP/2+VB_art*xBGP)/LGP; VA_GP=QGP+VB_art-VC

                st.markdown("### Pasul 1 ΓÇö Schema Gerber")
                fig_g,ax_g=plt.subplots(figsize=(14,5.5),dpi=150)
                ax_g.plot([0,xBGP],[0,0],"k-",lw=6,zorder=3); ax_g.plot([xBGP,LGP],[0,0],"navy",lw=6,zorder=3)
                sg=max(0.22,LGP*0.027)
                draw_pin(ax_g,0,0,sg); draw_roller(ax_g,LGP*0.45,0,sg); draw_roller(ax_g,LGP,0,sg)
                ax_g.plot(xBGP,0,"ko",ms=12,zorder=7); ax_g.plot(xBGP,0,"wo",ms=6,zorder=8)
                ax_g.text(xBGP,sg*3.5,"B\n(M=0)",ha="center",fontsize=9,color="navy",fontweight="bold")
                ax_g.text(0,-sg*3.5,"A",fontsize=12,fontweight="bold",ha="center"); ax_g.text(LGP,-sg*3.5,"D",fontsize=12,fontweight="bold",ha="center")
                if qGP>0: draw_distributed_load(ax_g,0,xBGP,0.0,qGP,f"q_GP={qGP}")
                if qGS>0: draw_distributed_load(ax_g,xBGP,LGP,0.0,qGS,f"q_GS={qGS}")
                if PGS>0: draw_force_arrow(ax_g,xBGP+aPS,0,0,1,f"P={PGS}kN","darkred",scale=sg*4)
                ax_g.set_xlim(-sg*6,LGP+sg*6); ax_g.set_ylim(-sg*9,sg*18); ax_g.set_aspect("equal"); ax_g.axis("off")
                ax_g.set_title("Grind─â Gerber ΓÇö Schema de Calcul",fontsize=13,fontweight="bold"); st.pyplot(fig_g); plt.close(fig_g)

                st.markdown("### Pasul 2 ΓÇö Ecua╚¢ii Echilibru")
                cg1,cg2=st.columns(2)
                with cg1:
                    st.markdown("**GS:**"); st.latex(rf"V_D=\frac{{Q_{{GS}}L/2+Pa}}{{{LGS:.2f}}}={VD:.4f}\text{{ kN}}")
                    st.latex(rf"V_B=Q_{{GS}}+P-V_D={VB_art:.4f}\text{{ kN}}")
                with cg2:
                    st.markdown("**GP:**"); st.latex(rf"V_C=\frac{{Q_{{GP}}L/2+V_B x_B}}{{{LGP:.2f}}}={VC:.4f}\text{{ kN}}")
                    st.latex(rf"V_A={VA_GP:.4f}\text{{ kN}}")

                xGP=np.linspace(0,xBGP,400); xGS=np.linspace(xBGP,LGP,400)
                TGP=VA_GP-qGP*xGP; MGP=VA_GP*xGP-qGP*xGP**2/2
                TGS=np.zeros_like(xGS); MGS=np.zeros_like(xGS)
                for i,x in enumerate(xGS):
                    xi=x-xBGP; TGS[i]=VB_art-qGS*xi-(PGS if xi>aPS else 0); MGS[i]=VB_art*xi-qGS*xi**2/2-(PGS*(xi-aPS) if xi>aPS else 0)
                xt=np.concatenate([xGP,xGS]); Tt=np.concatenate([TGP,TGS]); Mt=np.concatenate([MGP,MGS]); Nt=np.zeros_like(xt)
                st.markdown("### Pasul 3 ΓÇö Diagrame N,T,M")
                fig_gntm,(aNg,aTg,aMg)=plt.subplots(3,1,figsize=(12,10),dpi=150,sharex=True)
                fill_diagram(aNg,xt,Nt,"#1a6faf","N(kN)"); aNg.set_title("N(x)",fontweight="bold",color="#1a6faf")
                fill_diagram(aTg,xt,Tt,"#2ca02c","T(kN)"); aTg.axvline(xBGP,color="navy",ls="--",lw=1.5); aTg.set_title("T(x)",fontweight="bold",color="#2ca02c"); label_extremes(aTg,xt,Tt)
                fill_diagram(aMg,xt,Mt,"#d62728","M(kNm)"); aMg.axvline(xBGP,color="navy",ls="--",lw=1.5); aMg.invert_yaxis(); aMg.set_title("M(x)",fontweight="bold",color="#d62728"); label_extremes(aMg,xt,Mt); aMg.set_xlabel("x(m)")
                plt.tight_layout(); st.pyplot(fig_gntm); plt.close(fig_gntm)
                Mart=MGP[-1]
                cv1,cv2,cv3=st.columns(3); cv1.metric("T max",f"{np.max(np.abs(Tt)):.3f} kN"); cv2.metric("M max",f"{np.max(np.abs(Mt)):.3f} kNm")
                _ = cv3.success(f"M_artΓëê{Mart:.5f}Γëê0") if abs(Mart)<0.05 else cv3.error(f"M_art={Mart:.5f}Γëá0")

            # ---- CADRE 2D ----
            elif tip_struct=="Cadre 2D":
                st.header("Cadre Plane Static Determinate")
                with st.expander("Teorie (975-4.pdf, Cap.3)"):
                    st.markdown("""**Nodul rigid** ΓÇö pastreaza unghiurile intre bare. **Nodul articulat** ΓÇö M=0, permite rotire relativa.
        **Cadre simplu rezemate:** 3 ecuatii de echilibru. **Cadre cu 3 articulatii:** 3 ec. globale + M=0 in articulatie.""")

                # === MOD INTRODUCERE ===
                input_mode=st.radio("Mod introducere geometrie",["Desenare (click & draw)","Manual (coordonate)"],horizontal=True,key="cad_input_mode")

                if input_mode=="Desenare (click & draw)":
                    # --- CANVAS DRAWING MODE (HTML/JS) ---
                    st.subheader("1-2. Deseneaz─â Cadrul")
                    st.caption("**Click** pe gril─â = adaug─â nod. **Click pe dou─â noduri** succesiv = bara ├«ntre ele. **Click dreapta** pe nod/bar─â = ╚Öterge.")

                    _cad_grid=st.sidebar.number_input("Gril─â (m)",min_value=0.5,max_value=2.0,value=1.0,step=0.5,key="cad_grid_m")
                    _cad_W_m=st.sidebar.number_input("L─â╚¢ime canvas (m)",min_value=4.0,max_value=30.0,value=14.0,step=1.0,key="cad_Wm")
                    _cad_H_m=st.sidebar.number_input("├Än─âl╚¢ime canvas (m)",min_value=4.0,max_value=20.0,value=10.0,step=1.0,key="cad_Hm")
                    _ppm=50
                    _cW=int(_cad_W_m*_ppm); _cH=int(_cad_H_m*_ppm)

                    # Existing data to pre-populate canvas
                    _init_nodes=json.dumps(st.session_state.get("cad_nodes",[]))
                    _init_bars=json.dumps(st.session_state.get("cad_bars",[]))

                    _canvas_html=f"""
        <div style="position:relative;display:inline-block;">
        <canvas id="cad_cv" width="{_cW}" height="{_cH}" style="border:2px solid #1a3a5c;cursor:crosshair;border-radius:6px;"></canvas>
        <div id="cad_info" style="position:absolute;top:8px;right:12px;background:rgba(255,255,255,0.92);padding:4px 10px;border-radius:4px;font:12px monospace;color:#333;pointer-events:none;"></div>
        </div>
        <div style="margin-top:6px;">
        <button onclick="undoLast()" style="padding:4px 14px;margin-right:6px;border-radius:4px;border:1px solid #888;background:#f0f0f0;cursor:pointer;">Undo</button>
        <button onclick="clearAll()" style="padding:4px 14px;margin-right:6px;border-radius:4px;border:1px solid #888;background:#f0f0f0;cursor:pointer;">Sterge tot</button>
        <button onclick="exportData()" style="padding:4px 14px;border-radius:4px;border:1px solid #1a3a5c;background:#1a3a5c;color:#fff;cursor:pointer;font-weight:bold;">Aplica in calcul</button>
        <span id="cad_status" style="margin-left:12px;font:12px sans-serif;color:#2a2;"></span>
        </div>
        <textarea id="cad_output" style="display:none;"></textarea>
        <script>
        (function(){{
        const cv=document.getElementById('cad_cv'), ctx=cv.getContext('2d');
        const PPM={_ppm}, GRID={_cad_grid}, W={_cW}, H={_cH};
        const SNAP=GRID/2;
        let nodes=[], bars=[], selNode=-1, history=[];
        const NAMES='ABCDEFGHIJKLMNOPQRSTUVWXYZ';

        // Load initial data
        try{{
            const iN={_init_nodes}, iB={_init_bars};
            if(iN.length>0){{ nodes=iN.map(n=>({{name:n.name,x:n.x,y:n.y}})); }}
            if(iB.length>0){{ bars=iB.map(b=>({{n1:b.n1,n2:b.n2}})); }}
        }}catch(e){{}}

        function toP(mx,my){{ return [mx*PPM, H-my*PPM]; }}
        function toM(px,py){{ return [snap(px/PPM), snap((H-py)/PPM)]; }}
        function snap(v){{ return Math.round(v/SNAP)*SNAP; }}
        function dist(a,b){{ return Math.sqrt((a[0]-b[0])**2+(a[1]-b[1])**2); }}

        function findNode(mx,my){{
            for(let i=0;i<nodes.length;i++){{
                if(Math.abs(nodes[i].x-mx)<0.3 && Math.abs(nodes[i].y-my)<0.3) return i;
            }}
            return -1;
        }}

        function nextName(){{
            const used=new Set(nodes.map(n=>n.name));
            for(let c of NAMES) if(!used.has(c)) return c;
            return String(nodes.length);
        }}

        function draw(){{
            ctx.clearRect(0,0,W,H);
            // Grid
            ctx.strokeStyle='#e0e0e0'; ctx.lineWidth=0.5;
            const gp=GRID*PPM;
            for(let x=0;x<=W;x+=gp){{
                ctx.strokeStyle=(x/gp)%5===0?'#bbb':'#e0e0e0';
                ctx.lineWidth=(x/gp)%5===0?1.5:0.5;
                ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
            }}
            for(let y=0;y<=H;y+=gp){{
                ctx.strokeStyle=(y/gp)%5===0?'#bbb':'#e0e0e0';
                ctx.lineWidth=(y/gp)%5===0?1.5:0.5;
                ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W,y); ctx.stroke();
            }}
            // Axis labels
            ctx.fillStyle='#888'; ctx.font='11px monospace'; ctx.textAlign='center';
            for(let x=0;x<=W;x+=gp*2) ctx.fillText((x/PPM).toFixed(0),x,H-3);
            ctx.textAlign='left';
            for(let y=0;y<=H;y+=gp*2) ctx.fillText(((H-y)/PPM).toFixed(0),3,y+12);
            // Bars
            ctx.strokeStyle='#1a3a5c'; ctx.lineWidth=5; ctx.lineCap='round';
            for(const b of bars){{
                const n1=nodes.find(n=>n.name===b.n1), n2=nodes.find(n=>n.name===b.n2);
                if(!n1||!n2) continue;
                const[x1,y1]=toP(n1.x,n1.y),[x2,y2]=toP(n2.x,n2.y);
                ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
            }}
            // Nodes
            for(let i=0;i<nodes.length;i++){{
                const[px,py]=toP(nodes[i].x,nodes[i].y);
                ctx.beginPath(); ctx.arc(px,py,7,0,Math.PI*2);
                ctx.fillStyle=i===selNode?'#e63946':'#0d1b2a'; ctx.fill();
                ctx.fillStyle='#0d1b2a'; ctx.font='bold 13px sans-serif'; ctx.textAlign='center';
                ctx.fillText(nodes[i].name, px, py-12);
            }}
            // Info
            document.getElementById('cad_info').textContent=nodes.length+' noduri, '+bars.length+' bare';
        }}

        cv.addEventListener('click',function(e){{
            const rect=cv.getBoundingClientRect();
            const px=e.clientX-rect.left, py=e.clientY-rect.top;
            const[mx,my]=toM(px,py);
            const hit=findNode(mx,my);
            if(hit>=0){{
                if(selNode>=0 && selNode!==hit){{
                    const n1=nodes[selNode].name, n2=nodes[hit].name;
                    if(!bars.some(b=>(b.n1===n1&&b.n2===n2)||(b.n1===n2&&b.n2===n1))){{
                        bars.push({{n1,n2}});
                        history.push({{type:'bar',n1,n2}});
                    }}
                    selNode=-1;
                }} else {{
                    selNode=hit;
                }}
            }} else {{
                nodes.push({{name:nextName(),x:mx,y:my}});
                history.push({{type:'node',name:nodes[nodes.length-1].name}});
                selNode=-1;
            }}
            draw();
        }});

        cv.addEventListener('contextmenu',function(e){{
            e.preventDefault();
            const rect=cv.getBoundingClientRect();
            const px=e.clientX-rect.left, py=e.clientY-rect.top;
            const[mx,my]=toM(px,py);
            const hit=findNode(mx,my);
            if(hit>=0){{
                const nm=nodes[hit].name;
                bars=bars.filter(b=>b.n1!==nm&&b.n2!==nm);
                nodes.splice(hit,1);
                selNode=-1;
            }} else {{
                // Try removing nearest bar
                let bestD=20/PPM, bestI=-1;
                for(let i=0;i<bars.length;i++){{
                    const n1=nodes.find(n=>n.name===bars[i].n1), n2=nodes.find(n=>n.name===bars[i].n2);
                    if(!n1||!n2) continue;
                    const dx=n2.x-n1.x, dy=n2.y-n1.y, L=Math.sqrt(dx*dx+dy*dy);
                    if(L<0.01) continue;
                    const t=Math.max(0,Math.min(1,((mx-n1.x)*dx+(my-n1.y)*dy)/(L*L)));
                    const cx=n1.x+t*dx, cy=n1.y+t*dy;
                    const d=Math.sqrt((mx-cx)**2+(my-cy)**2);
                    if(d<bestD){{ bestD=d; bestI=i; }}
                }}
                if(bestI>=0) bars.splice(bestI,1);
            }}
            draw();
        }});

        cv.addEventListener('mousemove',function(e){{
            const rect=cv.getBoundingClientRect();
            const px=e.clientX-rect.left, py=e.clientY-rect.top;
            const[mx,my]=toM(px,py);
            cv.title=mx.toFixed(1)+', '+my.toFixed(1)+' m';
        }});

        window.undoLast=function(){{
            if(history.length===0) return;
            const last=history.pop();
            if(last.type==='node'){{
                const idx=nodes.findIndex(n=>n.name===last.name);
                if(idx>=0){{ bars=bars.filter(b=>b.n1!==last.name&&b.n2!==last.name); nodes.splice(idx,1); }}
            }} else if(last.type==='bar'){{
                const idx=bars.findIndex(b=>b.n1===last.n1&&b.n2===last.n2);
                if(idx>=0) bars.splice(idx,1);
            }}
            selNode=-1; draw();
        }};

        window.clearAll=function(){{ nodes=[]; bars=[]; selNode=-1; history=[]; draw(); }};

        window.exportData=function(){{
            const data=JSON.stringify({{nodes:nodes,bars:bars}});
            // Write to Streamlit via hidden textarea + fragment hack
            const ta=document.getElementById('cad_output');
            ta.value=data;
            // Use Streamlit's setFrameHeight to signal, and pass data via URL fragment
            const url=new URL(window.parent.location);
            url.searchParams.set('cad_draw_data',encodeURIComponent(data));
            window.parent.history.replaceState(null,'',url);
            document.getElementById('cad_status').textContent='Aplicat! Reincarca pagina (F5) pentru calcul.';
            // Auto-reload after short delay
            setTimeout(function(){{ window.parent.location.reload(); }}, 400);
        }};

        draw();
        }})();
        </script>
        """
                    components.html(_canvas_html, height=_cH+60, scrolling=False)

                    # Read data back from query params
                    _qp=st.query_params
                    _draw_data=_qp.get("cad_draw_data","")
                    if _draw_data:
                        try:
                            _parsed=json.loads(_draw_data)
                            _canvas_nodes=_parsed.get("nodes",[])
                            _canvas_bars=_parsed.get("bars",[])
                            if _canvas_nodes:
                                st.session_state.cad_nodes=[{"name":n["name"],"x":round(n["x"],2),"y":round(n["y"],2)} for n in _canvas_nodes]
                                st.session_state.cad_bars=[{"n1":b["n1"],"n2":b["n2"]} for b in _canvas_bars]
                                valid_names={n["name"] for n in _canvas_nodes}
                                st.session_state.cad_sup=[s for s in st.session_state.get("cad_sup",[]) if s["node"] in valid_names]
                                if not st.session_state.cad_sup and len(_canvas_nodes)>=2:
                                    st.session_state.cad_sup=[{"node":_canvas_nodes[0]["name"],"tip":1},{"node":_canvas_nodes[-1]["name"],"tip":2}]
                        except: pass

                    # Show detected geometry
                    _cur_nodes=st.session_state.get("cad_nodes",[])
                    _cur_bars=st.session_state.get("cad_bars",[])
                    if _cur_nodes:
                        nc1,nc2=st.columns(2)
                        with nc1:
                            st.markdown("**Noduri:**")
                            for nd in _cur_nodes:
                                st.text(f"  {nd['name']}: ({nd['x']:.1f}, {nd['y']:.1f}) m")
                        with nc2:
                            st.markdown("**Bare:**")
                            for i,br in enumerate(_cur_bars):
                                st.text(f"  Bara {i+1}: {br['n1']} -> {br['n2']}")
                    else:
                        st.info("Click pe gril─â pentru a ad─âuga noduri. Click pe dou─â noduri pentru a crea o bar─â.")

                else:
                    # --- MANUAL INPUT MODE ---
                    st.subheader("1. Noduri")
                    if "cad_nodes" not in st.session_state:
                        st.session_state.cad_nodes=[
                            {"name":"A","x":0.0,"y":0.0},
                            {"name":"1","x":0.0,"y":4.0},
                            {"name":"2","x":6.0,"y":4.0},
                            {"name":"B","x":6.0,"y":0.0}]
                    nc1,nc2=st.columns([1,5])
                    with nc1:
                        if st.button("+ Nod",key="cad_nadd"):
                            nn=len(st.session_state.cad_nodes)
                            st.session_state.cad_nodes.append({"name":str(nn),"x":3.0,"y":2.0})
                        if st.button("- Nod",key="cad_ndel"):
                            if len(st.session_state.cad_nodes)>2: st.session_state.cad_nodes.pop()
                    nodes_ed=[]
                    ncols=st.columns(min(len(st.session_state.cad_nodes),5))
                    for i,nd in enumerate(st.session_state.cad_nodes):
                        with ncols[i%5]:
                            nm=st.text_input(f"Nume",value=nd["name"],key=f"cad_nn_{i}")
                            nx_=st.number_input(f"x (m)",value=float(nd["x"]),step=0.5,key=f"cad_nx_{i}")
                            ny_=st.number_input(f"y (m)",value=float(nd["y"]),step=0.5,key=f"cad_ny_{i}")
                            nodes_ed.append({"name":nm,"x":nx_,"y":ny_})
                    st.session_state.cad_nodes=nodes_ed

                    st.subheader("2. Bare")
                    if "cad_bars" not in st.session_state:
                        st.session_state.cad_bars=[
                            {"n1":"A","n2":"1"},{"n1":"1","n2":"2"},{"n1":"2","n2":"B"}]
                    node_names_m=[n["name"] for n in st.session_state.cad_nodes]
                    bc1,bc2=st.columns([1,5])
                    with bc1:
                        if st.button("+ Bara",key="cad_badd"):
                            st.session_state.cad_bars.append({"n1":node_names_m[0],"n2":node_names_m[-1]})
                        if st.button("- Bara",key="cad_bdel"):
                            if len(st.session_state.cad_bars)>1: st.session_state.cad_bars.pop()
                    bars_ed_m=[]
                    bcols=st.columns(min(len(st.session_state.cad_bars),4))
                    for i,br in enumerate(st.session_state.cad_bars):
                        with bcols[i%4]:
                            st.markdown(f"**Bara {i+1}**")
                            n1s=st.selectbox("De la",node_names_m,index=node_names_m.index(br["n1"]) if br["n1"] in node_names_m else 0,key=f"cad_bn1_{i}")
                            n2s=st.selectbox("La",node_names_m,index=node_names_m.index(br["n2"]) if br["n2"] in node_names_m else min(1,len(node_names_m)-1),key=f"cad_bn2_{i}")
                            bars_ed_m.append({"n1":n1s,"n2":n2s})
                    st.session_state.cad_bars=bars_ed_m

                # Common: read from session state
                nodes=st.session_state.cad_nodes
                node_names=[n["name"] for n in nodes]
                bars_ed=st.session_state.cad_bars

                # === REAZEME ===
                st.subheader("3. Reazeme")
                ro_lbl_c={0:"Liber",1:"Articulatie (pin)",2:"Reazem simplu (roller)",3:"Incastrare"}
                if "cad_sup" not in st.session_state:
                    st.session_state.cad_sup=[{"node":"A","tip":1},{"node":"B","tip":2}]
                sc1,sc2=st.columns([1,5])
                with sc1:
                    if st.button("+ Reazem",key="cad_sadd"):
                        st.session_state.cad_sup.append({"node":node_names[0],"tip":2})
                    if st.button("- Reazem",key="cad_sdel"):
                        if len(st.session_state.cad_sup)>1: st.session_state.cad_sup.pop()
                sup_ed=[]
                scols=st.columns(min(len(st.session_state.cad_sup),4))
                for i,sp in enumerate(st.session_state.cad_sup):
                    with scols[i%4]:
                        sn=st.selectbox(f"Nod reazem {i+1}",node_names,index=node_names.index(sp["node"]) if sp["node"] in node_names else 0,key=f"cad_sn_{i}")
                        st_=st.selectbox(f"Tip reazem {i+1}",[0,1,2,3],index=[0,1,2,3].index(sp["tip"]),format_func=lambda x:ro_lbl_c[x],key=f"cad_st_{i}")
                        sup_ed.append({"node":sn,"tip":st_})
                st.session_state.cad_sup=sup_ed

                # Grad static
                total_r=sum([2 if s["tip"]==1 else 1 if s["tip"]==2 else 3 if s["tip"]==3 else 0 for s in sup_ed])
                n_eq=3
                G_val=total_r-n_eq
                if G_val==0: st.success(f"Static determinat -- {total_r} reactiuni, {n_eq} ecuatii")
                elif G_val>0: st.warning(f"Static nedeterminat ns={G_val}")
                else: st.error(f"MECANISM G={G_val}")

                # === INCARCARI ===
                st.subheader("4. Incarcari")
                st.markdown("**Incarcari distribuite**")
                bar_labels=[f"{b['n1']}-{b['n2']}" for b in bars_ed]
                if "cad_qdist" not in st.session_state:
                    st.session_state.cad_qdist=[]
                qb1,qb2=st.columns([1,5])
                with qb1:
                    if st.button("+ q dist.",key="cad_qadd"):
                        st.session_state.cad_qdist.append({"bar":0,"q":10.0,"dir":"Perpendicular pe bara (in jos)"})
                    if st.button("- q dist.",key="cad_qdel"):
                        if st.session_state.cad_qdist: st.session_state.cad_qdist.pop()
                qdist_ed=[]
                if st.session_state.cad_qdist:
                    qcols=st.columns(min(len(st.session_state.cad_qdist),3))
                    for i,qd in enumerate(st.session_state.cad_qdist):
                        with qcols[i%3]:
                            st.markdown(f"**q {i+1}**")
                            bi=st.selectbox("Bara",range(len(bar_labels)),index=min(qd["bar"],len(bar_labels)-1),format_func=lambda x:bar_labels[x],key=f"cad_qb_{i}")
                            qv=st.number_input("q (kN/m)",value=float(qd["q"]),step=1.0,key=f"cad_qv_{i}")
                            qdir=st.selectbox("Directie",["Perpendicular pe bara (in jos)","Vertical (in jos)","Vertical (in sus)"],key=f"cad_qdir_{i}")
                            qdist_ed.append({"bar":bi,"q":qv,"dir":qdir})
                st.session_state.cad_qdist=qdist_ed

                st.markdown("**Forte concentrate si momente**")
                if "cad_forces" not in st.session_state:
                    st.session_state.cad_forces=[]
                fb1,fb2=st.columns([1,5])
                with fb1:
                    if st.button("+ Forta/Moment",key="cad_fadd"):
                        st.session_state.cad_forces.append({"tip":"F","node":node_names[1] if len(node_names)>1 else node_names[0],"Fx":0.0,"Fy":-10.0,"M":0.0})
                    if st.button("- Forta/Moment",key="cad_fdel"):
                        if st.session_state.cad_forces: st.session_state.cad_forces.pop()
                forces_ed=[]
                if st.session_state.cad_forces:
                    fcols=st.columns(min(len(st.session_state.cad_forces),3))
                    for i,fc in enumerate(st.session_state.cad_forces):
                        with fcols[i%3]:
                            st.markdown(f"**Incarcare {i+1}**")
                            ft=st.selectbox("Tip",["Forta","Moment concentrat"],index=0 if fc["tip"]=="F" else 1,key=f"cad_ft_{i}")
                            fn=st.selectbox("In nodul",node_names,index=node_names.index(fc["node"]) if fc["node"] in node_names else 0,key=f"cad_fn_{i}")
                            if ft=="Forta":
                                ffx=st.number_input("Fx (kN) [+ dreapta]",value=float(fc.get("Fx",0.0)),step=1.0,key=f"cad_ffx_{i}")
                                ffy=st.number_input("Fy (kN) [+ sus, - jos]",value=float(fc.get("Fy",-10.0)),step=1.0,key=f"cad_ffy_{i}")
                                forces_ed.append({"tip":"F","node":fn,"Fx":ffx,"Fy":ffy,"M":0.0})
                            else:
                                fm=st.number_input("M (kNm) [+ antiorar]",value=float(fc.get("M",0.0)),step=1.0,key=f"cad_fm_{i}")
                                forces_ed.append({"tip":"M","node":fn,"Fx":0.0,"Fy":0.0,"M":fm})
                st.session_state.cad_forces=forces_ed

                # === CALCUL (anastruct) ===
                def get_node(name):
                    for n in nodes:
                        if n["name"]==name: return n["x"],n["y"]
                    return 0.0,0.0

                # Build anastruct model
                ss_cad=SystemElements()
                # Map node names to anastruct node IDs
                cad_node_id={}  # node_name -> anastruct node_id
                cad_elem_id={}  # bar_index -> anastruct element_id
                for i_br,br in enumerate(bars_ed):
                    x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
                    eid=ss_cad.add_element(location=[[x1b,y1b],[x2b,y2b]])
                    cad_elem_id[i_br]=eid
                    el=ss_cad.element_map[eid]
                    cad_node_id[br["n1"]]=el.node_id1
                    cad_node_id[br["n2"]]=el.node_id2

                # Supports
                for sp in sup_ed:
                    nid=cad_node_id.get(sp["node"])
                    if nid is None: continue
                    if sp["tip"]==1: ss_cad.add_support_hinged(node_id=nid)
                    elif sp["tip"]==2: ss_cad.add_support_roll(node_id=nid)
                    elif sp["tip"]==3: ss_cad.add_support_fixed(node_id=nid)

                # Distributed loads
                for qd in qdist_ed:
                    if qd["bar"]>=len(bars_ed): continue
                    eid=cad_elem_id[qd["bar"]]
                    qv=qd["q"]
                    if "Perpendicular" in qd["dir"]:
                        ss_cad.q_load(element_id=eid, q=-qv)
                    elif "in jos" in qd["dir"]:
                        ss_cad.q_load(element_id=eid, q=-qv, direction="y")
                    else:
                        ss_cad.q_load(element_id=eid, q=qv, direction="y")

                # Point loads and moments
                for fc in forces_ed:
                    nid=cad_node_id.get(fc["node"])
                    if nid is None: continue
                    if fc["tip"]=="F":
                        if abs(fc["Fx"])>1e-9: ss_cad.point_load(node_id=nid, Fx=fc["Fx"])
                        if abs(fc["Fy"])>1e-9: ss_cad.point_load(node_id=nid, Fy=fc["Fy"])
                    elif fc["tip"]=="M" and abs(fc["M"])>1e-9:
                        ss_cad.moment_load(node_id=nid, Ty=fc["M"])

                # Solve
                reactions={}; solved=False
                sumFx_ext=0.0; sumFy_ext=0.0
                try:
                    ss_cad.solve()
                    solved=True
                    # Extract reactions at support nodes
                    for sp in sup_ed:
                        nid=cad_node_id.get(sp["node"])
                        if nid is None: continue
                        r=ss_cad.get_node_results_system(node_id=nid)
                        reactions[sp["node"]]={"Fx":float(r["Fx"]),"Fy":float(r["Fy"]),"M":float(r["Tz"])}
                    # Compute external force sums for equilibrium check
                    for fc in forces_ed:
                        if fc["tip"]=="F":
                            sumFx_ext+=fc["Fx"]; sumFy_ext+=fc["Fy"]
                    for qd in qdist_ed:
                        if qd["bar"]>=len(bars_ed): continue
                        br=bars_ed[qd["bar"]]
                        x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
                        Lb=np.sqrt((x2b-x1b)**2+(y2b-y1b)**2)
                        if "in sus" in qd["dir"]: sumFy_ext+=qd["q"]*Lb
                        else: sumFy_ext-=qd["q"]*Lb
                except Exception as ex:
                    st.error(f"Eroare la rezolvare: {ex}")

                # === PASUL 1: SCHEMA ===
                st.markdown("### Pasul 1 -- Schema Cadrului")
                all_x=[n["x"] for n in nodes]; all_y=[n["y"] for n in nodes]
                dim=max(max(all_x)-min(all_x),max(all_y)-min(all_y),1.0)
                sc=max(0.18,dim*0.028)
                fig_s,ax_s=plt.subplots(figsize=(13,10),dpi=150)
                for br in bars_ed:
                    x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
                    ax_s.plot([x1b,x2b],[y1b,y2b],"k-",lw=5,zorder=3)
                for nd in nodes:
                    ax_s.plot(nd["x"],nd["y"],"ko",ms=6,zorder=6)
                    ax_s.text(nd["x"]-sc*1.5,nd["y"]+sc*1.5,nd["name"],fontsize=12,fontweight="bold",color="navy",zorder=7)
                for sp in sup_ed:
                    xn,yn=get_node(sp["node"])
                    if sp["tip"]==1: draw_pin(ax_s,xn,yn,sc)
                    elif sp["tip"]==2: draw_roller(ax_s,xn,yn,sc)
                    elif sp["tip"]==3: draw_fixed_bottom(ax_s,xn,yn,size=sc)
                for qd in qdist_ed:
                    if qd["bar"]>=len(bars_ed): continue
                    br=bars_ed[qd["bar"]]
                    x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
                    dxb,dyb=x2b-x1b,y2b-y1b; Lb=np.sqrt(dxb**2+dyb**2)
                    if Lb<1e-9: continue
                    cb,sb=dxb/Lb,dyb/Lb
                    if "Perpendicular" in qd["dir"]:
                        draw_distributed_load_perp(ax_s,0,Lb,cb,sb,qd["q"],q_down=True,n=max(5,int(Lb*1.5)))
                        mx,my=(x1b+x2b)/2,(y1b+y2b)/2
                        ax_s.text(mx-sb*sc*6,my+cb*sc*6,f"q={qd['q']} kN/m",fontsize=9,fontweight="bold",color="#2255cc")
                    else:
                        if abs(sb)<0.01:
                            draw_distributed_load(ax_s,x1b,x2b,y1b,qd["q"],f"q={qd['q']} kN/m",n_arrows=max(5,int(Lb)))
                        else:
                            draw_distributed_load_perp(ax_s,0,Lb,cb,sb,qd["q"],q_down="in jos" in qd["dir"],n=max(5,int(Lb*1.5)))
                            mx,my=(x1b+x2b)/2,(y1b+y2b)/2
                            ax_s.text(mx+sc*2,my+sc*2,f"q={qd['q']} kN/m",fontsize=9,fontweight="bold",color="#2255cc")
                for fc in forces_ed:
                    xn,yn=get_node(fc["node"])
                    if fc["tip"]=="F" and (abs(fc["Fx"])>0.01 or abs(fc["Fy"])>0.01):
                        mag=np.sqrt(fc["Fx"]**2+fc["Fy"]**2)
                        draw_force_arrow(ax_s,xn,yn,fc["Fx"]/mag,fc["Fy"]/mag,f"F={mag:.1f} kN","darkred",scale=sc*5)
                    elif fc["tip"]=="M" and abs(fc["M"])>0.01:
                        draw_moment_arc(ax_s,xn,yn,fc["M"],r=sc*2,color="purple")
                        ax_s.text(xn+sc*2.5,yn+sc*2.5,f"M={fc['M']:.1f} kNm",color="purple",fontsize=9,fontweight="bold")
                if solved:
                    src=max(0.6,dim*0.1)
                    for nd_name,rv in reactions.items():
                        xn,yn=get_node(nd_name)
                        if abs(rv["Fy"])>0.01:
                            sgn=1 if rv["Fy"]>0 else -1
                            ax_s.annotate("",xy=(xn,yn),xytext=(xn,yn-src*sgn),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=14))
                            ax_s.text(xn+sc*1.5,yn-src*sgn*0.6,f"V={rv['Fy']:.3f}",color="red",fontsize=9,fontweight="bold")
                        if abs(rv["Fx"])>0.01:
                            sgn=1 if rv["Fx"]>0 else -1
                            ax_s.annotate("",xy=(xn,yn),xytext=(xn-src*sgn,yn),arrowprops=dict(arrowstyle="->",color="#1a6faf",lw=2.5,mutation_scale=14))
                            ax_s.text(xn-src*sgn*1.2,yn+sc*2,f"H={rv['Fx']:.3f}",color="#1a6faf",fontsize=9,fontweight="bold")
                        if abs(rv.get("M",0))>0.01:
                            draw_moment_arc(ax_s,xn,yn,-rv["M"],r=sc*2.5,color="green")
                            ax_s.text(xn-sc*5,yn-sc*3,f"M={rv['M']:.3f}",color="green",fontsize=9,fontweight="bold")
                draw_axes(ax_s,min(all_x)-sc*5,min(all_y)-sc*2,length=sc*2.5)
                ax_s.set_aspect("equal"); ax_s.axis("off")
                pad=dim*0.35
                ax_s.set_xlim(min(all_x)-pad,max(all_x)+pad); ax_s.set_ylim(min(all_y)-pad,max(all_y)+pad)
                ax_s.set_title("Cadru -- Schema cu Reactiuni",fontsize=13,fontweight="bold")
                st.pyplot(fig_s); plt.close(fig_s)

                # === PASUL 2: REACTIUNI ===
                if solved:
                    st.markdown("### Pasul 2 -- Reactiuni")
                    rcols=st.columns(min(len(reactions),4))
                    for i,(nd_name,rv) in enumerate(reactions.items()):
                        with rcols[i%4]:
                            st.markdown(f"**Nod {nd_name}:**")
                            if abs(rv["Fx"])>0.001: st.latex(rf"H_{{{nd_name}}} = {rv['Fx']:.4f}\;\text{{kN}}")
                            if abs(rv["Fy"])>0.001: st.latex(rf"V_{{{nd_name}}} = {rv['Fy']:.4f}\;\text{{kN}}")
                            if abs(rv.get("M",0))>0.001: st.latex(rf"M_{{{nd_name}}} = {rv['M']:.4f}\;\text{{kNm}}")
                    sumRx=sum(r["Fx"] for r in reactions.values())
                    sumRy=sum(r["Fy"] for r in reactions.values())
                    chkFx=sumRx+sumFx_ext; chkFy=sumRy+sumFy_ext
                    vc1,vc2=st.columns(2)
                    _=vc1.success(f"SFx = {chkFx:.6f} ~ 0") if abs(chkFx)<0.01 else vc1.error(f"SFx = {chkFx:.6f}")
                    _=vc2.success(f"SFy = {chkFy:.6f} ~ 0") if abs(chkFy)<0.01 else vc2.error(f"SFy = {chkFy:.6f}")

                    # === PASUL 3: DIAGRAME N, T, M ===
                    st.markdown("### Pasul 3 -- Diagrame N, T, M")

                    all_bars_ntm=[]
                    for i_br,br in enumerate(bars_ed):
                        x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
                        eid=cad_elem_id[i_br]
                        el=ss_cad.element_map[eid]
                        npts=len(el.bending_moment)
                        N_arr=np.linspace(el.N_1,el.N_2,npts)
                        T_arr=np.array(el.shear_force)
                        M_arr=np.array(el.bending_moment)
                        all_bars_ntm.append({"n1":br["n1"],"n2":br["n2"],"x1":x1b,"y1":y1b,"x2":x2b,"y2":y2b,
                                             "N":N_arr,"T":T_arr,"M":M_arr})

                    all_N_vals=np.concatenate([b["N"] for b in all_bars_ntm])
                    all_T_vals=np.concatenate([b["T"] for b in all_bars_ntm])
                    all_M_vals=np.concatenate([b["M"] for b in all_bars_ntm])
                    scN=0.18*dim/max(0.01,np.max(np.abs(all_N_vals))) if np.max(np.abs(all_N_vals))>0.01 else 1
                    scT=0.18*dim/max(0.01,np.max(np.abs(all_T_vals))) if np.max(np.abs(all_T_vals))>0.01 else 1
                    scM=0.18*dim/max(0.01,np.max(np.abs(all_M_vals))) if np.max(np.abs(all_M_vals))>0.01 else 1

                    cls=["#1a6faf","#2ca02c","#d62728"]
                    titles=["N (kN)","T (kN)","M (kNm)"]
                    fig_d,axes_d=plt.subplots(1,3,figsize=(18,9),dpi=150)
                    for idx_d,(sc_d,vkey,color,title) in enumerate([
                        (scN,"N",cls[0],titles[0]),(scT,"T",cls[1],titles[1]),(scM,"M",cls[2],titles[2])]):
                        ax=axes_d[idx_d]
                        bars_draw=[{"x1":b["x1"],"y1":b["y1"],"x2":b["x2"],"y2":b["y2"],"values":b[vkey]} for b in all_bars_ntm]
                        draw_ntm_on_frame(ax,bars_draw,color,sc_d)
                        for sp in sup_ed:
                            xn,yn=get_node(sp["node"])
                            if sp["tip"]==1: draw_pin(ax,xn,yn,sc*0.5)
                            elif sp["tip"]==2: draw_roller(ax,xn,yn,sc*0.5)
                        for nd in nodes:
                            ax.plot(nd["x"],nd["y"],"ko",ms=4,zorder=6)
                        ax.set_aspect("equal"); ax.axis("off")
                        ax.set_xlim(min(all_x)-pad*0.6,max(all_x)+pad*0.6)
                        ax.set_ylim(min(all_y)-pad*0.6,max(all_y)+pad*0.6)
                        ax.set_title(title,fontsize=13,fontweight="bold",color=color)
                    plt.tight_layout()
                    fig_d.suptitle("Diagrame N, T, M",fontsize=14,fontweight="bold",y=1.01)
                    st.pyplot(fig_d); plt.close(fig_d)

                    # === PASUL 4: VERIFICARE ===
                    st.markdown("### Pasul 4 -- Verificare")
                    vm1,vm2,vm3=st.columns(3)
                    vm1.metric("M max",f"{np.max(np.abs(all_M_vals)):.3f} kNm")
                    vm2.metric("T max",f"{np.max(np.abs(all_T_vals)):.3f} kN")
                    vm3.metric("N max",f"{np.max(np.abs(all_N_vals)):.3f} kN")
                    with st.expander("Valori Caracteristice"):
                        for b in all_bars_ntm:
                            st.markdown(f"**Bara {b['n1']}-{b['n2']}:** N=[{np.min(b['N']):.3f}, {np.max(b['N']):.3f}] | T=[{np.min(b['T']):.3f}, {np.max(b['T']):.3f}] | M=[{np.min(b['M']):.3f}, {np.max(b['M']):.3f}]")

            # ---- ARC ----
            elif tip_struct=="Arc cu 3 Articula╚¢ii":
                st.header("Arc cu 3 Articula╚¢ii")
                with st.expander("Teorie (975-4.pdf, Cap.4)"):
                    st.latex(r"H=\frac{\sum M_C^{stg}}{f},\; M(x)=M_0(x)-H y(x)")
                    st.latex(r"y(x)=\frac{4f}{L^2}x(L-x)\quad(\text{parabol─â})")
                c1,c2=st.columns(2)
                with c1:
                    Larc=st.number_input("Deschidere L(m)",min_value=0.5,value=12.0,step=1.0,key="arc_L")
                    farc=st.number_input("S─âgeat─â f(m)",min_value=0.1,value=3.0,step=0.5,key="arc_f")
                    qarc=st.number_input("q(kN/m)",min_value=0.0,value=15.0,step=1.0,key="arc_q")
                with c2:
                    Parc=st.number_input("P(kN)",min_value=0.0,value=0.0,step=5.0,key="arc_P")
                    aarc=st.number_input("Poz P(m)",min_value=0.0,value=float(Larc)/4,key="arc_a")
                Qarc=qarc*Larc; VBarc=(Qarc*Larc/2+Parc*aarc)/Larc; VAarc=Qarc+Parc-VBarc
                smc=VAarc*Larc/2-qarc*(Larc/2)**2/2-(Parc*(Larc/2-aarc) if aarc<Larc/2 else 0)
                Harc=smc/farc
                xarc=np.linspace(0,Larc,400); yarc=4*farc/Larc**2*xarc*(Larc-xarc)
                dydx=4*farc/Larc**2*(Larc-2*xarc); phi=np.arctan(dydx)

                st.markdown("### Pasul 1 ΓÇö Schema Arcului")
                fig_arc,ax_arc=plt.subplots(figsize=(12,6.5),dpi=150)
                ax_arc.plot(xarc,yarc,"k-",lw=5,zorder=3)
                sa=max(0.22,Larc*0.025); draw_pin(ax_arc,0,0,sa); draw_pin(ax_arc,Larc,0,sa)
                ax_arc.plot(Larc/2,farc,"ko",ms=10,zorder=6); ax_arc.plot(Larc/2,farc,"wo",ms=5,zorder=7)
                ax_arc.text(Larc/2,farc+sa*2.5,"C (cheie, M=0)",ha="center",fontsize=9,color="navy",fontweight="bold")
                ax_arc.text(-sa*1.5,-sa*3,"A",fontsize=12,fontweight="bold"); ax_arc.text(Larc+sa*0.5,-sa*3,"B",fontsize=12,fontweight="bold")
                ax_arc.plot([Larc/2,Larc/2],[0,farc],"b--",lw=1.2,alpha=0.6); ax_arc.text(Larc/2+sa,farc/2,f"f={farc:.1f}m",fontsize=10,color="blue")
                ax_arc.annotate("",xy=(Larc,-sa*0.5),xytext=(0,-sa*0.5),arrowprops=dict(arrowstyle="<->",color="gray",lw=1.2)); ax_arc.text(Larc/2,-sa*1.5,f"L={Larc:.1f}m",ha="center",fontsize=10)
                if qarc>0: draw_distributed_load(ax_arc,0,Larc,farc+0.9,qarc,f"q={qarc}",n_arrows=9)
                if Parc>0: yp=4*farc/Larc**2*aarc*(Larc-aarc); draw_force_arrow(ax_arc,aarc,yp,0,1,f"P={Parc}kN","darkred",scale=sa*4)
                scar=max(0.9,farc*0.35)
                ax_arc.annotate("",xy=(0,0),xytext=(0,-scar),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=14)); ax_arc.text(-sa*7,-scar*0.6,f"VA={VAarc:.2f}",color="red",fontsize=9)
                ax_arc.annotate("",xy=(0,0),xytext=(-scar,0),arrowprops=dict(arrowstyle="->",color="#1a6faf",lw=2.5,mutation_scale=14)); ax_arc.text(-scar*1.7,sa*2,f"H={Harc:.2f}",color="#1a6faf",fontsize=9)
                ax_arc.annotate("",xy=(Larc,0),xytext=(Larc,-scar),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=14)); ax_arc.text(Larc+sa,-scar*0.6,f"VB={VBarc:.2f}",color="red",fontsize=9)
                ax_arc.annotate("",xy=(Larc,0),xytext=(Larc+scar,0),arrowprops=dict(arrowstyle="->",color="#1a6faf",lw=2.5,mutation_scale=14))
                draw_axes(ax_arc,-sa*3,-sa,length=sa*2.2); ax_arc.set_aspect("equal"); ax_arc.set_xlim(-sa*16,Larc+sa*16); ax_arc.set_ylim(-sa*12,farc+sa*16); ax_arc.axis("off")
                ax_arc.set_title("Arc cu 3 Articula╚¢ii ΓÇö Schema cu Reac╚¢iuni",fontsize=13,fontweight="bold"); st.pyplot(fig_arc); plt.close(fig_arc)

                st.markdown("### Pasul 2 ΓÇö Ecua╚¢ii de Calcul")
                ca1,ca2=st.columns(2)
                with ca1:
                    st.latex(rf"V_B={VBarc:.4f}\text{{ kN}},\; V_A={VAarc:.4f}\text{{ kN}}")
                    st.latex(r"\sum M_C^{{stg}}=0:\; V_A\frac{{L}}{{2}}-q\frac{{(L/2)^2}}{{2}}-P(L/2-a)=H\cdot f")
                with ca2:
                    st.latex(rf"H=\frac{{{smc:.4f}}}{{{farc:.2f}}}={Harc:.4f}\text{{ kN}}")
                    st.info(f"VA={VAarc:.4f} VB={VBarc:.4f} H={Harc:.4f} kN")

                M0arc=np.zeros_like(xarc)
                for i,x in enumerate(xarc): M0arc[i]=VAarc*x-qarc*x**2/2-(Parc*(x-aarc) if x>aarc else 0)
                Marc=M0arc-Harc*yarc
                Vsect=np.zeros_like(xarc)
                for i,x in enumerate(xarc): Vsect[i]=VAarc-qarc*x-(Parc if x>aarc else 0)
                Narc=-(Harc*np.cos(phi)+Vsect*np.sin(phi)); Tarc=-Harc*np.sin(phi)+Vsect*np.cos(phi)

                st.markdown("### Pasul 3 ΓÇö Diagrame M, N, T")
                fig_an,axes_an=plt.subplots(1,3,figsize=(15,5.5),dpi=150)
                scMs=0.25/max(0.01,np.max(np.abs(Marc))); scNs=0.2/max(0.01,np.max(np.abs(Narc))); scTs=0.2/max(0.01,np.max(np.abs(Tarc))+0.01)
                axes_an[0].plot(xarc,yarc,"k-",lw=3); axes_an[0].fill_between(xarc,yarc,yarc+Marc*scMs,color="#d62728",alpha=0.38); axes_an[0].plot(xarc,yarc+Marc*scMs,"r-",lw=2); axes_an[0].set_title("M(x)=M0-Hy",fontweight="bold",color="#d62728"); axes_an[0].axis("off")
                axes_an[1].plot(xarc,yarc,"k-",lw=3); axes_an[1].fill_between(xarc,yarc,yarc+Narc*scNs,color="#1a6faf",alpha=0.38); axes_an[1].set_title("N(x)",fontweight="bold",color="#1a6faf"); axes_an[1].axis("off")
                axes_an[2].plot(xarc,yarc,"k-",lw=3); axes_an[2].fill_between(xarc,yarc,yarc+Tarc*scTs,color="#2ca02c",alpha=0.38); axes_an[2].set_title("T(x)",fontweight="bold",color="#2ca02c"); axes_an[2].axis("off")
                plt.tight_layout(); st.pyplot(fig_an); plt.close(fig_an)
                Mc=Marc[len(Marc)//2]
                if abs(Mc)<abs(np.max(np.abs(Marc)))*0.02: st.success(f"M la cheie CΓëê{Mc:.5f}Γëê0 Γ£ô")
                else: st.warning(f"M la cheie C={Mc:.5f} (trebuie Γëê0)")

            # ---- ZABRELE ----
            elif tip_struct=="Z─âbrele":
                st.header("Grinzi cu Z─âbrele ΓÇö Metoda Nodurilor ╚Öi Sec╚¢iunilor")
                with st.expander("Teorie (975-4.pdf, Cap.5)"):
                    st.markdown("N>0 = ├«ntindere, N<0 = compresiune. **Condi╚¢ie SSD:** b+r=2j")
                    st.latex(r"N_{t.inf}=+\frac{M_1}{h},\; N_{t.sup}=-\frac{M_1}{h},\; N_{diag}=\frac{T_1}{\sin\varphi}")
                c1,c2=st.columns(2)
                with c1:
                    ncamp=st.number_input("Nr c├ómpuri",min_value=2,max_value=12,value=4,step=1,key="zab_n")
                    dcamp=st.number_input("Lungime panou d(m)",min_value=0.5,value=2.0,step=0.5,key="zab_d")
                    hzab=st.number_input("├Än─âl╚¢ime h(m)",min_value=0.5,value=2.0,step=0.5,key="zab_h")
                with c2:
                    Pzab=st.number_input("P pe nod inferior(kN)",min_value=0.0,value=20.0,step=5.0,key="zab_P")
                    tipz=st.selectbox("Tip z─âbrea",["Pratt","Warren"],key="zab_tip")
                Lzab=ncamp*dcamp; ninf=ncamp+1; Ftot=Pzab*(ninf-2); VAz=Ftot/2; VBz=Ftot/2
                xinf=np.array([i*dcamp for i in range(ninf)]); xsup=xinf.copy()

                fig_z,ax_z=plt.subplots(figsize=(max(10,ncamp*2.2),5.5),dpi=150)
                for i in range(ncamp):
                    ax_z.plot([xinf[i],xinf[i+1]],[0,0],"k-",lw=3.5); ax_z.plot([xsup[i],xsup[i+1]],[hzab,hzab],"k-",lw=3.5)
                    ax_z.plot([xinf[i],xsup[i]],[0,hzab],"k-",lw=2.5); ax_z.plot([xinf[i+1],xsup[i+1]],[0,hzab],"k-",lw=2.5)
                    if tipz=="Pratt":
                        mid=ncamp//2
                        if i<mid: ax_z.plot([xinf[i],xsup[i+1]],[0,hzab],"k-",lw=2)
                        else: ax_z.plot([xinf[i+1],xsup[i]],[0,hzab],"k-",lw=2)
                    else:
                        if i%2==0: ax_z.plot([xinf[i],xsup[i+1]],[0,hzab],"k-",lw=2)
                        else: ax_z.plot([xinf[i+1],xsup[i]],[0,hzab],"k-",lw=2)
                for xi in xinf: ax_z.plot(xi,0,"ko",ms=7,zorder=5)
                for xi in xsup: ax_z.plot(xi,hzab,"ko",ms=7,zorder=5)
                sz=dcamp*0.065; draw_pin(ax_z,0,0,sz); draw_roller(ax_z,Lzab,0,sz)
                for i in range(1,ninf-1):
                    if Pzab>0:
                        ax_z.annotate("",xy=(xinf[i],0),xytext=(xinf[i],hzab*0.45),arrowprops=dict(arrowstyle="->",color="darkred",lw=1.8,mutation_scale=11))
                        ax_z.text(xinf[i],hzab*0.55,f"P={Pzab:.0f}kN",ha="center",fontsize=8,color="darkred",fontweight="bold")
                ax_z.annotate("",xy=(0,0),xytext=(0,-hzab*0.35),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=13)); ax_z.text(-dcamp*0.25,-hzab*0.28,f"VA={VAz:.1f}kN",color="red",fontsize=9,fontweight="bold")
                ax_z.annotate("",xy=(Lzab,0),xytext=(Lzab,-hzab*0.35),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=13)); ax_z.text(Lzab+dcamp*0.05,-hzab*0.28,f"VB={VBz:.1f}kN",color="red",fontsize=9,fontweight="bold")
                ax_z.set_xlim(-dcamp*1.2,Lzab+dcamp*1.2); ax_z.set_ylim(-hzab*0.75,hzab*1.6); ax_z.set_aspect("equal"); ax_z.axis("off")
                ax_z.set_title(f"Z─âbrea {tipz} ΓÇö {ncamp} c├ómpuri├ù{dcamp}m h={hzab}m",fontsize=12,fontweight="bold"); st.pyplot(fig_z); plt.close(fig_z)

                st.latex(rf"V_A=V_B=\frac{{\sum P}}{{2}}=\frac{{{(ninf-2)*Pzab:.1f}}}{{2}}={VAz:.3f}\text{{ kN}}")
                M1=VAz*dcamp; Ntinf=M1/hzab; Ntsup=-M1/hzab; Ldiag=np.sqrt(dcamp**2+hzab**2); Nd=VAz/(hzab/Ldiag)
                st.markdown("#### Metoda Sec╚¢iunilor ΓÇö Panoul 1:")
                st.latex(rf"N_{{t.inf}}=+\frac{{V_A d}}{{h}}={Ntinf:.3f}\text{{ kN (\textit├«ntindere)}}")
                st.latex(rf"N_{{t.sup}}=-{abs(Ntsup):.3f}\text{{ kN (compresiune)}}")
                st.latex(rf"N_{{diag}}=\frac{{V_A}}{{\sin\varphi}}=\frac{{{VAz:.2f}}}{{{hzab/Ldiag:.4f}}}={Nd:.3f}\text{{ kN}}")

        # ============================================================
        # MODUL 4: STATICA 2
        # ============================================================
        elif modul == "Statica 2 ΓÇö Static Nedeterminate":
            st.title("Statica 2 ΓÇö Structuri Static Nedeterminate")
            st.markdown("Calcul conform *Metoda For╚¢elor + Metoda Deplas─ârilor* (138-3.pdf)")
            st.markdown("---")
            tip_s2=st.sidebar.selectbox("Metod─â / Structur─â",["Grind─â Continu─â (Metoda For╚¢elor)","Cadru Nedeterminat (Metoda For╚¢elor)","Metoda Deplas─ârilor","Metoda Cross (Distribu╚¢ia Momentelor)","Ced─âri de Reazeme","Deplas─âri Punctuale (Mohr)"],key="s2_tip")

            # ---- GRINDA CONTINUA ----
            if tip_s2=="Grind─â Continu─â (Metoda For╚¢elor)":
                st.header("Grind─â Continu─â pe 2 Deschideri ΓÇö Metoda For╚¢elor")
                with st.expander("Teorie (138-3.pdf, Cap.1-2)"):
                    st.markdown("**Pa╚Öi Metoda For╚¢elor:**\n1. Grad nedeterminare ns\n2. Sistem de Baz─â (SB)\n3. Diagrame Mf, m1,...\n4. Coeficien╚¢i Vere╚Öciagin ╬┤ij\n5. Ecua╚¢ii canonice\n6. Diagram─â M final─â")
                    st.latex(r"\delta_{11}X_1+\Delta_{1P}=0,\; M_{fin}=M_f+X_1 m_1")
                    st.latex(r"\delta_{ij}=\int_0^L\frac{m_i m_j}{EI}dx\quad(\text{Vere┼ƒciagin})")
                c1,c2=st.columns(2)
                with c1:
                    L1=st.number_input("L1(m)",min_value=0.5,value=6.0,step=0.5,key="s2_L1")
                    L2=st.number_input("L2(m)",min_value=0.5,value=6.0,step=0.5,key="s2_L2")
                    q1=st.number_input("q pe L1(kN/m)",min_value=0.0,value=20.0,step=1.0,key="s2_q1")
                    q2=st.number_input("q pe L2(kN/m)",min_value=0.0,value=0.0,step=1.0,key="s2_q2")
                with c2:
                    P1=st.number_input("P1 la mij L1(kN)",min_value=0.0,value=0.0,step=5.0,key="s2_P1")
                    P2=st.number_input("P2 la mij L2(kN)",min_value=0.0,value=30.0,step=5.0,key="s2_P2")
                    EIs=st.number_input("EI(kNm2)",min_value=1.0,value=10000.0,step=1000.0,key="s2_EI")

                st.markdown("---")
                st.markdown("### Pasul 1 ΓÇö Gradul de Nedeterminare")
                st.latex(r"n_s=r-3=4-3=1\quad(\text{r=4: VA,HA,VB,VC})")
                st.success("ns=1 ΓåÆ 1 necunoscut─â redundant─â X1=VB")
                st.markdown("### Pasul 2 ΓÇö Sistem de Baz─â")
                st.markdown("**SB** = grinda AΓÇôC simpl─â (f─âr─â reazem ├«n B). **X1=VB** redundant.")
                Ltot=L1+L2; xsb=np.linspace(0,Ltot,500)
                RA_m1=L2/Ltot; RC_m1=L1/Ltot
                m1=np.zeros_like(xsb)
                for i,x in enumerate(xsb):
                    m=RA_m1*x
                    if x>L1: m-=1.0*(x-L1)
                    m1[i]=m
                Q1t=q1*L1; Q2t=q2*L2; xQ1=L1/2; xQ2=L1+L2/2; xP1=L1/2; xP2=L1+L2/2
                RC_Mf=(Q1t*xQ1+Q2t*xQ2+P1*xP1+P2*xP2)/Ltot; RA_Mf=Q1t+Q2t+P1+P2-RC_Mf
                Mf=np.zeros_like(xsb)
                for i,x in enumerate(xsb):
                    m=RA_Mf*x
                    if x>0:
                        xq1=min(x,L1); m-=q1/2*xq1**2
                        if x>L1: xq2=min(x-L1,L2); m-=q2/2*xq2**2
                    if x>xP1 and P1>0: m-=P1*(x-xP1)
                    if x>xP2 and P2>0: m-=P2*(x-xP2)
                    Mf[i]=m
                m1B=RA_m1*L1; d11=(L1*m1B**2/3+L2*m1B**2/3)/EIs; D1P=np.trapezoid(m1*Mf/EIs,xsb); X1s=-D1P/d11; Mfin=Mf+X1s*m1

                st.markdown("### Pasul 3 ΓÇö Schema Structurii")
                fig_s2s,ax_s2=plt.subplots(figsize=(12,4.5),dpi=150)
                ax_s2.plot([0,Ltot],[0,0],"k-",lw=5.5,zorder=3)
                ss2=max(0.22,Ltot*0.022)
                draw_pin(ax_s2,0,0,ss2); draw_roller(ax_s2,L1,0,ss2); draw_roller(ax_s2,Ltot,0,ss2)
                ax_s2.text(0,-ss2*3.5,"A",fontsize=12,fontweight="bold",ha="center"); ax_s2.text(L1,-ss2*3.5,"B\n(X1=VB)",fontsize=10,ha="center",color="navy",fontweight="bold"); ax_s2.text(Ltot,-ss2*3.5,"C",fontsize=12,fontweight="bold",ha="center")
                if q1>0: draw_distributed_load(ax_s2,0,L1,0.0,q1,f"q1={q1}")
                if q2>0: draw_distributed_load(ax_s2,L1,Ltot,0.0,q2,f"q2={q2}")
                if P1>0: draw_force_arrow(ax_s2,L1/2,0,0,1,f"P1={P1}kN","darkred",scale=ss2*4)
                if P2>0: draw_force_arrow(ax_s2,L1+L2/2,0,0,1,f"P2={P2}kN","darkred",scale=ss2*4)
                ax_s2.set_xlim(-ss2*6,Ltot+ss2*6); ax_s2.set_ylim(-ss2*7,ss2*15); ax_s2.set_aspect("equal"); ax_s2.axis("off")
                ax_s2.set_title("Grind─â Continu─â pe 2 Deschideri",fontsize=13,fontweight="bold"); st.pyplot(fig_s2s); plt.close(fig_s2s)

                st.markdown("### Pasul 4 ΓÇö Diagrame pe SB")
                fig_sb2,(axMf,axm1)=plt.subplots(2,1,figsize=(12,9),dpi=150,sharex=True)
                fill_diagram(axMf,xsb,Mf,"#d62728","Mf(kNm)"); axMf.set_title("Mf ΓÇö din ├«nc─ârc─âri pe SB",fontweight="bold",color="#d62728"); axMf.invert_yaxis(); axMf.axvline(L1,color="navy",ls="--",lw=1.2); label_extremes(axMf,xsb,Mf)
                fill_diagram(axm1,xsb,m1,"#9467bd","m1(m)"); axm1.set_title("m1 ΓÇö din X1=1 pe SB",fontweight="bold",color="#9467bd"); axm1.invert_yaxis(); axm1.axvline(L1,color="navy",ls="--",lw=1.2); axm1.text(L1,m1B*0.65,f"m1(B)={m1B:.4f}m",color="#9467bd",fontsize=9,ha="center",fontweight="bold"); axm1.set_xlabel("x(m)",fontsize=11)
                plt.tight_layout(); st.pyplot(fig_sb2); plt.close(fig_sb2)

                st.markdown("### Pasul 5 ΓÇö Coeficien╚¢i Vere╚Öciagin ╚Öi Ecua╚¢ie Canonic─â")
                cv1,cv2=st.columns(2)
                with cv1:
                    st.latex(r"\delta_{11}=\frac{1}{EI}\left(\frac{L_1 m_{1B}^2}{3}+\frac{L_2 m_{1B}^2}{3}\right)")
                    st.latex(rf"\delta_{{11}}={d11:.8f}\text{{ m/kN}}")
                    st.latex(rf"\Delta_{{1P}}={D1P:.6f}\text{{ m}}")
                with cv2:
                    st.latex(r"\delta_{11}X_1+\Delta_{1P}=0")
                    st.latex(rf"X_1=V_B=-\frac{{\Delta_{{1P}}}}{{\delta_{{11}}}}={X1s:.4f}\text{{ kN}}")
                    st.success(f"X1=VB={X1s:.4f} kN")

                st.markdown("### Pasul 6 ΓÇö Diagram─â M Final─â")
                st.latex(r"M_{fin}(x)=M_f(x)+X_1\cdot m_1(x)")
                fig_fin,ax_fin=plt.subplots(figsize=(12,5.5),dpi=150)
                fill_diagram(ax_fin,xsb,Mfin,"#d62728","M fin(kNm)"); ax_fin.invert_yaxis(); ax_fin.axvline(L1,color="navy",ls="--",lw=1.5,label=f"Reazem B(x={L1}m)"); label_extremes(ax_fin,xsb,Mfin); ax_fin.set_xlabel("x(m)",fontsize=11); ax_fin.set_title(f"Diagram─â M Final─â | X1=VB={X1s:.4f}kN",fontsize=12,fontweight="bold"); ax_fin.legend()
                plt.tight_layout(); st.pyplot(fig_fin); plt.close(fig_fin)

                st.markdown("### Pasul 7 ΓÇö Verificare")
                dB=d11*X1s+D1P
                if abs(dB)<1e-4: st.success(f"╬┤11 X1+╬ö1P={dB:.2e}Γëê0 Γ£ô")
                else: st.error(f"╬┤11 X1+╬ö1P={dB:.2e}Γëá0")
                RA_f=RA_Mf+X1s*RA_m1; RC_f=RC_Mf+X1s*RC_m1
                cr1,cr2,cr3=st.columns(3); cr1.metric("VA",f"{RA_f:.4f} kN"); cr2.metric("VB",f"{X1s:.4f} kN"); cr3.metric("VC",f"{RC_f:.4f} kN")
                chk=RA_f+X1s+RC_f-Q1t-Q2t-P1-P2
                if abs(chk)<0.01: st.success(f"╬úFy={chk:.6f}Γëê0")
                else: st.warning(f"╬úFy={chk:.6f}")

            # ---- CADRU NEDETERMINAT ----
            elif tip_s2=="Cadru Nedeterminat (Metoda For╚¢elor)":
                st.header("Cadru 2D cu 2 ├Äncast─âri ΓÇö Metoda For╚¢elor")
                with st.expander("Teorie (138-3.pdf, Cap.2)"):
                    st.markdown("ns=3 (X1=MA, X2=MB, X3=HB). SB=cadru cu 2 articula╚¢ii.")
                    st.latex(r"\delta_{ij}X_j+\Delta_{iP}=0\;(i=1,2,3)")
                c1,c2=st.columns(2)
                with c1: Hcf=st.number_input("h st├ólpi(m)",min_value=0.5,value=4.0,step=0.5,key="cf_H"); Lcf=st.number_input("L grind─â(m)",min_value=0.5,value=6.0,step=0.5,key="cf_L"); qcf=st.number_input("q(kN/m)",min_value=0.0,value=20.0,step=1.0,key="cf_q")
                with c2: Hvcf=st.number_input("H orizontal(kN)",value=0.0,step=1.0,key="cf_Hv"); EIcf=st.number_input("EI(kNm2)",min_value=1.0,value=20000.0,step=1000.0,key="cf_EI")
                st.markdown("---"); st.markdown("### Pas 1 ΓÇö ns=3"); st.latex(r"n_s=r-3=6-3=3"); st.success("ns=3")
                st.markdown("### Pas 2 ΓÇö SB (2 articula╚¢ii la baze)")
                Qcf=qcf*Lcf; VBsb=Qcf/2-Hvcf*Hcf/Lcf; VAsb=Qcf-VBsb; HAsb=Hvcf
                yst=np.linspace(0,Hcf,200); xgr=np.linspace(0,Lcf,300)
                Mfss=HAsb*yst; Mfgr=VAsb*xgr-qcf*xgr**2/2
                m1ss=(Hcf-yst)/Hcf; m1sd=np.zeros_like(yst); m1gr=np.zeros_like(xgr)
                m2ss=np.zeros_like(yst); m2sd=(Hcf-yst)/Hcf; m2gr=np.zeros_like(xgr)
                m3ss=-yst; m3sd=Hcf-yst; m3gr=Hcf*np.ones_like(xgr)
                def itg(f1,f2,fg,g1,g2,gg,EI): return (np.trapezoid(f1*g1,yst)+np.trapezoid(f2*g2,yst)+np.trapezoid(fg*gg,xgr))/EI
                d11=itg(m1ss,m1sd,m1gr,m1ss,m1sd,m1gr,EIcf); d22=itg(m2ss,m2sd,m2gr,m2ss,m2sd,m2gr,EIcf); d33=itg(m3ss,m3sd,m3gr,m3ss,m3sd,m3gr,EIcf)
                d12=itg(m1ss,m1sd,m1gr,m2ss,m2sd,m2gr,EIcf); d13=itg(m1ss,m1sd,m1gr,m3ss,m3sd,m3gr,EIcf); d23=itg(m2ss,m2sd,m2gr,m3ss,m3sd,m3gr,EIcf)
                D1P=itg(m1ss,m1sd,m1gr,Mfss,np.zeros_like(yst),Mfgr,EIcf); D2P=itg(m2ss,m2sd,m2gr,Mfss,np.zeros_like(yst),Mfgr,EIcf); D3P=itg(m3ss,m3sd,m3gr,Mfss,np.zeros_like(yst),Mfgr,EIcf)
                st.markdown("### Pas 3 ΓÇö Diagrame pe SB")
                scms=0.12/max(0.01,max(np.max(np.abs(Mfss)),np.max(np.abs(Mfgr)),0.1))
                fig_scf,axes_scf=plt.subplots(1,4,figsize=(16,6.5),dpi=150)
                tls=["Mf","m1(MA=1)","m2(MB=1)","m3(HB=1)"]; cls=["#d62728","#9467bd","#8c564b","#17becf"]
                alls=[(Mfss,np.zeros_like(yst),Mfgr),(m1ss,m1sd,m1gr),(m2ss,m2sd,m2gr),(m3ss,m3sd,m3gr)]
                scs=[scms,0.12,0.12,0.04]
                for idx,(axf,tl,cl,(ss2,ds2,gs2),sc) in enumerate(zip(axes_scf,tls,cls,alls,scs)):
                    axf.plot([0,0],[0,Hcf],"k-",lw=2.5); axf.plot([Lcf,Lcf],[0,Hcf],"k-",lw=2.5); axf.plot([0,Lcf],[Hcf,Hcf],"k-",lw=2.5)
                    if idx==0: draw_fixed_bottom(axf,0,0,size=0.18); draw_fixed_bottom(axf,Lcf,0,size=0.18)
                    else: draw_pin(axf,0,0,0.18); draw_pin(axf,Lcf,0,0.18)
                    axf.fill_betweenx(yst,ss2*sc,0,color=cl,alpha=0.38); axf.fill_between(xgr,Hcf+gs2*sc,Hcf,color=cl,alpha=0.38)
                    axf.plot(ss2*sc,yst,color=cl,lw=2); axf.plot(xgr,Hcf+gs2*sc,color=cl,lw=2)
                    axf.set_aspect("equal"); axf.axis("off"); axf.set_title(tl,fontweight="bold",color=cl,fontsize=10)
                plt.tight_layout(); fig_scf.suptitle("Diagrame pe SB",fontsize=13,fontweight="bold"); st.pyplot(fig_scf); plt.close(fig_scf)
                st.markdown("### Pas 4 ΓÇö Coeficien╚¢i Vere╚Öciagin")
                cv1,cv2=st.columns(2)
                with cv1: st.latex(rf"\delta_{{11}}={d11:.6f},\; \delta_{{22}}={d22:.6f},\; \delta_{{33}}={d33:.6f}"); st.latex(rf"\delta_{{12}}={d12:.6f},\; \delta_{{13}}={d13:.6f},\; \delta_{{23}}={d23:.6f}"); st.latex(rf"\Delta_{{1P}}={D1P:.6f},\; \Delta_{{2P}}={D2P:.6f},\; \Delta_{{3P}}={D3P:.6f}")
                with cv2: st.latex(r"\delta_{11}X_1+\delta_{12}X_2+\delta_{13}X_3+\Delta_{1P}=0"); st.latex(r"\delta_{21}X_1+\delta_{22}X_2+\delta_{23}X_3+\Delta_{2P}=0"); st.latex(r"\delta_{31}X_1+\delta_{32}X_2+\delta_{33}X_3+\Delta_{3P}=0")
                Dm=np.array([[d11,d12,d13],[d12,d22,d23],[d13,d23,d33]]); DPv=np.array([D1P,D2P,D3P])
                try:
                    Xcf=np.linalg.solve(Dm,-DPv); X1cf,X2cf,X3cf=Xcf
                    st.markdown("### Pas 5 ΓÇö Solu╚¢ie")
                    st.latex(rf"X_1=M_A={X1cf:.4f}\text{{ kNm}},\; X_2=M_B={X2cf:.4f}\text{{ kNm}},\; X_3=H_B={X3cf:.4f}\text{{ kN}}")
                    Mssf=Mfss+X1cf*m1ss+X2cf*m2ss+X3cf*m3ss; Msdf=np.zeros_like(yst)+X1cf*m1sd+X2cf*m2sd+X3cf*m3sd; Mgrf=Mfgr+X1cf*m1gr+X2cf*m2gr+X3cf*m3gr
                    st.markdown("### Pas 6 ΓÇö Diagram─â M Final─â")
                    scMf=0.14/max(0.01,max(np.max(np.abs(Mssf)),np.max(np.abs(Msdf)),np.max(np.abs(Mgrf))))
                    fig_cff,ax_cff=plt.subplots(figsize=(9,8),dpi=150)
                    ax_cff.plot([0,0],[0,Hcf],"k-",lw=4); ax_cff.plot([Lcf,Lcf],[0,Hcf],"k-",lw=4); ax_cff.plot([0,Lcf],[Hcf,Hcf],"k-",lw=4)
                    draw_fixed_bottom(ax_cff,0,0,size=0.22); draw_fixed_bottom(ax_cff,Lcf,0,size=0.22)
                    ax_cff.fill_betweenx(yst,Mssf*scMf,0,color="#d62728",alpha=0.38); ax_cff.plot(Mssf*scMf,yst,"#d62728",lw=2.5)
                    ax_cff.fill_betweenx(yst,Lcf-Msdf*scMf,Lcf,color="#d62728",alpha=0.38); ax_cff.plot(Lcf-Msdf*scMf,yst,"#d62728",lw=2.5)
                    ax_cff.fill_between(xgr,Hcf+Mgrf*scMf,Hcf,color="#d62728",alpha=0.38); ax_cff.plot(xgr,Hcf+Mgrf*scMf,"#d62728",lw=2.5)
                    ax_cff.text(-0.2,0,f"MA={X1cf:.2f}kNm",ha="right",fontsize=9,color="#d62728",fontweight="bold"); ax_cff.text(Lcf+0.1,0,f"MB={X2cf:.2f}kNm",ha="left",fontsize=9,color="#d62728",fontweight="bold")
                    Mmaxg=np.max(np.abs(Mgrf)); idxMg=np.argmax(np.abs(Mgrf)); ax_cff.text(xgr[idxMg],Hcf+Mgrf[idxMg]*scMf+0.15,f"Mmax={Mmaxg:.2f}kNm",ha="center",fontsize=9,color="#d62728",fontweight="bold")
                    if qcf>0: draw_distributed_load(ax_cff,0,Lcf,Hcf,qcf,f"q={qcf}")
                    ax_cff.set_aspect("equal"); ax_cff.set_xlim(-1.8,Lcf+1.8); ax_cff.set_ylim(-1.0,Hcf+2.0); ax_cff.axis("off")
                    ax_cff.set_title(f"Diagram─â M Final─â\nq={qcf}kN/m EI={EIcf:.0f}kNm2",fontsize=12,fontweight="bold"); plt.tight_layout(); st.pyplot(fig_cff); plt.close(fig_cff)
                    vf=Dm@Xcf+DPv; ok=all(abs(v)<1e-4 for v in vf)
                    if ok: st.success(f"Verificare: {[f'{v:.2e}' for v in vf]}Γëê0 Γ£ô")
                    else: st.warning(f"Ecuatii: {[f'{v:.4f}' for v in vf]}")
                except np.linalg.LinAlgError: st.error("Eroare numeric─â.")

            # ---- METODA DEPLASARILOR ----
            elif tip_s2=="Metoda Deplas─ârilor":
                st.header("Metoda Deplas─ârilor ΓÇö Cadru 2D Simetric")
                with st.expander("Teorie (138-3.pdf, Cap.3)"):
                    st.markdown("Necunoscute: rota╚¢ii noduri. Ecua╚¢ii echilibru ├«n noduri.")
                    st.latex(r"M_0^{BC}=+\frac{qL^2}{12},\; r_{11}=4i_{st}+4i_{gr},\; r_{12}=2i_{gr}")
                    st.latex(r"M_{BC}=4i_{gr}\varphi_B+2i_{gr}\varphi_C+M_0^{BC}")
                c1,c2=st.columns(2)
                with c1: Hmd=st.number_input("h st├ólpi(m)",min_value=0.5,value=4.0,step=0.5,key="md_H"); Lmd=st.number_input("L(m)",min_value=0.5,value=6.0,step=0.5,key="md_L"); qmd=st.number_input("q(kN/m)",min_value=0.0,value=24.0,step=1.0,key="md_q")
                with c2: Pmd=st.number_input("P la mij.(kN)",min_value=0.0,value=0.0,step=5.0,key="md_P"); EIgr=st.number_input("EI grind─â(kNm2)",min_value=1.0,value=20000.0,step=1000.0,key="md_EIgr"); EIst=st.number_input("EI st├ólpi(kNm2)",min_value=1.0,value=15000.0,step=1000.0,key="md_EIst")
                st.markdown("---"); st.markdown("### Pas 1 ΓÇö nc=2 (rota╚¢ii fB, fC)"); st.latex(r"n_c=2\;(\varphi_B,\varphi_C)")
                Minc=qmd*Lmd**2/12+(Pmd*Lmd/8 if Pmd>0 else 0)
                st.markdown("### Pas 2 ΓÇö Momente de ├Äncastrare")
                st.latex(rf"M_0^{{BC}}=+{Minc:.4f}\text{{ kNm}},\; M_0^{{CB}}=-{Minc:.4f}\text{{ kNm}}")
                igr=EIgr/Lmd; ist=EIst/Hmd; r11=4*ist+4*igr; r12=2*igr; r22=4*ist+4*igr; R1P=-Minc; R2P=Minc
                st.markdown("### Pas 3 ΓÇö Coeficien╚¢i Rigiditate")
                st.latex(rf"i_{{gr}}={igr:.4f},\; i_{{st}}={ist:.4f},\; r_{{11}}={r11:.4f},\; r_{{12}}={r12:.4f}")
                Rm=np.array([[r11,r12],[r12,r22]]); RPv=np.array([R1P,R2P])
                try:
                    Z=np.linalg.solve(Rm,-RPv); fB,fC=Z
                    st.markdown("### Pas 4 ΓÇö Solu╚¢ie")
                    st.latex(rf"\varphi_B={fB:.8f},\; \varphi_C={fC:.8f}")
                    MBC=4*igr*fB+2*igr*fC+Minc; MCB=4*igr*fC+2*igr*fB-Minc
                    MBAst=4*ist*fB; MABst=2*ist*fB; MCDst=4*ist*fC; MDCst=2*ist*fC
                    st.markdown("### Pas 5 ΓÇö Momente Finale")
                    cm1,cm2=st.columns(2)
                    with cm1: st.latex(rf"M_{{BC}}={MBC:.4f}\text{{ kNm}},\; M_{{CB}}={MCB:.4f}\text{{ kNm}}")
                    with cm2: st.latex(rf"M_{{BA}}={MBAst:.4f},\; M_{{AB}}={MABst:.4f},\; M_{{CD}}={MCDst:.4f},\; M_{{DC}}={MDCst:.4f}\text{{ kNm}}")
                    eqB=MBC+MBAst; eqC=MCB+MCDst
                    cvm1,cvm2=st.columns(2)
                    _ = cvm1.success(f"Echilibru B: ╬úM={eqB:.6f}Γëê0") if abs(eqB)<0.01 else cvm1.error(f"Nod B: ╬úM={eqB:.6f}")
                    _ = cvm2.success(f"Echilibru C: ╬úM={eqC:.6f}Γëê0") if abs(eqC)<0.01 else cvm2.error(f"Nod C: ╬úM={eqC:.6f}")
                    yst_md=np.linspace(0,Hmd,200); Mstg=MABst+(MBAst-MABst)*yst_md/Hmd; Mstd=MDCst+(MCDst-MDCst)*yst_md/Hmd
                    xgr_md=np.linspace(0,Lmd,400); RAgr=(MBC-MCB)/Lmd+qmd*Lmd/2+Pmd/2; Mgr_md=np.zeros_like(xgr_md)
                    for i,x in enumerate(xgr_md): Mgr_md[i]=MBC+RAgr*x-qmd*x**2/2-(Pmd*(x-Lmd/2) if x>Lmd/2 and Pmd>0 else 0)
                    st.markdown("### Pas 6 ΓÇö Diagram─â M Final─â")
                    scMmd=0.14/max(0.01,max(abs(MABst),abs(MBC),np.max(np.abs(Mgr_md)))+0.01)
                    fig_md,ax_md=plt.subplots(figsize=(10,8.5),dpi=150)
                    ax_md.plot([0,0],[0,Hmd],"k-",lw=4.5); ax_md.plot([Lmd,Lmd],[0,Hmd],"k-",lw=4.5); ax_md.plot([0,Lmd],[Hmd,Hmd],"k-",lw=4.5)
                    draw_fixed_bottom(ax_md,0,0,size=0.25); draw_fixed_bottom(ax_md,Lmd,0,size=0.25)
                    ax_md.fill_betweenx(yst_md,Mstg*scMmd,0,color="#d62728",alpha=0.38); ax_md.plot(Mstg*scMmd,yst_md,"#d62728",lw=2.5)
                    ax_md.fill_betweenx(yst_md,Lmd+Mstd*scMmd,Lmd,color="#d62728",alpha=0.38); ax_md.plot(Lmd+Mstd*scMmd,yst_md,"#d62728",lw=2.5)
                    ax_md.fill_between(xgr_md,Hmd-Mgr_md*scMmd,Hmd,color="#d62728",alpha=0.38); ax_md.plot(xgr_md,Hmd-Mgr_md*scMmd,"#d62728",lw=2.5)
                    lk=dict(fontsize=9,color="#d62728",fontweight="bold")
                    ax_md.text(-0.2,0,f"{MABst:.2f}kNm",ha="right",**lk); ax_md.text(-0.2,Hmd,f"{MBC:.2f}kNm",ha="right",**lk)
                    ax_md.text(Lmd+0.1,0,f"{MDCst:.2f}kNm",ha="left",**lk); ax_md.text(Lmd+0.1,Hmd,f"{MCB:.2f}kNm",ha="left",**lk)
                    idxMmd=np.argmax(np.abs(Mgr_md)); ax_md.text(xgr_md[idxMmd],Hmd-Mgr_md[idxMmd]*scMmd-0.15,f"{Mgr_md[idxMmd]:.2f}kNm",ha="center",**lk)
                    if qmd>0: draw_distributed_load(ax_md,0,Lmd,Hmd,qmd,f"q={qmd}")
                    ax_md.set_aspect("equal"); ax_md.set_xlim(-1.8,Lmd+1.8); ax_md.set_ylim(-0.9,Hmd+2.2); ax_md.axis("off")
                    ax_md.set_title(f"Diagram─â M Final─â ΓÇö Metoda Deplas─ârilor\nq={qmd}kN/m EI_gr={EIgr:.0f} EI_st={EIst:.0f}kNm2",fontsize=12,fontweight="bold")
                    plt.tight_layout(); st.pyplot(fig_md); plt.close(fig_md)
                except np.linalg.LinAlgError: st.error("Eroare numeric─â.")

            # ---- METODA CROSS ----
            elif tip_s2=="Metoda Cross (Distribu╚¢ia Momentelor)":
                st.header("Metoda Cross ΓÇö Distribu╚¢ia Momentelor")
                with st.expander("Teorie (L10-Cross)"):
                    st.markdown("""**Algoritmul Cross (moment distribution):**
        1. Se calculeaz─â **rigidiz─ârile** k = EI/L pentru fiecare bar─â
        2. Se calculeaz─â **factorii de distribu╚¢ie** ╬╝ = k / ╬úk pentru fiecare nod
        3. Se calculeaz─â **momentele de ├«ncastrare** MΓéÇ din ├«nc─ârc─âri
        4. Se distribuie iterativ dezechilibrele nodale (factor de transfer = 1/2)
        5. Se sumeaz─â coloanele ΓåÆ momentele finale""")
                    st.latex(r"\mu_{ij}=\frac{k_{ij}}{\sum k}\;,\quad k_{ij}=\frac{EI_{ij}}{L_{ij}}")
                    st.latex(r"M_0^{AB}=+\frac{qL^2}{12}+\frac{PL}{8},\quad M_0^{BA}=-\frac{qL^2}{12}-\frac{PL}{8}")

                st.markdown("#### Configurare Grind─â Continu─â pe 3 Deschideri")
                cc1,cc2,cc3=st.columns(3)
                with cc1:
                    Lc1=st.number_input("L1 (m)",min_value=1.0,value=5.0,step=0.5,key="cr_L1")
                    EI1=st.number_input("EI1 (kNm┬▓)",min_value=1.0,value=10000.0,step=1000.0,key="cr_EI1")
                    q1c=st.number_input("q1 (kN/m)",min_value=0.0,value=20.0,step=1.0,key="cr_q1")
                    P1c=st.number_input("P1 la mijloc (kN)",min_value=0.0,value=0.0,step=5.0,key="cr_P1")
                with cc2:
                    Lc2=st.number_input("L2 (m)",min_value=1.0,value=6.0,step=0.5,key="cr_L2")
                    EI2=st.number_input("EI2 (kNm┬▓)",min_value=1.0,value=10000.0,step=1000.0,key="cr_EI2")
                    q2c=st.number_input("q2 (kN/m)",min_value=0.0,value=0.0,step=1.0,key="cr_q2")
                    P2c=st.number_input("P2 la mijloc (kN)",min_value=0.0,value=40.0,step=5.0,key="cr_P2")
                with cc3:
                    Lc3=st.number_input("L3 (m)",min_value=1.0,value=5.0,step=0.5,key="cr_L3")
                    EI3=st.number_input("EI3 (kNm┬▓)",min_value=1.0,value=10000.0,step=1000.0,key="cr_EI3")
                    q3c=st.number_input("q3 (kN/m)",min_value=0.0,value=15.0,step=1.0,key="cr_q3")
                    P3c=st.number_input("P3 la mijloc (kN)",min_value=0.0,value=0.0,step=5.0,key="cr_P3")
                niter_cr=st.slider("Num─âr itera╚¢ii Cross",2,12,6,key="cr_niter")

                k1=EI1/Lc1; k2=EI2/Lc2; k3=EI3/Lc3
                muB_A=k1/(k1+k2); muB_C=k2/(k1+k2)
                muC_B=k2/(k2+k3); muC_D=k3/(k2+k3)

                st.markdown("#### Rigidit─â╚¢i ╚Öi Factori de Distribu╚¢ie")
                cr_c1,cr_c2=st.columns(2)
                with cr_c1:
                    st.latex(rf"k_1={k1:.3f},\; k_2={k2:.3f},\; k_3={k3:.3f}\text{{ kNm}}")
                with cr_c2:
                    st.latex(rf"\mu_{{BA}}={muB_A:.4f},\; \mu_{{BC}}={muB_C:.4f},\; \mu_{{CB}}={muC_B:.4f},\; \mu_{{CD}}={muC_D:.4f}")

                def mf_cr(q,P,L): return q*L**2/12 + P*L/8
                M0_AB=+mf_cr(q1c,P1c,Lc1); M0_BA=-mf_cr(q1c,P1c,Lc1)
                M0_BC=+mf_cr(q2c,P2c,Lc2); M0_CB=-mf_cr(q2c,P2c,Lc2)
                M0_CD=+mf_cr(q3c,P3c,Lc3); M0_DC=-mf_cr(q3c,P3c,Lc3)

                cols_names=["AB","BA","BC","CB","CD","DC"]
                rows=[["├Äncastrare",M0_AB,M0_BA,M0_BC,M0_CB,M0_CD,M0_DC]]
                mAB,mBA,mBC,mCB,mCD,mDC=M0_AB,M0_BA,M0_BC,M0_CB,M0_CD,M0_DC
                for it in range(niter_cr):
                    dB=-(mBA+mBC); dC=-(mCB+mCD)
                    dBA=muB_A*dB; dBC=muB_C*dB
                    dCB=muC_B*dC; dCD=muC_D*dC
                    tAB=0.5*dBA; tBC_to_CB=0.5*dBC; tCB_to_BC=0.5*dCB; tDC=0.5*dCD
                    rows.append([f"Dist.{it+1}",0,dBA,dBC,dCB,dCD,0])
                    rows.append([f"Transf.{it+1}",tAB,0,tCB_to_BC,tBC_to_CB,0,tDC])
                    mAB+=tAB; mBA+=dBA; mBC+=dBC+tCB_to_BC; mCB+=dCB+tBC_to_CB; mCD+=dCD; mDC+=tDC
                rows.append(["**TOTAL**",mAB,mBA,mBC,mCB,mCD,mDC])

                import pandas as pd
                df_cr=pd.DataFrame(rows,columns=["Pas"]+cols_names)
                for col in cols_names: df_cr[col]=df_cr[col].apply(lambda v: f"{v:.4f}" if isinstance(v,float) else v)
                st.dataframe(df_cr,width="stretch")

                st.markdown("#### Momente Finale (kNm)")
                fm_c1,fm_c2,fm_c3=st.columns(3)
                fm_c1.metric("M_AB",f"{mAB:.3f}"); fm_c1.metric("M_BA",f"{mBA:.3f}")
                fm_c2.metric("M_BC",f"{mBC:.3f}"); fm_c2.metric("M_CB",f"{mCB:.3f}")
                fm_c3.metric("M_CD",f"{mCD:.3f}"); fm_c3.metric("M_DC",f"{mDC:.3f}")

                eqB=mBA+mBC; eqC=mCB+mCD
                eq_c1,eq_c2=st.columns(2)
                _ = eq_c1.success(f"Echilibru B: ╬úM={eqB:.4f}Γëê0") if abs(eqB)<0.05 else eq_c1.warning(f"Nod B: ╬úM={eqB:.4f} (mai multe itera╚¢ii)")
                _ = eq_c2.success(f"Echilibru C: ╬úM={eqC:.4f}Γëê0") if abs(eqC)<0.05 else eq_c2.warning(f"Nod C: ╬úM={eqC:.4f} (mai multe itera╚¢ii)")

                st.markdown("#### Diagram─â M Final─â")
                fig_cr,ax_cr=plt.subplots(figsize=(13,5),dpi=150)
                Ltot_cr=Lc1+Lc2+Lc3
                offsets=[0,Lc1,Lc1+Lc2,Ltot_cr]
                spans=[(Lc1,q1c,P1c,mAB,mBA),(Lc2,q2c,P2c,mBC,mCB),(Lc3,q3c,P3c,mCD,mDC)]
                ax_cr.plot([0,Ltot_cr],[0,0],"k-",lw=4)
                draw_pin(ax_cr,0,0,size=0.15); draw_roller(ax_cr,Ltot_cr,0,size=0.15)
                for xi in offsets[1:-1]: ax_cr.plot(xi,0,"ko",ms=8,zorder=6)
                scM_cr=0.5/max(0.01,max(abs(mAB),abs(mBA),abs(mBC),abs(mCB),abs(mCD),abs(mDC))+0.01)
                colors_cr=["#1f77b4","#ff7f0e","#2ca02c"]
                for idx,(Ls,qs,Ps,Ml,Mr) in enumerate(spans):
                    x0=offsets[idx]; xs=np.linspace(0,Ls,200)
                    RL=(Mr-Ml)/Ls+qs*Ls/2+Ps/2
                    Mx=np.array([Ml+RL*x-qs*x**2/2-(Ps*(x-Ls/2) if x>Ls/2 and Ps>0 else 0) for x in xs])
                    ax_cr.fill_between(x0+xs,-Mx*scM_cr,0,alpha=0.32,color=colors_cr[idx])
                    ax_cr.plot(x0+xs,-Mx*scM_cr,color=colors_cr[idx],lw=2.2)
                    imax=np.argmax(np.abs(Mx)); ax_cr.text(x0+xs[imax],-Mx[imax]*scM_cr-0.12,f"{Mx[imax]:.2f}",ha="center",fontsize=8,color=colors_cr[idx],fontweight="bold")
                for xi,mv in zip(offsets,[mAB]+[mBA,mBC,mCB,mCD,mDC]):
                    ax_cr.text(xi if xi==0 else xi,-mv*scM_cr+0.05,f"{mv:.2f}",ha="center",fontsize=8,color="#333",fontweight="bold")
                ax_cr.axhline(0,color="k",lw=0.7,ls="--"); ax_cr.set_xlim(-0.5,Ltot_cr+0.5); ax_cr.axis("off")
                ax_cr.set_title("Diagram─â M ΓÇö Metoda Cross",fontsize=12,fontweight="bold")
                st.pyplot(fig_cr); plt.close(fig_cr)

            # ---- CEDARI DE REAZEME ----
            elif tip_s2=="Ced─âri de Reazeme":
                st.header("Ced─âri de Reazeme ΓÇö Metoda Deplas─ârilor")
                with st.expander("Teorie (L13-ced─âri)"):
                    st.markdown("""**Ced─ârile de reazeme** introduc deplas─âri impuse la noduri.
        ├Än Metoda Deplas─ârilor, o cedare ╬ö la un reazem produce momente suplimentare:""")
                    st.latex(r"M_{AB}^{\Delta}=-\frac{6EI}{L^2}\Delta,\quad M_{BA}^{\Delta}=-\frac{6EI}{L^2}\Delta")
                    st.markdown("Aceste momente se adaug─â la momentele din ├«nc─ârc─âri ├«nainte de distribu╚¢ie.")

                st.markdown("#### Grind─â Continu─â 2 Deschideri cu Cedare la Reazem Intermediar")
                cd_c1,cd_c2=st.columns(2)
                with cd_c1:
                    Lcd1=st.number_input("L1 (m)",min_value=1.0,value=6.0,step=0.5,key="ced_L1")
                    EIcd1=st.number_input("EI (kNm┬▓)",min_value=1.0,value=15000.0,step=1000.0,key="ced_EI")
                    qcd=st.number_input("q (kN/m) uniform pe ambele deschideri",min_value=0.0,value=25.0,step=1.0,key="ced_q")
                with cd_c2:
                    Lcd2=st.number_input("L2 (m)",min_value=1.0,value=6.0,step=0.5,key="ced_L2")
                    delta_B=st.number_input("Cedare ╬ö_B la reazem B (mm, jos pozitiv)",value=10.0,step=1.0,key="ced_dB")/1000.0
                    delta_B_dir=st.selectbox("Direc╚¢ie cedare",["Jos (pozitiv)","Sus (negativ)"],key="ced_dir")
                if delta_B_dir=="Sus (negativ)": delta_B=-delta_B

                EIv=EIcd1
                icd1=EIv/Lcd1; icd2=EIv/Lcd2
                M0_cd1=qcd*Lcd1**2/12; M0_cd2=qcd*Lcd2**2/12
                Mced1=6*EIv/Lcd1**2*delta_B; Mced2=6*EIv/Lcd2**2*delta_B
                R1P=-(M0_cd1-Mced1)+( M0_cd2-Mced2)
                r11_cd=4*icd1+4*icd2
                try:
                    phiB_cd=-R1P/r11_cd
                    MAB_cd=2*icd1*phiB_cd - M0_cd1 + Mced1
                    MBA_cd=4*icd1*phiB_cd + M0_cd1 - Mced1
                    MBC_cd=4*icd2*phiB_cd - M0_cd2 + Mced2
                    MCB_cd=2*icd2*phiB_cd + M0_cd2 - Mced2

                    st.markdown("#### Calcul Pas cu Pas")
                    st.latex(rf"i_1=\frac{{EI}}{{L_1}}={icd1:.3f},\quad i_2=\frac{{EI}}{{L_2}}={icd2:.3f}\text{{ kNm}}")
                    st.latex(rf"M_0^{{(1)}}=\pm{M0_cd1:.3f}\text{{ kNm}},\quad M_0^{{(2)}}=\pm{M0_cd2:.3f}\text{{ kNm}}")
                    st.latex(rf"M_{{\Delta}}^{{(1)}}=\frac{{6EI}}{{L_1^2}}\Delta_B={Mced1:.4f}\text{{ kNm}}")
                    st.latex(rf"r_{{11}}=4i_1+4i_2={r11_cd:.3f}\text{{ kNm}},\quad R_{{1P}}={R1P:.4f}\text{{ kNm}}")
                    st.latex(rf"\varphi_B=\frac{{-R_{{1P}}}}{{r_{{11}}}}={phiB_cd:.8f}\text{{ rad}}")

                    cols_cd=st.columns(2)
                    with cols_cd[0]:
                        st.latex(rf"M_{{AB}}={MAB_cd:.4f}\text{{ kNm}}")
                        st.latex(rf"M_{{BA}}={MBA_cd:.4f}\text{{ kNm}}")
                    with cols_cd[1]:
                        st.latex(rf"M_{{BC}}={MBC_cd:.4f}\text{{ kNm}}")
                        st.latex(rf"M_{{CB}}={MCB_cd:.4f}\text{{ kNm}}")
                    eqB_cd=MBA_cd+MBC_cd
                    _ = st.success(f"Echilibru nod B: ╬úM={eqB_cd:.6f}Γëê0") if abs(eqB_cd)<0.01 else st.error(f"Echilibru B: ╬úM={eqB_cd:.6f}")

                    st.markdown("#### Diagram─â M Final─â")
                    fig_ced,ax_ced=plt.subplots(figsize=(11,4.5),dpi=150)
                    Ltot_ced=Lcd1+Lcd2
                    ax_ced.plot([0,Ltot_ced],[0,0],"k-",lw=4)
                    draw_pin(ax_ced,0,0,0.12); draw_roller(ax_ced,Lcd1,0,0.12); draw_roller(ax_ced,Ltot_ced,0,0.12)
                    if abs(delta_B)>1e-6:
                        ax_ced.annotate("",xy=(Lcd1,-delta_B*60),xytext=(Lcd1,0),arrowprops=dict(arrowstyle="->",color="purple",lw=2))
                        ax_ced.text(Lcd1+0.1,-delta_B*30,f"╬ö={delta_B*1000:.1f}mm",color="purple",fontsize=9,fontweight="bold")
                    scM_ced=0.5/max(0.01,max(abs(MAB_cd),abs(MBA_cd),abs(MBC_cd),abs(MCB_cd))+0.01)
                    for (x0,Ls,Ml,Mr,qs) in [(0,Lcd1,MAB_cd,MBA_cd,qcd),(Lcd1,Lcd2,MBC_cd,MCB_cd,qcd)]:
                        xs=np.linspace(0,Ls,200)
                        RL=(Mr-Ml)/Ls+qs*Ls/2
                        Mx=np.array([Ml+RL*x-qs*x**2/2 for x in xs])
                        ax_ced.fill_between(x0+xs,-Mx*scM_ced,0,alpha=0.35,color="#d62728")
                        ax_ced.plot(x0+xs,-Mx*scM_ced,"#d62728",lw=2.2)
                        imax=np.argmax(np.abs(Mx)); ax_ced.text(x0+xs[imax],-Mx[imax]*scM_ced-0.1,f"{Mx[imax]:.2f}",ha="center",fontsize=8,color="#d62728",fontweight="bold")
                    ax_ced.text(0,-MAB_cd*scM_ced+0.05,f"{MAB_cd:.2f}",ha="center",fontsize=9,fontweight="bold")
                    ax_ced.text(Lcd1,-MBA_cd*scM_ced+0.05,f"{MBA_cd:.2f}",ha="right",fontsize=9,fontweight="bold")
                    ax_ced.text(Lcd1,-MBC_cd*scM_ced+0.05,f"{MBC_cd:.2f}",ha="left",fontsize=9,fontweight="bold")
                    ax_ced.text(Ltot_ced,-MCB_cd*scM_ced+0.05,f"{MCB_cd:.2f}",ha="center",fontsize=9,fontweight="bold")
                    ax_ced.axhline(0,color="k",lw=0.5,ls="--"); ax_ced.set_xlim(-0.5,Ltot_ced+0.5); ax_ced.axis("off")
                    ax_ced.set_title(f"Diagram─â M ΓÇö Cedare ╬ö_B={delta_B*1000:.1f}mm",fontsize=12,fontweight="bold")
                    st.pyplot(fig_ced); plt.close(fig_ced)
                except ZeroDivisionError: st.error("Eroare la calcul.")

            # ---- DEPLASARI PUNCTUALE (MOHR) ----
            elif tip_s2=="Deplas─âri Punctuale (Mohr)":
                st.header("Deplas─âri Punctuale ΓÇö Integrala Mohr / Teorema Unit─â╚¢ii")
                with st.expander("Teorie (L1 ΓÇö Deplas─âri Punctuale)"):
                    st.markdown("""**Metoda Integralelor Mohr** (principiul lucr─ârilor virtuale):""")
                    st.latex(r"\delta = \int_0^L \frac{\bar{M}(x) \cdot M_P(x)}{EI}\,dx")
                    st.markdown("""- **M╠ä(x)** = diagrama de moment de la o for╚¢─â unitar─â virtual─â ├«n punctul/direc╚¢ia deplas─ârii
        - **MΓéÜ(x)** = diagrama de moment din ├«nc─ârcarea real─â
        - Se calculeaz─â cu **regula lui Vere╚Öciagin** (produs grafic)

        **Formula Vere╚Öciagin (diagrame trapezoidale):**""")
                    st.latex(r"\int_0^L \bar{M}\cdot M_P\,dx = \frac{L}{6}(2m_1\bar{m}_1+2m_2\bar{m}_2+m_1\bar{m}_2+m_2\bar{m}_1)")
                    st.markdown("Pentru diagram─â triunghiular─â ├ù dreptunghiular─â: **╬⌐ ┬╖ ╚│** (aria ├ù ordinata sub centrul ariei)")

                st.markdown("#### Grind─â Simpl─â ΓÇö S─âgeat─â ╚Öi Rotire")
                mo_c1,mo_c2=st.columns(2)
                with mo_c1:
                    Lmo=st.number_input("Lungime L (m)",min_value=1.0,value=8.0,step=0.5,key="mo_L")
                    EImo=st.number_input("EI (kNm┬▓)",min_value=1.0,value=20000.0,step=1000.0,key="mo_EI")
                    qmo=st.number_input("q distribuit (kN/m)",min_value=0.0,value=15.0,step=1.0,key="mo_q")
                with mo_c2:
                    Pmo=st.number_input("For╚¢─â concentrat─â P (kN)",min_value=0.0,value=30.0,step=5.0,key="mo_P")
                    xPmo=st.number_input("Pozi╚¢ie P (m de la A)",min_value=0.0,value=float(Lmo)/2,max_value=float(Lmo),step=0.5,key="mo_xP")
                    tipmo=st.selectbox("Calcul deplasare",["S─âgeat─â la mijloc (╬┤_C)","Rotire la cap─ât A (╬╕_A)","S─âgeat─â sub for╚¢a P"],key="mo_tip")

                RBmo=(qmo*Lmo**2/2+Pmo*(Lmo-xPmo))/Lmo; RAmo=qmo*Lmo+Pmo-RBmo
                xs_mo=np.linspace(0,Lmo,400)
                MP_mo=np.array([RAmo*x-qmo*x**2/2-(Pmo*(x-xPmo) if x>=xPmo else 0) for x in xs_mo])

                if tipmo=="S─âgeat─â la mijloc (╬┤_C)":
                    xv=Lmo/2
                    MB1_mo=np.array([0.5*x if x<=xv else 0.5*(Lmo-x) for x in xs_mo])
                    delta_mo=np.trapz(MB1_mo*MP_mo,xs_mo)/EImo
                    label_mo=r"\delta_C=\int_0^L\frac{\bar{M}_C\cdot M_P}{EI}dx"
                    val_label=f"╬┤_C = {delta_mo*1000:.4f} mm"
                elif tipmo=="Rotire la cap─ât A (╬╕_A)":
                    MB1_mo=np.array([1-x/Lmo for x in xs_mo])
                    delta_mo=np.trapz(MB1_mo*MP_mo,xs_mo)/EImo
                    label_mo=r"\theta_A=\int_0^L\frac{\bar{M}_A\cdot M_P}{EI}dx"
                    val_label=f"╬╕_A = {delta_mo*1000:.4f} mrad"
                else:
                    xv=xPmo; b=Lmo-xv
                    MB1_mo=np.array([(b/Lmo)*x if x<=xv else (xv/Lmo)*(Lmo-x) for x in xs_mo])
                    delta_mo=np.trapz(MB1_mo*MP_mo,xs_mo)/EImo
                    label_mo=r"\delta_P=\int_0^L\frac{\bar{M}_P\cdot M_P}{EI}dx"
                    val_label=f"╬┤_P = {delta_mo*1000:.4f} mm"

                st.latex(rf"{label_mo}")
                st.metric(val_label.split("=")[0].strip(), val_label.split("=")[1].strip())

                fig_mo,(ax_mp,ax_mb)=plt.subplots(2,1,figsize=(11,7),dpi=150,sharex=True)
                scP=0.5/max(0.01,np.max(np.abs(MP_mo))+0.01)
                ax_mp.fill_between(xs_mo,-MP_mo*scP,0,alpha=0.38,color="#d62728"); ax_mp.plot(xs_mo,-MP_mo*scP,"#d62728",lw=2.2)
                ax_mp.axhline(0,color="k",lw=1.5); ax_mp.set_title("MΓéÜ(x) ΓÇö Momentul din ├Änc─ârcarea Real─â",fontsize=11,fontweight="bold",color="#d62728")
                ax_mp.axis("off")
                imax_p=np.argmax(np.abs(MP_mo)); ax_mp.text(xs_mo[imax_p],-MP_mo[imax_p]*scP-0.08,f"{MP_mo[imax_p]:.2f}kNm",ha="center",fontsize=9,color="#d62728",fontweight="bold")
                scB=0.5/max(0.01,np.max(np.abs(MB1_mo))+0.01)
                ax_mb.fill_between(xs_mo,-MB1_mo*scB,0,alpha=0.32,color="#1f77b4"); ax_mb.plot(xs_mo,-MB1_mo*scB,"#1f77b4",lw=2.2)
                ax_mb.axhline(0,color="k",lw=1.5); ax_mb.set_title("M╠ä(x) ΓÇö Momentul Virtual (for╚¢─â unitar─â)",fontsize=11,fontweight="bold",color="#1f77b4")
                ax_mb.set_xlabel("x (m)",fontsize=11); ax_mb.axis("off")
                ax_mb.text(xs_mo[len(xs_mo)//2],-MB1_mo[len(xs_mo)//2]*scB-0.08,f"max={np.max(MB1_mo):.3f}",ha="center",fontsize=9,color="#1f77b4",fontweight="bold")
                plt.tight_layout(); st.pyplot(fig_mo); plt.close(fig_mo)

                if qmo>0 and Pmo==0:
                    st.markdown("#### Verificare Analitic─â (formula clasic─â pentru q uniform)")
                    if tipmo=="S─âgeat─â la mijloc (╬┤_C)":
                        delta_ana=5*qmo*Lmo**4/(384*EImo)
                        st.latex(rf"\delta_C=\frac{{5qL^4}}{{384EI}}=\frac{{5\times{qmo}\times{Lmo:.0f}^4}}{{384\times{EImo:.0f}}}={delta_ana*1000:.4f}\text{{ mm}}")
                    elif tipmo=="Rotire la cap─ât A (╬╕_A)":
                        theta_ana=qmo*Lmo**3/(24*EImo)
                        st.latex(rf"\theta_A=\frac{{qL^3}}{{24EI}}={theta_ana*1000:.4f}\text{{ mrad}}")
