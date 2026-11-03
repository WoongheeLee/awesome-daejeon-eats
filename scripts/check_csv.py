"""daejeon_eats.csv 형식 검사. 문제가 있으면 exit 1 (커밋이 막힘), 경고는 통과.

    python scripts/check_csv.py
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

CSV = Path(__file__).resolve().parent.parent / 'daejeon_eats.csv'
HEADER = ['지역', '상호', '업종', '메뉴 & 감상', '네이버 지도']
CATEGORIES = {
    '🍚한식', '🍜중식', '🍣일식', '🍕이탈리안', '🍝양식', '🥘스페인식', '🌶️태국음식',
    '🥢베트남', '🌏퓨전', '🍗치킨', '🐟횟집', '🔥분식', '🥩양고기', '🍸술',
    '☕카페/🍰디저트', '🥖빵집',
}
MAP_PREFIXES = ('https://naver.me/', 'https://map.naver.com/', 'https://m.place.naver.com/',
                'https://place.naver.com/', 'https://pcmap.place.naver.com/')

errors, warnings = [], []
rows = list(csv.reader(CSV.open(encoding='utf-8', newline='')))

if rows[0] != HEADER:
    errors.append(f'헤더가 다름: {rows[0]} (기대값: {HEADER})')

seen = Counter()
for i, r in enumerate(rows[1:], start=2):
    where = f'{i}행'
    if len(r) != len(HEADER):
        errors.append(f'{where}: 칸 수 {len(r)}개 (기대값 {len(HEADER)}개) → {r}')
        continue
    region, name, cat, note, link = r
    where = f'{i}행 {name or "(상호 없음)"}'
    if not name:
        errors.append(f'{where}: 상호가 비어 있음')
    if any(c != c.strip() for c in r):
        errors.append(f'{where}: 앞뒤 공백')
    if cat not in CATEGORIES:
        errors.append(f'{where}: 업종 "{cat}"이 목록에 없음 → scripts/check_csv.py CATEGORIES에 추가하거나 고치기')
    if link and not link.startswith(MAP_PREFIXES):
        errors.append(f'{where}: 네이버 지도 링크 형식이 아님 ({link})')
    if not region:
        warnings.append(f'{where}: 지역이 비어 있음')
    if region.endswith('동동'):
        errors.append(f'{where}: 지역 오타 의심 "{region}"')
    seen[(region, name)] += 1

for (region, name), n in seen.items():
    if n > 1:
        errors.append(f'중복: {region} {name} ({n}번)')

names = Counter(r[1] for r in rows[1:] if len(r) == len(HEADER))
for name, n in names.items():
    if n > 1:
        warnings.append(f'같은 상호 {n}곳: {name} (방문 횟수가 함께 세어짐 — 다른 곳이면 지점명을 붙이기)')

for w in warnings:
    print('⚠️ ', w)
for e in errors:
    print('❌', e)
print(f'{len(rows) - 1}곳 검사: 오류 {len(errors)}개, 경고 {len(warnings)}개')
sys.exit(1 if errors else 0)
