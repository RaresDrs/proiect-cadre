
# build_app.py — writes the complete redesigned app.py
# Run: python build_app.py

import os

HEADER = '''\
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages

# ============================================================
# PAGINA
# ============================================================
st.set_page_config(
    page_title="EduStruct \u2014 Mini-SAP2000 Educational",
    layout="wide", page_icon="\U0001f3d7\ufe0f", initial_sidebar_state="expanded"
)
st.markdown("""
<style>
[data-testid="stSidebar"]{background:#0d1b2a;}
[data-testid="stSidebar"] *{color:#e8e8e8!important;}
h1{color:#0d1b2a;border-bottom:3px solid #E8641A;padding-bottom:8px;}
h2{color:#1a3a5c;}h3{color:#0d1b2a;}
.result-box{background:linear-gradient(135deg,#f0f4ff,#e8f0fe);border-left:5px solid #E8641A;
  padding:14px 18px;border-radius:8px;margin:10px 0;}
div[data-testid="stMetric"]{background:#f8f9fa;border-radius:10px;padding:12px;border:1px solid #dee2e6;}
.stTabs [data-baseweb="tab"]{background:#f0f4ff;border-radius:8px 8px 0 0;padding:8px 18px;font-weight:600;}
.stTabs [aria-selected="true"]{background:#E8641A!important;color:white!important;}
</style>
""", unsafe_allow_html=True)
st.markdown("<div style='text-align:right;color:#999;font-size:14px;'>Stud. Pop Rare\u015f Darius | EduStruct v2.0</div>", unsafe_allow_html=True)

# ============================================================
# UTILITARE
# ============================================================
def to_sci(val):
    if val==0: return "0"
    exp=int(np.floor(np.log10(abs(val))))
    coef=val/(10**exp)
    return rf"{coef:.3f} \\cdot 10^{{{exp}}}"

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

def draw_fixed_bottom(ax,x,y,size=0.35,color='k'):
    ax.plot([x-size*1.6,x+size*1.6],[y,y],color=color,lw=3,zorder=5)
    for xx in np.linspace(x-size*1.3,x+size*1.3,9):
        ax.plot([xx,xx-size*0.4],[y,y-size*0.55],color=color,lw=1,zorder=4)

def draw_fixed_left(ax,x,y_bot,height,size=0.3,color='k'):
    ax.plot([x,x],[y_bot,y_bot+height],color=color,lw=3.5,zorder=5)
    for yy in np.linspace(y_bot,y_bot+height,9):
        ax.plot([x-size*0.9,x],[yy-size*0.35,yy],color=color,lw=1,zorder=4)

def draw_axes(ax,ox,oy,length=0.8,color='gray',fontsize=8):
    ax.annotate('',xy=(ox+length,oy),xytext=(ox,oy),arrowprops=dict(arrowstyle='->',color=color,lw=1.2))
    ax.text(ox+length+0.06,oy,'x',color=color,fontsize=fontsize,va='center')
    ax.annotate('',xy=(ox,oy+length),xytext=(ox,oy),arrowprops=dict(arrowstyle='->',color=color,lw=1.2))
    ax.text(ox,oy+length+0.06,'y',color=color,fontsize=fontsize,ha='center')

def draw_force_arrow(ax,x,y,fx,fy,label,color='red',scale=0.8):
    mag=np.sqrt(fx**2+fy**2)
    if mag<1e-10: return
    ux,uy=fx/mag,fy/mag
    ax.annotate('',xy=(x,y),xytext=(x-ux*scale,y-uy*scale),
                arrowprops=dict(arrowstyle='->',color=color,lw=2.2,mutation_scale=14))
    ax.text(x-ux*scale*1.15,y-uy*scale*1.15,label,color=color,fontsize=8.5,fontweight='bold',
            ha='center',va='center',bbox=dict(fc='white',alpha=0.6,ec='none',pad=1))

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

def draw_moment_arc(ax,x,y,M,r=0.25,color='purple'):
    if abs(M)<1e-9: return
    t1,t2=(30,330) if M>0 else (210,510)
    ax.add_patch(Arc((x,y),r*2,r*2,angle=0,theta1=t1,theta2=t2,color=color,lw=2))
    ang=np.radians(t2 if M>0 else t1); eps=0.01*(-1 if M>0 else 1)
    ax.annotate('',xy=(x+r*np.cos(ang),y+r*np.sin(ang)),
                xytext=(x+r*np.cos(ang-eps),y+r*np.sin(ang-eps)),
                arrowprops=dict(arrowstyle='->',color=color,lw=1.5))

def fill_diagram(ax,x,y,color,label,alpha=0.32):
    ax.fill_between(x,y,0,color=color,alpha=alpha); ax.plot(x,y,color=color,lw=2.2)
    ax.axhline(0,color='black',lw=1.2); ax.set_ylabel(label,color=color,fontweight='bold',fontsize=10)
    ax.grid(True,alpha=0.18,linestyle='--'); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

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

# ============================================================
# NAVIGARE
# ============================================================
st.sidebar.markdown("## \U0001f3d7\ufe0f EduStruct")
st.sidebar.markdown("<small>Mini-SAP2000 Educational</small>",unsafe_allow_html=True)
st.sidebar.markdown("---")
modul=st.sidebar.radio("**Selecteaz\u0103 Modulul**",[
    "\U0001f527 Calcul 2D FEM",
    "\U0001f4d0 Rezisten\u021ba Materialelor",
    "\U0001f4cf Statica 1 \u2014 Static Determinate",
    "\U0001f501 Statica 2 \u2014 Static Nedeterminate",
],key="nav_modul_main")
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#aaa;'>Bazat pe manualele rom\u00e2ne\u0219ti:<br>975-4.pdf Statica1<br>138-3.pdf Statica2<br>481-0.pdf RezMat</small>",unsafe_allow_html=True)
'''

