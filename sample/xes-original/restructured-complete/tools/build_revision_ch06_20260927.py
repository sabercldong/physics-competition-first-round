"""Scoped chapter 6 revision; preserve all peer generated chapters."""
import argparse
import build_review_ch06 as regen
import build_revision_ch06_ch10 as compile
BASE=compile.book.BOOK/'build/revision-ch06-20260927'
regen.DEST=BASE
compile.BASE=BASE
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--regenerate',action='store_true');p.add_argument('--target');a=p.parse_args()
 if a.regenerate:regen.regenerate()
 if a.target:compile.build(a.target)
