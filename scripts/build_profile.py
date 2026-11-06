"""Build GitHub-compatible SVGs using local logos and outlined Poppins text.

Run: python scripts/build_profile.py
Requires fonttools. No network, JavaScript or remote fonts at render time.
"""
from pathlib import Path
import base64
import json
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
D = json.loads((ROOT / 'data/profile.json').read_text(encoding='utf-8'))
BG, SURFACE, HIGH, CREAM, MUTED, YELLOW = '#171717', '#232323', '#3A3A3A', '#FEF9ED', '#B8B1A5', '#F9C852'
FONTS = {w: TTFont(ASSETS / 'fonts' / f'Poppins-{name}.ttf') for w, name in [(300,'Light'), (400,'Regular'), (600,'SemiBold')]}

def width(s, size, weight=400):
    f = FONTS[weight]; cmap = f.getBestCmap(); metrics = f['hmtx'].metrics
    return sum(metrics[cmap.get(ord(c), '.notdef')][0] for c in s) * size / f['head'].unitsPerEm

def text(s, x, y, size=22, color=CREAM, weight=400):
    s = s.replace('→', '>').replace('↔', '/')
    f = FONTS[weight]; gs=f.getGlyphSet(); cmap=f.getBestCmap(); scale=size/f['head'].unitsPerEm
    out=[]; cursor=0
    for c in s:
        name=cmap.get(ord(c), '.notdef'); pen=SVGPathPen(gs); gs[name].draw(pen)
        if pen.getCommands(): out.append(f'<path transform="translate({cursor} 0)" d="{pen.getCommands()}"/>')
        cursor += f['hmtx'].metrics[name][0]
    return f'<g aria-label="{escape(s, quote=True)}" fill="{color}" transform="translate({x} {y}) scale({scale} {-scale})">{"".join(out)}</g>'

def lines(s,x,y,max_width,size=21,color=CREAM,weight=400,leading=None):
    leading=leading or size*1.5; out=[]; line=''
    for word in s.split():
        candidate=(line+' '+word).strip()
        if line and width(candidate,size,weight)>max_width:
            out.append(text(line,x,y,size,color,weight)); y+=leading; line=word
        else: line=candidate
    if line: out.append(text(line,x,y,size,color,weight)); y+=leading
    return ''.join(out),y

def rect(x,y,w,h,fill=SURFACE,r=20,extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" {extra}/>'

def logo(name,x,y,size=64):
    if name=='ibs':
        raw=(ASSETS/'logos/ibs.svg').read_text(encoding='utf-8')
        return raw.replace('<svg ',f'<svg x="{x}" y="{y}" width="{size*2.3}" height="{size}" ',1)
    raw=(ASSETS/'logos'/f'{name}.jpg').read_bytes()
    return rect(x-1,y-1,size+2,size+2,'#FFFFFF',8)+f'<image x="{x}" y="{y}" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet" href="data:image/jpeg;base64,{base64.b64encode(raw).decode()}"/>'

def start(w,h,title,desc):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc"><title id="title">{escape(title)}</title><desc id="desc">{escape(desc)}</desc>',
    '''<defs>
    <linearGradient id="metal" x2="0" y2="1"><stop stop-color="#FEF9ED"/><stop offset=".32" stop-color="#9A958C"/><stop offset=".49" stop-color="#3A3A3A"/><stop offset=".51" stop-color="#E4DDCE"/><stop offset="1" stop-color="#6B665E"/></linearGradient>
    <linearGradient id="glass" x2="1" y2="1"><stop stop-color="#FEF9ED" stop-opacity=".09"/><stop offset=".5" stop-color="#FEF9ED" stop-opacity=".02"/><stop offset="1" stop-color="#F9C852" stop-opacity=".06"/></linearGradient>
    <radialGradient id="amber"><stop stop-color="#613F0F" stop-opacity=".55"/><stop offset="1" stop-color="#613F0F" stop-opacity="0"/></radialGradient>
    <pattern id="grid" width="36" height="36" patternUnits="userSpaceOnUse"><path d="M36 0H0V36" fill="none" stroke="#FEF9ED" stroke-opacity=".035"/></pattern>
    </defs>''',rect(0,0,w,h,BG,24),rect(0,0,w,h,'url(#grid)',24)]

def save(name,out):
    (ASSETS/name).write_text(''.join(out)+'</svg>',encoding='utf-8')

