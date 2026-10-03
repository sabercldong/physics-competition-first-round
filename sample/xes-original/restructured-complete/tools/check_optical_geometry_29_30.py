"""Independent numeric checks; assertions are not a substitute for visual review."""
import math,json
import numpy as np
from scipy.special import j1
import build_review_ch29_ch30 as r
results={}
def passed(name):results[name]=True
for width in np.linspace(0,20,401):
 centres=sum(abs(m)<=width/2+1e-10 for m in range(-30,31))
 full=sum(abs(m)+.5<=width/2+1e-10 for m in range(-30,31))
 assert centres==2*math.floor(width/2+1e-10)+1
 assert full==max(0,2*math.floor(width/2-.5+1e-10)+1)
passed('billet_centre_and_complete_band_counts')
for q in range(1,7):
 for j in range(8):
  y=j*math.sqrt(2*q)
  assert abs(y*y/2-q*j*j)<1e-10
passed('equal_spaced_wedge_slits_square_orders')
unit=lambda v:np.array(v)/np.linalg.norm(v)
for angle,v,point in [(-51,(-2*math.cos(math.radians(12)),2*math.sin(math.radians(12))),(-.254342226,.314086491)),
                       (-39,(-2*math.cos(math.radians(12)),-2*math.sin(math.radians(12))),(.343717036,-.278336567))]:
 point=np.array(point);n=np.array([-math.sin(math.radians(angle)),math.cos(math.radians(angle))])
 inc=unit(point-[0,2]);out=unit(np.array([5,0])-point)
 assert np.linalg.norm(inc-2*np.dot(inc,n)*n-out)<1e-8
 assert abs(np.linalg.det(np.stack([point-np.array(v),np.array([5,0])-point])))<1e-8
passed('double_mirror_specular_reflections_and_virtual_extensions')
n=1.5;i=math.atan(.1);inside=math.asin(math.sin(i)/n)
normal=math.atan(.3);out=normal+math.asin(n*math.sin(inside-normal))
exit=np.array([.352960321,.323465596])
assert abs(exit[0]+.3*exit[1]-.45)<1e-8
assert abs(exit[1]-.3-exit[0]*math.tan(inside))<1e-8
assert abs(exit[1]+(-3-exit[0])*math.tan(out)-.490914661)<1e-8
assert abs(exit[1]+(6-exit[0])*math.tan(out)-.041448685)<1e-8
passed('biprism_snell_interfaces_and_collinearity')
for x in np.linspace(-2.2,2.2,31):
 y=4-math.sqrt(16-x*x)
 assert abs(x*x+(y-4)**2-16)<1e-12
assert 4-math.sqrt(16)==0
passed('newton_sphere_plane_contact_and_thickness')
assert abs(1/(1/1.5-1/3)-3)<1e-12
assert abs(2+1/(1/1.5-1/5)-29/7)<1e-12
assert 3<25/7<29/7
passed('meslin_common_axis_and_screen_between_images')
r0=20*math.pi/180;i=math.asin(1.5*math.sin(r0));D=1.5
assert abs(2*1.5*D/math.cos(r0)-2*D*math.tan(r0)*math.sin(i)-2*1.5*D*math.cos(r0))<1e-12
passed('film_common_wavefront_optical_path')
for theta in (.1,.3,.7,1.1):
 v=np.array([math.sin(theta),math.cos(theta)])
 H=2*math.sin(theta)*v;B=np.array([2.,0.])
 assert abs(np.dot(B-H,v))<1e-12
 assert abs(np.linalg.norm(H)-2*math.sin(theta))<1e-12
passed('grating_projection_to_common_wavefront')
z=3.8317059702075125
assert abs(j1(z))<1e-14
centre_dip=2*(2*j1(z*.5)/(z*.5))**2
assert .73<centre_dip<.74
passed('airy_first_zero_and_rayleigh_dip')
for n in range(1,6):assert abs((.65*math.sqrt(n+1))**2-(.65*math.sqrt(n))**2-.65**2)<1e-12
for y in (1.028,1.379):assert int((y/.65)**2)+1 in (3,5)
passed('zone_plate_equal_area_annuli_and_open_band_rays')
for a in (.2,.5,.785,1.1):
 for t in np.linspace(0,2*math.pi,31):
  ex=math.cos(a)*math.cos(t);ey=math.sin(a)*math.sin(t)
  assert abs(ex*ex/math.cos(a)**2+ey*ey/math.sin(a)**2-1)<1e-12
passed('quarter_wave_polarization_ellipse')
assert abs(1.22*632.8e-9/100e-6*3.84e8-2.96454144e6)<1e-5
assert 2.96454144e6>1.7374e6
passed('moon_beam_plane_larger_than_lunar_projection')
(r.BASE/'physics-checks.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
