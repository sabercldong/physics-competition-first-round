"""Scoped source-object map. Does not replace or certify the whole-book ledger."""
import hashlib,json,re
from pathlib import Path
from release_gate import expanded_tex

BOOK=Path(__file__).resolve().parents[1]
BASE=BOOK/'build/modern-source-revision-20260923'
SOURCE=Path('/Users/dongxingxi/Downloads/学而思资料/二轮/兴趣二阶春季.pdf')
ROWS=[
 (10,1,[193],'closed-clock',['一周固有时','局部同步接缝差及可持续性','不等式与等号'],[('closed-clock-source',1)]),
 (10,2,[193,194],'rod-pulse-aberration',['静止杆方向和长度','脉冲方向和两种长度约定','不换系望远镜朝向','换系望远镜和恒星方向'],[('rod-telescope-source',2)]),
 (10,3,[195],'radiation-angle',['发射与接收强度角分布','所见星数与同时位置角密度及条件'],[]),
 (10,4,[195,196],'accelerating-rod',['收缩率及lambda/mu/nu','本征加速度与纵向力','头尾信号频移及刚性条件'],[]),
 (10,5,[196,197],'relativistic-accelerator',['磁场及三段电荷','Y/Z速度与新系三段电荷','不套场变换求新系场'],[('accelerator-source',1)]),
 (10,6,[198],'synchrotron',['原子经典寿命','弯道平均每光口功率','接收脉冲持续时间'],[]),
 (10,7,[199],'successive-boosts',['同步钟方法','洛伦兹坐标方法'],[]),
 (11,1,[200],'nuclear-resonance',['发射反冲','吸收反冲与运动共振','一般D及低速结果','单核与晶体模型区别'],[('recoil-resonance-source',2)]),
 (11,2,[200,201],'photon-scattering',['实中间态不可能性','波矢允许面','频率方向关系和极值'],[('photon-scattering-source',2)]),
 (11,3,[201,202],'pursuit-doppler',['距离','力及方向','迟延接收频率'],[('pursuit-source',1)]),
 (11,4,[202],'wire-field-transform',['原系力','新系力','一般横向场变换'],[]),
 (11,5,[203],'nuclear-chain-speed',['反常结合能质量','二体递推','最大末快度和速度'],[]),
 (11,6,[204],'elliptic-cylinder',['原系磁场及换系速度','面电荷与面电流','移动边界下新系内场'],[('elliptic-current-source',2)]),
 (11,7,[205,206],'grand-neutrino',['反应阈能','一般入射能量定角电子端点','阈值特例与全能量上确界'],[]),
 (14,1,[217],'toponium-estimate',['基态间距','周期与激发态标度','寿命判据'],[]),
 (14,2,[217,218],'finite-fermi-gas',['经典绝热指数','驻波量子化','有限N奇偶求和及力','长度减半的功'],[]),
 (14,3,[218],'infinite-well',['势阱边界条件','归一化波函数','能级'],[]),
 (14,4,[219],'rutherford-recoil',['质心与实验室角变换','反冲氢核截面','反冲动能'],[('rutherford-recoil-source',1)]),
 (14,5,[219,220],'neutron-gravity',['菱形及倾转几何','重力相位','两个端口强度','非理想分束条件'],[('neutron-interferometer-source',1)]),
 (14,6,[220],'landau-action',['正则作用量','横向能级','机械与正则角动量区别'],[]),
 (14,7,[221],'action-optics',['作用量相位常量','等效折射率势能','圆轨道向心力','相位闭合角动量'],[]),
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run():
    text=expanded_tex(BOOK/'advanced/A6.tex')
    labels=re.findall(r'\\label\{(advA6:[^}]+)\}',text)
    assert len(labels)==len(set(labels))
    assert text.count(r'\begin{advexamplebox}')==text.count(r'\begin{advsolution}')==34
    aux=(BASE/'A6/A6-standalone.aux').read_text()
    built={a:(b,int(c)) for a,b,c in re.findall(r'\\newlabel\{(advA6:ex:[^}]+)\}\{\{([^}]+)\}\{(\d+)\}',aux)}
    entries=[]
    for lec,q,pages,key,parts,figs in ROWS:
        label='advA6:ex:'+key
        assert labels.count(label)==1 and label in built,label
        number,page=built[label]
        figures=[]
        for name,panels in figs:
            p=BOOK/f'assets/diagrams-modern/{name}.tex'
            assert p.is_file() and f'assets/diagrams-modern/{name}.tex' in text
            figures.append({'source_object_id':f'spring-II:exercise:L{lec}:Q{q}:figure',
                'target_asset':str(p.relative_to(BOOK)),'source_panels':panels,
                'sha256':sha(p),'manual_visual_status':'reviewed_current_render',
                'review_record':'audit/第31—32章题图与解答修订记录_20260923.md',
                'reviewed_pdf_sha256':sha(BASE/'A6/A6-standalone.pdf')})
        entries.append({'source_object_id':f'spring-II:exercise:L{lec}:Q{q}',
            'physical_pages':pages,'printed_pages':[p-144 for p in pages],
            'target_label':label,'target_example':number,'target_printed_page':page,
            'target_A6_pdf_physical_page':page+2,'covered_subquestions':parts,
            'figures':figures,'mapping_status':'mapped',
            'content_review':'main-agent source comparison and independent physics review; not a whole-source prose audit',
            'merge_note':'Existing advanced problem: multi-source mapping' if key=='infinite-well' else ''})
    assert len(entries)==21 and len({e['target_label'] for e in entries})==21
    assert sum(bool(e['figures']) for e in entries)==9
    assert sum(f['source_panels'] for e in entries for f in e['figures'])==13
    files=[BOOK/'advanced/A6.tex',BOOK/'advanced/A6-relativity.tex',BOOK/'advanced/A6-source-exercises.tex',BOOK/'advanced/A6-source-more.tex',
        BOOK/'chapters/new/ch31-relativity.tex',BOOK/'chapters/new/ch32-modern.tex']
    report={'scope':'spring-II exercise lectures10,11,14 only; chapters1-30 and full source prose not certified',
        'source_pdf':str(SOURCE),'source_sha256':sha(SOURCE),'source_hashes':{str(p.relative_to(BOOK)):sha(p) for p in files},
        'counts':{'source_questions':21,'newly_recovered_questions':16,'previously_present_questions':5,
            'question_figure_groups':9,'question_subpanels':13,'unmapped_questions_in_this_inventory':0,
            'unmapped_figure_groups_in_this_inventory':0,'A6_examples':34,'A6_solutions':34},
        'questions':entries,
        'visual_review':{'status':'scoped rendered-page review complete',
            'final_geometry_recheck':'A6 page 29: k3/k0, k4/k0 and hydrogen-target legend clear',
            'four_fresh_reviewers_gate_passed':False,
            'limitation':'Runtime agent quota: two fresh reviewers, one existing reviewer, and main-agent review; not four fresh reviewers'},
        'published':False,'global_release_gate_passed':False}
    out=BOOK/'audit/source-review/modern-source-revision-map-20260923.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report['counts'],ensure_ascii=False))

if __name__=='__main__':run()
