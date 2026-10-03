from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import json,hashlib,os,collections,subprocess
root=Path.cwd();target=Path.home()/'Downloads/物理竞赛讲义_最终成果_2026-10-03.zip';prefix='物理竞赛讲义_最终成果';formal=root/'output/pdf';items=[]
manifest=json.loads((formal/'发布清单_20261003.json').read_text())
for row in manifest['files']:
 name=row['file'];p=formal/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
 if name=='高中物理竞赛一轮讲义.pdf':category='一轮讲义/完整合订本'
 elif '第01—02章' in name or '第1—7章' in name:category='附加版本/局部合订版'
 elif '高阶选读_A' in name:category='一轮讲义/高阶选读'
 elif '附录E' in name:category='一轮讲义/附录'
 elif '卷_' in name:category='一轮讲义/分卷版'
 else:category='一轮讲义/分章版'
 items.append((p,f'{prefix}/{category}/{name}'))
tracked={root/p.decode() for p in subprocess.check_output(['git','ls-files','-z','output']).split(b'\0') if p}
# Preserve the remaining outputs and their exact paths from the existing bundle.
with ZipFile(target) as old:
 for info in old.infolist():
  if not any(f'/{cat}/' in info.filename for cat in ['二轮讲义','测试资料','论文修改']):continue
  name=Path(info.filename).name;matches=[p for p in (root/'output').rglob(name) if p.is_file() and p in tracked]
  assert len(matches)==1,(name,matches);items.append((matches[0],info.filename))
items.extend([(formal/'发布清单_20261003.json',f'{prefix}/发布清单_20261003.json'),(formal/'发布说明.md',f'{prefix}/发布说明.md'),(root/'audit/全书复查问题_修订完成记录_20261003.md',f'{prefix}/修订完成记录_20261003.md')])
assert len({name for _,name in items})==len(items)
text='# 物理竞赛讲义最终成果\n\n更新日期：2026-10-03。全书复查修订版，合订本1106页。\n\n保留原包的一轮、二轮、测试和论文修改分类；第19章只保留现行37页版本。习题册仍暂停，未列入本成果包。\n\n仓库：https://github.com/sabercldong/physics-competition-first-round\n\n'
counts=collections.Counter(p.suffix for p,_ in items);text+=f'本包共{len(items)+1}个文件（含本清单），其中PDF {counts[".pdf"]}份、Word {counts[".docx"]}份。\n\n'
groups=collections.defaultdict(list)
for p,name in items:groups[str(Path(name).parent.relative_to(prefix))].append(p.name)
for category,names in sorted(groups.items()):text+=f'## {category if category!="." else "发布记录"}\n\n'+''.join(f'- {n}\n' for n in sorted(names))+'\n'
pending=target.with_name(target.name+'.pending')
with ZipFile(pending,'w',ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
 for p,name in items:z.write(p,name)
 z.writestr(f'{prefix}/文件清单.md',text)
with ZipFile(pending) as z:
 assert z.testzip() is None
 for p,name in items:
  assert hashlib.sha256(z.read(name)).digest()==hashlib.sha256(p.read_bytes()).digest(),name
 assert len(z.namelist())==len(items)+1
 assert not any('较早版本' in n or '第19章_静电场与电势_含解答' in n for n in z.namelist())
os.replace(pending,target)
result=dict(archive=str(target),files=len(items)+1,pdfs=counts['.pdf'],bytes=target.stat().st_size,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),all_members_verified=True)
(root/'audit/full_book_fix_20261003/download_package.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False,indent=2))
