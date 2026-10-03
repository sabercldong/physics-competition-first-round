"""Render review evidence, not replacement artwork; independent numeric checks."""
from pathlib import Path
import json, math, hashlib
import fitz
import numpy as np
BOOK=Path(__file__).resolve().parent.parent
BASE=BOOK/'build/review-ch11-ch12-20260912'
manifest=json.loads((BASE/'manifest.json').read_text())
figures={
 'ch11':[(1,2,510,690),(2,5,145,380),(3,7,345,495)],
 'ch12':[(1,3,140,300),(2,5,215,392),(3,6,45,260),
 (4,7,310,503),(5,8,245,367),(6,9,48,177),
 (7,9,530,715),(8,10,575,729),(9,12,128,295),
 (10,13,48,230),(11,14,48,232)]}
out=BASE/'details';out.mkdir(exist_ok=True)
for ch,items in figures.items():
 doc=fitz.open(manifest['files'][ch]['path'])
 for num,p,y0,y1 in items:
  doc[p-1].get_pixmap(dpi=300,clip=fitz.Rect(44,y0,552,y1),alpha=False).save(out/f'{ch}-fig-{num:02}.png')
for key,pages in {'exercises':[40,49,51,52],'notes':[100,101,112,113,114,115,116,117]}.items():
 doc=fitz.open(manifest['files'][key]['path'])
 for p in pages:
  doc[p-1].get_pixmap(dpi=240,alpha=False).save(out/f'{key}-{p:03}.png')
checks={}
a=76.1**(2/3);e=1-.590/a;p=a*(1-e*e);theta=math.radians(72);r=p/(1+e*math.cos(theta))
h=math.sqrt(4*math.pi**2*p);vr=4*math.pi**2/h*e*math.sin(theta);vt=4*math.pi**2/h*(1+e*math.cos(theta))
checks['halley']={'a_AU':a,'e':e,'p_AU':p,'r_AU':r,'speed_AU_per_year':math.hypot(vr,vt),'direction_deg':72+math.degrees(math.atan2(vt,vr))}
checks['ch11_dust_trajectory_end_tangent_deg']=math.degrees(math.atan2(-.55-.82,2.85+.55))
checks['ch11_dust_drawn_velocity_deg']=math.degrees(math.atan2(-.26,1.15))
checks['ch11_dust_drawn_angle_deg']=12.5
# Incoming string at leftmost circle point is radial rather than tangent.
checks['ch12_pulley_incoming_tangent_dot_radius']=-.2
mu=.015;length=1.;freq=50.;g=9.8
# Transverse excitation, weak-end-displacement/high-Q resonance approximation.
T1=mu*(2*length*freq)**2
checks['ch12_melde_fixed_fixed_tension_to_mixed_first_mode_ratio']=.25
checks['ch12_melde_T1_N']=T1
checks['ch12_melde_g9p8_masses']=[T1/(g*n*n) for n in (1,2,3)]
checks['ch12_melde_g10_masses']=[T1/(10*n*n) for n in (1,2,3)]
checks['ch12_hinge_K_Nm']=.5e9*math.pi*.01**4/(2*.01)
checks['ch12_hinge_tau_Nm']=2*.3*100*.01/3
checks['ch12_hinge_assumed_mass_kg']=100/9.8
checks['ch12_hinge_Omega_using_unsupported_mass']=math.sqrt(checks['ch12_hinge_K_Nm']/(.5*(100/9.8)*.01**2))
checks['point_mass_energy']=[{'beta':b,'sum_RT':abs(-1j*b/(1+1j*b))**2+abs(1/(1+1j*b))**2} for b in (0,.1,1,10)]
# Elastic rope: dimensionless M=L0=EA=1, alpha=omega. Compare numerical energy integrals.
checks['elastic_rope']=[]
for alpha in (.01,.2,.8):
 s=np.linspace(0,1,100001);r=np.sin(alpha*s)/(alpha*np.cos(alpha));eps=np.cos(alpha*s)/np.cos(alpha)-1
 integ=getattr(np,'trapezoid',np.trapz)
 U_num=.5*integ(eps**2,s);K_num=.5*alpha**2*integ(r**2,s)
 U=.5*(1+(1/(2*np.cos(alpha)**2))-(3*np.tan(alpha)/(2*alpha)))
 K=(1/(4*np.cos(alpha)**2))-(np.tan(alpha)/(4*alpha))
 checks['elastic_rope'].append({'alpha':alpha,'max_strain':float(1/np.cos(alpha)-1),'U_num':float(U_num),'U_formula':float(U),'K_num':float(K_num),'K_formula':float(K)})
(BASE/'physics-checks.json').write_text(json.dumps(checks,indent=2,ensure_ascii=False))
frozen=dict(manifest['teaching_source_hashes'])
frozen.update({item['path']:item['sha256'] for item in manifest['files'].values()})
changed=[path for path,digest in frozen.items() if hashlib.sha256(Path(path).read_bytes()).hexdigest()!=digest]
(BASE/'end-state-check.json').write_text(json.dumps({'checked_files':len(frozen),'changed_files':changed},indent=2))
assert not changed, changed
print(json.dumps(checks,indent=2,ensure_ascii=False))