def window(x,y,w,h,label):
    return [rect(x,y,w,h,'url(#metal)',20),rect(x+2,y+2,w-4,h-4,BG,18),rect(x+3,y+3,w-6,42,'url(#metal)',16),rect(x+3,y+30,w-6,15,'url(#metal)',0),rect(x+14,y+9,465,27,BG,7),text(label,x+22,y+29,14,CREAM,400),f'<path d="M{x+w-76} {y+24}h14m14-7h14v14h-14m27-14 14 14m0-14-14 14" fill="none" stroke="{BG}" stroke-width="1.5"/>',rect(x+3,y+46,w-6,h-49,'url(#glass)',16)]

def hero():
    o=start(1200,654,'Fabian Langer | Data Science, AI & Business','Lead Data Science & AI Consultant at Isatis Business Solutions. AI Trainer at CIU. Business Analist Digitalisering & AI at Enexis, an IBS assignment.')
    o += ['<ellipse cx="1040" cy="310" rx="430" ry="390" fill="url(#amber)"/>']
    # Visible circuit board beneath the translucent window.
    o += [f'<g stroke="{YELLOW}" stroke-opacity=".15" fill="none" stroke-width="2"><path d="M30 100h100l45 45h235m-370 350h160l50-50h185M970 70v90l60 60v230l100 100m-120-210h100l50-50"/><rect x="870" y="235" width="100" height="120" rx="8"/><circle cx="410" cy="145" r="5"/><circle cx="435" cy="445" r="5"/></g>']
    o += [text('FABIAN / PERSONAL INTERFACE',42,40,14,MUTED,600),text('STRATEGY ↔ TECHNOLOGY',884,40,14,MUTED,600)]
    o += window(35,68,1130,541,'profile.exe / from strategy to solutions')
    o += [f'<g fill="none" stroke="{YELLOW}" stroke-opacity=".16" stroke-width="1.5"><rect x="941" y="298" width="96" height="74" rx="12"/><rect x="952" y="309" width="74" height="52" rx="6"/><path d="M941 319h-42l-27-27h-48m117 49h-27l-30 30h-70m223-52h36l36-36m-72 59h46l26 26M969 298v-35h50v-26m-29 135v38h82"/><circle cx="824" cy="292" r="4"/><circle cx="814" cy="371" r="4"/><circle cx="1072" cy="410" r="4"/></g>']
    o += [logo('ibs',916,139,77),text('DATA SCIENCE · AI · BUSINESS',76,169,16,YELLOW,600),text('Fabian Langer',70,260,80,CREAM,300),text('From strategy to solutions.',76,315,34,CREAM,300)]
    o += [text('Lead Data Science & AI Consultant',77,383,24,CREAM,600),text('@ Isatis Business Solutions',77,418,22,MUTED)]
    o += [rect(76,450,1048,1,HIGH,0),text('AI Trainer @ CIU',77,495,22,CREAM),text('Business Analist Digitalisering & AI @ Enexis',77,534,22,CREAM),text('CLIENT ASSIGNMENT VIA IBS',77,570,13,YELLOW,600)]
    o += [text('> computer_science → data_science → business_impact',42,638,16,MUTED)]
    save('profile.svg',o)

def button(name,title,subtitle,primary=False,icon='web'):
    o=start(580,140,title,subtitle)
    o += [rect(2,2,576,136,'url(#metal)',18),rect(5,5,570,130,YELLOW if primary else SURFACE,15),rect(8,8,564,124,'url(#glass)',13)]
    c=BG if primary else CREAM; sub='#454137' if primary else MUTED
    if icon=='in':
        o += [rect(27,39,56,56,c,7),text('in',37,81,33,YELLOW if primary else SURFACE,600)]
    else:
        o += [f'<g fill="none" stroke="{c}" stroke-width="2"><circle cx="55" cy="68" r="23"/><ellipse cx="55" cy="68" rx="10" ry="23"/><path d="M32 68h46M36 55h38M36 81h38"/></g>']
    o += [text(title,106,63,25,c,600),text(subtitle,107,96,17,sub),f'<path d="M521 47h20v20m-21 0 21-20" stroke="{c}" stroke-width="2" fill="none"/>']
    save(name,o)

