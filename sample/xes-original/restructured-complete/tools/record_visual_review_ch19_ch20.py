"""Bind the completed human visual review to the verified publication candidates.

This is a record writer, not an automatic visual evaluator. Run only after reading
the rendered pages and the targeted enlarged figures described below.
"""
import hashlib
import json
from pathlib import Path
import build_review_ch19_ch20 as r

checks=json.loads((r.BASE/'release-checks.json').read_text())
result={
    'date':'2026-09-20',
    'scope':'第19—20章全部独立章页面与重点技术图；分卷/总册以正文像素一致性作回归',
    'method':[
        '独立章全部页面200 dpi渲染，逐组查看整页缩略图。',
        '放大查看新绘矢量资产及关键图在最终页面的位置，检查透明标签、方向、相切/交点、边界和图注。',
        '最终高斯图重新查看250 dpi页面裁图，正电荷加号已置于场线之上。',
        '主册与分卷的对应正文页同独立章进行文字和裁区像素一致性核验；其他正文页同归档主册作回归。'
    ],
    'enlarged_targets':[
        '零势圆、阿波罗尼斯圆、两导线正交圆族、有限导线共焦曲线',
        '卢瑟福散射、偶极近远场、四极场、等势线与场线图组',
        '电像球面点与像距、导体球场、双导体场、介质球边界、平行板边缘场',
        '同轴电容器上下轮廓、球形电容器边界、串并联连接与标记',
        '六面法向、高斯图、球腔矢量三角形、有限线场元、带电平板、等离子体图',
        '扭秤、人物/实景图与图文关系、电离能分类与坐标标签'
    ],
    'limits':[
        '不声称未改动的每一幅技术图均单独作了高分辨率放大。',
        '不以图号、题数相等证明逐字零遗漏。',
        '总册两条原有松散行警告位于本轮范围之外，详见release-checks.json。'
    ],
    'pdfs':{}
}
for key,row in checks['pdfs'].items():
    p=r.BASE/key/f'{key}.pdf'
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    assert digest==row['sha256']
    if key.startswith('ch'):
        rendered=json.loads((r.BASE/'render'/key/'manifest.json').read_text())
        assert rendered['sha256']==digest
    result['pdfs'][key]={'sha256':digest,'pages':row['pages']}
(r.BASE/'visual-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('Recorded visual review against all four verified PDF hashes.')
