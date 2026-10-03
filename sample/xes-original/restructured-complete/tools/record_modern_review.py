"""Freeze evidence after completed human/independent visual reviews."""
import json,re
import build_review_ch31_ch32 as r
checks=json.loads((r.BASE/'release-checks.json').read_text())
reviewers={
 '/root/modern_geometry':{'lens':'geometry','high':0,'medium':0,'evidence':'实际查看13张技术图；重算平行车端世界线、光线交点、布拉格垂足、反冲电子角、黑体峰坐标。'},
 '/root/modern_semantic':{'lens':'semantics','high':0,'medium':0,'evidence':'阅读两章正文并实际查看14图；检查换系约定、四力密度、阈能边界、辐出度、康普顿/玻尔/衰变推导。'},
 '/root/modern_labels':{'lens':'text_labels','high':0,'medium':0,'evidence':'实际查看14图及整页排除裁切误报；符号、下标与单位清晰，无标签压线。'},
 '/root/modern_layout':{'lens':'aesthetic_layout','high':0,'medium':0,'evidence':'实际查看23页；重查分页更新后31章6—11页、32章7—12页。两处大空白与近空白尾页消除。'}
}
pdfs={}
for key,c in checks['pdfs'].items():
 pdfs[key]={'sha256':c['sha256'],'review_complete':True}
 if key in ['ch31','ch32']:
  pdfs[key].update(reviewed_pages=c['pages'],reviewed_figures={'ch31':6,'ch32':8}[key],
   method='160 dpi全页、3.6倍局部放大；root与独立审查交叉复核。')
 else:
  regress=json.loads((r.BASE/f'{key}-pixel-regression.json').read_text())
  assert all(not x.get('pixel_differences') for x in regress['records'])
  pdfs[key].update(method='根代理检查标题、目录和章节边界；两章正文逐页匹配独立PDF，其他章节正文90 dpi逐页像素比较一致。')
data={'pdfs':pdfs,'independent_reviewers':reviewers,
 'checklist':{x:'pass_with_evidence_in_figure_model_and_visual_reports' for x in ['T1','T3','T4','T5','S1','S6','S8','S9','M1','M2','M3','M8','E1','E2','E3','E9','E12','A1','V1']},
 'scope_exceptions':['T1/T3等框架连接器正交化规则不用于物理斜线；世界线、光线和断轴必须保持其几何含义。',
  '设计linter的hero框、区域底色、节点尺寸层级等建议不适用于用户要求的克制数学教学图。',
  '坐标validator把氢能级断轴斜线和ct-prime时空轴误报micro-slope；已按实际几何保留。'],
 'nonblocking_notes':['图31.3图注末行较短；例32.6题目在页末、完整解答从次页开始，未拆开题设或遗失解答。',
  '总册继承一处本轮范围外Underfull hbox提示，与旧稿一致；没有新增告警。'],
 'not_claimed':['没有重新验收其他30章物理内容。','没有宣称二轮春季145—146页静电学练习已在主线完整映射。']}
(r.BASE/'visual-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
print('Recorded actual reviewer evidence and SHA-bound visual acceptance.')