def timeline():
    o=start(1200,2460,'Experience | Consultancy and client assignments','Newest assignments first, grouped under IBS and Wiconic. CIU and NISI are independent parallel roles. Spacing is not proportional to time.')
    o += [text('EXPERIENCE / REVERSE CHRONOLOGICAL',44,58,15,YELLOW,600),text('One career. Many contexts.',42,114,43,CREAM,300),text('Consultancy & client assignments',44,160,20,MUTED),text('PARALLEL ROLES',883,160,15,MUTED,600)]
    # Main consultancy umbrella.
    o += [rect(38,195,791,221,'url(#metal)',18),rect(40,197,787,217,SURFACE,16),logo('ibs',68,222,52),text('Isatis Business Solutions',225,246,29,CREAM,400),text(D['ibs']['period'],225,279,18,YELLOW)]
    for i,r in enumerate(D['ibs']['roles']): o += [text(r,70,323+i*30,18,MUTED)]
    o += [f'<path d="M67 443V1591" stroke="{YELLOW}" stroke-width="3" fill="none"/>']
    ys=[443,630,817,1004,1191,1378,1815,2002]
    for a,y in zip(D['assignments'],ys):
        o += [f'<circle cx="67" cy="{y+29}" r="7" fill="{YELLOW}"/>',rect(95,y,734,174,SURFACE,20),rect(95,y,734,174,'url(#glass)',20),logo(a['logo'],117,y+23,58),text(a['company'],195,y+47,27,CREAM,400),text(a['period'],195,y+78,17,YELLOW),text(a['role'],118,y+108,18,MUTED)]
        body,end=lines(a['summary'],118,y+135,682,18,CREAM,leading=24)
        o += [body]
    # Dotted tracks represent the full role period, independently of card height.
    # CIU: present down to Jul 2024 (between Rabobank and Gasunie).
    # NISI: Oct 2021 transition down to the Oct 2017 career start.
    for p,y,h,top,bottom,newest,oldest in [
        (D['parallel'][0],225,392,195,790,'PRESENT','JUL 2024'),
        (D['parallel'][1],1815,390,1591,2244,'OCT 2021','OCT 2017'),
    ]:
        o += [f'<path d="M861 {top}V{bottom}" stroke="{MUTED}" stroke-opacity=".65" stroke-dasharray="5 8" stroke-width="2"/>',
              f'<circle cx="861" cy="{top}" r="5" fill="{MUTED}"/><circle cx="861" cy="{bottom}" r="5" fill="{MUTED}"/>',
              text(newest,881,top+7,14,MUTED,600),text(oldest,881,bottom+7,14,MUTED,600),
              rect(881,y,281,h,'#202020',18),logo(p['logo'],902,y+22,55)]
        body,end=lines(p['company'],902,y+112,238,22,CREAM,weight=400,leading=29);o += [body]
        body,end=lines(p['period'],902,end+10,238,17,MUTED,leading=25);o += [body]
        o += [text(p['role'],902,end+16,18,CREAM)]
        body,end=lines(p['summary'],902,end+53,237,18,MUTED,leading=28);o += [body]
    # Employer transition: Respectzorg is explicitly represented on both sides.
    o += [rect(38,1591,791,201,'url(#metal)',18),rect(40,1593,787,197,SURFACE,16),logo('wiconic',68,1617,64),text('Wiconic',155,1648,30,CREAM),text(D['wiconic']['period'],155,1682,18,YELLOW)]
    for i,r in enumerate(D['wiconic']['roles']):o += [text(r,70,1730+i*30,18,MUTED)]
    o += [f'<path d="M67 1815v390" stroke="{YELLOW}" stroke-width="3" fill="none"/>',text('Respectzorg continued at IBS from Oct 2021.',97,1565,17,MUTED),text('CAREER START / OCT 2017',95,2244,15,YELLOW,600)]
    o += [text('Client assignments may overlap. Parallel roles sit outside the consultancy umbrellas.',44,2410,17,MUTED),text('Ordered by assignment start date within each consultancy; spacing is not to scale.',44,2441,17,MUTED)]
    save('experience.svg',o)