FEM = '''\

# ============================================================
# MODUL 1: CALCUL 2D FEM
# ============================================================
if modul == "\U0001f527 Calcul 2D FEM":
    st.title("Calcul FEM Bar\u0103 2D")
    st.markdown("Analiz\u0103 structural\u0103 prin **Metoda Elementelor Finite** pentru bar\u0103/grind\u0103 2D.")
    st.markdown("---")
    if "L_val" not in st.session_state: st.session_state.L_val=6.0
    if "Ang_val" not in st.session_state: st.session_state.Ang_val=0.0
    def _upd_Lsl(): st.session_state.L_val=st.session_state.L_slider_fem
    def _upd_Lni(): st.session_state.L_val=st.session_state.L_num_fem
    def _upd_Asl(): st.session_state.Ang_val=float(st.session_state.A_slider_fem)
    def _upd_Ani(): st.session_state.Ang_val=float(st.session_state.A_num_fem)
    st.sidebar.header("1. Geometrie Bar\u0103")
    st.sidebar.slider("Lungime L (m)",0.1,30.0,float(st.session_state.L_val),key="L_slider_fem",on_change=_upd_Lsl)
    L=st.sidebar.number_input("L exact (m):",value=float(st.session_state.L_val),key="L_num_fem",on_change=_upd_Lni,min_value=0.1)
    st.sidebar.slider("\u00cenclinare (\u00b0)",0.0,90.0,float(st.session_state.Ang_val),key="A_slider_fem",on_change=_upd_Asl)
    theta_deg=st.sidebar.number_input("Unghi (\u00b0):",value=float(st.session_state.Ang_val),key="A_num_fem",on_change=_upd_Ani,min_value=0.0,max_value=90.0)
    b_cm=st.sidebar.number_input("L\u0103\u021bime b (cm)",min_value=0.0,value=30.0,key="fem_b_cm")
    h_cm=st.sidebar.number_input("\u00cen\u0103l\u021bime h (cm)",min_value=0.0,value=50.0,key="fem_h_cm")
    b,h_sec=b_cm/100,h_cm/100; A_sec=b*h_sec; I_sec=(b*h_sec**3)/12 if b>0 and h_sec>0 else 0
    st.sidebar.markdown("### Sec\u021biune")
    if A_sec>0:
        st.sidebar.latex(rf"A={b_cm:.0f}\\times{h_cm:.0f}={A_sec*1e4:.1f}\\text{{ cm}}^2")
        st.sidebar.latex(rf"I={to_sci(I_sec)}\\text{{ m}}^4")
    st.sidebar.header("2. Material")
    mat=st.sidebar.selectbox("Material",["Beton C20/25","Beton C25/30","Beton C30/37","Beton C35/45","O\u021bel S235","O\u021bel S275","O\u021bel S355"],key="fem_mat")
    E_dict={"Beton C20/25":30e6,"Beton C25/30":31e6,"Beton C30/37":33e6,"Beton C35/45":34e6,"O\u021bel S235":210e6,"O\u021bel S275":210e6,"O\u021bel S355":210e6}
    E=E_dict[mat]
    st.sidebar.header("3. Reazeme")
    ro={0:"Liber",1:"Articula\u021bie",2:"Reazem simplu",3:"\u00cencastrare"}
    r1=st.sidebar.selectbox("Nod A",[0,1,2,3],index=1,format_func=lambda x:ro[x],key="fem_r1")
    r2=st.sidebar.selectbox("Nod B",[0,1,2,3],index=2,format_func=lambda x:ro[x],key="fem_r2")
    gdl=sum([2 if r==1 else 1 if r==2 else 3 if r==3 else 0 for r in [r1,r2]])
    G=gdl-3
    if G==0: st.sidebar.success(f"Static Determinat\u0103 (G=0)")
    elif G>0: st.sidebar.warning(f"Nedeterminat\u0103 ns={G}")
    else: st.sidebar.error(f"MECANISM! G={G}")

    st.header("Configurare \u00cenc\u0103rc\u0103ri")
    c1,c2,c3=st.columns(3)
    with c1: q_val=st.number_input("q (kN/m) jos pozitiv",value=0.0,step=1.0,key="fem_q")
    with c2: q_start=st.number_input("De la x(m)",min_value=0.0,value=0.0,key="fem_qstart")
    with c3: q_end=st.number_input("P\u00e2n\u0103 la x(m)",min_value=0.0,value=float(L),key="fem_qend")
    if "fem_forces" not in st.session_state: st.session_state.fem_forces=[]
    ca,cb=st.columns([1,5])
    with ca:
        if st.button("+ For\u021b\u0103/Moment",key="fem_add"): st.session_state.fem_forces.append({"tip":"Fy","val":0.0,"dist":L/2})
        if st.button("- \u0218terge ultima",key="fem_del"):
            if st.session_state.fem_forces: st.session_state.fem_forces.pop()
    edited=[]
    if st.session_state.fem_forces:
        cols=st.columns(min(len(st.session_state.fem_forces),4))
        for i,f in enumerate(st.session_state.fem_forces):
            with cols[i%4]:
                st.markdown(f"**Ac\u021biunea {i+1}**")
                tip=st.selectbox("Tip",["Fy","Fx","M"],index=["Fy","Fx","M"].index(f["tip"]),key=f"fem_tip_{i}")
                val=st.number_input("Valoare",value=f["val"],key=f"fem_val_{i}")
                d=st.number_input("x(m)",0.0,float(L),float(f["dist"]),key=f"fem_d_{i}")
                edited.append({"tip":tip,"val":val,"dist":d})
        st.session_state.fem_forces=edited

    th=np.radians(theta_deg); c_ang,s_ang=np.cos(th),np.sin(th); end_x,end_y=L*c_ang,L*s_ang
    fig1,ax1=plt.subplots(figsize=(11,max(3.5,7*s_ang+1.5)),dpi=150)
    ax1.plot([0,end_x],[0,end_y],"k-",lw=5.5,zorder=3,solid_capstyle="round")
    ax1.text(end_x/2,end_y/2+0.35,f"L={L:.2f} m",ha="center",fontsize=11,fontweight="bold",color="#1a3a5c")
    ss=max(0.18,L*0.028)
    if r1==1: draw_pin(ax1,0,0,ss)
    elif r1==2: draw_roller(ax1,0,0,ss)
    elif r1==3: draw_fixed_bottom(ax1,0,0,ss)
    if r2==1: draw_pin(ax1,end_x,end_y,ss)
    elif r2==2: draw_roller(ax1,end_x,end_y,ss)
    elif r2==3: draw_fixed_bottom(ax1,end_x,end_y,ss)
    ax1.text(0,ss*2,"A",fontsize=11,fontweight="bold",ha="center")
    ax1.text(end_x,end_y+ss*2,"B",fontsize=11,fontweight="bold",ha="center")
    if q_val>0 and q_end>q_start: draw_distributed_load(ax1,q_start*c_ang,q_end*c_ang,end_y+0.7,q_val)
    arsc=max(0.55,L*0.09)
    for f in st.session_state.fem_forces:
        if abs(f["val"])>0:
            fp,fyp=f["dist"]*c_ang,f["dist"]*s_ang
            if f["tip"]=="Fy": draw_force_arrow(ax1,fp,fyp,0,1 if f["val"]>0 else -1,f"{abs(f['val'])}kN",scale=arsc)
            elif f["tip"]=="Fx": draw_force_arrow(ax1,fp,fyp,1 if f["val"]>0 else -1,0,f"{abs(f['val'])}kN",scale=arsc)
            else: draw_moment_arc(ax1,fp,fyp,f["val"],r=ss*1.5,color="purple")
    draw_axes(ax1,min(0,end_x)-1.2,min(0,end_y)-0.1,length=0.7)
    mg=max(L*0.22,1.8)
    ax1.set_xlim(min(0,end_x)-mg,max(0,end_x)+mg); ax1.set_ylim(min(0,end_y)-mg,max(0,end_y)+mg)
    ax1.set_aspect("equal"); ax1.axis("off"); ax1.set_title("Schi\u021b\u0103 Model Structural FEM",fontsize=13,fontweight="bold")
    st.pyplot(fig1); plt.close(fig1)

    st.markdown("---")
    if st.button("Efectueaz\u0103 Calculul FEM",type="primary",use_container_width=True,key="fem_calc_btn"):
        if A_sec==0: st.error("Introduce\u021bi sec\u021biunea.")
        else:
            try:
                raw_nodes=[0.0,L]+[f["dist"] for f in st.session_state.fem_forces if abs(f["val"])>0]
                if q_val>0: raw_nodes+=[q_start,q_end]
                nodes_s=np.unique(np.round(raw_nodes,6)).tolist(); nn=len(nodes_s); ne=nn-1
                T_blk=np.array([[c_ang,s_ang,0],[-s_ang,c_ang,0],[0,0,1]])
                T6=np.zeros((6,6)); T6[:3,:3]=T_blk; T6[3:,3:]=T_blk
                K_g=np.zeros((3*nn,3*nn)); F_g=np.zeros(3*nn)
                for i in range(ne):
                    Le=nodes_s[i+1]-nodes_s[i]
                    if Le<=0: continue
                    EA=E*A_sec/Le; EI12=12*E*I_sec/Le**3; EI6=6*E*I_sec/Le**2; EI4=4*E*I_sec/Le; EI2=2*E*I_sec/Le
                    k_l=np.array([[EA,0,0,-EA,0,0],[0,EI12,EI6,0,-EI12,EI6],[0,EI6,EI4,0,-EI6,EI2],
                        [-EA,0,0,EA,0,0],[0,-EI12,-EI6,0,EI12,-EI6],[0,EI6,EI2,0,-EI6,EI4]])
                    k_glob=T6.T@k_l@T6; idx=slice(3*i,3*i+6); K_g[idx,idx]+=k_glob
                    mid=(nodes_s[i]+nodes_s[i+1])/2
                    if q_val>0 and (q_start-1e-6<=mid<=q_end+1e-6):
                        qv=-q_val; qyl=qv*c_ang; qxl=qv*s_ang
                        fe=np.array([qxl*Le/2,qyl*Le/2,qyl*Le**2/12,qxl*Le/2,qyl*Le/2,-qyl*Le**2/12])
                        F_g[idx]+=T6.T@fe
                for f in st.session_state.fem_forces:
                    if abs(f["val"])>0:
                        ni=nodes_s.index(round(f["dist"],6))
                        if f["tip"]=="Fx": F_g[3*ni]+=f["val"]
                        elif f["tip"]=="Fy": F_g[3*ni+1]+=f["val"]
                        else: F_g[3*ni+2]+=f["val"]
                bl=[]
                if r1==1: bl+=[0,1]
                elif r1==2: bl+=[1]
                elif r1==3: bl+=[0,1,2]
                lst=3*(nn-1)
                if r2==1: bl+=[lst,lst+1]
                elif r2==2: bl+=[lst+1]
                elif r2==3: bl+=[lst,lst+1,lst+2]
                free=[i for i in range(3*nn) if i not in bl]
                U_g=np.zeros(3*nn); U_g[free]=np.linalg.solve(K_g[np.ix_(free,free)],F_g[free])
                R_g=K_g@U_g-F_g
                x_pl,N_pl,V_pl,M_pl=[],[],[],[]
                U_loc=np.zeros(3*nn)
                for i in range(nn): U_loc[3*i:3*i+3]=T_blk@U_g[3*i:3*i+3]
                for i in range(ne):
                    Le=nodes_s[i+1]-nodes_s[i]
                    if Le<=0: continue
                    EA=E*A_sec/Le; EI12=12*E*I_sec/Le**3; EI6=6*E*I_sec/Le**2; EI4=4*E*I_sec/Le; EI2=2*E*I_sec/Le
                    k_l=np.array([[EA,0,0,-EA,0,0],[0,EI12,EI6,0,-EI12,EI6],[0,EI6,EI4,0,-EI6,EI2],
                        [-EA,0,0,EA,0,0],[0,-EI12,-EI6,0,EI12,-EI6],[0,EI6,EI2,0,-EI6,EI4]])
                    ue=np.concatenate([U_loc[3*i:3*i+3],U_loc[3*(i+1):3*(i+1)+3]])
                    fel=np.zeros(6); mid=(nodes_s[i]+nodes_s[i+1])/2
                    hq=q_val>0 and (q_start-1e-6<=mid<=q_end+1e-6); qyl=0
                    if hq:
                        qv=-q_val; qyl=qv*c_ang; qxl=qv*s_ang
                        fel=np.array([qxl*Le/2,qyl*Le/2,qyl*Le**2/12,qxl*Le/2,qyl*Le/2,-qyl*Le**2/12])
                    fe2=k_l@ue-fel; Ns=-fe2[0]; Vs=fe2[1]; Ms=-fe2[2]
                    xs=np.linspace(0,Le,60)
                    if hq: Nx=Ns*np.ones_like(xs); Vx=Vs+qyl*xs; Mx=Ms+Vs*xs+qyl*xs**2/2
                    else: Nx=Ns*np.ones_like(xs); Vx=Vs*np.ones_like(xs); Mx=Ms+Vs*xs
                    x_pl.extend(nodes_s[i]+xs); N_pl.extend(Nx); V_pl.extend(Vx); M_pl.extend(Mx)
                st.success("Calcul FEM finalizat!")
                RxA,RyA,MzA=R_g[0],R_g[1],R_g[2]; RxB,RyB,MzB=R_g[-3],R_g[-2],R_g[-1]
                cr1,cr2=st.columns(2)
                with cr1:
                    st.markdown("**Reac\u021biuni Nod A:**")
                    if r1 in [1,3]: st.markdown(f"HA = **{RxA:.4f} kN**")
                    if r1 in [1,2,3]: st.markdown(f"VA = **{RyA:.4f} kN**")
                    if r1==3: st.markdown(f"MA = **{MzA:.4f} kNm**")
                with cr2:
                    st.markdown("**Reac\u021biuni Nod B:**")
                    if r2 in [1,3]: st.markdown(f"HB = **{RxB:.4f} kN**")
                    if r2 in [1,2,3]: st.markdown(f"VB = **{RyB:.4f} kN**")
                    if r2==3: st.markdown(f"MB = **{MzB:.4f} kNm**")
                st.metric("S\u0103geat\u0103 max",f"{np.max(np.abs(U_loc[1::3]))*1000:.4f} mm")
                xa=np.array(x_pl)
                fig_r,(aN,aV,aM)=plt.subplots(3,1,figsize=(12,10),sharex=True,dpi=180)
                fill_diagram(aN,xa,np.array(N_pl),"#1a6faf","N (kN)"); aN.set_title("N(x)",fontweight="bold",color="#1a6faf"); label_extremes(aN,xa,np.array(N_pl),"#1a6faf")
                fill_diagram(aV,xa,np.array(V_pl),"#2ca02c","T (kN)"); aV.set_title("T(x)",fontweight="bold",color="#2ca02c"); label_extremes(aV,xa,np.array(V_pl),"#2ca02c")
                fill_diagram(aM,xa,np.array(M_pl),"#d62728","M (kNm)"); aM.set_title("M(x) [fibra \u00efntins\u0103]",fontweight="bold",color="#d62728"); aM.invert_yaxis(); label_extremes(aM,xa,np.array(M_pl),"#d62728")
                aM.set_xlabel("x (m)",fontsize=11); plt.tight_layout(); fig_r.suptitle("Diagrame N,T,M \u2014 FEM",fontsize=14,fontweight="bold",y=1.01)
                st.pyplot(fig_r)
                buf=BytesIO()
                with PdfPages(buf) as pdf:
                    pdf.savefig(fig1,bbox_inches="tight"); pdf.savefig(fig_r,bbox_inches="tight")
                st.download_button("Descarc\u0103 PDF",buf.getvalue(),"FEM.pdf","application/pdf",key="fem_dl"); plt.close(fig_r)
            except np.linalg.LinAlgError:
                st.error("MECANISM! Structura instabil\u0103.")
'''

