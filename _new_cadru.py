        # === NODURI ===
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
        nodes=nodes_ed
        node_names=[n["name"] for n in nodes]

        # === BARE ===
        st.subheader("2. Bare")
        if "cad_bars" not in st.session_state:
            st.session_state.cad_bars=[
                {"n1":"A","n2":"1"},{"n1":"1","n2":"2"},{"n1":"2","n2":"B"}]
        bc1,bc2=st.columns([1,5])
        with bc1:
            if st.button("+ Bara",key="cad_badd"):
                st.session_state.cad_bars.append({"n1":node_names[0],"n2":node_names[-1]})
            if st.button("- Bara",key="cad_bdel"):
                if len(st.session_state.cad_bars)>1: st.session_state.cad_bars.pop()
        bars_ed=[]
        bcols=st.columns(min(len(st.session_state.cad_bars),4))
        for i,br in enumerate(st.session_state.cad_bars):
            with bcols[i%4]:
                st.markdown(f"**Bara {i+1}**")
                n1s=st.selectbox("De la",node_names,index=node_names.index(br["n1"]) if br["n1"] in node_names else 0,key=f"cad_bn1_{i}")
                n2s=st.selectbox("La",node_names,index=node_names.index(br["n2"]) if br["n2"] in node_names else min(1,len(node_names)-1),key=f"cad_bn2_{i}")
                bars_ed.append({"n1":n1s,"n2":n2s})
        st.session_state.cad_bars=bars_ed

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

        # Articulatie intermediara (cadru cu 3 articulatii)
        has_hinge=False
        hinge_node=None
        if subtip_cadru=="Cadru cu 3 Articulatii":
            st.subheader("3b. Articulatie Intermediara")
            hinge_node=st.selectbox("Nod articulatie (M=0)",node_names,index=min(2,len(node_names)-1),key="cad_hinge")
            has_hinge=True

        # Grad static
        total_r=sum([2 if s["tip"]==1 else 1 if s["tip"]==2 else 3 if s["tip"]==3 else 0 for s in sup_ed])
        n_hinges=1 if has_hinge else 0
        n_eq=3+n_hinges
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

        # === CALCUL ===
        def get_node(name):
            for n in nodes:
                if n["name"]==name: return n["x"],n["y"]
            return 0.0,0.0

        Fext={n["name"]:{"Fx":0.0,"Fy":0.0,"M":0.0} for n in nodes}
        for fc in forces_ed:
            nd=fc["node"]
            if nd in Fext:
                Fext[nd]["Fx"]+=fc["Fx"]; Fext[nd]["Fy"]+=fc["Fy"]; Fext[nd]["M"]+=fc["M"]

        # Contributia incarcarilor distribuite ca forte nodale echivalente
        for qd in qdist_ed:
            if qd["bar"]>=len(bars_ed): continue
            br=bars_ed[qd["bar"]]
            x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
            dxb,dyb=x2b-x1b,y2b-y1b; Lb=np.sqrt(dxb**2+dyb**2)
            if Lb<1e-9: continue
            cb,sb=dxb/Lb,dyb/Lb
            qv=qd["q"]
            if "Perpendicular" in qd["dir"]:
                qfx=qv*sb; qfy=-qv*cb
            elif "in jos" in qd["dir"]:
                qfx=0.0; qfy=-qv
            else:
                qfx=0.0; qfy=qv
            Fext[br["n1"]]["Fx"]+=qfx*Lb/2; Fext[br["n1"]]["Fy"]+=qfy*Lb/2
            Fext[br["n2"]]["Fx"]+=qfx*Lb/2; Fext[br["n2"]]["Fy"]+=qfy*Lb/2

        # Sistem de ecuatii
        unknowns=[]
        for sp in sup_ed:
            if sp["tip"]==1: unknowns.append((sp["node"],"Fx")); unknowns.append((sp["node"],"Fy"))
            elif sp["tip"]==2: unknowns.append((sp["node"],"Fy"))
            elif sp["tip"]==3: unknowns.append((sp["node"],"Fx")); unknowns.append((sp["node"],"Fy")); unknowns.append((sp["node"],"M"))
        n_unk=len(unknowns)
        ref_x,ref_y=get_node(sup_ed[0]["node"]) if sup_ed else (0.0,0.0)
        A_mat=np.zeros((n_eq,n_unk)); b_vec=np.zeros(n_eq)

        sumFx_ext=sum(Fext[n]["Fx"] for n in Fext)
        sumFy_ext=sum(Fext[n]["Fy"] for n in Fext)
        sumM_ext=sum(Fext[n]["M"]+Fext[n]["Fy"]*(get_node(n)[0]-ref_x)-Fext[n]["Fx"]*(get_node(n)[1]-ref_y) for n in Fext)
        b_vec[0]=-sumFx_ext; b_vec[1]=-sumFy_ext; b_vec[2]=-sumM_ext

        for j,(nd,comp) in enumerate(unknowns):
            xn,yn=get_node(nd)
            if comp=="Fx": A_mat[0,j]=1.0; A_mat[2,j]=-(yn-ref_y)
            elif comp=="Fy": A_mat[1,j]=1.0; A_mat[2,j]=(xn-ref_x)
            elif comp=="M": A_mat[2,j]=1.0

        if has_hinge and n_eq>3:
            xh,yh=get_node(hinge_node)
            sumM_hinge=sum(Fext[n]["M"]+Fext[n]["Fy"]*(get_node(n)[0]-xh)-Fext[n]["Fx"]*(get_node(n)[1]-yh) for n in Fext)
            b_vec[3]=-sumM_hinge
            for j,(nd,comp) in enumerate(unknowns):
                xn,yn=get_node(nd)
                if comp=="Fx": A_mat[3,j]=-(yn-yh)
                elif comp=="Fy": A_mat[3,j]=(xn-xh)
                elif comp=="M": A_mat[3,j]=1.0

        reactions={}; solved=False
        if n_unk==n_eq and n_unk>0:
            try:
                sol=np.linalg.solve(A_mat,b_vec); solved=True
                for j,(nd,comp) in enumerate(unknowns):
                    if nd not in reactions: reactions[nd]={"Fx":0.0,"Fy":0.0,"M":0.0}
                    reactions[nd][comp]=sol[j]
            except np.linalg.LinAlgError:
                st.error("Sistem singular!")
        elif n_unk!=n_eq:
            st.error(f"Necunoscute ({n_unk}) != ecuatii ({n_eq})")

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
        if has_hinge:
            xh,yh=get_node(hinge_node)
            ax_s.plot(xh,yh,"ko",ms=12,zorder=7); ax_s.plot(xh,yh,"wo",ms=6,zorder=8)
            ax_s.text(xh+sc*1.5,yh+sc*1.5,f"{hinge_node}\n(M=0)",fontsize=9,color="navy",fontweight="bold")
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
            npts=200

            all_bars_ntm=[]
            for br in bars_ed:
                x1b,y1b=get_node(br["n1"]); x2b,y2b=get_node(br["n2"])
                dxb,dyb=x2b-x1b,y2b-y1b; Lb=np.sqrt(dxb**2+dyb**2)
                if Lb<1e-9:
                    all_bars_ntm.append({"n1":br["n1"],"n2":br["n2"],"x1":x1b,"y1":y1b,"x2":x2b,"y2":y2b,"N":np.zeros(npts),"T":np.zeros(npts),"M":np.zeros(npts)})
                    continue
                cb,sb=dxb/Lb,dyb/Lb
                s_arr=np.linspace(0,Lb,npts)
                N_arr=np.zeros(npts); T_arr=np.zeros(npts); M_arr=np.zeros(npts)

                q_perp_x=0.0; q_perp_y=0.0
                for qd in qdist_ed:
                    if qd["bar"]<len(bars_ed) and bars_ed[qd["bar"]]["n1"]==br["n1"] and bars_ed[qd["bar"]]["n2"]==br["n2"]:
                        if "Perpendicular" in qd["dir"]:
                            q_perp_x+=qd["q"]*sb; q_perp_y+=-qd["q"]*cb
                        elif "in jos" in qd["dir"]:
                            q_perp_y+=-qd["q"]
                        else:
                            q_perp_y+=qd["q"]

                # Forte la capatul n1: reactiuni + forte externe
                Fx_n1=Fext.get(br["n1"],{}).get("Fx",0.0)+reactions.get(br["n1"],{}).get("Fx",0.0)
                Fy_n1=Fext.get(br["n1"],{}).get("Fy",0.0)+reactions.get(br["n1"],{}).get("Fy",0.0)
                M_n1=Fext.get(br["n1"],{}).get("M",0.0)+reactions.get(br["n1"],{}).get("M",0.0)

                for i_s,s in enumerate(s_arr):
                    Fx_tot=Fx_n1+q_perp_x*s
                    Fy_tot=Fy_n1+q_perp_y*s
                    N_arr[i_s]=Fx_tot*cb+Fy_tot*sb
                    T_arr[i_s]=-Fx_tot*sb+Fy_tot*cb
                    M_arr[i_s]=M_n1+Fy_n1*s*cb-Fx_n1*s*sb+(q_perp_y*cb-q_perp_x*sb)*s**2/2

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
                if has_hinge:
                    xh,yh=get_node(hinge_node)
                    ax.plot(xh,yh,"ko",ms=8,zorder=7); ax.plot(xh,yh,"wo",ms=4,zorder=8)
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
                if has_hinge:
                    for b in all_bars_ntm:
                        if b["n2"]==hinge_node:
                            st.markdown(f"**M la articulatia {hinge_node} (bara {b['n1']}-{b['n2']}):** {b['M'][-1]:.4f} kNm")
                        elif b["n1"]==hinge_node:
                            st.markdown(f"**M la articulatia {hinge_node} (bara {b['n1']}-{b['n2']}):** {b['M'][0]:.4f} kNm")

