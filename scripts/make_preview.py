"""Local PNG preview only; GitHub itself renders README.md/SVG."""
from pathlib import Path
from io import BytesIO
import cairosvg
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
W=1018
canvas=Image.new('RGB',(W,1150),'#0d1117')
d=ImageDraw.Draw(canvas)
fonts=['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf']
fb='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
regular=next(x for x in fonts if Path(x).exists())
titlefont=ImageFont.truetype(fb,22)
small=ImageFont.truetype(regular,13)

def title(label,y,right=None):
    d.text((49,y),label,font=titlefont,fill='#f0f6fc')
    if right:
        bb=d.textbbox((0,0),right,font=small)
        d.text((968-(bb[2]-bb[0]),y+8),right,font=small,fill='#58a6ff')

def paste(svg_name,rect,scale=1):
    f=root/'assets'/svg_name
    png=cairosvg.svg2png(url=str(f),output_width=rect[2],output_height=rect[3])
    im=Image.open(BytesIO(png)).convert('RGBA')
    canvas.paste(im,(rect[0],rect[1]),im)

d.rounded_rectangle((20,15,998,1120), radius=13, fill='#0d1117',outline='#30363d',width=2)
d.text((48,26),'nguyendao16 / README.md',font=small,fill='#9198a1')
paste('hero.svg',(49,59,920,167))
title('Tech Stack',247)
paste('tech-stack.svg',(49,281,920,106))
title('Featured Projects',412, 'View all repositories  →')
paste('project-hana.svg',(49,446,300,212))
paste('project-portfolio.svg',(359,446,300,212))
paste('project-fpt.svg',(669,446,300,212))
title('My Recent Articles',685,'View all posts  →')
# Real links are visible in README (instead of fake article titles).
d.text((50,735),'Explore my technical notes on Machine Learning, Computer Vision and NLP',font=ImageFont.truetype(regular,15),fill='#c9d1d9')
d.text((50,761),'Published posts appear here after a GitHub Actions refresh.',font=ImageFont.truetype(regular,14),fill='#9198a1')
d.line((49,800,969,800), fill='#30363d',width=1)
title('My GitHub Contributions Summary',815)
paste('stats.svg',(49,853,420,230))
paste('contributions.svg',(489,853,480,230))
canvas.crop((0,0,W,1144)).save(root/'PREVIEW.png')
print('Saved PREVIEW.png')