REZMAT = '''\

# ============================================================
# MODUL 2: REZISTENTA MATERIALELOR
# ============================================================
elif modul == "\U0001f4d0 Rezisten\u021ba Materialelor":
    st.title("Rezisten\u021ba Materialelor I")
    st.markdown("Calcule conform *Rezisten\u021ba Materialelor I* (481-0.pdf)")
    st.markdown("---")
    tab1,tab2,tab3,tab4,tab5=st.tabs(["Propriet\u0103\u021bi Geometrice","Tensiune Axial\u0103","Invoiere Plan\u0103","Forfecare & Torsiune","Flambaj Euler"])

    with tab1:
        st.subheader("Propriet\u0103\u021bi Geometrice")
        with st.expander("Teorie (481-0.pdf, Cap.1)"):
            st.latex(r"I_x=\\frac{bh^3}{12},\\; I_x^{cerc}=\\frac{\\pi d^4}{64},\\; W_x=\\frac{I_x}{y_{max}},\\; i_x=\\sqrt{I_x/A}")
            st.latex(r"\\text{Steiner: }I_{x\\'} = I_x + A\\cdot d^2")
        forma=st.selectbox("Form\u0103 sec\u021biune",["Dreptunghi plin","Cerc plin","Inel circular","Sec\u021biune T","Sec\u021biune I"],key="rm_forma")
        ci,cd=st.columns(2)
        if forma=="Dreptunghi plin":
            with ci:
                b_d=st.number_input("L\u0103\u021bime b (cm)",min_value=0.1,value=30.0,step=1.0,key="rm_bd")
                h_d=st.number_input("\u00cen\u0103l\u021bime h (cm)",min_value=0.1,value=50.0,step=1.0,key="rm_hd")
            A_d=b_d*h_d; Ix=b_d*h_d**3/12; Iy=h_d*b_d**3/12; Wx=Ix/(h_d/2); ix=np.sqrt(Ix/A_d)
            with ci:
                st.latex(rf"A={b_d:.1f}\\times{h_d:.1f}={A_d:.2f}\\text{{ cm}}^2")
                st.latex(rf"I_x=\\frac{{bh^3}}{{12}}={Ix:.2f}\\text{{ cm}}^4")
                st.latex(rf"W_x={Wx:.2f}\\text{{ cm}}^3,\\; i_x={ix:.3f}\\text{{ cm}}")
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
                st.latex(rf"A=\\frac{{\\pi d^2}}{{4}}={Ac:.3f}\\text{{ cm}}^2")
                st.latex(rf"I_x=\\frac{{\\pi d^4}}{{64}}={Ixc:.3f}\\text{{ cm}}^4")
                st.latex(rf"W_x={Wxc:.3f}\\text{{ cm}}^3,\\; i_x={ixc:.3f}\\text{{ cm}}")
                st.latex(rf"I_p=\\frac{{\\pi d^4}}{{32}}={Ipc:.3f}\\text{{ cm}}^4")
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
                    st.latex(rf"A=\\frac{{\\pi(D^2-d^2)}}{{4}}={Ai:.3f}\\text{{ cm}}^2")
                    st.latex(rf"I_x=\\frac{{\\pi(D^4-d^4)}}{{64}}={Ixi:.3f}\\text{{ cm}}^4")
                    st.latex(rf"W_x={Wxi:.3f}\\text{{ cm}}^3")
        elif forma=="Sec\u021biune T":
            with ci:
                bt=st.number_input("L\u0103\u021bime talp\u0103 bt (cm)",value=20.0,key="rm_bt")
                tt=st.number_input("Grosime talp\u0103 tt (cm)",value=3.0,key="rm_tt")
                bw=st.number_input("L\u0103\u021bime inim\u0103 bw (cm)",value=3.0,key="rm_bw")
                hw=st.number_input("\u00cen\u0103l\u021bime inim\u0103 hw (cm)",value=15.0,key="rm_hw")
            At=bt*tt; Aw=bw*hw; AT=At+Aw; yt=hw+tt/2; yw=hw/2; yC=(At*yt+Aw*yw)/AT
            IT=bt*tt**3/12+At*(yt-yC)**2+bw*hw**3/12+Aw*(yw-yC)**2; Wx_T=IT/max(yC,hw+tt-yC)
            with ci:
                st.latex(rf"y_C={yC:.3f}\\text{{ cm}}")
                st.latex(rf"I_x={IT:.3f}\\text{{ cm}}^4")
                st.latex(rf"W_x={Wx_T:.3f}\\text{{ cm}}^3")
        elif forma=="Sec\u021biune I":
            with ci:
                bf=st.number_input("L\u0103\u021bime t\u0103lpi bf (cm)",value=15.0,key="rm_bf")
                tf=st.number_input("Grosime t\u0103lpi tf (cm)",value=1.5,key="rm_tf")
                hwI=st.number_input("\u00cen\u0103l\u021bime inim\u0103 (cm)",value=20.0,key="rm_hwI")
                twI=st.number_input("Grosime inim\u0103 (cm)",value=1.0,key="rm_twI")
            htot=hwI+2*tf; AI=2*bf*tf+hwI*twI; IxI=(bf*htot**3-(bf-twI)*hwI**3)/12; WxI=IxI/(htot/2)
            with ci:
                st.latex(rf"A={AI:.3f}\\text{{ cm}}^2")
                st.latex(rf"I_x={IxI:.3f}\\text{{ cm}}^4")
                st.latex(rf"W_x={WxI:.3f}\\text{{ cm}}^3")

    with tab2:
        st.subheader("\u00centindere \u0219i Compresiune Axial\u0103")
        with st.expander("Teorie (481-0.pdf, Cap.2)"):
            st.latex(r"\\sigma=\\frac{N}{A}\\leq f_d,\\; \\varepsilon=\\frac{\\sigma}{E},\\; \\Delta l=\\frac{NL}{EA}")
        c1,c2=st.columns(2)
        with c1:
            Ntc=st.number_input("For\u021b\u0103 axial\u0103 N (kN) [+ \u00eentindere]",value=100.0,step=10.0,key="rm_N")
            Ltc=st.number_input("Lungime L (m)",min_value=0.01,value=3.0,key="rm_L")
            btc=st.number_input("L\u0103\u021bime b (cm)",min_value=0.1,value=20.0,key="rm_btc")
            htc=st.number_input("\u00cen\u0103l\u021bime h (cm)",min_value=0.1,value=30.0,key="rm_htc")
        with c2:
            matc=st.selectbox("Material",["Beton C25/30","Beton C30/37","O\u021bel S235","O\u021bel S275","O\u021bel S355"],key="rm_matc")
            Ecd={"Beton C25/30":31000,"Beton C30/37":33000,"O\u021bel S235":210000,"O\u021bel S275":210000,"O\u021bel S355":210000}
            fdd={"Beton C25/30":1.67,"Beton C30/37":2.0,"O\u021bel S235":23.5,"O\u021bel S275":27.5,"O\u021bel S355":35.5}
            Etc=Ecd[matc]; fdtc=fdd[matc]; st.info(f"E={Etc} kN/cm\u00b2 | f_d={fdtc} kN/cm\u00b2")
        Atc=btc*htc; sigma=Ntc/Atc; eps=sigma/Etc; dl=Ntc*Ltc*100/(Etc*Atc)
        st.latex(rf"A={btc:.1f}\\times{htc:.1f}={Atc:.2f}\\text{{ cm}}^2")
        st.latex(rf"\\sigma=\\frac{{N}}{{A}}=\\frac{{{Ntc:.2f}}}{{{Atc:.2f}}}={sigma:.4f}\\text{{ kN/cm}}^2={sigma*10:.3f}\\text{{ MPa}}")
        st.latex(rf"\\varepsilon={eps:.2e},\\; \\Delta l={dl:.4f}\\text{{ cm}}")
        if abs(sigma)<=fdtc: st.success(f"VERIFICARE OK: |\u03c3|={abs(sigma):.4f}\u2264f_d={fdtc}")
        else:
            st.error(f"DEP\u0102\u0218IT\u0102: |\u03c3|={abs(sigma):.4f}>f_d={fdtc}")
            st.warning(f"A_nec={abs(Ntc)/fdtc:.2f} cm\u00b2")
        fig_tc,ax_tc=plt.subplots(figsize=(9,3),dpi=120)
        cc="#1a6faf" if Ntc>=0 else "#d62728"
        ax_tc.fill_between([0,Ltc],[Ntc,Ntc],0,color=cc,alpha=0.35); ax_tc.plot([0,Ltc],[Ntc,Ntc],color=cc,lw=3)
        ax_tc.axhline(0,color="k",lw=1.5); ax_tc.set_xlabel("x(m)"); ax_tc.set_ylabel("N(kN)",color=cc)
        ax_tc.set_title(f"Diagram\u0103 N | {'\u00centindere' if Ntc>=0 else 'Compresiune'}",fontweight="bold")
        ax_tc.text(Ltc/2,Ntc*0.7 if abs(Ntc)>0 else 0.5,f"N={Ntc:.2f}kN",ha="center",color=cc,fontsize=11,fontweight="bold")
        plt.tight_layout(); st.pyplot(fig_tc); plt.close(fig_tc)

    with tab3:
        st.subheader("Invoiere Plan\u0103 \u2014 Formula Navier")
        with st.expander("Teorie (481-0.pdf, Cap.4)"):
            st.latex(r"\\sigma_x(y)=\\frac{M}{I_x}\\cdot y,\\; \\sigma_{max}=\\frac{M}{W_x},\\; W_x=\\frac{I_x}{y_{max}}")
        c1,c2=st.columns(2)
        with c1:
            Mnc=st.number_input("Moment M (kNm)",value=50.0,step=5.0,key="rm_Mnc")
            bnc=st.number_input("L\u0103\u021bime b (cm)",min_value=0.1,value=20.0,key="rm_bnc")
            hnc=st.number_input("\u00cen\u0103l\u021bime h (cm)",min_value=0.1,value=40.0,key="rm_hnc")
        with c2:
            matnc=st.selectbox("Material",["Beton C25/30","Beton C30/37","O\u021bel S235","O\u021bel S275","O\u021bel S355"],key="rm_matnc")
            fdnc={"Beton C25/30":1.67,"Beton C30/37":2.0,"O\u021bel S235":23.5,"O\u021bel S275":27.5,"O\u021bel S355":35.5}[matnc]
        Ixnc=bnc*hnc**3/12; Wxnc=Ixnc/(hnc/2); Mcm=Mnc*100; smax=Mcm/Wxnc
        st.latex(rf"I_x=\\frac{{bh^3}}{{12}}={Ixnc:.2f}\\text{{ cm}}^4,\\; W_x={Wxnc:.2f}\\text{{ cm}}^3")
        st.latex(rf"\\sigma_{{max}}=\\frac{{M}}{{W_x}}=\\frac{{{Mcm:.1f}}}{{{Wxnc:.2f}}}={smax:.4f}\\text{{ kN/cm}}^2={smax*10:.3f}\\text{{ MPa}}")
        if abs(smax)<=fdnc: st.success(f"VERIFICARE OK: \u03c3={abs(smax):.4f}\u2264f_d={fdnc}")
        else:
            st.error(f"DEP\u0102\u0218IT\u0102: \u03c3={abs(smax):.4f}>f_d={fdnc}")
            st.warning(f"W_nec={Mcm/fdnc:.2f} cm\u00b3")
        fig_nc,ax_nc=plt.subplots(figsize=(5,5),dpi=120)
        ync=np.linspace(-hnc/2,hnc/2,200); snc=Mcm/Ixnc*ync
        ax_nc.fill_betweenx(ync,snc,0,color="#d62728",alpha=0.35); ax_nc.plot(snc,ync,"r-",lw=2.5)
        ax_nc.axvline(0,color="k",lw=1.5); ax_nc.axhline(0,color="gray",ls="--",lw=1,label="Ax\u0103 neutr\u0103")
        ax_nc.set_xlabel("\u03c3(kN/cm\u00b2)"); ax_nc.set_ylabel("y(cm)"); ax_nc.legend()
        ax_nc.set_title("Distribu\u021bie tensiuni \u03c3(y)",fontweight="bold"); plt.tight_layout(); st.pyplot(fig_nc); plt.close(fig_nc)

    with tab4:
        st.subheader("Forfecare \u0219i Torsiune")
        sub1,sub2=st.tabs(["Forfecare","Torsiune"])
        with sub1:
            with st.expander("Teorie"):
                st.latex(r"\\tau=\\frac{T S_x^*}{I_x b},\\; \\tau_{max}^{drept}=\\frac{3T}{2A}")
            c1,c2=st.columns(2)
            with c1:
                Tff=st.number_input("For\u021b\u0103 t\u0103ietoare T(kN)",value=80.0,key="rm_Tff")
                bff=st.number_input("L\u0103\u021bime b(cm)",min_value=0.1,value=20.0,key="rm_bff")
                hff=st.number_input("\u00cen\u0103l\u021bime h(cm)",min_value=0.1,value=40.0,key="rm_hff")
            Aff=bff*hff; Ixff=bff*hff**3/12; tmx=1.5*Tff/Aff
            with c2:
                st.latex(rf"\\tau_{{max}}=\\frac{{3T}}{{2A}}=\\frac{{3\\times{Tff:.2f}}}{{2\\times{Aff:.2f}}}={tmx:.4f}\\text{{ kN/cm}}^2={tmx*10:.3f}\\text{{ MPa}}")
            yarr=np.linspace(-hff/2,hff/2,200); Sarr=bff*(hff**2/8-yarr**2/2); tarr=Tff*Sarr/(Ixff*bff)
            fig_ff,ax_ff=plt.subplots(figsize=(5,4.5),dpi=120)
            ax_ff.fill_betweenx(yarr,tarr,0,color="#2ca02c",alpha=0.35); ax_ff.plot(tarr,yarr,"g-",lw=2.5)
            ax_ff.axvline(0,color="k",lw=1.5); ax_ff.axhline(0,color="gray",ls="--",lw=1)
            ax_ff.set_xlabel("\u03c4(kN/cm\u00b2)"); ax_ff.set_ylabel("y(cm)"); ax_ff.set_title("Distribu\u021bie \u03c4 Zhuravski",fontweight="bold")
            plt.tight_layout(); st.pyplot(fig_ff); plt.close(fig_ff)
        with sub2:
            with st.expander("Teorie"):
                st.latex(r"\\tau_{tors}=\\frac{M_t}{W_p},\\; \\varphi=\\frac{M_t L}{G I_p}")
            c1,c2=st.columns(2)
            with c1:
                Mt=st.number_input("M_t (kNm)",value=10.0,key="rm_Mt"); dt=st.number_input("d(cm)",min_value=0.1,value=10.0,key="rm_dt")
                Lt=st.number_input("L(m)",min_value=0.01,value=2.0,key="rm_Lt"); Gt=st.number_input("G(kN/cm\u00b2)",value=8100.0,key="rm_Gt")
            Mtcm=Mt*100; Ipt=np.pi*dt**4/32; Wpt=Ipt/(dt/2); taut=Mtcm/Wpt; phit=Mtcm*Lt*100/(Gt*Ipt)
            with c2:
                st.latex(rf"I_p=\\frac{{\\pi d^4}}{{32}}={Ipt:.3f}\\text{{ cm}}^4")
                st.latex(rf"\\tau_{{tors}}=\\frac{{M_t}}{{W_p}}={taut:.4f}\\text{{ kN/cm}}^2={taut*10:.3f}\\text{{ MPa}}")
                st.latex(rf"\\varphi={phit:.5f}\\text{{ rad}}={np.degrees(phit):.4f}\\degree")

    with tab5:
        st.subheader("Flambaj Euler \u2014 Bare Comprimate")
        with st.expander("Teorie (481-0.pdf, Cap.7)"):
            st.latex(r"N_{cr}=\\frac{\\pi^2 E I_{min}}{(\\mu L)^2},\\; \\lambda=\\frac{\\mu L}{i_{min}},\\; \\sigma_{cr}=\\frac{N_{cr}}{A}")
            st.markdown("| Rezemare | \u03bc |\\n|---|---|\\n| Art-Art | 1.0 |\\n| \u00cencast-Liber | 2.0 |\\n| \u00cencast-Art | 0.7 |\\n| \u00cencast-\u00cencast | 0.5 |")
        c1,c2=st.columns(2)
        with c1:
            Lfl=st.number_input("L(m)",min_value=0.01,value=4.0,key="rm_Lfl"); bfl=st.number_input("b(cm)",min_value=0.1,value=15.0,key="rm_bfl"); hfl=st.number_input("h(cm)",min_value=0.1,value=20.0,key="rm_hfl")
            cfl=st.selectbox("Rezemare",["Art-Art (\u03bc=1.0)","\u00cencast-Liber (\u03bc=2.0)","\u00cencast-Art (\u03bc=0.7)","\u00cencast-\u00cencast (\u03bc=0.5)"],key="rm_cfl")
            mfl=st.selectbox("Material",["O\u021bel S235","O\u021bel S275","O\u021bel S355","Beton C25/30","Beton C30/37"],key="rm_mfl")
        mud={"Art-Art (\u03bc=1.0)":1.0,"\u00cencast-Liber (\u03bc=2.0)":2.0,"\u00cencast-Art (\u03bc=0.7)":0.7,"\u00cencast-\u00cencast (\u03bc=0.5)":0.5}
        mu=mud[cfl]; Efd={"O\u021bel S235":21000,"O\u021bel S275":21000,"O\u021bel S355":21000,"Beton C25/30":3100,"Beton C30/37":3300}; Efl=Efd[mfl]
        Afl=bfl*hfl; Imin=min(bfl*hfl**3,hfl*bfl**3)/12; imin=np.sqrt(Imin/Afl); Lcm=Lfl*100
        Ncr=np.pi**2*Efl*Imin/(mu*Lcm)**2; lam=mu*Lcm/imin; scr=np.pi**2*Efl/lam**2
        with c2:
            st.latex(rf"I_{{min}}={Imin:.3f}\\text{{ cm}}^4,\\; i_{{min}}={imin:.4f}\\text{{ cm}}")
            st.latex(rf"\\lambda={lam:.2f},\\; N_{{cr}}={Ncr:.2f}\\text{{ kN}}")
            st.latex(rf"\\sigma_{{cr}}={scr:.4f}\\text{{ kN/cm}}^2={scr*10:.3f}\\text{{ MPa}}")
        if lam>100: st.info(f"\u03bb={lam:.1f}>100 Euler valabil")
        elif lam>60: st.warning(f"\u03bb={lam:.1f} intermediar")
        else: st.success(f"\u03bb={lam:.1f}\u226460 bar\u0103 scurt\u0103")
        fig_fl,ax_fl=plt.subplots(figsize=(9,4),dpi=120)
        Lr=np.linspace(0.5,max(Lfl*2,10),200); Ncr_r=np.pi**2*Efl*Imin/(mu*Lr*100)**2
        ax_fl.plot(Lr,Ncr_r,"#d62728",lw=2.5); ax_fl.axvline(Lfl,color="gray",ls="--",lw=1.5,label=f"L={Lfl}m")
        ax_fl.axhline(Ncr,color="orange",ls="--",lw=1.5,label=f"Ncr={Ncr:.2f}kN"); ax_fl.scatter([Lfl],[Ncr],color="red",s=80,zorder=5)
        ax_fl.set_xlabel("L(m)"); ax_fl.set_ylabel("Ncr(kN)"); ax_fl.set_title("Curba Euler",fontweight="bold")
        ax_fl.legend(fontsize=9); ax_fl.grid(True,alpha=0.25); plt.tight_layout(); st.pyplot(fig_fl); plt.close(fig_fl)
'''

