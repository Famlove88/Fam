#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_towns.py — يبني قوائم كل القرى دفعة واحدة.

الاستعمال:
    python3 build_towns.py source/                 # كل ملفات PDF داخل مجلد source
    python3 build_towns.py source/ --primary "بر الياس"

المخرجات:
    data.js             ← البلدة الأساسية (بر الياس) — الصفحة بتقرأها مباشرة
    towns/<id>.js       ← ملف لكل قرية إضافية، بيتحمّل فقط لما يلزم (بحث القرى)
    towns.js            ← فهرس القرى (الاسم، العدد، مسار الملف)

لإضافة قرية: حطّ ملف الـ PDF الرسمي داخل مجلد source وشغّل السكربت (أو ارفعه على
GitHub والـ Action بيشتغل لحاله). كل شي بيتولّد تلقائياً — ما في شي بيتكتب بالإيد.
"""
import os, re, sys, json, glob, argparse, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_voters import parse_pdf, build   # نفس محرّك القراءة

# نقحرة بسيطة لتوليد اسم ملف لاتيني ثابت لكل قرية (ما بيتغيّر مع إضافة قرى جديدة)
TR = {'ا':'a','أ':'a','إ':'i','آ':'a','ب':'b','ت':'t','ث':'th','ج':'j','ح':'h','خ':'kh','د':'d','ذ':'th',
      'ر':'r','ز':'z','س':'s','ش':'sh','ص':'s','ض':'d','ط':'t','ظ':'z','ع':'a','غ':'gh','ف':'f','ق':'q',
      'ك':'k','ل':'l','م':'m','ن':'n','ه':'h','ة':'a','و':'w','ي':'y','ى':'a','ئ':'y','ؤ':'w','ء':'', ' ':'-'}

def slug(name, used):
    s = ''.join(TR.get(ch, '') for ch in name).strip('-')
    s = re.sub(r'-{2,}', '-', s) or 'town'
    base, i = s, 2
    while s in used:
        s = base + '-' + str(i); i += 1
    used.add(s)
    return s

def pages_of(pdf):
    try:
        out = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout
        return int(re.search(r'Pages:\s+(\d+)', out).group(1))
    except Exception:
        return 0

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src', nargs='?', default='source')
    ap.add_argument('--primary', default='بر الياس')
    ap.add_argument('--out', default='.')
    a = ap.parse_args()

    pdfs = sorted(glob.glob(os.path.join(a.src, '*.pdf')) + glob.glob(os.path.join(a.src, '*.PDF')))
    if not pdfs:
        print('ما في ملفات PDF داخل ' + a.src); sys.exit(1)

    os.makedirs(os.path.join(a.out, 'towns'), exist_ok=True)
    used, index, primary_done = set(), [], False

    for pdf in pdfs:
        recs, kind, year, place = parse_pdf(pdf)
        if not recs:
            print('تخطّينا (ما في أسماء): ' + os.path.basename(pdf)); continue
        town = place.get('town') or os.path.splitext(os.path.basename(pdf))[0].replace('_', ' ')
        tid = slug(town, used)
        f = sum(1 for r in recs if r['sex'] == 0)
        is_primary = (not primary_done) and (town == a.primary or len(pdfs) == 1)

        if is_primary:
            primary_done = True
            js = build(recs, kind, year, town, pages_of(pdf), place, tid)
            path = os.path.join(a.out, 'data.js')
            index.append({'id': tid, 'name': town, 'count': len(recs), 'females': f, 'males': len(recs)-f,
                          'edition': json.loads(js.split('window.VOTERS_META = ')[1].split(';\nwindow.VOTERS')[0])['edition'],
                          'primary': True})
        else:
            js = build(recs, kind, year, town, pages_of(pdf), place, tid)
            meta = json.loads(js.split('window.VOTERS_META = ')[1].split(';\nwindow.VOTERS')[0])
            rows = js.split('window.VOTERS = ')[1].rstrip().rstrip(';')
            js = ('// ' + town + ' – ' + meta['edition'] + '\n'
                  'window.addTown({"id":' + json.dumps(tid) + ',"name":' + json.dumps(town, ensure_ascii=False) +
                  ',"meta":' + json.dumps(meta, ensure_ascii=False) + ',"rows":' + rows + '});\n')
            path = os.path.join(a.out, 'towns', tid + '.js')
            index.append({'id': tid, 'name': town, 'count': len(recs), 'females': f, 'males': len(recs)-f,
                          'edition': meta['edition'], 'file': 'towns/' + tid + '.js'})

        open(path, 'w', encoding='utf-8').write(js)
        print('%-14s %-10s %6d ناخب (%d إناث / %d ذكور) -> %s' %
              (town, '(أساسية)' if is_primary else '', len(recs), f, len(recs)-f, os.path.relpath(path, a.out)))

    index.sort(key=lambda t: (not t.get('primary'), -t['count']))
    open(os.path.join(a.out, 'towns.js'), 'w', encoding='utf-8').write(
        '// فهرس القرى — مولّد تلقائياً من build_towns.py\n'
        'window.VOTERS_TOWNS = ' + json.dumps(index, ensure_ascii=False, indent=1) + ';\n')
    print('towns.js: ' + str(len(index)) + ' قرية، المجموع ' + str(sum(t['count'] for t in index)) + ' ناخب')
