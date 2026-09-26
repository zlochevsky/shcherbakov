#!/usr/bin/env python3
import json, os, re, sys, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fconv
sys.dont_write_bytecode = True
SECTION = os.environ.get('SECTION', 'fans')
if SECTION == 'fans':
    from meta import META
else:
    import importlib
    META = importlib.import_module('meta_' + SECTION).META
FANS_NAMES="andr2 andrianov andr-rusalka-d andr-rusalka answer bes bestiar bom-bram brahms chgk chgkizb discussion elfy eslinado fedenkova herbary horatius izvraty julia katrin kogolublu lirika mandlsh2 mandlsht memory metafora mueller nikst-glaza oncetran parabola polkovnik potop rakety rechisty rubcov-doroga sardanapal shuty suzy1 szs-intrm4 zhandarov comix/comix memo/podborka memo/schneider utf/covers utf/crocodile".split()
NAMES = FANS_NAMES if SECTION == 'fans' else sorted(f[:-5] for f in os.listdir(fconv.SRC) if f.endswith('.html'))
if SECTION == 'SCH2':
    NAMES = ['index', '103-e', 'gb/index', 'profiles']
    fconv.SRC_OVERRIDE['profiles'] = fconv.SRC + 'profiles'
DEFAULT_BACK = {'fans': ('fans/index.html', 'Фан-клуб'), 'Parodies': ('Parodies/index.html', 'Пародии'), 'SCH2': ('SCH2/index.html', 'SCH2')}
def OUTNAME(n):
    if n == 'index': return SECTION.lower() + '-index'
    if n.endswith('/index'): return n[:-5] + os.path.basename(os.path.dirname(n)) + '-index'
    return n
ENC={'brahms':'iso-8859-1', 'utf/covers':'utf-8', 'utf/crocodile':'utf-8'}
import glob
HAVE = {}
for _f in glob.glob('/home/sergius/schugo/content/texts/*/*.md'):
    HAVE.setdefault(os.path.basename(_f)[:-3], []).append(_f.split('/')[-2])
MANUAL = {'akoekto': '1988/akoektop', 'pesenka': '1989/vpoxodny', 'kontrrev': '1989/kupljubi', 'romans': '1994/vrjadli', 'krym1': '1982/krym10', 'pustye': '1986/pustyjeb', 'nazimnej0': '1987/nazimne0', 'onceinou': '1995/once',
          'unasopj0': '1980/unasopja', 'obrasche': '1988/obraschx', 'krajzeml': '1986/krajzem', 'voslavu': '1989/voslavug'}
DELINK = []
def resolve_songs(body, n):
    def rep(m):
        pre, y, i, anchor, txt = m.group(1), m.group(2), m.group(3), m.group(4) or '', m.group(5)
        if i == 'monologi':
            tgt = {'#apr': '1981/aprel', '#jul': '1981/jul'}.get(anchor)
            if tgt:
                return '<a href="%s%s.html">%s</a>' % (pre, tgt, txt)
            DELINK.append((n, y + '/' + i + anchor))
            return txt
        if os.path.exists('/home/sergius/schugo/content/texts/%s/%s.md' % (y, i)):
            return m.group(0)
        if i in MANUAL:
            return '<a href="%s%s.html%s">%s</a>' % (pre, MANUAL[i], anchor, txt)
        if len(HAVE.get(i, [])) == 1 and True:
            return '<a href="%s%s/%s.html%s">%s</a>' % (pre, HAVE[i][0], i, anchor, txt)
        DELINK.append((n, y + '/' + i))
        return txt
    return re.sub(r'<a href="((?:\.\./)+texts/)(\d{4})/(\w+)\.html(#\w+)?">(.*?)</a>', rep, body, flags=re.S)

D=os.path.dirname(os.path.abspath(__file__))+'/draft/'+('' if SECTION == 'fans' else SECTION + '/')
for n in (sys.argv[1:] or NAMES):
    mp = os.path.dirname(os.path.abspath(__file__)) + '/manual/' + (SECTION + '/' if SECTION != 'fans' else '') + n + '.md'
    if os.path.exists(mp):
        os.makedirs(D + os.path.dirname(n), exist_ok=True)
        open(D + n + '.md', 'w').write(open(mp).read())
        print(n, 'MANUAL')
        continue
    fconv.DEBUG.clear(); fconv.KEEP_TABLES[0] = META.get(n, {}).get('keep_table', False); fconv.SRC_REPLACE[:] = META.get(n, {}).get('src_replace', []); fconv.SRC_FN[0] = META.get(n, {}).get('src_fn'); fconv.SPLIT_BR2[0] = META.get(n, {}).get('split_br2', False); fconv.NO_TYPO[0] = META.get(n, {}).get('no_typo', False); fconv.RAW_QUOTES[0] = META.get(n, {}).get('raw_quotes', False); fconv.FONTMAP.clear(); fconv.FONTMAP.update(META.get(n, {}).get('fontmap', {}))
    title, blocks = fconv.convert(n, ENC.get(n,'koi8-r'))
    m = META.get(n, {})
    blocks = fconv.post(blocks)
    # блоки верхнего уровня: убираем первые/последние по метаданным
    body = fconv.render(blocks)
    parts = [p for p in re.split(r'\n\n+', body.strip('\n'))]
    parts = parts[m.get('drop_first', 0): len(parts) - m.get('drop_last', 0)]
    body = '\n\n'.join(parts) + '\n'
    for a, b in m.get('replace', []):
        if a.startswith('re:'):
            new, cnt = re.subn(a[3:], b, body, flags=re.S | re.M)
            if not cnt:
                print('  ! re replace not found:', a[:60])
            body = new
            continue
        if a not in body:
            print('  ! replace not found:', a[:50])
        body = body.replace(a, b)
    body = resolve_songs(body, n)
    title = m.get('title', title)
    back = m.get('back', DEFAULT_BACK[SECTION])
    os.makedirs(D+os.path.dirname(n), exist_ok=True)
    fm = {"title": title, "type": "miscellaneous", "layout": "praises-article", "url": "/%s/%s.html" % (SECTION, n)}
    if m.get('lastmod'): fm['lastmod'] = m['lastmod']
    if m.get('aliases'): fm['aliases'] = m['aliases']
    fm['params'] = {}
    if m.get('author'): fm['params']['author'] = m['author']
    if m.get('subtitle'): fm['params']['subtitle'] = m['subtitle']
    fm['params']['backUrl'], fm['params']['backTitle'] = back
    open(D+OUTNAME(n)+'.md','w').write(json.dumps(fm, ensure_ascii=False, indent=3)+'\n\n'+body)
    print(n, 'homoglyph fixes:', fconv.HOMO_COUNT[0], [d for d in fconv.DEBUG if 'nav' not in d and 'TABLE' not in d]); fconv.HOMO_COUNT[0]=0

print('DELINKED:', DELINK)