S1 = '''\

# ============================================================
# MODUL 3: STATICA 1
# ============================================================
elif modul == "\U0001f4cf Statica 1 \u2014 Static Determinate":
    st.title("Statica 1 \u2014 Structuri Static Determinate")
    st.markdown("Calcul conform *Statica \u2014 Structuri Static Determinate* (975-4.pdf)")
    st.markdown("---")
    tip_struct=st.sidebar.selectbox("Tip Structur\u0103",["Grind\u0103 Simpl\u0103","Grind\u0103 Gerber","Cadru Portal","Arc cu 3 Articula\u021bii","Z\u0103brele"],key="s1_tip")

    # ---- GRINDA SIMPLA ----
    if tip_struct=="Grind\u0103 Simpl\u0103":
        st.header("Grind\u0103 Dreapt\u0103 Static Determinat\u0103")
        with st.expander("Teorie (975-4.pdf, Cap.1)"):
            st.markdown("**3 ecua\u021bii de echilibru:** \u03a3Fx=0, \u03a3Fy=0, \u03a3MA=0")
            st.latex(r"V_B=\\frac{Q x_Q+P a+M_0}{L},\\; V_A=Q+P-V_B")
            st.latex(r"T(x)=V_A-q(x-x_1)H(x-x_1)-PH(x-a),\\; M(x)=V_Ax-\\ldots")
        c1,c2=st.columns(2)
        with c1:
            Ls=st.number_input("Lungime L(m)",min_value=0.1,value=6.0,step=0.5,key="s1_L")
            qs=st.number_input("q distribuit (kN/m)",value=10.0,step=1.0,key="s1_q")
            qx1=st.number_input("q de la x1(m)",min_value=0.0,value=0.0,key="s1_qx1")
            qx2=st.number_input("q pana la x2(m)",min_value=0.0,value=float(Ls),key="s1_qx2")
        with c2:
            Ps=st.number_input("For\u021b\u0103 P(kN)",value=0.0,step=5.0,key="s1_P")
            as_=st.number_input("Poz P fa\u021b\u0103 de A(m)",min_value=0.0,value=float(Ls)/2,key="s1_a")
            M0s=st.number_input("Moment M0(kNm)",value=0.0,step=5.0,key="s1_M0")
            m0p=st.number_input("Poz M0 fa\u021b\u0103 de A(m)",min_value=0.0,value=float(Ls)/2,key="s1_m0p")
            tipg=st.selectbox("Rezemare",["Articula\u021bie A + Reazem simplu B","Consol\u0103 (\u00cencastrare A)"],key="s1_tipg")

        # Desen structura
        st.markdown("### Pasul 1 \u2014 Structura cu \u00cenc\u0103rc\u0103ri")
        fig_s1,ax_s1=plt.subplots(figsize=(12,4.5),dpi=150)
        ax_s1.plot([0,Ls],[0,0],"k-",lw=5.5,zorder=3)
        ss=max(0.22,Ls*0.032)
        if "Articula\u021bie" in tipg:
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
        ax_s1.set_aspect("equal"); ax_s1.axis("off"); ax_s1.set_title("Structura cu \u00cenc\u0103rc\u0103ri",fontsize=13,fontweight="bold")
        st.pyplot(fig_s1); plt.close(fig_s1)

        # Calcul reactiuni
        Qs=qs*max(0.0,qx2-qx1); xQs=(qx1+qx2)/2 if Qs>0 else 0.0
        if "Articula\u021bie" in tipg:
            VBs=(Qs*xQs+Ps*as_+M0s)/Ls; VAs=Qs+Ps-VBs; HAs=0.0; MAs=0.0
        else:
            VAs=Qs+Ps; HAs=0.0; MAs=Qs*xQs+Ps*as_+M0s; VBs=0.0

        st.markdown("### Pasul 2 \u2014 Ecua\u021bii de Echilibru")
        ce1,ce2=st.columns(2)
        with ce1:
            st.latex(r"\\sum F_x=0:\\; H_A=0")
            if "Articula\u021bie" in tipg:
                st.latex(r"\\sum M_A=0:\\; V_B\\cdot L=Q x_Q+P a+M_0")
                st.latex(r"\\sum F_y=0:\\; V_A+V_B=Q+P")
            else:
                st.latex(r"\\sum F_y=0:\\; V_A=Q+P")
                st.latex(r"\\sum M_A=0:\\; M_A=Q x_Q+P a+M_0")
        with ce2:
            st.latex(rf"Q=q(x_2-x_1)={qs:.2f}\\times{max(0,qx2-qx1):.2f}={Qs:.3f}\\text{{ kN}}")
            if "Articula\u021bie" in tipg:
                st.latex(rf"V_B=\\frac{{{Qs:.2f}\\times{xQs:.2f}+{Ps:.2f}\\times{as_:.2f}+{M0s:.2f}}}{{{Ls:.2f}}}={VBs:.4f}\\text{{ kN}}")
                st.latex(rf"V_A={VAs:.4f}\\text{{ kN}}")
            else:
                st.latex(rf"V_A={VAs:.4f}\\text{{ kN}},\\; M_A={MAs:.4f}\\text{{ kNm}}")

        # FBD cu reactiuni
        st.markdown("### Pasul 3 \u2014 Diagram\u0103 Corp Liber")
        fig_fbd,ax_fbd=plt.subplots(figsize=(12,4.5),dpi=150)
        ax_fbd.plot([0,Ls],[0,0],"k-",lw=5.5,zorder=3)
        sf=max(0.22,Ls*0.032)
        if "Articula\u021bie" in tipg: draw_pin(ax_fbd,0,0,sf); draw_roller(ax_fbd,Ls,0,sf)
        else: draw_fixed_left(ax_fbd,0,-sf*2,sf*4,sf)
        scr=max(sf*4.5,0.9)
        if abs(VAs)>0.001:
            ax_fbd.annotate("",xy=(0,0),xytext=(0,-scr if VAs>0 else scr),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=16))
            ax_fbd.text(-sf*3.5,-scr*0.55 if VAs>0 else scr*0.55,f"VA={VAs:.3f}kN",color="red",fontsize=9,fontweight="bold")
        if abs(VBs)>0.001 and "Articula\u021bie" in tipg:
            ax_fbd.annotate("",xy=(Ls,0),xytext=(Ls,-scr if VBs>0 else scr),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=16))
            ax_fbd.text(Ls+sf*0.5,-scr*0.55 if VBs>0 else scr*0.55,f"VB={VBs:.3f}kN",color="red",fontsize=9,fontweight="bold")
        if abs(MAs)>0.001: draw_moment_arc(ax_fbd,0,0,-MAs,r=sf*2.2,color="purple"); ax_fbd.text(-sf*5.5,sf*3,f"MA={MAs:.3f}kNm",color="purple",fontsize=9)
        if qs>0 and qx2>qx1: draw_distributed_load(ax_fbd,qx1,qx2,0.0,qs,f"q={qs}")
        if abs(Ps)>0: draw_force_arrow(ax_fbd,as_,0,0,1 if Ps>0 else -1,f"P={abs(Ps)}kN","darkred",scale=scr)
        ax_fbd.set_xlim(-sf*9,Ls+sf*9); ax_fbd.set_ylim(-sf*12,sf*16)
        ax_fbd.set_aspect("equal"); ax_fbd.axis("off"); ax_fbd.set_title("Diagram\u0103 Corp Liber cu Reac\u021biuni",fontsize=12,fontweight="bold")
        st.pyplot(fig_fbd); plt.close(fig_fbd)

        # Diagrame NTM
        x_arr=np.linspace(0,Ls,800); T_arr=np.zeros_like(x_arr); M_arr=np.zeros_like(x_arr); N_arr=np.zeros_like(x_arr)
        if "Articula\u021bie" in tipg:
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

        st.markdown("### Pasul 4 \u2014 Diagrame N, T, M")
        fig_ntm,(axN,axT,axM)=plt.subplots(3,1,figsize=(12,11),dpi=150,sharex=True)
        fill_diagram(axN,x_arr,N_arr,"#1a6faf","N(kN)"); axN.set_title("N(x)",fontweight="bold",color="#1a6faf"); label_extremes(axN,x_arr,N_arr,"#1a6faf")
        fill_diagram(axT,x_arr,T_arr,"#2ca02c","T(kN)"); axT.set_title("T(x)",fontweight="bold",color="#2ca02c"); label_extremes(axT,x_arr,T_arr,"#2ca02c")
        fill_diagram(axM,x_arr,M_arr,"#d62728","M(kNm)"); axM.set_title("M(x) [fibra \u00efntins\u0103]",fontweight="bold",color="#d62728"); axM.invert_yaxis(); label_extremes(axM,x_arr,M_arr,"#d62728")
        axM.set_xlabel("x(m)",fontsize=11); plt.tight_layout(); fig_ntm.suptitle("Diagrame N,T,M \u2014 Grind\u0103 Simpl\u0103",fontsize=14,fontweight="bold",y=1.01)
        st.pyplot(fig_ntm); plt.close(fig_ntm)

        # Verificare
        st.markdown("### Pasul 5 \u2014 Verificare Echilibru")
        sFy=VAs+VBs-Qs-Ps
        sMA=VBs*Ls-Qs*xQs-Ps*as_-M0s if "Articula\u021bie" in tipg else MAs-Qs*xQs-Ps*as_-M0s
        cv1,cv2,cv3=st.columns(3)
        _ = cv1.success(f"\u03a3Fy={sFy:.6f}\u22480") if abs(sFy)<0.01 else cv1.error(f"\u03a3Fy={sFy:.6f}\u22600")
        _ = cv2.success(f"\u03a3MA={sMA:.6f}\u22480") if abs(sMA)<0.01 else cv2.error(f"\u03a3MA={sMA:.6f}\u22600")
        cv3.metric("M max",f"{np.max(np.abs(M_arr)):.4f} kNm")
        with st.expander("Valori Caracteristice"):
            idx_T0=np.where(np.diff(np.sign(T_arr)))[0]
            st.metric("T max",f"{np.max(np.abs(T_arr)):.4f} kN")
            for sc in idx_T0: st.info(f"T=0 la x\u2248{x_arr[sc]:.3f}m \u2192 M={M_arr[sc]:.4f}kNm")

    # ---- GRINDA GERBER ----
    elif tip_struct=="Grind\u0103 Gerber":
        st.header("Grind\u0103 Gerber (cu Articula\u021bii Intermediare)")
        with st.expander("Teorie (975-4.pdf, Cap.2)"):
            st.markdown("**M=0 \u00een articula\u021bia intermediar\u0103.** Calcul GS \u2192 GP.")
            st.latex(r"\\text{Verificare: }M_B=0")
        c1,c2,c3=st.columns(3)
        with c1: LGP=st.number_input("L GP(m)",min_value=1.0,value=8.0,step=0.5,key="gerb_LGP"); qGP=st.number_input("q GP(kN/m)",min_value=0.0,value=15.0,step=1.0,key="gerb_qGP")
        with c2: LGS=st.number_input("L GS(m)",min_value=0.5,value=4.0,step=0.5,key="gerb_LGS"); qGS=st.number_input("q GS(kN/m)",min_value=0.0,value=10.0,step=1.0,key="gerb_qGS")
        with c3: PGS=st.number_input("P pe GS(kN)",min_value=0.0,value=0.0,step=5.0,key="gerb_PGS"); aPS=st.number_input("Poz P(m)",min_value=0.0,value=float(LGS)/2,key="gerb_aPS")
        QGS=qGS*LGS; VD=(QGS*LGS/2+PGS*aPS)/LGS; VB_art=QGS+PGS-VD
        xBGP=LGP-LGS; QGP=qGP*LGP; VC=(QGP*LGP/2+VB_art*xBGP)/LGP; VA_GP=QGP+VB_art-VC

        st.markdown("### Pasul 1 \u2014 Schema Gerber")
        fig_g,ax_g=plt.subplots(figsize=(14,5.5),dpi=150)
        ax_g.plot([0,xBGP],[0,0],"k-",lw=6,zorder=3); ax_g.plot([xBGP,LGP],[0,0],"navy",lw=6,zorder=3)
        sg=max(0.22,LGP*0.027)
        draw_pin(ax_g,0,0,sg); draw_roller(ax_g,LGP*0.45,0,sg); draw_roller(ax_g,LGP,0,sg)
        ax_g.plot(xBGP,0,"ko",ms=12,zorder=7); ax_g.plot(xBGP,0,"wo",ms=6,zorder=8)
        ax_g.text(xBGP,sg*3.5,"B\\n(M=0)",ha="center",fontsize=9,color="navy",fontweight="bold")
        ax_g.text(0,-sg*3.5,"A",fontsize=12,fontweight="bold",ha="center"); ax_g.text(LGP,-sg*3.5,"D",fontsize=12,fontweight="bold",ha="center")
        if qGP>0: draw_distributed_load(ax_g,0,xBGP,0.0,qGP,f"q_GP={qGP}")
        if qGS>0: draw_distributed_load(ax_g,xBGP,LGP,0.0,qGS,f"q_GS={qGS}")
        if PGS>0: draw_force_arrow(ax_g,xBGP+aPS,0,0,1,f"P={PGS}kN","darkred",scale=sg*4)
        ax_g.set_xlim(-sg*6,LGP+sg*6); ax_g.set_ylim(-sg*9,sg*18); ax_g.set_aspect("equal"); ax_g.axis("off")
        ax_g.set_title("Grind\u0103 Gerber \u2014 Schema de Calcul",fontsize=13,fontweight="bold"); st.pyplot(fig_g); plt.close(fig_g)

        st.markdown("### Pasul 2 \u2014 Ecua\u021bii Echilibru")
        cg1,cg2=st.columns(2)
        with cg1:
            st.markdown("**GS:**"); st.latex(rf"V_D=\\frac{{Q_{{GS}}L/2+Pa}}{{{LGS:.2f}}}={VD:.4f}\\text{{ kN}}")
            st.latex(rf"V_B=Q_{{GS}}+P-V_D={VB_art:.4f}\\text{{ kN}}")
        with cg2:
            st.markdown("**GP:**"); st.latex(rf"V_C=\\frac{{Q_{{GP}}L/2+V_B x_B}}{{{LGP:.2f}}}={VC:.4f}\\text{{ kN}}")
            st.latex(rf"V_A={VA_GP:.4f}\\text{{ kN}}")

        xGP=np.linspace(0,xBGP,400); xGS=np.linspace(xBGP,LGP,400)
        TGP=VA_GP-qGP*xGP; MGP=VA_GP*xGP-qGP*xGP**2/2
        TGS=np.zeros_like(xGS); MGS=np.zeros_like(xGS)
        for i,x in enumerate(xGS):
            xi=x-xBGP; TGS[i]=VB_art-qGS*xi-(PGS if xi>aPS else 0); MGS[i]=VB_art*xi-qGS*xi**2/2-(PGS*(xi-aPS) if xi>aPS else 0)
        xt=np.concatenate([xGP,xGS]); Tt=np.concatenate([TGP,TGS]); Mt=np.concatenate([MGP,MGS]); Nt=np.zeros_like(xt)
        st.markdown("### Pasul 3 \u2014 Diagrame N,T,M")
        fig_gntm,(aNg,aTg,aMg)=plt.subplots(3,1,figsize=(12,10),dpi=150,sharex=True)
        fill_diagram(aNg,xt,Nt,"#1a6faf","N(kN)"); aNg.set_title("N(x)",fontweight="bold",color="#1a6faf")
        fill_diagram(aTg,xt,Tt,"#2ca02c","T(kN)"); aTg.axvline(xBGP,color="navy",ls="--",lw=1.5); aTg.set_title("T(x)",fontweight="bold",color="#2ca02c"); label_extremes(aTg,xt,Tt)
        fill_diagram(aMg,xt,Mt,"#d62728","M(kNm)"); aMg.axvline(xBGP,color="navy",ls="--",lw=1.5); aMg.invert_yaxis(); aMg.set_title("M(x)",fontweight="bold",color="#d62728"); label_extremes(aMg,xt,Mt); aMg.set_xlabel("x(m)")
        plt.tight_layout(); st.pyplot(fig_gntm); plt.close(fig_gntm)
        Mart=MGP[-1]
        cv1,cv2,cv3=st.columns(3); cv1.metric("T max",f"{np.max(np.abs(Tt)):.3f} kN"); cv2.metric("M max",f"{np.max(np.abs(Mt)):.3f} kNm")
        _ = cv3.success(f"M_art\u2248{Mart:.5f}\u22480") if abs(Mart)<0.05 else cv3.error(f"M_art={Mart:.5f}\u22600")

    # ---- CADRU PORTAL ----
    elif tip_struct=="Cadru Portal":
        st.header("Cadru Portal Static Determinat")
        with st.expander("Teorie (975-4.pdf, Cap.3)"):
            st.latex(r"\\text{St\u00e2lp st\u00e2ng: }M(y)=H_A y,\\; \\text{Grind\u0103: }M(x)=V_Ax-\\frac{qx^2}{2}")
        c1,c2=st.columns(2)
        with c1:
            Hc=st.number_input("\u00cen\u0103l\u021bime st\u00e2lpi h(m)",min_value=0.5,value=4.0,step=0.5,key="cad_H")
            Lc=st.number_input("Deschidere L(m)",min_value=0.5,value=6.0,step=0.5,key="cad_L")
            qgc=st.number_input("q grind\u0103(kN/m)",min_value=0.0,value=20.0,step=1.0,key="cad_q")
        with c2:
            Hvant=st.number_input("For\u021b\u0103 orizontal\u0103 H(kN)",value=10.0,step=1.0,key="cad_H2")
            Pc=st.number_input("P grind\u0103(kN)",min_value=0.0,value=0.0,step=5.0,key="cad_P")
            aPc=st.number_input("Poz P de la st\u00e2ng(m)",min_value=0.0,value=float(Lc)/2,key="cad_aP")
            tipc=st.selectbox("Rezemare",["Articula\u021bie A + Articula\u021bie B","\u00cencastrare A + Articula\u021bie B"],key="cad_tip")
        Qgc=qgc*Lc
        if "Articula\u021bie A" in tipc: VBc=(Qgc*Lc/2+Pc*aPc-Hvant*Hc)/Lc; HAc=Hvant; HBc=0.0; MAc=0.0
        else: VBc=(Qgc*Lc/2+Pc*aPc-Hvant*Hc/2)/Lc; HAc=Hvant; HBc=0.0; MAc=Hvant*Hc/2
        VAc=Qgc+Pc-VBc

        st.markdown("### Pasul 1 \u2014 Schema Cadrului cu Reac\u021biuni")
        fig_cad,ax_cad=plt.subplots(figsize=(10,9),dpi=150)
        ax_cad.plot([0,0],[0,Hc],"k-",lw=5.5,zorder=3); ax_cad.plot([Lc,Lc],[0,Hc],"k-",lw=5.5,zorder=3); ax_cad.plot([0,Lc],[Hc,Hc],"k-",lw=5.5,zorder=3)
        sc=max(0.15,Lc*0.028)
        if "Articula\u021bie A" in tipc: draw_pin(ax_cad,0,0,sc)
        else: draw_fixed_bottom(ax_cad,0,0,sc)
        draw_pin(ax_cad,Lc,0,sc)
        ax_cad.text(-sc*3,-sc*3,"A",fontsize=13,fontweight="bold",ha="center"); ax_cad.text(Lc+sc,-sc*3,"B",fontsize=13,fontweight="bold",ha="center")
        if qgc>0: draw_distributed_load(ax_cad,0,Lc,Hc,qgc,f"q={qgc}",n_arrows=8)
        if Pc>0: draw_force_arrow(ax_cad,aPc,Hc,0,1,f"P={Pc}kN","darkred",scale=sc*5)
        if Hvant>0: draw_force_arrow(ax_cad,0,Hc*0.6,1,0,f"H={Hvant}kN","#8B4513",scale=sc*5)
        src=max(0.55,Hc*0.16)
        if abs(VAc)>0.01: ax_cad.annotate("",xy=(0,0),xytext=(0,-src),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=14)); ax_cad.text(-sc*6,-src*0.6,f"VA={VAc:.3f}kN",color="red",fontsize=9)
        if abs(VBc)>0.01: ax_cad.annotate("",xy=(Lc,0),xytext=(Lc,-src),arrowprops=dict(arrowstyle="->",color="red",lw=2.5,mutation_scale=14)); ax_cad.text(Lc+sc*0.8,-src*0.6,f"VB={VBc:.3f}kN",color="red",fontsize=9)
        if abs(HAc)>0.01: ax_cad.annotate("",xy=(0,0),xytext=(-src,0),arrowprops=dict(arrowstyle="->",color="#1a6faf",lw=2.5,mutation_scale=14)); ax_cad.text(-src*1.7,sc*1.5,f"HA={HAc:.3f}kN",color="#1a6faf",fontsize=9)
        ax_cad.set_aspect("equal"); ax_cad.set_xlim(-sc*14,Lc+sc*14); ax_cad.set_ylim(-sc*10,Hc+sc*16); ax_cad.axis("off")
        ax_cad.set_title("Cadru Portal \u2014 Schema cu Reac\u021biuni",fontsize=13,fontweight="bold"); st.pyplot(fig_cad); plt.close(fig_cad)

        st.markdown("### Pasul 2 \u2014 Ecua\u021bii Echilibru")
        cc1,cc2=st.columns(2)
        with cc1: st.latex(r"\\sum M_A=0:\\; V_B L=Q L/2+P a-H h"); st.latex(r"\\sum F_x=0:\\; H_A+H_B=H_{ext}")
        with cc2: st.latex(rf"V_B={VBc:.4f}\\text{{ kN}},\\; V_A={VAc:.4f}\\text{{ kN}},\\; H_A={HAc:.4f}\\text{{ kN}}")

        yst=np.linspace(0,Hc,200); Mstg=HAc*yst; Mstd=HBc*yst; xgr=np.linspace(0,Lc,400)
        Mgr=np.zeros_like(xgr); Ngr=-HAc*np.ones_like(xgr)
        for i,x in enumerate(xgr): Mgr[i]=VAc*x-qgc*x**2/2-(Pc*(x-aPc) if x>aPc else 0)
        scM=0.15/max(0.01,max(np.max(np.abs(Mstg)),np.max(np.abs(Mgr)),0.1))
        fig_cd,axes_cd=plt.subplots(1,3,figsize=(15,8),dpi=150)
        tl=["N(kN)","T(kN)","M(kNm)"]; cls=["#1a6faf","#2ca02c","#d62728"]
        Nstg=-VAc*np.ones_like(yst); Nstd=-VBc*np.ones_like(yst)
        Tstg=HAc*np.ones_like(yst); Tstd=HBc*np.ones_like(yst); Tgr=VAc-qgc*xgr-(Pc*np.heaviside(xgr-aPc,0.5) if Pc>0 else 0.0)
        scN=0.08/max(0.01,max(abs(Nstg[0]),abs(Nstd[0]),0.1)); scT=0.12/max(0.01,max(abs(Tstg[0]),0.1))
        for axf in axes_cd:
            axf.plot([0,0],[0,Hc],"k-",lw=3); axf.plot([Lc,Lc],[0,Hc],"k-",lw=3); axf.plot([0,Lc],[Hc,Hc],"k-",lw=3)
            draw_pin(axf,0,0,sc*0.6); draw_pin(axf,Lc,0,sc*0.6); axf.set_aspect("equal"); axf.axis("off")
        axes_cd[0].set_title("N(kN)",fontweight="bold",color=cls[0]); axes_cd[0].fill_betweenx(yst,Nstg*scN,0,color=cls[0],alpha=0.35); axes_cd[0].fill_betweenx(yst,Lc+Nstd*scN,Lc,color=cls[0],alpha=0.35); axes_cd[0].fill_between(xgr,Hc+Ngr*scN,Hc,color=cls[0],alpha=0.35)
        axes_cd[1].set_title("T(kN)",fontweight="bold",color=cls[1]); axes_cd[1].fill_betweenx(yst,Tstg*scT,0,color=cls[1],alpha=0.35); axes_cd[1].fill_between(xgr,Hc+Tgr*scT,Hc,color=cls[1],alpha=0.35)
        axes_cd[2].set_title("M(kNm)",fontweight="bold",color=cls[2]); axes_cd[2].fill_betweenx(yst,Mstg*scM,0,color=cls[2],alpha=0.35); axes_cd[2].plot(Mstg*scM,yst,color=cls[2],lw=2); axes_cd[2].fill_between(xgr,Hc+Mgr*scM,Hc,color=cls[2],alpha=0.35); axes_cd[2].plot(xgr,Hc+Mgr*scM,color=cls[2],lw=2)
        axes_cd[2].text(0,Hc/2,f"{Mstg[-1]:.2f}kNm",fontsize=8,color=cls[2],ha="center")
        plt.tight_layout(); fig_cd.suptitle("Diagrame N,T,M \u2014 Cadru Portal",fontsize=14,fontweight="bold"); st.pyplot(fig_cd); plt.close(fig_cd)
        sFyc=VAc+VBc-Qgc-Pc; sFxc=HAc+HBc-Hvant
        ccv1,ccv2=st.columns(2)
        _ = ccv1.success(f"\u03a3Fy={sFyc:.6f}\u22480") if abs(sFyc)<0.01 else ccv1.error(f"\u03a3Fy={sFyc:.6f}")
        _ = ccv2.success(f"\u03a3Fx={sFxc:.6f}\u22480") if abs(sFxc)<0.01 else ccv2.error(f"\u03a3Fx={sFxc:.6f}")

    # ---- ARC ----
    elif tip_struct=="Arc cu 3 Articula\u021bii":
        st.header("Arc cu 3 Articula\u021bii")
        with st.expander("Teorie (975-4.pdf, Cap.4)"):
            st.latex(r"H=\\frac{\\sum M_C^{stg}}{f},\\; M(x)=M_0(x)-H y(x)")
            st.latex(r"y(x)=\\frac{4f}{L^2}x(L-x)\\quad(\\text{parabol\u0103})")
        c1,c2=st.columns(2)
        with c1:
            Larc=st.number_input("Deschidere L(m)",min_value=0.5,value=12.0,step=1.0,key="arc_L")
            farc=st.number_input("S\u0103geat\u0103 f(m)",min_value=0.1,value=3.0,step=0.5,key="arc_f")
            qarc=st.number_input("q(kN/m)",min_value=0.0,value=15.0,step=1.0,key="arc_q")
        with c2:
            Parc=st.number_input("P(kN)",min_value=0.0,value=0.0,step=5.0,key="arc_P")
            aarc=st.number_input("Poz P(m)",min_value=0.0,value=float(Larc)/4,key="arc_a")
        Qarc=qarc*Larc; VBarc=(Qarc*Larc/2+Parc*aarc)/Larc; VAarc=Qarc+Parc-VBarc
        smc=VAarc*Larc/2-qarc*(Larc/2)**2/2-(Parc*(Larc/2-aarc) if aarc<Larc/2 else 0)
        Harc=smc/farc
        xarc=np.linspace(0,Larc,400); yarc=4*farc/Larc**2*xarc*(Larc-xarc)
        dydx=4*farc/Larc**2*(Larc-2*xarc); phi=np.arctan(dydx)

        st.markdown("### Pasul 1 \u2014 Schema Arcului")
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
        ax_arc.set_title("Arc cu 3 Articula\u021bii \u2014 Schema cu Reac\u021biuni",fontsize=13,fontweight="bold"); st.pyplot(fig_arc); plt.close(fig_arc)

        st.markdown("### Pasul 2 \u2014 Ecua\u021bii de Calcul")
        ca1,ca2=st.columns(2)
        with ca1:
            st.latex(rf"V_B={VBarc:.4f}\\text{{ kN}},\\; V_A={VAarc:.4f}\\text{{ kN}}")
            st.latex(r"\\sum M_C^{{stg}}=0:\\; V_A\\frac{{L}}{{2}}-q\\frac{{(L/2)^2}}{{2}}-P(L/2-a)=H\\cdot f")
        with ca2:
            st.latex(rf"H=\\frac{{{smc:.4f}}}{{{farc:.2f}}}={Harc:.4f}\\text{{ kN}}")
            st.info(f"VA={VAarc:.4f} VB={VBarc:.4f} H={Harc:.4f} kN")

        M0arc=np.zeros_like(xarc)
        for i,x in enumerate(xarc): M0arc[i]=VAarc*x-qarc*x**2/2-(Parc*(x-aarc) if x>aarc else 0)
        Marc=M0arc-Harc*yarc
        Vsect=np.zeros_like(xarc)
        for i,x in enumerate(xarc): Vsect[i]=VAarc-qarc*x-(Parc if x>aarc else 0)
        Narc=-(Harc*np.cos(phi)+Vsect*np.sin(phi)); Tarc=-Harc*np.sin(phi)+Vsect*np.cos(phi)

        st.markdown("### Pasul 3 \u2014 Diagrame M, N, T")
        fig_an,axes_an=plt.subplots(1,3,figsize=(15,5.5),dpi=150)
        scMs=0.25/max(0.01,np.max(np.abs(Marc))); scNs=0.2/max(0.01,np.max(np.abs(Narc))); scTs=0.2/max(0.01,np.max(np.abs(Tarc))+0.01)
        axes_an[0].plot(xarc,yarc,"k-",lw=3); axes_an[0].fill_between(xarc,yarc,yarc+Marc*scMs,color="#d62728",alpha=0.38); axes_an[0].plot(xarc,yarc+Marc*scMs,"r-",lw=2); axes_an[0].set_title("M(x)=M0-Hy",fontweight="bold",color="#d62728"); axes_an[0].axis("off")
        axes_an[1].plot(xarc,yarc,"k-",lw=3); axes_an[1].fill_between(xarc,yarc,yarc+Narc*scNs,color="#1a6faf",alpha=0.38); axes_an[1].set_title("N(x)",fontweight="bold",color="#1a6faf"); axes_an[1].axis("off")
        axes_an[2].plot(xarc,yarc,"k-",lw=3); axes_an[2].fill_between(xarc,yarc,yarc+Tarc*scTs,color="#2ca02c",alpha=0.38); axes_an[2].set_title("T(x)",fontweight="bold",color="#2ca02c"); axes_an[2].axis("off")
        plt.tight_layout(); st.pyplot(fig_an); plt.close(fig_an)
        Mc=Marc[len(Marc)//2]
        if abs(Mc)<abs(np.max(np.abs(Marc)))*0.02: st.success(f"M la cheie C\u2248{Mc:.5f}\u22480 \u2713")
        else: st.warning(f"M la cheie C={Mc:.5f} (trebuie \u22480)")

    # ---- ZABRELE ----
    elif tip_struct=="Z\u0103brele":
        st.header("Grinzi cu Z\u0103brele \u2014 Metoda Nodurilor \u0219i Sec\u021biunilor")
        with st.expander("Teorie (975-4.pdf, Cap.5)"):
            st.markdown("N>0 = \u00eentindere, N<0 = compresiune. **Condi\u021bie SSD:** b+r=2j")
            st.latex(r"N_{t.inf}=+\\frac{M_1}{h},\\; N_{t.sup}=-\\frac{M_1}{h},\\; N_{diag}=\\frac{T_1}{\\sin\\varphi}")
        c1,c2=st.columns(2)
        with c1:
            ncamp=st.number_input("Nr c\u00e2mpuri",min_value=2,max_value=12,value=4,step=1,key="zab_n")
            dcamp=st.number_input("Lungime panou d(m)",min_value=0.5,value=2.0,step=0.5,key="zab_d")
            hzab=st.number_input("\u00cen\u0103l\u021bime h(m)",min_value=0.5,value=2.0,step=0.5,key="zab_h")
        with c2:
            Pzab=st.number_input("P pe nod inferior(kN)",min_value=0.0,value=20.0,step=5.0,key="zab_P")
            tipz=st.selectbox("Tip z\u0103brea",["Pratt","Warren"],key="zab_tip")
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
        ax_z.set_title(f"Z\u0103brea {tipz} \u2014 {ncamp} c\u00e2mpuri\u00d7{dcamp}m h={hzab}m",fontsize=12,fontweight="bold"); st.pyplot(fig_z); plt.close(fig_z)

        st.latex(rf"V_A=V_B=\\frac{{\\sum P}}{{2}}=\\frac{{{(ninf-2)*Pzab:.1f}}}{{2}}={VAz:.3f}\\text{{ kN}}")
        M1=VAz*dcamp; Ntinf=M1/hzab; Ntsup=-M1/hzab; Ldiag=np.sqrt(dcamp**2+hzab**2); Nd=VAz/(hzab/Ldiag)
        st.markdown("#### Metoda Sec\u021biunilor \u2014 Panoul 1:")
        st.latex(rf"N_{{t.inf}}=+\\frac{{V_A d}}{{h}}={Ntinf:.3f}\\text{{ kN (\\textit\u00eentindere)}}")
        st.latex(rf"N_{{t.sup}}=-{abs(Ntsup):.3f}\\text{{ kN (compresiune)}}")
        st.latex(rf"N_{{diag}}=\\frac{{V_A}}{{\\sin\\varphi}}=\\frac{{{VAz:.2f}}}{{{hzab/Ldiag:.4f}}}={Nd:.3f}\\text{{ kN}}")
'''

