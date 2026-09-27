#!/usr/bin/env python3
"""Deterministic proposed apparatus geometry; no measured data or field solver."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, Arc
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/setups'; OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'newton-tesla-apparatus-v1','axes.spines.top':False,'axes.spines.right':False})
C={'copper':'#a7632f','primary':'#9e3229','secondary':'#176d79','measure':'#506781','ink':'#172b36','gray':'#697a82','paper':'#f7fafb'}
COILS=[{'id':'L1','center_m':[.42,.42,.105],'radius_m':.028,'length_m':.05,'winding_pack_inner_radius_m':.016,'turn_count':None},
       {'id':'L2','center_m':[.50,.42,.105],'radius_m':.028,'length_m':.05,'winding_pack_inner_radius_m':.016,'turn_count':None}]
WITNESS={'id':'W','center_m':[.84,.50,.105],'radius_m':.028,'length_m':.05,'winding_pack_inner_radius_m':.016,'turn_count':None,'role':'proposed environmental pickup; raw voltage requires independent complex calibration to w; not assumed blind to signal'}
WITNESS_WIRES=[[[.815,.528,.105],[.815,.57,.04],[1.01,.57,.045]],[[.865,.528,.105],[.865,.585,.04],[1.01,.585,.045]]]
COMPONENTS=[{'id':'source','label':'Isolated source','position_m':[.07,.13,.015],'size_m':[.13,.18,.065]},
 {'id':'R1','label':'R₁','position_m':[.25,.151,.025],'size_m':[.05,.028,.025]},
 {'id':'C1','label':'C₁','position_m':[.335,.143,.025],'size_m':[.035,.04,.04]},
 {'id':'C2','label':'C₂','position_m':[.565,.143,.025],'size_m':[.035,.04,.04]},
 {'id':'R2','label':'R₂','position_m':[.755,.208,.025],'size_m':[.055,.028,.025]},
 {'id':'RL','label':'Rᴸ','position_m':[.845,.203,.025],'size_m':[.07,.04,.035]},
 {'id':'recorder','label':'Isolated readout','position_m':[1.01,.35,.015],'size_m':[.15,.26,.1]}]
# Separate electrically closed loops. Each positive reference current enters its coil dot.
WIRES=[('primary',[[.2,.165,.045],[.25,.165,.0375]]),('primary',[[.3,.165,.0375],[.335,.163,.045]]),
 ('primary',[[.37,.163,.045],[.395,.2,.035],[.395,.448,.105]]),
 ('primary',[[.445,.448,.105],[.455,.448,.035],[.455,.64,.025],[.2,.64,.025],[.2,.275,.045]]),
 ('secondary',[[.6,.163,.045],[.475,.2,.035],[.475,.448,.105]]),
 ('secondary',[[.525,.448,.105],[.72,.448,.035],[.72,.222,.0375],[.755,.222,.0375]]),
 ('secondary',[[.81,.222,.0375],[.845,.223,.0425]]),
 ('secondary',[[.915,.223,.0425],[.955,.223,.025],[.955,.64,.025],[.55,.64,.025],[.55,.163,.045],[.565,.163,.045]])]
DOTS=[[.395,.448,.105],[.475,.448,.105]]
PARAM={'L1_H':.01,'L2_H':.04,'M_H':.003,'k':.15,'C1_F':1e-5,'C2_F':2.5e-6,'R1_ohm':2,'R2_ohm':3,'RL_ohm':20,'source_peak_V':1,'uncoupled_resonance_Hz':1/(2*np.pi*np.sqrt(.01*1e-5))}

def save(fig,name):
    fig.savefig(OUT/name,bbox_inches='tight',metadata={'Date':None} if name.endswith('.svg') else {'Software':'Deterministic Python geometry'},dpi=190)
    plt.close(fig)

def dim(ax,a,b,label,offset=0):
    a=np.asarray(a,float);b=np.asarray(b,float)
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'<->','color':C['gray'],'lw':.9})
    p=(a+b)/2;ax.text(p[0],p[1]+offset,label,ha='center',va='bottom',fontsize=9,color=C['ink'],bbox={'facecolor':'white','edgecolor':'none','pad':1})

def header(fig,title,subtitle):
    fig.suptitle(title,x=.07,y=.985,ha='left',fontsize=17,color=C['ink'],fontweight='bold')
    fig.text(.07,.92,subtitle,fontsize=10,color=C['gray'])

def make_plan(witness=False):
    fig,ax=plt.subplots(figsize=(13,8.3));fig.subplots_adjust(top=.84,bottom=.15)
    header(fig,'Environmental-witness bench · plan' if witness else 'Coupled-coil bench · dimensioned plan','PROPOSED / UNBUILT   |   Coordinates in metres   |   Geometry does not determine circuit or witness transfer')
    ax.add_patch(Rectangle((0,0),1.2,.72,fc=C['paper'],ec=C['gray'],lw=1.4))
    ax.add_patch(Rectangle((.465,.09),.515,.59,fill=False,ec=C['secondary'],ls='--',lw=1.2))
    ax.text(.75,.69,'FLOATING RECEIVER LOOP',ha='center',color=C['secondary'],fontsize=9)
    for kind,points in WIRES:
        p=np.array(points);ax.plot(p[:,0],p[:,1],color=C[kind],lw=2.1,zorder=3)
    for c in COMPONENTS:
        x,y,z=c['position_m'];sx,sy,sz=c['size_m']
        ax.add_patch(Rectangle((x,y),sx,sy,fc='#e3e9ec',ec=C['ink'],lw=1,zorder=4))
        ax.text(x+sx/2,y+sy/2,c['label'],ha='center',va='center',fontsize=9,rotation=90 if c['id']=='recorder' else 0,zorder=5)
    for coil in COILS+([WITNESS] if witness else []):
        x,y,z=coil['center_m'];l=coil['length_m'];r=coil['radius_m']
        ax.add_patch(Rectangle((x-l/2,y-r),l,2*r,fc='#f0d5be',ec=C['copper'],zorder=4))
        ax.plot([x-l/2,x+l/2],[y-r*.6,y-r*.6],color=C['copper'],lw=.6,zorder=5)
        ax.text(x,y-.047,coil['id'],ha='center',fontsize=9)
        ax.plot(x,y,'+',color=C['ink'])
    for p in DOTS:ax.plot(p[0],p[1],'o',color=C['ink'],ms=4,zorder=7)
    if witness:
        for wire in WITNESS_WIRES:
            p=np.array(wire);ax.plot(p[:,0],p[:,1],color=C['measure'],lw=1.6)
        ax.text(.86,.39,'W: proposed pickup\nraw voltage ≠ calibrated w\nsignal cross-leak must be tested',ha='center',fontsize=8,color=C['measure'])
    # Measurement symbols are zero-burden references, not conductive bridges to ground.
    for x,y,label in [(.23,.165,'I₁'),(.72,.30,'I₂')]:
        ax.add_patch(Circle((x,y),.014,fill=False,ec=C['measure'],lw=1.6,zorder=8));ax.text(x+.018,y+.016,label,color=C['measure'],fontsize=9)
    ax.text(.09,.10,'Primary return = 0 V reference\nNo shared secondary or earth bond',fontsize=8,color=C['gray'])
    ax.annotate('Same-phase timebase;\nisolated differential channels',xy=(1.08,.35),xytext=(.87,.05),ha='center',fontsize=9,color=C['measure'],arrowprops={'arrowstyle':'->','color':C['measure']})
    dim(ax,[0,-.045],[1.2,-.045],'1.20 m',.008);dim(ax,[-.045,0],[-.045,.72],'0.72 m',0)
    dim(ax,[.42,.535],[.50,.535],'0.080 m centre spacing',.008)
    dim(ax,[.445,.585],[.475,.585],'0.030 m face gap',.008)
    ax.text(.07,.76,'Circuit values are in the companion schematic; positive current references enter the marked winding dots.',fontsize=9,color=C['gray'])
    ax.set(xlim=(-.09,1.24),ylim=(-.085,.79),aspect='equal',xlabel='x (m)',ylabel='y (m)');ax.grid(alpha=.15)
    fig.text(.07,.055,'Red: primary conductive loop  ·  Teal: isolated receiver conductive loop  ·  Blue rings: proposed current readouts\nRecorder drawings have no measurement display. Sensor burden, bandwidth and isolation require separate characterization.',fontsize=9,color=C['gray'])
    save(fig,'environmental-witness-plan.svg' if witness else 'coupled-coils-plan.svg')

def make_elevation():
    fig,ax=plt.subplots(figsize=(12,5.7));fig.subplots_adjust(top=.77,bottom=.20)
    header(fig,'Coupled coils · orthographic elevation','PROPOSED / UNBUILT   |   Looking along −y   |   Wiring is defined by the plan and circuit, not this projection')
    ax.plot([0,1.2],[0,0],color=C['ink'],lw=2)
    for coil in COILS:
        x,y,z=coil['center_m'];l=coil['length_m'];r=coil['radius_m']
        ax.add_patch(Rectangle((x-.032,.002),.064,.027,fc='#dce3e6',ec=C['gray']))
        ax.add_patch(Rectangle((x-.012,.029),.024,z-r-.029,fc='#dce3e6',ec=C['gray']))
        ax.add_patch(Rectangle((x-l/2,z-r),l,2*r,fc='#f0d5be',ec=C['copper']))
        ax.plot([x-l/2,x+l/2],[z-r*.6,z-r*.6],color=C['copper'],lw=.6)
        ax.text(x,z+r+.008,coil['id'],ha='center')
    dim(ax,[.42,.18],[.50,.18],'0.080 m centre spacing',.004)
    dim(ax,[.395,.045],[.445,.045],'0.050 m winding length',.004)
    dim(ax,[.77,.077],[.77,.133],'Ø 0.056 m',0)
    ax.plot([.42,.34],[.105,.105],color=C['gray'],ls=':')
    ax.annotate('',xy=(.32,.105),xytext=(.32,0),arrowprops={'arrowstyle':'<->','color':C['gray'],'lw':.9})
    ax.text(.31,.053,'0.105 m axis height',rotation=90,ha='right',va='center',fontsize=9,color=C['ink'])
    ax.set(xlim=(.2,.9),ylim=(-.005,.21),aspect='equal',xlabel='x (m)',ylabel='z (m)');ax.grid(alpha=.14)
    fig.text(.07,.07,'Winding packs have unspecified turns, wire gauge and inductance. Adjustable nonconductive rail: measure L₁, L₂ and M at each gap.\nCircuit values are a separate numerical fixture. This physical layout is not a validated parts kit or a prediction of coupling.',fontsize=10,color=C['gray'])
    save(fig,'coupled-coils-elevation.svg')

def resistor(ax,a,b,label,color):
    a=np.array(a);b=np.array(b);v=b-a;u=v/np.linalg.norm(v);n=np.array([-u[1],u[0]])
    pts=[a]
    for j,t in enumerate(np.linspace(.15,.85,8)):pts.append(a+t*v+n*(.055 if j%2 else -.055))
    pts.append(b);p=np.array(pts);ax.plot(p[:,0],p[:,1],color=color,lw=1.8);mid=(a+b)/2;ax.text(mid[0],mid[1]+.19,label,ha='center',fontsize=10)

def capacitor(ax,x,y,label,color):
    ax.plot([x-.42,x-.055],[y,y],color=color,lw=1.8);ax.plot([x+.055,x+.42],[y,y],color=color,lw=1.8)
    for xx in [x-.055,x+.055]:ax.plot([xx,xx],[y-.16,y+.16],color=color,lw=1.8)
    ax.text(x,y-.35,label,ha='center',fontsize=10)

def coil_symbol(ax,x,y0,y1,label,color,side):
    n=5;span=(y1-y0)/n
    for j in range(n):
        th=np.linspace(-np.pi/2,np.pi/2,45);yy=y0+span*(j+.5)+span*.5*np.sin(th);xx=x+side*.12*np.cos(th);ax.plot(xx,yy,color=color,lw=1.8)
    ax.plot(x,y1+.045,'o',color=C['ink'],ms=5);ax.text(x+side*.37,(y0+y1)/2,label,ha='center',va='center',fontsize=10)

def make_circuit():
    fig,ax=plt.subplots(figsize=(13,7));fig.subplots_adjust(top=.79,bottom=.18)
    header(fig,'R1 circuit · dot convention and full energy boundary','FROZEN NUMERICAL MODEL / PROPOSED MEASUREMENT   |   Positive I₁ and I₂ enter the dotted winding terminals')
    P=C['primary'];S=C['secondary']
    # Primary source left, resistor top, coil right, capacitor bottom.
    ax.plot([1,1],[1,1.78],color=P,lw=1.8);ax.plot([1,1],[2.42,3.2],color=P,lw=1.8)
    ax.add_patch(Circle((1,2.1),.32,fill=False,ec=P,lw=1.8));xx=np.linspace(.8,1.2,70);ax.plot(xx,2.1+.12*np.sin((xx-.8)*5*np.pi),color=P,lw=1.3)
    ax.text(.46,2.1,'vₛ(t)\n1 V peak',ha='right',va='center')
    ax.plot([1,1.65],[3.2,3.2],color=P,lw=1.8);resistor(ax,(1.65,3.2),(2.5,3.2),'R₁ = 2 Ω',P);ax.plot([2.5,3.4,3.4],[3.2,3.2,2.9],color=P,lw=1.8)
    coil_symbol(ax,3.4,1.4,2.9,'L₁\n10 mH',P,-1);ax.plot([3.4,3.4,2.62],[1.4,1,1],color=P,lw=1.8);capacitor(ax,2.2,1,'C₁ = 10 µF',P);ax.plot([1.78,1],[1,1],color=P,lw=1.8)
    ax.annotate('I₁',xy=(3.4,2.56),xytext=(3.83,3.1),color=P,arrowprops={'arrowstyle':'->','color':P})
    # Secondary current enters top dot and traverses coil downward, capacitor rightward, top resistors leftward.
    coil_symbol(ax,5,1.4,2.9,'L₂\n40 mH',S,1);ax.plot([5,5,5.55],[2.9,3.2,3.2],color=S,lw=1.8)
    resistor(ax,(5.55,3.2),(6.27,3.2),'R₂ = 3 Ω',S);ax.plot([6.27,6.5],[3.2,3.2],color=S,lw=1.8);resistor(ax,(6.5,3.2),(7.35,3.2),'Rᴸ = 20 Ω',S)
    ax.plot([7.35,7.7,7.7,6.57],[3.2,3.2,1,1],color=S,lw=1.8);capacitor(ax,6.15,1,'C₂ = 2.5 µF',S);ax.plot([5.73,5,5],[1,1,1.4],color=S,lw=1.8)
    ax.annotate('I₂',xy=(5,2.5),xytext=(4.55,3.1),color=S,arrowprops={'arrowstyle':'->','color':S})
    ax.annotate('',xy=(4.91,2.2),xytext=(3.52,2.2),arrowprops={'arrowstyle':'<->','color':C['gray'],'lw':1.3});ax.text(4.2,2.47,'M = +3 mH\nk = 0.15',ha='center',fontsize=10)
    ax.plot([.88,1.12],[.8,.8],color=P);ax.plot([.94,1.06],[.73,.73],color=P);ax.plot([1,1],[1,.8],color=P);ax.text(.38,.4,'Primary 0 V reference',fontsize=9)
    ax.text(6.45,.35,'Receiver floating; no galvanic source connection',ha='center',fontsize=9,color=S)
    ax.add_patch(Rectangle((.22,.12),8.06,3.58,fill=False,ec=C['gray'],ls='--',lw=1.2));ax.text(4.2,3.87,'Complete model boundary includes both loops and mutual magnetic energy',ha='center',fontsize=11,color=C['ink'])
    ax.set(xlim=(-.05,8.5),ylim=(-.2,4.2),aspect='equal');ax.axis('off')
    fig.text(.07,.115,'Synchronized channels: vₛ, I₁, I₂, vᴸ; capacitor endpoint voltages are also needed for transient storage.\nReadout burden, channel phase and source impedance must be characterized. Physical channels must not short the floating loop.',fontsize=10,color=C['measure'])
    fig.text(.07,.045,'Instantaneous E(t) = ½L₁i₁(t)² + M i₁(t)i₂(t) + ½L₂i₂(t)² + ½C₁vC₁(t)² + ½C₂vC₂(t)²\nWin = ΔE + winding heat + load heat. Peak phasors: average real power Re(V I*) / 2; uncoupled f₀ ≈ 503.292 Hz.',fontsize=10,color=C['ink'])
    save(fig,'coupled-coils-circuit.svg')

def make_readout():
    fig,ax=plt.subplots(figsize=(13,7.5));fig.subplots_adjust(top=.81,bottom=.20)
    header(fig,'R2 coherent readout · observation and calibration boundary','PROPOSED / UNBUILT   |   Four real current components require one calibrated phase reference')
    def block(x,y,w,h,label,color):
        ax.add_patch(Rectangle((x,y),w,h,fc='white',ec=color,lw=1.6))
        ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10,color=color)
    block(.25,2.5,2.0,1.0,'Primary loop\nsource + R₁ L₁ C₁',C['primary'])
    block(3.3,2.5,2.3,1.0,'Floating receiver loop\nR₂ Rᴸ L₂ C₂',C['secondary'])
    ax.annotate('',xy=(3.25,3),xytext=(2.3,3),arrowprops={'arrowstyle':'<->','color':C['gray']})
    ax.text(2.78,3.26,'measured M',ha='center',fontsize=9)
    block(6.85,2.5,2.15,1.0,'Optional known source\nseries injection e₂\npositive control only',C['gray'])
    ax.annotate('',xy=(5.64,3),xytext=(6.8,3),arrowprops={'arrowstyle':'->','color':C['gray']})
    ax.text(6.22,3.25,'V and polarity',ha='center',fontsize=9)
    block(.25,.4,5.35,1.1,'Synchronized isolated acquisition\nvₛ(t), i₁(t), i₂(t), vᴸ(t)\nshared timebase + calibrated channel delay/gain',C['measure'])
    block(6.85,.4,2.15,1.1,'Complex reconstruction\nê = Ẑ Î\nconditional error disk',C['ink'])
    for x1,y1,x2,y2,txt in [(1.25,2.45,1.25,1.55,'vₛ, i₁'),(4.45,2.45,4.45,1.55,'i₂, vᴸ')]:
        ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops={'arrowstyle':'->','color':C['measure'],'linestyle':'--'})
        ax.text(x1+.16,(y1+y2)/2,txt,color=C['measure'],fontsize=10)
    ax.annotate('',xy=(6.8,.95),xytext=(5.65,.95),arrowprops={'arrowstyle':'->','color':C['measure'],'linestyle':'--'})
    ax.text(6.23,1.17,'Î₁, Î₂',ha='center',fontsize=10,color=C['measure'])
    ax.text(4.55,3.95,'Solid arrows: coupling / deliberate source connection · dashed arrows: readout information, not ground wiring',ha='center',fontsize=9,color=C['gray'])
    ax.set(xlim=(0,9.25),ylim=(0,4.2),aspect='equal');ax.axis('off')
    fig.text(.07,.135,'Amplitude-only currents leave exact rival drives. Relative channel phase error can create a false receiver-port residual.\nThe R2 disk assumes stated current and M error bounds; all other impedances are exact in that fixture.',fontsize=10,color=C['ink'])
    fig.text(.07,.052,'A physical build must include calibrated sensor transfer functions, burden, source impedance and complete wiring.\nAn inferred effective e₂ is a port quantity: this diagram provides no dark-matter, gravity or free-energy identification.',fontsize=10,color=C['gray'])
    save(fig,'coherent-readout.svg')

def make_witness_map():
    fig,ax=plt.subplots(figsize=(13,7.5));fig.subplots_adjust(top=.81,bottom=.23)
    header(fig,'R3 environmental witness · calibrated observation map','PROPOSED / UNBUILT   |   Model voltages are effective peak phasors, not automatic raw instrument readings')
    def block(x,y,w,h,label,color):
        ax.add_patch(Rectangle((x,y),w,h,fc='white',ec=color,lw=1.5));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=10,color=color)
    block(.1,2.5,2.55,1.15,'R2 coherent currents\n+ calibrated circuit Z\n→ reconstructed receiver port y',C['secondary'])
    block(.1,.35,2.55,1.15,'Separate pickup W\nraw pickup voltage\n+ calibrated response → w',C['measure'])
    block(3.4,2.5,2.6,1.15,'Declared observation model\ny = s + a b\nw = b (clean-witness premise)',C['ink'])
    block(3.4,.35,2.6,1.15,'Test witness cross-leak\nw = b + βs\ncalibrate a and β independently',C['gray'])
    block(6.75,1.35,2.55,1.45,'Clean known witness\nŝ = ŷ − â ŵ\nconditional deterministic disk\nnot physical source identity',C['ink'])
    for a,b in [((2.7,3.05),(3.35,3.05)),((2.7,.9),(3.35,.9)),((6.05,3.05),(6.7,2.5)),((6.05,.9),(6.7,1.6))]:
        ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','color':C['measure'],'linestyle':'--'})
    ax.text(4.65,2,'Known cross-leak: determinant 1 − aβ\nSingular at aβ = 1; no unique inverse',ha='center',va='center',fontsize=10,color=C['gray'])
    ax.set(xlim=(-.05,9.45),ylim=(0,3.95),aspect='equal');ax.axis('off')
    fig.text(.07,.15,'Calibration controls: background-only injection, known receiver-port injection, source-off runs, orientation and position changes.\nUse synchronous channels. A witness may respond to the intended signal; geometry alone cannot certify β = 0.',fontsize=10,color=C['ink'])
    fig.text(.07,.055,'Unbounded transfer a admits a zero-signal rival. Even perfect subtraction retains an unmonitored ordinary same-port drive rival.\nThe proposed pickup is a calibration platform. No dark-matter coupling, electromagnetic field solution or sensitivity is claimed.',fontsize=10,color=C['gray'])
    save(fig,'environmental-witness-map.svg')

def box3d(ax,pos,size,face,alpha=1):
    x,y,z=pos;dx,dy,dz=size
    v=np.array([[x,y,z],[x+dx,y,z],[x+dx,y+dy,z],[x,y+dy,z],[x,y,z+dz],[x+dx,y,z+dz],[x+dx,y+dy,z+dz],[x,y+dy,z+dz]])
    faces=[[v[i] for i in ids] for ids in [[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]]
    ax.add_collection3d(Poly3DCollection(faces,facecolors=face,edgecolors='#84929a',linewidths=.4,alpha=alpha))

def make_3d(witness=False):
    fig=plt.figure(figsize=(14,7.1));ax=fig.add_subplot(111,projection='3d',computed_zorder=False);fig.subplots_adjust(top=1.04,bottom=.11,left=.015,right=.88)
    header(fig,'Environmental-witness bench · 3D geometry' if witness else 'Coupled-coil bench · deterministic 3D geometry','PROPOSED / UNBUILT   |   Same coordinates as dimensioned plan   |   No measured field map or instrument readout')
    box3d(ax,[0,0,-.018],[1.2,.72,.018],'#eef2f4')
    box3d(ax,[.33,.38,.001],[.26,.08,.006],'#bdcbd2')
    for c in COMPONENTS:
        face='#d3dde1' if c['id'] in ['source','recorder'] else ('#b6c9cc' if c['id'].startswith('C') else '#e0c49d')
        box3d(ax,c['position_m'],c['size_m'],face)
        x,y,z=c['position_m'];dx,dy,dz=c['size_m'];ax.text(x+dx/2,y+dy/2,z+dz+.018,c['label'],ha='center',fontsize=9,color=C['ink'])
    for coil in COILS+([WITNESS] if witness else []):
        x,y,z=coil['center_m'];r=coil['radius_m'];l=coil['length_m'];inner=coil['winding_pack_inner_radius_m']
        box3d(ax,[x-.032,y-.036,.002],[.064,.072,.027],'#d9d1c2')
        box3d(ax,[x-.012,y-.012,.029],[.024,.024,z-r-.029],'#d9d1c2')
        th=np.linspace(0,2*np.pi,65);xx=np.array([x-l/2,x+l/2]);X,T=np.meshgrid(xx,th)
        ax.plot_surface(X,y+r*np.cos(T),z+r*np.sin(T),color=C['copper'],alpha=.96,linewidth=0,shade=True)
        for face_x in xx:
            faces=[]
            for j in range(len(th)-1):
                faces.append([[face_x,y+rr*np.cos(tt),z+rr*np.sin(tt)] for rr,tt in [(inner,th[j]),(r,th[j]),(r,th[j+1]),(inner,th[j+1])]])
            ax.add_collection3d(Poly3DCollection(faces,facecolors='#ba7947',edgecolors='none'))
        ax.text(x,y,z+.07,coil['id'],ha='center',color=C['ink'],fontweight='bold')
    for kind,points in WIRES:
        p=np.asarray(points);ax.plot(p[:,0],p[:,1],p[:,2],color=C[kind],lw=2.2)
    if witness:
        for wire in WITNESS_WIRES:
            p=np.array(wire);ax.plot(p[:,0],p[:,1],p[:,2],color=C['measure'],lw=1.5)
    p=np.asarray(DOTS);ax.scatter(p[:,0],p[:,1],p[:,2],c=C['ink'],s=16,depthshade=False)
    ax.set(xlim=(0,1.2),ylim=(0,.72),zlim=(0,.20),xlabel='x (m)',ylabel='y (m)',zlabel='')
    ax.set_zticks([0,.05,.10,.15,.20]);ax.zaxis.labelpad=3;ax.tick_params(axis='z',pad=1,labelsize=9)
    fig.text(.735,.59,'z (m)',rotation=90,ha='center',va='center',fontsize=10,color=C['ink'])
    ax.set_box_aspect((1.2,.72,.20));ax.view_init(elev=31,azim=-60)
    for axis in [ax.xaxis,ax.yaxis,ax.zaxis]:axis.pane.set_facecolor((1,1,1,0));axis._axinfo['grid']['color']=(.8,.85,.87,.25)
    caption='Separate pickup W requires calibration from its raw voltage to the model witness w; signal blindness is not assumed.\nIts coordinates are proposed, not optimized. Measure transfer, phase, loading and cross-leak before applying the R3 inverse.' if witness else 'Winding packs, adjustable nonconductive rail, stands and conductive loops use explicit metre coordinates.\nTurns, wire gauge and physical inductances are unspecified: characterize L₁, L₂ and M independently before a numerical comparison.'
    fig.text(.07,.045,caption,fontsize=10,color=C['gray'])
    save(fig,'environmental-witness-3d.png' if witness else 'coupled-coils-3d.png')

def refract(d,n,n1,n2):
    d=np.asarray(d,float);n=np.asarray(n,float);d/=np.linalg.norm(d);n/=np.linalg.norm(n)
    tangent=(n1/n2)*(d-np.dot(d,n)*n);s=1-np.dot(tangent,tangent)
    if s<0:raise ValueError('Total internal reflection in selected prism geometry')
    return tangent+n*np.sqrt(s)

def prism_geometry():
    # Millimetres: a modern 120-mm equilateral illustration, not Newton's dimensions.
    side=120.;height=np.sqrt(3)*side/2;entry=np.array([60/np.sqrt(3),60.])
    din=np.array([np.cos(np.deg2rad(20)),np.sin(np.deg2rad(20))]);nin=np.array([np.sqrt(3)/2,-.5]);nout=np.array([np.sqrt(3)/2,.5])
    rows=[]
    for wavelength,index,color in [(650,1.51,'#b94437'),(550,1.52,'#368368'),(450,1.53,'#3962ab')]:
        inside=refract(din,nin,1,index);distance=(np.sqrt(3)*(120-entry[0])-entry[1])/(inside[1]+np.sqrt(3)*inside[0]);exitpoint=entry+distance*inside
        dout=refract(inside,nout,index,1);screen=exitpoint+(450-exitpoint[0])/dout[0]*dout
        rows.append({'wavelength_nm':wavelength,'stipulated_refractive_index':index,'entry_mm':entry.tolist(),'exit_mm':exitpoint.tolist(),'screen_mm':screen.tolist(),'exit_angle_deg':float(np.rad2deg(np.arctan2(dout[1],dout[0]))),'color':color,'entry_snell_residual':float(abs(np.sin(np.deg2rad(50))-index*abs(nin[0]*inside[1]-nin[1]*inside[0]))),'exit_snell_residual':float(abs(index*abs(nout[0]*inside[1]-nout[1]*inside[0])-abs(nout[0]*dout[1]-nout[1]*dout[0])))})
    return side,height,entry,din,rows

def make_prism():
    side,height,entry,din,rows=prism_geometry();fig,ax=plt.subplots(figsize=(13,6.8));fig.subplots_adjust(top=.78,bottom=.21)
    header(fig,'Newton-style prism study · calculated ray paths','SOURCE-SUPPORTED MODERN RECONSTRUCTION / NOT PERFORMED   |   NT-NEWTON-LIGHT1672   |   Snell-law geometry')
    ax.add_patch(Polygon([[0,0],[120,0],[60,height]],fc='#d9e7eb',ec=C['gray'],alpha=.8));ax.text(60,40,'60° prism',ha='center',fontsize=10)
    start=entry-170*din;ax.plot([start[0],entry[0]],[start[1],entry[1]],color=C['ink'],lw=2)
    aperture=entry-140*din;ax.plot([aperture[0],aperture[0]],[aperture[1]-22,aperture[1]-3],color=C['ink'],lw=3);ax.plot([aperture[0],aperture[0]],[aperture[1]+3,aperture[1]+22],color=C['ink'],lw=3)
    ax.text(aperture[0]-5,aperture[1]+30,'Aperture',ha='center',fontsize=9);ax.text(start[0],start[1]-20,'Incident ray\n20° to horizontal',fontsize=9)
    ax.plot([450,450],[-145,100],color=C['gray'],lw=2);ax.text(450,115,'Illustrated screen\nx = 450 mm',ha='center',fontsize=9)
    for row in rows:
        e=np.array(row['exit_mm']);s=np.array(row['screen_mm']);ax.plot([entry[0],e[0],s[0]],[entry[1],e[1],s[1]],color=row['color'],lw=1.8,label=f"{row['wavelength_nm']} nm, stipulated n = {row['stipulated_refractive_index']:.2f}")
        ax.plot(s[0],s[1],'o',color=row['color'],ms=4)
    dim(ax,[0,-20],[120,-20],'120 mm side',5)
    ax.set(xlim=(-140,495),ylim=(-155,155),aspect='equal',xlabel='x (mm)',ylabel='y (mm)');ax.grid(alpha=.15);ax.legend(loc='lower left',fontsize=9,frameon=False)
    fig.text(.07,.105,'Indices 1.51 / 1.52 / 1.53 are stipulated teaching inputs, not a measured glass dispersion curve.\nAll intersections and transmitted directions are computed; no wavelength-to-angle measurement is fabricated.',fontsize=10,color=C['gray'])
    fig.text(.07,.045,'Newton’s 1672 letter describes aperture/prism controls and a second-prism discrimination. This one-prism drawing illustrates\nthe first separation only; it does not reproduce his full experiment, apparatus dimensions or complete experimental inference.',fontsize=10,color=C['ink'])
    save(fig,'newton-prism-rays.svg');return rows

def main():
    make_plan();make_elevation();make_circuit();make_3d();make_readout();make_plan(True);make_3d(True);make_witness_map();rays=make_prism()
    geometry={'schemaVersion':1,'units':'metres unless explicitly mm','status':'proposed_unbuilt','table_m':[1.2,.72,.018],'adjustableNonconductiveRail_m':{'position':[.33,.38,.001],'size':[.26,.08,.006]},'coils':COILS,'components':COMPONENTS,'conductiveWires':[{'loop':k,'vertices_m':p} for k,p in WIRES],'dotTerminals_m':DOTS,'modelParameters':PARAM,'parameterGeometryRelation':'L,M,R,C are stipulated by R1 contract; adjustable calibration-coil geometry has unspecified turns/wire gauge and does not derive or validate them.','environmentalWitness':{'pickup':WITNESS,'differentialLeads_m':WITNESS_WIRES,'contractPath':'docs/contracts/R3.json','limitation':'Proposed raw pickup voltage must be mapped to witness-equivalent w by independent complex calibration; geometric position does not establish a or beta.'},'prism':{'units':'mm','side_mm':120,'apex_angle_deg':60,'incident_angle_deg':20,'screen_x_mm':450,'rayCalculations':rays}}
    (OUT/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n')
    sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
    files=['coupled-coils-plan.svg','coupled-coils-elevation.svg','coupled-coils-circuit.svg','coupled-coils-3d.png','coherent-readout.svg','environmental-witness-plan.svg','environmental-witness-3d.png','environmental-witness-map.svg','newton-prism-rays.svg','geometry.json']
    manifest={'generatorPath':'scripts/render_setups.py','generatorSHA256':sha(__file__),'files':{f:sha(OUT/f) for f in files},'checks':{'coilCenterSeparation_m':.08,'coilClearAxialGap_m':.03,'k_from_parameters':PARAM['M_H']/np.sqrt(PARAM['L1_H']*PARAM['L2_H']),'inductanceMatrixEigenvalues_H':np.linalg.eigvalsh([[.01,.003],[.003,.04]]).tolist(),'prismMaxSnellResidual':max(max(r['entry_snell_residual'],r['exit_snell_residual']) for r in rays)},'limits':'Deterministic drawing geometry and stipulated-ray calculation, not field simulation, material calibration or completed apparatus.'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(manifest['checks'],indent=2))

if __name__=='__main__':main()
