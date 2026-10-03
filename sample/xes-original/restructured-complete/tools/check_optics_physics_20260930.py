"""Numerical checks for the four new problems; not a whole-book certificate."""
import math,json,cmath
from pathlib import Path
from revise_optics_20260930 import BASE,save,sha,book

def close(a,b,tol=1e-9):
    assert abs(a-b)<tol,(a,b)

def check():
    out={}
    A=math.pi/3;nD=1.5;nC=1.495;nF=nC+(nD-1)/40
    i=math.asin(nD*math.sin(A/2))
    def angle(n):return math.asin(n*math.sin(A-math.asin(math.sin(i)/n)))
    eC,eF=angle(nC),angle(nF)
    close((eF-eC)*180/math.pi,1.0849,5e-5)  # Published four-decimal rounding.
    out['abbe']={'nF':nF,'i_deg':math.degrees(i),'eC_deg':math.degrees(eC),'eF_deg':math.degrees(eF),'difference_deg':math.degrees(eF-eC)}
    for n in (1.01,4/3,2,5):
        a=math.atan(math.sqrt(n))
        beta=lambda x:x-math.atan(math.tan(x)/n)
        close(beta(a),math.asin((n-1)/(n+1)))
        assert beta(a)>beta(a-.001) and beta(a)>beta(a+.001)
    out['rod']={'water_alpha_deg':math.degrees(math.atan(math.sqrt(4/3))),'water_beta_deg':math.degrees(math.asin(1/7)),'n2_points':{'P':[2.2,-2.2*math.sqrt(2)],'Pprime':[2.2,-1.1*math.sqrt(2)]},'tested_n':[1.01,4/3,2,5]}
    R=.1;L=2.1;alpha=math.radians(20/60);wavelength=600e-9
    dy=wavelength*(L+R*math.cos(alpha))/(2*R*math.sin(alpha));M=L/R
    # Direct midpoint quadrature of independent source intensities, normalized
    # to Cw; contrast coefficient compared with the analytic signed sinc.
    residuals=[]
    for u in (.1,.5,1,1.43,2,2.5):
        w=u*dy/M;steps=10000
        numeric=sum(math.cos(2*math.pi*M*((j+.5)/steps-.5)*w/dy) for j in range(steps))/steps
        analytic=math.sin(math.pi*u)/(math.pi*u)
        close(numeric,analytic,2e-8);residuals.append(abs(numeric-analytic))
    out['source_width']={'spacing_m':dy,'M':M,'first_zero_width_m':dy/M,'max_quadrature_residual':max(residuals)}
    X=.75;Y=.25;U=1.5
    close(X+U/2,1.5);close(Y+U/2,1)
    close(math.degrees(math.atan(math.sqrt(Y/X))),30)
    close(U/(X+Y+U),.6);close(X+Y+U/2,1.75)
    out['polarization']={'X_over_I0':X,'Y_over_I0':Y,'U_over_I0':U,'natural_fraction':.6,'after_max':1.75,'after_min':.75,'total':2.5}
    # Exact thin-film amplitude series, including all internal reflections.
    residuals=[]
    for n0,ns,film,phase in [(1,1.5,math.sqrt(1.5),math.pi/2),(1,1.5,1.4,.73),(1.3,1.8,1.6,.26)]:
        r01=(n0-film)/(n0+film);r12=(film-ns)/(film+ns);q=cmath.exp(2j*phase)
        direct=r01+(1-r01*r01)*r12*q*sum((-r01*r12*q)**j for j in range(200))
        formula=(r01+r12*q)/(1+r01*r12*q)
        close(abs(direct-formula),0);residuals.append(abs(direct-formula))
        if film==math.sqrt(n0*ns):close(abs(formula),0)
    out['thin_film']={'max_series_residual':max(residuals),'quarter_wave_matching_zero_verified':True}
    out['scope']='Four new examples plus added thin-film derivation only; existing 53 examples not recertified here.'
    out['source_hashes']={p.name:sha(p) for p in (book.BOOK/'chapters/new/optics-depth').glob('*.tex')}
    save(BASE/'physics-checks.json',out);print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=='__main__':check()