S2 = '''\

# ============================================================
# MODUL 4: STATICA 2
# ============================================================
elif modul == "\U0001f501 Statica 2 \u2014 Static Nedeterminate":
    st.title("Statica 2 \u2014 Structuri Static Nedeterminate")
    st.markdown("Calcul conform *Metoda For\u021belor + Metoda Deplas\u0103rilor* (138-3.pdf)")
    st.markdown("---")
    tip_s2=st.sidebar.selectbox("Metod\u0103 / Structur\u0103",["Grind\u0103 Continu\u0103 (Metoda For\u021belor)","Cadru Nedeterminat (Metoda For\u021belor)","Metoda Deplas\u0103rilor"],key="s2_tip")

    # ---- GRINDA CONTINUA ----
    if tip_s2=="Grind\u0103 Continu\u0103 (Metoda For\u021belor)":
        st.header("Grind\u0103 Continu\u0103 pe 2 Deschideri \u2014 Metoda For\u021belor")
        with st.expander("Teorie (138-3.pdf, Cap.1-2)"):
            st.markdown("**Pa\u0219i Metoda For\u021belor:**\\n1. Grad nedeterminare ns\\n2. Sistem de Baz\u0103 (SB)\\n3. Diagrame Mf, m1,...\\n4. Coeficien\u021bi Vere\u0219ciagin \u03b4ij\\n5. Ecua\u021bii canonice\\n6. Diagram\u0103 M final\u0103")
            st.latex(r"\\delta_{11}X_1+\\Delta_{1P}=0,\\; M_{fin}=M_f+X_1 m_1")
            st.latex(r"\\delta_{ij}=\\int_0^L\\frac{m_i m_j}{EI}dx\\quad(\\text{Vere\u015fciagin})")
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
        st.markdown("### Pasul 1 \u2014 Gradul de Nedeterminare")
        st.latex(r"n_s=r-3=4-3=1\\quad(\\text{r=4: VA,HA,VB,VC})")
        st.success("ns=1 \u2192 1 necunoscut\u0103 redundant\u0103 X1=VB")
        st.markdown("### Pasul 2 \u2014 Sistem de Baz\u0103")
        st.markdown("**SB** = grinda A\u2013C simpl\u0103 (f\u0103r\u0103 reazem \u00een B). **X1=VB** redundant.")
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

        st.markdown("### Pasul 3 \u2014 Schema Structurii")
        fig_s2s,ax_s2=plt.subplots(figsize=(12,4.5),dpi=150)
        ax_s2.plot([0,Ltot],[0,0],"k-",lw=5.5,zorder=3)
        ss2=max(0.22,Ltot*0.022)
        draw_pin(ax_s2,0,0,ss2); draw_roller(ax_s2,L1,0,ss2); draw_roller(ax_s2,Ltot,0,ss2)
        ax_s2.text(0,-ss2*3.5,"A",fontsize=12,fontweight="bold",ha="center"); ax_s2.text(L1,-ss2*3.5,"B\\n(X1=VB)",fontsize=10,ha="center",color="navy",fontweight="bold"); ax_s2.text(Ltot,-ss2*3.5,"C",fontsize=12,fontweight="bold",ha="center")
        if q1>0: draw_distributed_load(ax_s2,0,L1,0.0,q1,f"q1={q1}")
        if q2>0: draw_distributed_load(ax_s2,L1,Ltot,0.0,q2,f"q2={q2}")
        if P1>0: draw_force_arrow(ax_s2,L1/2,0,0,1,f"P1={P1}kN","darkred",scale=ss2*4)
        if P2>0: draw_force_arrow(ax_s2,L1+L2/2,0,0,1,f"P2={P2}kN","darkred",scale=ss2*4)
        ax_s2.set_xlim(-ss2*6,Ltot+ss2*6); ax_s2.set_ylim(-ss2*7,ss2*15); ax_s2.set_aspect("equal"); ax_s2.axis("off")
        ax_s2.set_title("Grind\u0103 Continu\u0103 pe 2 Deschideri",fontsize=13,fontweight="bold"); st.pyplot(fig_s2s); plt.close(fig_s2s)

        st.markdown("### Pasul 4 \u2014 Diagrame pe SB")
        fig_sb2,(axMf,axm1)=plt.subplots(2,1,figsize=(12,9),dpi=150,sharex=True)
        fill_diagram(axMf,xsb,Mf,"#d62728","Mf(kNm)"); axMf.set_title("Mf \u2014 din \u00eenc\u0103rc\u0103ri pe SB",fontweight="bold",color="#d62728"); axMf.invert_yaxis(); axMf.axvline(L1,color="navy",ls="--",lw=1.2); label_extremes(axMf,xsb,Mf)
        fill_diagram(axm1,xsb,m1,"#9467bd","m1(m)"); axm1.set_title("m1 \u2014 din X1=1 pe SB",fontweight="bold",color="#9467bd"); axm1.invert_yaxis(); axm1.axvline(L1,color="navy",ls="--",lw=1.2); axm1.text(L1,m1B*0.65,f"m1(B)={m1B:.4f}m",color="#9467bd",fontsize=9,ha="center",fontweight="bold"); axm1.set_xlabel("x(m)",fontsize=11)
        plt.tight_layout(); st.pyplot(fig_sb2); plt.close(fig_sb2)

        st.markdown("### Pasul 5 \u2014 Coeficien\u021bi Vere\u0219ciagin \u0219i Ecua\u021bie Canonic\u0103")
        cv1,cv2=st.columns(2)
        with cv1:
            st.latex(r"\\delta_{11}=\\frac{1}{EI}\\left(\\frac{L_1 m_{1B}^2}{3}+\\frac{L_2 m_{1B}^2}{3}\\right)")
            st.latex(rf"\\delta_{{11}}={d11:.8f}\\text{{ m/kN}}")
            st.latex(rf"\\Delta_{{1P}}={D1P:.6f}\\text{{ m}}")
        with cv2:
            st.latex(r"\\delta_{11}X_1+\\Delta_{1P}=0")
            st.latex(rf"X_1=V_B=-\\frac{{\\Delta_{{1P}}}}{{\\delta_{{11}}}}={X1s:.4f}\\text{{ kN}}")
            st.success(f"X1=VB={X1s:.4f} kN")

        st.markdown("### Pasul 6 \u2014 Diagram\u0103 M Final\u0103")
        st.latex(r"M_{fin}(x)=M_f(x)+X_1\\cdot m_1(x)")
        fig_fin,ax_fin=plt.subplots(figsize=(12,5.5),dpi=150)
        fill_diagram(ax_fin,xsb,Mfin,"#d62728","M fin(kNm)"); ax_fin.invert_yaxis(); ax_fin.axvline(L1,color="navy",ls="--",lw=1.5,label=f"Reazem B(x={L1}m)"); label_extremes(ax_fin,xsb,Mfin); ax_fin.set_xlabel("x(m)",fontsize=11); ax_fin.set_title(f"Diagram\u0103 M Final\u0103 | X1=VB={X1s:.4f}kN",fontsize=12,fontweight="bold"); ax_fin.legend()
        plt.tight_layout(); st.pyplot(fig_fin); plt.close(fig_fin)

        st.markdown("### Pasul 7 \u2014 Verificare")
        dB=d11*X1s+D1P
        if abs(dB)<1e-4: st.success(f"\u03b411 X1+\u03941P={dB:.2e}\u22480 \u2713")
        else: st.error(f"\u03b411 X1+\u03941P={dB:.2e}\u22600")
        RA_f=RA_Mf+X1s*RA_m1; RC_f=RC_Mf+X1s*RC_m1
        cr1,cr2,cr3=st.columns(3); cr1.metric("VA",f"{RA_f:.4f} kN"); cr2.metric("VB",f"{X1s:.4f} kN"); cr3.metric("VC",f"{RC_f:.4f} kN")
        chk=RA_f+X1s+RC_f-Q1t-Q2t-P1-P2
        if abs(chk)<0.01: st.success(f"\u03a3Fy={chk:.6f}\u22480")
        else: st.warning(f"\u03a3Fy={chk:.6f}")

    # ---- CADRU NEDETERMINAT ----
    elif tip_s2=="Cadru Nedeterminat (Metoda For\u021belor)":
        st.header("Cadru Portal cu 2 \u00cencast\u0103ri \u2014 Metoda For\u021belor")
        with st.expander("Teorie (138-3.pdf, Cap.2)"):
            st.markdown("ns=3 (X1=MA, X2=MB, X3=HB). SB=cadru cu 2 articula\u021bii.")
            st.latex(r"\\delta_{ij}X_j+\\Delta_{iP}=0\\;(i=1,2,3)")
        c1,c2=st.columns(2)
        with c1: Hcf=st.number_input("h st\u00e2lpi(m)",min_value=0.5,value=4.0,step=0.5,key="cf_H"); Lcf=st.number_input("L grind\u0103(m)",min_value=0.5,value=6.0,step=0.5,key="cf_L"); qcf=st.number_input("q(kN/m)",min_value=0.0,value=20.0,step=1.0,key="cf_q")
        with c2: Hvcf=st.number_input("H orizontal(kN)",value=0.0,step=1.0,key="cf_Hv"); EIcf=st.number_input("EI(kNm2)",min_value=1.0,value=20000.0,step=1000.0,key="cf_EI")
        st.markdown("---"); st.markdown("### Pas 1 \u2014 ns=3"); st.latex(r"n_s=r-3=6-3=3"); st.success("ns=3")
        st.markdown("### Pas 2 \u2014 SB (2 articula\u021bii la baze)")
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
        st.markdown("### Pas 3 \u2014 Diagrame pe SB")
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
        st.markdown("### Pas 4 \u2014 Coeficien\u021bi Vere\u0219ciagin")
        cv1,cv2=st.columns(2)
        with cv1: st.latex(rf"\\delta_{{11}}={d11:.6f},\\; \\delta_{{22}}={d22:.6f},\\; \\delta_{{33}}={d33:.6f}"); st.latex(rf"\\delta_{{12}}={d12:.6f},\\; \\delta_{{13}}={d13:.6f},\\; \\delta_{{23}}={d23:.6f}"); st.latex(rf"\\Delta_{{1P}}={D1P:.6f},\\; \\Delta_{{2P}}={D2P:.6f},\\; \\Delta_{{3P}}={D3P:.6f}")
        with cv2: st.latex(r"\\delta_{11}X_1+\\delta_{12}X_2+\\delta_{13}X_3+\\Delta_{1P}=0"); st.latex(r"\\delta_{21}X_1+\\delta_{22}X_2+\\delta_{23}X_3+\\Delta_{2P}=0"); st.latex(r"\\delta_{31}X_1+\\delta_{32}X_2+\\delta_{33}X_3+\\Delta_{3P}=0")
        Dm=np.array([[d11,d12,d13],[d12,d22,d23],[d13,d23,d33]]); DPv=np.array([D1P,D2P,D3P])
        try:
            Xcf=np.linalg.solve(Dm,-DPv); X1cf,X2cf,X3cf=Xcf
            st.markdown("### Pas 5 \u2014 Solu\u021bie")
            st.latex(rf"X_1=M_A={X1cf:.4f}\\text{{ kNm}},\\; X_2=M_B={X2cf:.4f}\\text{{ kNm}},\\; X_3=H_B={X3cf:.4f}\\text{{ kN}}")
            Mssf=Mfss+X1cf*m1ss+X2cf*m2ss+X3cf*m3ss; Msdf=np.zeros_like(yst)+X1cf*m1sd+X2cf*m2sd+X3cf*m3sd; Mgrf=Mfgr+X1cf*m1gr+X2cf*m2gr+X3cf*m3gr
            st.markdown("### Pas 6 \u2014 Diagram\u0103 M Final\u0103")
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
            ax_cff.set_title(f"Diagram\u0103 M Final\u0103\\nq={qcf}kN/m EI={EIcf:.0f}kNm2",fontsize=12,fontweight="bold"); plt.tight_layout(); st.pyplot(fig_cff); plt.close(fig_cff)
            vf=Dm@Xcf+DPv; ok=all(abs(v)<1e-4 for v in vf)
            if ok: st.success(f"Verificare: {[f'{v:.2e}' for v in vf]}\u22480 \u2713")
            else: st.warning(f"Ecuatii: {[f'{v:.4f}' for v in vf]}")
        except np.linalg.LinAlgError: st.error("Eroare numeric\u0103.")

    # ---- METODA DEPLASARILOR ----
    elif tip_s2=="Metoda Deplas\u0103rilor":
        st.header("Metoda Deplas\u0103rilor \u2014 Cadru Portal Simetric")
        with st.expander("Teorie (138-3.pdf, Cap.3)"):
            st.markdown("Necunoscute: rota\u021bii noduri. Ecua\u021bii echilibru \u00een noduri.")
            st.latex(r"M_0^{BC}=+\\frac{qL^2}{12},\\; r_{11}=4i_{st}+4i_{gr},\\; r_{12}=2i_{gr}")
            st.latex(r"M_{BC}=4i_{gr}\\varphi_B+2i_{gr}\\varphi_C+M_0^{BC}")
        c1,c2=st.columns(2)
        with c1: Hmd=st.number_input("h st\u00e2lpi(m)",min_value=0.5,value=4.0,step=0.5,key="md_H"); Lmd=st.number_input("L(m)",min_value=0.5,value=6.0,step=0.5,key="md_L"); qmd=st.number_input("q(kN/m)",min_value=0.0,value=24.0,step=1.0,key="md_q")
        with c2: Pmd=st.number_input("P la mij.(kN)",min_value=0.0,value=0.0,step=5.0,key="md_P"); EIgr=st.number_input("EI grind\u0103(kNm2)",min_value=1.0,value=20000.0,step=1000.0,key="md_EIgr"); EIst=st.number_input("EI st\u00e2lpi(kNm2)",min_value=1.0,value=15000.0,step=1000.0,key="md_EIst")
        st.markdown("---"); st.markdown("### Pas 1 \u2014 nc=2 (rota\u021bii fB, fC)"); st.latex(r"n_c=2\\;(\\varphi_B,\\varphi_C)")
        Minc=qmd*Lmd**2/12+(Pmd*Lmd/8 if Pmd>0 else 0)
        st.markdown("### Pas 2 \u2014 Momente de \u00cencastrare")
        st.latex(rf"M_0^{{BC}}=+{Minc:.4f}\\text{{ kNm}},\\; M_0^{{CB}}=-{Minc:.4f}\\text{{ kNm}}")
        igr=EIgr/Lmd; ist=EIst/Hmd; r11=4*ist+4*igr; r12=2*igr; r22=4*ist+4*igr; R1P=-Minc; R2P=Minc
        st.markdown("### Pas 3 \u2014 Coeficien\u021bi Rigiditate")
        st.latex(rf"i_{{gr}}={igr:.4f},\\; i_{{st}}={ist:.4f},\\; r_{{11}}={r11:.4f},\\; r_{{12}}={r12:.4f}")
        Rm=np.array([[r11,r12],[r12,r22]]); RPv=np.array([R1P,R2P])
        try:
            Z=np.linalg.solve(Rm,-RPv); fB,fC=Z
            st.markdown("### Pas 4 \u2014 Solu\u021bie")
            st.latex(rf"\\varphi_B={fB:.8f},\\; \\varphi_C={fC:.8f}")
            MBC=4*igr*fB+2*igr*fC+Minc; MCB=4*igr*fC+2*igr*fB-Minc
            MBAst=4*ist*fB; MABst=2*ist*fB; MCDst=4*ist*fC; MDCst=2*ist*fC
            st.markdown("### Pas 5 \u2014 Momente Finale")
            cm1,cm2=st.columns(2)
            with cm1: st.latex(rf"M_{{BC}}={MBC:.4f}\\text{{ kNm}},\\; M_{{CB}}={MCB:.4f}\\text{{ kNm}}")
            with cm2: st.latex(rf"M_{{BA}}={MBAst:.4f},\\; M_{{AB}}={MABst:.4f},\\; M_{{CD}}={MCDst:.4f},\\; M_{{DC}}={MDCst:.4f}\\text{{ kNm}}")
            eqB=MBC+MBAst; eqC=MCB+MCDst
            cvm1,cvm2=st.columns(2)
            _ = cvm1.success(f"Echilibru B: \u03a3M={eqB:.6f}\u22480") if abs(eqB)<0.01 else cvm1.error(f"Nod B: \u03a3M={eqB:.6f}")
            _ = cvm2.success(f"Echilibru C: \u03a3M={eqC:.6f}\u22480") if abs(eqC)<0.01 else cvm2.error(f"Nod C: \u03a3M={eqC:.6f}")
            yst_md=np.linspace(0,Hmd,200); Mstg=MABst+(MBAst-MABst)*yst_md/Hmd; Mstd=MDCst+(MCDst-MDCst)*yst_md/Hmd
            xgr_md=np.linspace(0,Lmd,400); RAgr=(MBC-MCB)/Lmd+qmd*Lmd/2+Pmd/2; Mgr_md=np.zeros_like(xgr_md)
            for i,x in enumerate(xgr_md): Mgr_md[i]=MBC+RAgr*x-qmd*x**2/2-(Pmd*(x-Lmd/2) if x>Lmd/2 and Pmd>0 else 0)
            st.markdown("### Pas 6 \u2014 Diagram\u0103 M Final\u0103")
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
            ax_md.set_title(f"Diagram\u0103 M Final\u0103 \u2014 Metoda Deplas\u0103rilor\\nq={qmd}kN/m EI_gr={EIgr:.0f} EI_st={EIst:.0f}kNm2",fontsize=12,fontweight="bold")
            plt.tight_layout(); st.pyplot(fig_md); plt.close(fig_md)
        except np.linalg.LinAlgError: st.error("Eroare numeric\u0103.")
'''

full_app = HEADER + FEM + REZMAT + S1 + S2

with open('C:/Users/Rares/proiect-cadre/app.py', 'w', encoding='utf-8') as f:
    f.write(full_app)

print("Written:", len(full_app), "chars,", full_app.count('\\n'), "lines")

