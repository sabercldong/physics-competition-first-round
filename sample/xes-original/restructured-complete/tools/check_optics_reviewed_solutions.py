"""Independent numerical checks for this batch's existing-solution expansions."""
import math
import fitz
from optics_solution_review import INSERTIONS,strip_additions
from revise_optics_20260930 import BASE,book,save,sha

def near(a,b,tol=1e-9):
    assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(a,b)

def check():
    result={}
    # Intersect a forward ray with the wall, not its supporting line alone.
    mirror=[]
    for angle in (1,15,30,44,46,60):
        t=math.radians(angle);cx=-2*math.tan(t)
        ray_parameter=-cx/math.cos(2*t)
        y=2+ray_parameter*math.sin(2*t)
        near(y,2/math.cos(2*t))
        assert (ray_parameter>0)==(angle<45)
        if angle<45:
            h=1e-7
            numeric=(2/math.cos(2*(t+h))-2/math.cos(2*(t-h)))/(2*h)
            analytic=4/math.cos(2*t)*math.tan(2*t)
            near(numeric,analytic,1e-7)
        mirror.append({'theta_degrees':angle,'wall_hit_is_forward':ray_parameter>0})
    result['rotating_mirror']=mirror

    # Same arc has horizontal initial tangent and n cos(theta) = n0.
    for angle in (0,10,35,math.degrees(math.acos(.4))):
        t=math.radians(angle);R=3;y=R*(1-math.cos(t));n=1/(1-y/R)
        near(n*math.cos(t),1);assert y<=.6*R+1e-12
    result['gradient_arc']={'maximum_angle_degrees':math.degrees(math.acos(.4)),'maximum_height_over_R':.6}

    circles=[]
    for R,n0,alpha in ((1,1.5,.3),(4,2,.5),(2,1,.8)):
        h=(n0-alpha*R)/(2*alpha);r=R+h;n=n0-alpha*h
        near(n/r,alpha)
        circles.append({'R':R,'n0':n0,'alpha':alpha,'h':h,'above_surface':h>0,'positive_n':n>0})
    result['circular_ray']=circles

    rainbows=[]
    for n in (1.1,4/3,1.5,1.9):
        i=math.asin(math.sqrt((4-n*n)/3));r=math.asin(math.sin(i)/n)
        D=lambda t:math.pi+2*t-4*math.asin(math.sin(t)/n)
        near(2-4*math.cos(i)/(n*math.cos(r)),0)
        assert D(i-1e-4)>D(i) and D(i+1e-4)>D(i)
        rainbows.append({'n':n,'i_deg':math.degrees(i),'r_deg':math.degrees(r),'radius_deg':math.degrees(math.pi-D(i))})
    result['rainbow']=rainbows

    # Trace paraxial reduced angle p=n*theta through both surfaces. This has
    # no intermediate-image denominator and stays regular at x=R/(n-1).
    def ball_height(R,n,x,v,theta):
        y=x*theta;p=theta-(n-1)*y/R
        y+=2*R*p/n;p-=(n-1)*y/R
        return y+v*p
    balls=[]
    for n in (1.05,1.5,2,2.5,4):
        R=2.;x=R/(n-1);v=x;Lmin=2*n*R/(n-1)
        near(x+2*R+v,Lmin)
        for angle in (-.001,.001,.002):near(ball_height(R,n,x,v,angle),0)
        for factor in (.9,.999,1.001,1.1):
            u=x*factor;v2=-R*((n-2)*u-2*R)/(2*(n-1)*u+(n-2)*R)
            assert v2>0;near(ball_height(R,n,u,v2,.001),0)
            assert u+2*R+v2>Lmin
        balls.append({'n':n,'x_opt':x,'v_opt':v,'Lmin':Lmin})
    result['ball_lens']=balls

    # Explicit ray propagation independently checks the B matrix polynomial.
    for f,L,u in ((2,3,.7),(2,3,2),(2,3,6),(2,1,2),(2,2,2)):
        y=u;p=1-y/f;y+=2*L*p;p-=y/f;y+=u*p
        B=2*u*(1-2*L/f)+2*L+2*(L-f)*u*u/f**2
        near(y,B)
        if u==f or (L!=f and u==L*f/(L-f)):near(y,0)
    result['self_conjugate']='Explicit ray propagation agrees with B; both physical roots checked.'
    # Confirm new additions actually reached the built PDF, not only source.
    markers={27:['超过这个角度','允许轨迹','端点项','42.03'],28:['分母为零','每一项都有长度量纲','球内']}
    # The ball text says first-face parallel light, without requiring the
    # colloquial marker "球内" to be adjacent after PDF extraction.
    markers[28][-1]='平行光'
    for n in (27,28):
        pdf=BASE/f'ch{n}/ch{n}.pdf'
        text=''.join(p.get_text() for p in fitz.open(pdf)).replace('\n','').replace(' ','')
        assert all(m in text for m in markers[n]),(n,[m for m in markers[n] if m not in text])
        body=(BASE/f'staged/ch{n}-body.tex').read_text()
        assert body.count('%<optics-review:')==len(INSERTIONS[n])
        assert strip_additions(body).count('%<optics-review:')==0
    result['inputs']={str(p.relative_to(book.BOOK)):sha(p) for p in [book.BOOK/'tools/optics_solution_review.py',book.BOOK/'tools/optics_teaching_layout.py',*sorted((book.BOOK/'chapters/new/optics-depth').glob('review-solutions-ch*.tex'))]}
    result['pdf_hashes']={str(n):sha(BASE/f'ch{n}/ch{n}.pdf') for n in (27,28)}
    result['scope']='This batch only; neither all source objects nor all old figures are certified.'
    save(BASE/'reviewed-solutions-checks.json',result)
    print('Reviewed solution checks passed; source/PDF hashes recorded.')

if __name__=='__main__':check()
