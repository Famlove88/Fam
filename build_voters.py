#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_voters.py — يحوّل ملف قوائم الناخبين الرسمي (PDF من المديرية العامة للأحوال الشخصية)
إلى data.js الذي تقرأه صفحة index.html.

الاستعمال:
    python3 build_voters.py "بر_الياس.pdf"            # ينتج data.js بجانب السكربت
    python3 build_voters.py "بر_الياس.pdf" -o data.js

المتطلبات: poppler-utils (الأمر pdftotext) — على ويندوز نزّل poppler وضع مجلد bin على الـ PATH.

يعمل مع الـ PDF الرسمي (Ghostscript / SimplifiedArabic) حيث تُخزَّن الحروف بترتيب بصري
وبأشكال Presentation Forms، لذلك يُعكس كل كلمة عربية ثم يُطبَّق NFKC.
"""
import sys, os, re, json, argparse, subprocess, tempfile, unicodedata, collections

BIDI   = re.compile(r'[\u200e\u200f\u202a-\u202e\u2066-\u2069]')
ARLET  = re.compile(r'[\u0621-\u064A\u0671-\u06D3\uFB50-\uFDFF\uFE70-\uFEFF]')
AR2EN  = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
MIRROR = str.maketrans('()[]{}', ')(][}{')

# أعمدة الجدول حسب موقعها الأفقي (الصفحة A4 عرضية، عرضها 842pt)
COLS = [(240, 'notes'), (290, 'reg'), (352, 'sect'), (430, 'dob'), (560, 'mother'), (700, 'father'), (10**9, 'name')]

def fix_word(t):
    """كلمة واحدة من مخرجات pdftotext -bbox-layout -> نص عربي صحيح."""
    t = BIDI.sub('', t)
    if ARLET.search(t):
        t = t[::-1]                                  # الحروف مخزّنة بترتيب بصري
    t = unicodedata.normalize('NFKC', t).replace('\u0640', '')
    t = t.translate(MIRROR) if any(c in t for c in '()[]{}') else t
    # رموز خاصة بالخط: ligature "ريال" بلا Unicode، وحرف ى المسند إلى حرف لاتيني (e أو l حسب النسخة)، والـ Allah ligature بألف مضاعفة
    t = t.replace('\ue816', 'ريال').replace('االله', 'الله')
    if ARLET.search(t): t = re.sub(r'[A-Za-z]', 'ى', t)
    return t.strip()

def join_rtl(ws):
    """كلمات عمود واحد -> نص بترتيب القراءة (يمين -> يسار)، مع دمج الحروف المتراكبة (مثل «زا» في تريزا)."""
    out = []
    for x0, x1, t in sorted(ws, key=lambda w: -w[1]):
        if out and x1 > out[-1][0] - 0.5:      # يتداخل أو يلامس الكلمة السابقة -> نفس الكلمة
            out[-1] = (min(out[-1][0], x0), out[-1][1] + t)
        else:
            out.append((x0, t))
    return ' '.join(t for _, t in out)

def parse_pdf(pdf_path):
    tmp = tempfile.NamedTemporaryFile(suffix='.html', delete=False).name
    subprocess.run(['pdftotext', '-bbox-layout', pdf_path, tmp], check=True)
    html = open(tmp, encoding='utf-8').read(); os.unlink(tmp)
    pages = re.split(r'<page ', html)[1:]
    records, sex, section, list_kind, year = [], None, None, None, None
    place = {}
    for pno, ph in enumerate(pages, start=1):
        words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', ph)
        rows = collections.OrderedDict()
        for x0, y0, x1, y1, t in words:
            y = round(float(y0)); key = next((k for k in rows if abs(k - y) <= 2), None)
            if key is None: key = y; rows[key] = []
            rows[key].append((float(x0), float(x1), fix_word(t)))
        for y, ws in rows.items():
            txt = join_rtl(ws)                                                 # قراءة من اليمين إلى اليسار
            if 'قائمة الناخبين' in txt:
                sex = 0 if ('الإناث' in txt or 'الاناث' in txt) else 1
                list_kind = 'النهائية' if 'النهائية' in txt else 'الأولية'
            for key, lbl in (('town', 'القرية أو الحي'), ('district', 'القضاء'), ('governorate', 'المحافظة')):
                if key not in place and lbl in txt:
                    v = txt.split(lbl, 1)[1].lstrip(' :').strip()
                    v = re.split(r'\s{2,}|قائمة|المحافظة|القضاء', v)[0].strip()
                    if v: place[key] = v
            if 'لغاية' in txt and year is None:
                m = re.findall(r'\d{4}', txt.translate(AR2EN))
                if m: year = m[-1]
            if 58 <= y <= 63 and len(ws) <= 3 and all(400 < w[0] < 560 for w in ws):
                section = txt                                              # ترويسة المذهب (سني، ماروني...)
        for y, ws in rows.items():
            if y < 100: continue
            cols = collections.defaultdict(list)
            for x0, x1, t in ws:
                xm = (x0 + x1) / 2
                col = next(name for lim, name in COLS if xm < lim)
                # اسم أم طويل بيفيض على خانة تاريخ الولادة: التاريخ أرقام فقط، فأي كلمة عربية هون أصلها من اسم الأم
                if col == 'dob' and ARLET.search(t):
                    col = 'mother'
                cols[col].append((x0, x1, t))
            rec = {k: join_rtl(v) for k, v in cols.items()}
            rec = {k: rec.get(k, '') for _, k in COLS}
            if 'الاسم والشهرة' in rec['name'] or 'ملاحظات' in rec['notes']: continue   # صف العناوين
            if not rec['reg'] or not rec['name'] or not ARLET.search(rec['name']): continue  # سطر فارغ أو حركة شاردة
            rec.update(sex=sex, section=section, page=pno,
                       reg_n=rec['reg'].translate(AR2EN), dob_n=rec['dob'].translate(AR2EN))
            records.append(rec)
    return records, list_kind or 'الأولية', year, place

def build(records, list_kind, year, town='بر الياس', pages=0, place=None, town_id=None):
    sects = []
    def sidx(s):
        if s not in sects: sects.append(s)
        return sects.index(s)
    rows = [[r['name'], r['father'], r['mother'], r['dob_n'], sidx(r['sect']), r['reg_n'], r['notes'],
             r['sex'], sidx(r['section']), r['page']] for r in records]
    yr_ar = (year or '').translate(str.maketrans('0123456789', '٠١٢٣٤٥٦٧٨٩'))
    place = place or {}
    meta = {
        "id": town_id or '', "town": place.get('town') or town,
        "district": place.get('district', 'زحلة'), "governorate": place.get('governorate', 'البقاع'),
        "edition": "القائمة " + list_kind + (" " + yr_ar if yr_ar else ""),
        "listKind": list_kind, "year": year, "pages": pages, "count": len(rows),
        "source": "وزارة الداخلية والبلديات – المديرية العامة للأحوال الشخصية",
        "sects": sects,
        "fields": ["name", "father", "mother", "dob", "sect", "reg", "notes", "list(0=F,1=M)", "section", "page"]
    }
    return ("// قوائم الناخبين – " + town + " – " + meta['edition'] + "\n"
            "// generated by build_voters.py from the official DGCS PDF\n"
            "window.VOTERS_META = " + json.dumps(meta, ensure_ascii=False) + ";\n"
            "window.VOTERS = " + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ";\n")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf'); ap.add_argument('-o', '--out', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.js'))
    ap.add_argument('--town', default='بر الياس')
    a = ap.parse_args()
    recs, kind, year, place = parse_pdf(a.pdf)
    try:
        pages = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', a.pdf], capture_output=True, text=True).stdout).group(1))
    except Exception:
        pages = 0
    js = build(recs, kind, year, a.town, pages, place)
    open(a.out, 'w', encoding='utf-8').write(js)
    f = sum(1 for r in recs if r['sex'] == 0)
    print(f"{place.get('town', a.town)}: {len(recs)} ناخب ({f} إناث / {len(recs)-f} ذكور) — {kind} {year} — {pages} صفحة -> {a.out} ({os.path.getsize(a.out)//1024} KB)")
