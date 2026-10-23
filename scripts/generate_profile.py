#!/usr/bin/env python3
"""Build GitHub-safe SVG profile panels. Standard library only.

Offline:  python scripts/generate_profile.py --offline
Live:     GH_TOKEN=... python scripts/generate_profile.py --live

All claims that can change (stars, streak, contributions, article listings)
are fetched live; the offline design deliberately uses placeholders rather than
manufacturing numbers.
"""
from __future__ import annotations

import argparse
import base64
from datetime import date, timedelta
import html
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
USER = 'nguyendao16'
SITE = 'https://nguyendao16.github.io'
GH_API = 'https://api.github.com'
BG = '#0d1117'
CARD = '#151b23'
BORDER = '#30363d'
WHITE = '#f0f6fc'
MUTED = '#9198a1'
ACCENT = '#f78136'
BLUE = '#58a6ff'
GREEN = '#3fb950'
FONT = "'DejaVu Sans',Arial,Helvetica,sans-serif"


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def svg_doc(width: int, height: int, inner: str, title: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">'
            f'<title>{escape(title)}</title>{inner}</svg>\n')


def box(x, y, width, height, radius=12, fill=CARD, stroke=BORDER, sw=1):
    return (f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def tx(x, y, text, size=16, color=WHITE, weight=400, anchor=None, opacity=None):
    opts = f' text-anchor="{anchor}"' if anchor else ''
    opts += f' opacity="{opacity}"' if opacity is not None else ''
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-family="{FONT}" font-weight="{weight}"{opts}>{escape(text)}</text>')


def make_hero():
    s = box(0.5, 0.5, 919, 166, 15, BG, BORDER)
    s += '<rect x="1" y="1" width="6" height="165" rx="3" fill="#f78136"/>'
    s += '<circle cx="845" cy="31" r="6" fill="#f78136"/><circle cx="867" cy="31" r="6" fill="#1f9cf0"/><circle cx="889" cy="31" r="6" fill="#3fb950"/>'
    s += tx(28, 33, 'PROFILE  /  README.md', 12, BLUE, 700)
    s += tx(28, 87, "Hi there, I'm Khôi Nguyên!", 38, WHITE, 750)
    s += tx(29, 120, 'AI Engineering  ·  Computer Vision  ·  Natural Language Processing', 17, '#b9c1cb', 400)
    s += '<path d="M29 139H890" stroke="#30363d" stroke-width="1"/>'
    s += tx(29, 156, 'Building, studying and sharing practical machine learning systems.', 11, MUTED)
    return svg_doc(920, 167, s, 'Introduction — Khôi Nguyên, AI Engineering, Computer Vision and NLP')


def make_skills():
    rows = [
        [('Python','#3776AB','Py'),('PyTorch','#EE4C2C','PT'),('TensorFlow','#EF6C00','TF'),
         ('Hugging Face','#D89B00','HF'),('OpenCV','#455A92','CV'),('scikit-learn','#F7931E','SK'),
         ('Transformers','#9065C0','TR'),('NumPy','#4D77AB','NP')],
        [('Pandas','#5A5FB9','PD'),('Git','#F05032','GT'),('Docker','#2496ED','DK'),
         ('Linux','#666666','LX'),('GitHub Actions','#2671E5','GH'),('Astro','#E04C84','AS'),
         ('LangGraph','#327B70','LG'),('Tailwind CSS','#169EC0','TW')],
    ]
    s = box(0.5, 0.5, 919, 105, 12, BG, BORDER)
    for row_num, tags in enumerate(rows):
        x = 15
        y = 14 + 44 * row_num
        for label, color, abbreviation in tags:
            w = min(155, 40 + len(label) * 7.0)
            s += f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="34" rx="6" fill="{color}"/>'
            s += f'<rect x="{x+4:.1f}" y="{y+6}" width="22" height="22" rx="5" fill="#0d1117" fill-opacity="0.24"/>'
            s += tx(x+15, y+21, abbreviation, 9, '#ffffff', 700, 'middle')
            s += tx(x+32, y+22, label, 11.5, '#ffffff', 650)
            x += w + 9
    return svg_doc(920, 106, s, 'Technology stack badges')


PROJECTS = [
    dict(filename='project-hana.svg', title='Hana · AI Friend',
         lines=['Voice-enabled AI companion built', 'with LangGraph and memory.'],
         tags=['Python','LangGraph','Redis'], icon='hana',
         url='https://github.com/nguyendao16/hana-bot-langgraph', repo='hana-bot-langgraph', accent='#58a6ff'),
    dict(filename='project-portfolio.svg', title='AI CV Portfolio',
         lines=['Personal AI / CV portfolio and', 'technical blog powered by Astro.'],
         tags=['Astro','TypeScript','Tailwind'], icon='portfolio',
         url='https://github.com/nguyendao16/nguyendao16.github.io', repo='nguyendao16.github.io', accent='#f78136'),
    dict(filename='project-fpt.svg', title='FPT Stock Forecast',
         lines=['Public FPT market dashboard with', 'tracked forecast outcomes.'],
         tags=['ML','Time Series','Actions'], icon='fpt',
         url='https://nguyendao16.github.io/', repo=None, accent='#b987ff'),
]


def make_project(project: dict, repo_info: dict | None = None):
    s = box(.5, .5, 299, 211, 12, CARD, BORDER)
    accent = project['accent']
    s += f'<rect x="1" y="1" width="298" height="4" rx="2" fill="{accent}"/>'
    s += f'<rect x="18" y="22" width="34" height="34" rx="8" fill="{accent}" fill-opacity="0.14"/>'
    if project['icon'] == 'hana':
        for dx, dy in [(-7,0),(7,0),(0,-7),(0,7)]:
            s += f'<circle cx="{35+dx}" cy="{39+dy}" r="5.5" fill="{accent}"/>'
        s += '<circle cx="35" cy="39" r="4" fill="#f0f6fc"/>'
    elif project['icon'] == 'portfolio':
        s += f'<rect x="26" y="29" width="18" height="20" rx="2" fill="none" stroke="{accent}" stroke-width="2"/>'
        s += f'<path d="M26 34H44M30 39H40M30 43H38" stroke="{accent}" stroke-width="2"/>'
    else:
        s += f'<path d="M24 47L30 41L35 44L44 31" fill="none" stroke="{accent}" stroke-width="2.5" stroke-linejoin="round"/>'
    s += tx(60, 44, project['title'], 15.6, WHITE, 700)
    s += '<path d="M275 26h10v10m-10 0 10-10" fill="none" stroke="#8b949e" stroke-width="1.8"/>'
    for index, line in enumerate(project['lines']):
        s += tx(18, 83+index*19, line, 12.7, '#c5ccd4')
    px = 18
    for tag in project['tags']:
        w = 18 + 6.5*len(tag)
        s += f'<rect x="{px:.1f}" y="132" width="{w:.1f}" height="25" rx="5" fill="{accent}" fill-opacity="0.15" stroke="{accent}" stroke-opacity="0.19"/>'
        s += tx(px+9, 149, tag, 10.8, accent, 600)
        px += w+6
    s += '<path d="M18 171H282" stroke="#30363d"/>'
    if isinstance(repo_info, dict) and repo_info.get('stargazers_count') is not None:
        stars = int(repo_info['stargazers_count'])
        forks = int(repo_info.get('forks_count', 0))
        s += tx(18, 193, f'★  {stars}     Forks  {forks}', 11.5, MUTED, 600)
    else:
        label = 'PUBLIC DASHBOARD' if not project['repo'] else 'VIEW REPOSITORY'
        s += tx(18, 193, label, 11, MUTED, 650)
    s += tx(281, 193, '↗', 15, accent, 700, 'end')
    return svg_doc(300, 212, s, project['title'] + ': ' + ' '.join(project['lines']))


def streaks(days: list[dict], today: date | None = None) -> tuple[int,int]:
    """Current streak may end yesterday, not before; longest within provided window."""
    today = today or date.today()
    counts = {date.fromisoformat(d['date']): int(d['contributionCount']) for d in days}
    longest, run = 0, 0
    for day in sorted(counts):
        if day > today:
            continue
        if counts[day] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0
    start = today if counts.get(today, 0) > 0 else today-timedelta(days=1)
    current = 0
    while counts.get(start, 0) > 0:
        current += 1
        start -= timedelta(days=1)
    return current, longest


def make_stats(calendar: dict | None):
    s = box(.5, .5, 419, 229, 12, CARD, BORDER)
    s += tx(20, 30, 'Contribution summary', 14, WHITE, 700)
    s += tx(20, 49, 'Last 12 months', 11, MUTED)
    s += '<path d="M20 61H400" stroke="#30363d"/>'
    if calendar:
        total = str(calendar['totalContributions'])
        ds = [day for wk in calendar['weeks'] for day in wk['contributionDays']]
        current, longest = streaks(ds)
        nums = [total, str(current), str(longest)]
        sub = ['Contributions', 'Current streak', 'Longest streak']
    else:
        nums = ['—','—','—']
        sub = ['Contributions', 'Current streak', 'Longest streak']
    for i, val in enumerate(nums):
        center = [75, 209, 346][i]
        if i == 1:
            s += '<circle cx="209" cy="123" r="49" fill="none" stroke="#f78136" stroke-width="4" stroke-opacity="0.80"/>'
            s += '<path d="M209 74a49 49 0 0 1 30 10" fill="none" stroke="#ffa657" stroke-width="5" stroke-linecap="round"/>'
        s += tx(center, 133, val, 29, ACCENT if i==1 else WHITE, 700, 'middle')
        s += tx(center, 165, sub[i], 11.2, ACCENT if i==1 else '#c5ccd4', 600, 'middle')
    s += '<path d="M142 76V177M278 76V177" stroke="#3e454e"/>'
    s += tx(20, 207, 'Synced from GitHub' if calendar else 'Data appears after your first GitHub Action run', 10.7, MUTED)
    return svg_doc(420, 230, s, 'GitHub contribution summary with verified totals and streaks')


def make_calendar(calendar: dict | None):
    s = box(.5, .5, 479, 229, 12, CARD, BORDER)
    s += tx(19, 30, 'Contributions in the last year', 13.5, WHITE, 700)
    weeks = calendar.get('weeks', []) if calendar else []
    cell, step, x0, y0 = 6, 8, 30, 81
    levels = ['#21262d','#0e4429','#006d32','#26a641','#39d353']
    if weeks:
        # GraphQL calendar returns complete Sunday-to-Saturday weeks.
        weeklist = list(weeks)[-53:]
        for j, week in enumerate(weeklist):
            days = week['contributionDays']
            if days and j < 51:
                first = date.fromisoformat(days[0]['date'])
                if first.day <= 7:
                    s += tx(x0+j*step, 64, first.strftime('%b'), 9.2, MUTED)
            for day in days:
                wd = (date.fromisoformat(day['date']).weekday()+1)%7
                count = int(day['contributionCount'])
                lvl = 0 if count == 0 else 1 if count <= 2 else 2 if count <= 5 else 3 if count <= 9 else 4
                s += f'<rect x="{x0+j*step}" y="{y0+wd*12}" width="{cell}" height="9" rx="1.3" fill="{levels[lvl]}"/>'
    else:
        s += tx(30, 62, 'Awaiting GitHub contribution data', 10.8, MUTED)
        for j in range(53):
            for i in range(7):
                s += f'<rect x="{x0+j*step}" y="{y0+i*12}" width="{cell}" height="9" rx="1.3" fill="{levels[0]}"/>'
    for name, row in [('Mon',1),('Wed',3),('Fri',5)]:
        s += tx(7, y0+row*12+8, name, 8.5, MUTED)
    s += tx(303, 207, 'Less', 10.4, MUTED)
    for i, color in enumerate(levels):
        s += f'<rect x="{334+i*16}" y="196" width="12" height="12" rx="2" fill="{color}"/>'
    s += tx(416, 207, 'More', 10.4, MUTED)
    return svg_doc(480, 230, s, 'GitHub contribution activity heatmap for the last year')


def request_json(url, token, *, post=None):
    headers = {'Accept':'application/vnd.github+json', 'User-Agent':'nguyendao16-profile-readme',
               'X-GitHub-Api-Version':'2022-11-28'}
    if token:
        headers['Authorization'] = 'Bearer ' + token
    payload = None
    if post is not None:
        headers['Content-Type'] = 'application/json'
        payload = json.dumps(post).encode('utf-8')
    with urlopen(Request(url, data=payload, headers=headers), timeout=18) as response:
        return json.loads(response.read().decode('utf-8'))


def fetch_calendar(token: str):
    if not token:
        raise ValueError('GH_TOKEN is required for contribution-calendar GraphQL API')
    query = '''query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks { contributionDays { date contributionCount } }
          }
        }
      }
    }'''
    obj = request_json('https://api.github.com/graphql', token,
                       post={'query':query,'variables':{'login':USER}})
    if obj.get('errors'):
        raise RuntimeError('GitHub GraphQL returned errors: ' + str(obj['errors'])[:200])
    return obj['data']['user']['contributionsCollection']['contributionCalendar']


def fetch_repo_info(token: str, name: str):
    return request_json(f'{GH_API}/repos/{USER}/{name}', token)


def parse_article_frontmatter(source: str, path: str):
    m = re.match(r'\A\s*---\s*\n(.*?)\n---\s*\n', source, re.DOTALL)
    if not m:
        return None
    meta = m.group(1)
    def val(key):
        mm = re.search(r'^'+re.escape(key)+r':\s*(.+)$',meta, re.MULTILINE)
        return mm.group(1).strip().strip('"\'') if mm else None
    if (val('draft') or '').lower() in ('true', 'yes'):
        return None
    title = val('title')
    pubdate = val('date') or val('pubDate') or val('publishedDate')
    if not title or not pubdate:
        return None
    published = pubdate[:10]
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',published):
        return None
    try:
        date.fromisoformat(published)
    except ValueError:
        return None
    slug = str(Path(path).relative_to('src/content/blog/')).rsplit('.',1)[0]
    if slug.endswith('/index'):
        slug = slug[:-len('/index')]
    url = SITE+'/blog/'+slug.strip('/')+'/'
    return {'title':title, 'date':published,'url':url}


def fetch_articles(token: str):
    # Git Trees provides all paths at once, including projects and nested posts.
    tree = request_json(f'{GH_API}/repos/{USER}/{USER}.github.io/git/trees/main?recursive=1',token)
    paths = [e['path'] for e in tree.get('tree', [])
             if e.get('type') == 'blob' and e.get('path','').startswith('src/content/blog/')
             and e['path'].endswith(('.md','.mdx'))]
    rows = []
    for path in paths[:90]:
        data = request_json(f'{GH_API}/repos/{USER}/{USER}.github.io/contents/{path}?ref=main',token)
        if data.get('encoding') != 'base64':
            continue
        content = base64.b64decode(data['content']).decode('utf8',errors='replace')
        entry = parse_article_frontmatter(content,path)
        if entry and entry['date'] <= date.today().isoformat():
            rows.append(entry)
    return sorted(rows,key=lambda e:(e['date'],e['title']), reverse=True)[:3]


def write_articles(articles: list[dict]):
    readme = ROOT/'README.md'
    content = readme.read_text(encoding='utf8')
    start, end = '<!-- ARTICLES:START -->', '<!-- ARTICLES:END -->'
    if start not in content or end not in content:
        raise ValueError('Article markers missing from README.md')
    if not articles:
        return False
    rows = ['| Article | Published |', '| :-- | --: |']
    for item in articles:
        title = item['title'].replace('|','\\|').replace('[','\\[').replace(']','\\]')
        url = item['url']
        rows.append(f'| 📄 [{title}]({url}) | {item["date"]} |')
    out = content.split(start,1)[0] + start + '\n' + '\n'.join(rows) + '\n' + end + content.split(end,1)[1]
    if out != content:
        readme.write_text(out,encoding='utf8')
        return True
    return False


def save_asset(filename: str, svg: str):
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS/filename
    if not p.exists() or p.read_text(encoding='utf8') != svg:
        p.write_text(svg,encoding='utf8')
        print('Rendered', p.relative_to(ROOT))


def main():
    ap = argparse.ArgumentParser()
    p = ap.add_mutually_exclusive_group(required=True)
    p.add_argument('--offline',action='store_true',help='Make static art and honest placeholder metrics')
    p.add_argument('--live',action='store_true',help='Use GitHub API for metrics and latest articles')
    args = ap.parse_args()
    token = os.getenv('GH_TOKEN', '')
    save_asset('hero.svg', make_hero())
    save_asset('tech-stack.svg', make_skills())
    for project in PROJECTS:
        repo_data = None
        if args.live and project.get('repo'):
            try:
                repo_data = fetch_repo_info(token,project['repo'])
            except (HTTPError,URLError,TimeoutError,KeyError) as e:
                print('Repository metrics unavailable:', project['repo'], str(e), file=sys.stderr)
        save_asset(project['filename'],make_project(project,repo_data))
    calendar = None
    if args.live:
        try:
            calendar = fetch_calendar(token)
        except (HTTPError,URLError,TimeoutError,KeyError,ValueError,RuntimeError) as e:
            print('Contribution update unavailable; preserving any existing cached SVG:',str(e),file=sys.stderr)
    if calendar or args.offline or not (ASSETS/'stats.svg').exists():
        save_asset('stats.svg', make_stats(calendar))
        save_asset('contributions.svg', make_calendar(calendar))
    if args.live:
        try:
            posts = fetch_articles(token)
            if posts:
                write_articles(posts)
                print('Updated newest articles:',len(posts))
            else:
                print('No published articles found; keeping existing links')
        except (HTTPError,URLError,TimeoutError,KeyError,ValueError,RuntimeError) as e:
            print('Article listing unavailable; preserving existing README:',str(e),file=sys.stderr)

if __name__ == '__main__':
    main()