def education():
    o=start(1200,804,'Education & continued learning','MIT xPRO AI Strategy and Leadership, issued September 2025. Master Information Studies, Data Science at University of Amsterdam, 2019 to 2020. Bachelor Computer Science and Gametechnology at Utrecht University, 2014 to 2019.')
    o += [text('EDUCATION / CONTINUED LEARNING',44,55,15,YELLOW,600),text('A technical foundation. A wider perspective.',42,111,39,CREAM,300),f'<path d="M76 159v550" stroke="{HIGH}" stroke-width="3"/>']
    for e,y in zip(D['education'],[149,372,574]):
        h=201 if e['logo']=='mit' else 180
        o += [f'<circle cx="76" cy="{y+34}" r="7" fill="{YELLOW}"/>',rect(109,y,1049,h,SURFACE,20),logo(e['logo'],134,y+27,64),text(e['company'],224,y+48,25,CREAM),text(e['period'],224,y+81,18,YELLOW),text(e['title'],135,y+126,25,CREAM,300)]
        offset=0
        if e['subtitle']:o += [text(e['subtitle'],135,y+156,19,MUTED)]; offset=30
        o += [text(e['summary'],135,y+160+offset,18,MUTED)]
    save('education.svg',o)

def readme():
    md='''<a href="https://www.fabianlanger.nl/">
  <img src="assets/profile.svg" width="100%" alt="Fabian Langer — Lead Data Science &amp; AI Consultant at Isatis Business Solutions; AI Trainer at CIU; Business Analist Digitalisering &amp; AI at Enexis, via IBS." />
</a>

<p align="center">
  <a href="https://www.linkedin.com/in/fabian--langer/"><img src="assets/linkedin-button.svg" width="48%" alt="Open LinkedIn — experience, ideas and conversations" /></a>
  <a href="https://www.fabianlanger.nl/"><img src="assets/website-button.svg" width="48%" alt="Visit fabianlanger.nl — projects, speaking and AI expertise" /></a>
</p>

'''+D['intro']+'''

Explore my work and speaking on **[fabianlanger.nl](https://www.fabianlanger.nl/)**, or connect on **[LinkedIn](https://www.linkedin.com/in/fabian--langer/)** for experience, ideas and conversations about AI in practice.

<img src="assets/experience.svg" width="100%" alt="Career timeline, newest first: IBS since October 2021, with Enexis, Rabobank, Gasunie, Landscape AI / Univé, NIPV and the Respectzorg continuation; Wiconic from October 2017 to October 2021, with Respectzorg and VOGSY. CIU and NISI are separate parallel roles." />

<img src="assets/education.svg" width="100%" alt="Education: MIT xPRO AI Strategy and Leadership certificate, September 2025; Master Information Studies: Data Science, University of Amsterdam, 2019–2020; BSc Computer Science / Gametechnology, Utrecht University, 2014–2019." />

<details>
<summary>Experience & education · text version</summary>

### Isatis Business Solutions · '''+D['ibs']['period']+'\n\n'
    md+='\n'.join('- '+r for r in D['ibs']['roles'])+'\n\n'+D['ibs']['summary']+'\n\n**Client assignments via IBS**\n\n'
    for a in D['assignments']:
        if a['umbrella']=='IBS':md+=f"- **{a['company']} · {a['period']}** — {a['role']}. {a['summary']}\n"
    md+='\n### Wiconic · '+D['wiconic']['period']+'\n\n'+'\n'.join('- '+r for r in D['wiconic']['roles'])+'\n\n**Client assignments via Wiconic**\n\n'
    for a in D['assignments']:
        if a['umbrella']=='Wiconic':md+=f"- **{a['company']} · {a['period']}** — {a['role']}. {a['summary']}\n"
    md+='\nRespectzorg ran from March 2020 to December 2021, moving with me from Wiconic to IBS in October 2021.\n\n### Parallel roles\n\n'
    for p in D['parallel']:md+=f"- **{p['company']} · {p['period']}** — {p['role']}. {p['summary']}\n"
    md+='\n### Education & continued learning\n\n'
    for e in D['education']:md+=f"- **{e['company']} · {e['period']}** — {e['title']}{': '+e['subtitle'] if e['subtitle'] else ''}.\n"
    md+='\n</details>\n'
    (ROOT/'README.md').write_text(md,encoding='utf-8')

if __name__=='__main__':
    hero();button('linkedin-button.svg','Open LinkedIn','Experience, ideas & conversations',True,'in')
    button('website-button.svg','Visit fabianlanger.nl','Projects, speaking & AI expertise')
    timeline();education();readme()
    print('Built five SVG assets and README.md.')
