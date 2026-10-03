"""Reproduce concrete errors in the current drawings; does not modify book source."""
import json, math
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'build/review-ch27-ch28-20260923'
def slope(a,b):return (b[1]-a[1])/(b[0]-a[0])
def area2(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def unit(a):
    m=math.hypot(*a);return (a[0]/m,a[1]/m)
def cross(a,b):return a[0]*b[1]-a[1]*b[0]

results={}
results['prism_intersections']={'first_point_distance_from_left_face':abs(area2((0,2),(-2,-1.3),(-1.08,.35)))/math.hypot(2,3.3),'second_point_distance_from_right_face':abs(area2((0,2),(2,-1.3),(.72,-.2)))/math.hypot(2,3.3)}
results['apparent_depth']={'incoming_angle_from_normal_deg':math.degrees(math.atan(1.25/1.8)),'outgoing_angle_from_normal_deg':math.degrees(math.atan(1.15/1.3)),'actual_extension_depth':1.25*1.3/1.15,'marked_depth':.95,'finding':'折射方向正确，但虚像不在出射线反向延长线上。'}
results['microscope_free_space_kink']={'before_image_slope':slope((-2.5,.32),(1.3,-1.05)),'after_image_slope':slope((1.3,-1.05),(2.2,-.48)),'finding':'中间像处无元件，却从负斜率改成正斜率。'}
results['telescope_free_space_kink']={'before_image_slope':slope((-3,.76),(1,.28)),'after_image_slope':slope((1,.28),(2.5,.10)),'second_ray_before':slope((-3,.31),(1,.28)),'second_ray_after':slope((1,.28),(2.5,.27)),'finding':'第二条光线在空中折弯；全图亦不满足共同物镜焦距。'}
results['thin_lens_third_ray']={'incoming_axis_crossing_x':-4.2+1.5/(1.85/4.2),'marked_front_focus':-1.5,'outgoing_slope':slope((0,-.35),(2.35,-.84)),'finding':'第三条既不过物方焦点，出射也不平行光轴，不能称为第三条特征光线。'}
R=1;v=5
results['sphere_distance_axis_limit']={'old_l2_phi0':math.sqrt((v-R)**2+R*R-2*R*(v-R)),'required_l2_phi0':v,'corrected_plus_sign_phi0':math.sqrt((v-R)**2+R*R+2*R*(v-R))}
n=1.5;theta=.4;P=(math.cos(theta),math.sin(theta));O=(-1/n,0);Q=(-n,0)
incoming=unit((P[0]-O[0],P[1]));outgoing=unit((P[0]-Q[0],P[1]));normal=P
results['aplanatic_virtual_image']={'n':n,'R':1,'C1':O,'Q':Q,'P':P,'snell_residual':n*abs(cross(incoming,normal))-abs(cross(outgoing,normal)),'outgoing_x_component':outgoing[0],'finding':'折射光向右离开P，Q在左侧；只有反向延长线经过Q。'}
assert abs(results['aplanatic_virtual_image']['snell_residual'])<1e-12
results['door_viewer']={'reverse_virtual_image_cm':(-1)*(-1.4)/(-1.4+1),'ordinary_reference_near_point_cm':25,'finding':'近贴不能把约3.5cm虚像自动变到常规明视距离；还需讨论调焦条件。'}
(OUT/'geometry-counterexamples.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
