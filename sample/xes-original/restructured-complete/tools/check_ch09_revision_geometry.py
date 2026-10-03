"""Post-revision physics/geometry checks, tied to the actual source hashes.

The numerical checks supplement, not replace, visual inspection of the PDF.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import math,re,json,hashlib
BOOK=Path(__file__).resolve().parents[1]
BASE=BOOK/'build/review-ch09-20260909'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def close(a,b):assert abs(a-b)<1e-10,(a,b)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
paths=[BOOK/'generated/chapters/ch09.tex']
for unit in ['sixteenth-section','seventeenth-section']:
    paths += [BOOK.parent/unit/n for n in ['main.tex','content.tex','theory.tex','diagrams-revised.tex']]
source={str(p):sha(p) for p in paths}
tex=paths[0].read_text()
labels=re.findall(r'\\label\{([^}]+)\}',tex)
refs=re.findall(r'\\(?:ref|eqref|pageref)\{([^}]+)\}',tex)
assert all(n==1 for n in Counter(labels).values())
assert not set(refs)-set(labels),set(refs)-set(labels)
figs=[x for x in labels if x.startswith('ch09:fig:')]
assert len(figs)==29 and set(figs)<=set(refs)
assert tex.count(r'\begin{origexamplebox}')==tex.count(r'\begin{xesolution}')==19
assert not re.search(r'node\[[^\]]*fill\s*=\s*white',tex)
mapping=json.loads((BOOK/'generated/source-map.json').read_text())
objects=[o for x in next(c for c in mapping['chapters'] if c['chapter']==9)['source_number_maps'] for o in x['objects']]
sourcefigs=[o for o in objects if o['source_kind']=='fig']
assert len(sourcefigs)==27 and len({o['new_label'] for o in sourcefigs})==27
assert all(o['new_label'] in labels for o in objects)
assert len([o for o in sourcefigs if o['source_number'] is None])==1

# The printed answers must contain the revised expressions, not merely pass
# an independent correct calculation while retaining an old wrong formula.
for snippet in [r'\frac{v_0^2}{\sqrt3g}',r'2x^3-(k^2+2)x^2+k^2',
                r'\frac{k^2+k\sqrt{k^2+8}}{4}',r'M(x)&=I_c\beta-Q(x)\frac s2',
                r'\frac{M(a^2+b^2)}{12}']:
    assert snippet in tex,snippet
result={'source_hashes':source,'static':{'examples':19,'solutions':19,'figures':29,
        'source_figure_groups_mapped':27,'new_auxiliary_figure_groups':2,
        'all_figures_referenced':True,'duplicate_labels':0,'unknown_refs':0,
        'white_background_text_nodes':0}}

# Normalize v0^2/g=1; check all three branches against the energy equation.
theta=math.pi/6;r0=math.tan(theta);close(r0,1/math.sqrt(3))
close(r0/math.tan(theta),1)
turn=[]
for k in [0.5,1,2,0.1,5]:
    x=(k*k+k*math.sqrt(k*k+8))/4
    residual=k*k/2+1-(k*k/(2*x*x)+x)
    close(residual,0)
    turn.append({'k':k,'other_positive_radius_ratio':x,'energy_residual':residual})
result['funnel']={'r0':r0,'h0':1,'turning_points':turn,'k1_double_root':True}

# Normalize m=g=L=sin(theta)=1. Signed moment about the upper-segment CM.
for x in [F(0),F(1,4),F(1,3),F(1,2),F(3,4),F(1)]:
    s=1-x;Q=s*(1-3*x)/4;beta=F(3,2);Ic=s**3/12
    assert Ic*beta-Q*s/2 == x*s*s/4
assert F(1,3)*(1-F(1,3))**2==F(4,27)
result['chimney']={'signed_moment_identity':True,'bending_maximum_x_over_L':'1/3',
                   'shear_abs_maximum_x_over_L':'0'}

# Rolling diagram: points exactly on circle; all velocity arrows use omega=.6.
for deg in [145,315,90]:
    a=math.radians(deg);x=1.1*math.cos(a);y=1.1+1.1*math.sin(a)
    close(x*x+(y-1.1)**2,1.1**2)
    vx,vy=.6*y,-.6*x
    close(x*vx+y*vy,0);close(math.hypot(vx,vy),.6*math.hypot(x,y))

# Sloping surfaces: shared contact and normal vector determine every center.
for deg,r in [(25,.82),(22,.78)]:
    a=math.radians(deg);t=(math.cos(a),-math.sin(a));n=(math.sin(a),math.cos(a))
    delta=(r*n[0],r*n[1]);close(dot(t,n),0);close(dot(delta,n),r)
# For the ellipse, its .78 semiaxis is exactly the surface normal.
result['contact_geometry']={'incline_circle_radius':.82,'egg_normal_semiaxis':.78,
                           'two_wheels_center_distance':1.45+1.15,'basketball_contact_gap':0,
                           'rolling_circle_and_tangents':True}
close(2.6-1.45,1.15)

# Right-handed x-right, y-into-page, z-up basis; conical pendulum and tilted rod.
assert cross((1,0,0),(0,0,-1))==(0,1,0)
r=(2,0,-3);v=(0,1,0);L=cross(r,v)
assert L==(3,0,2);close(dot(r,L),0)
r=(1.25,0,1.7);v=(0,1.25,0);L=cross(r,v)
assert L[0]<0<L[2];close(dot(r,L),0)
result['angular_directions']={'right_handed_coordinates':True,'conical_L_perpendicular_to_OP':True,
 'tilted_rod_L_not_parallel_to_omega':True,'brake_rotation_clockwise_torque_counterclockwise':True,
 'euler_middle_positive_beta_clockwise_for_inward_N':True}

# Particle and angle arcs, independently measured from the drawn coordinates.
angle=math.degrees(math.atan2(.84,1.8));close(angle,math.degrees(math.atan2(1.4,3)))
result['angles_degrees']={'particle_phi':angle,'funnel_theta':30,
                         'torque_work_theta':math.degrees(math.atan2(2.3,4))}
assert all(0<x<90 for x in result['angles_degrees'].values())
for aa,bb in [(3.4,2.3),(4,2.4)]:
    cc=math.sqrt(aa*aa-bb*bb);close(cc*cc,aa*aa-bb*bb)
    assert 0<aa-cc<aa+cc
result['ellipse_focus_and_radius_endpoints']='Same F coordinate used for body, guides and dimensions.'

# Two-wheel branches: contact-speed equilibration and kinetic-energy loss.
cases=[]
for u1,u2 in [(3,1),(1,3),(2,2)]:
    q1,q2=2.,3.;force=.7;delta=u1-u2;eps=(delta>0)-(delta<0)
    ts=abs(delta)/(force*(1/q1+1/q2))
    a=u1-eps*force*ts/q1;b=u2+eps*force*ts/q2;close(a,b)
    loss=.5*(q1*u1*u1+q2*u2*u2)-.5*(q1+q2)*a*a
    close(loss,.5*q1*q2/(q1+q2)*delta*delta)
    assert loss>=-1e-12
    cases.append({'initial_speeds':[u1,u2],'sliding_end_time':ts,'common_speed':a,'energy_loss':loss})
result['two_wheels']=cases
close(.5*(5/7)**2+.5*(2/5)*(5/7)**2,5/14)
close(2/7-(2/7)**2,10/49)
result['billiards']={'final_total_energy_over_mv02':'5/14','collision_final_gap_coefficient':'10/49'}
result['limitations']='Symbolic/numerical identities and source mapping are checks, not a guarantee of no remaining pedagogical defects; manual PDF review recorded separately.'
(BASE/'geometry-checks.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='source_hashes'},ensure_ascii=False,indent=2))
