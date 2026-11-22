"""Build the static guide library and matching PDFs. Requires reportlab."""
from pathlib import Path
import json, html, re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'guides'
data=json.loads((OUT/'content.json').read_text()); e=html.escape
DATE='November 22, 2026'
def shell(title,desc,body,slug=''):
 url='https://sarahforrestai.com/guides/'+slug
 return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | Sarah Forrest</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{url}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:type" content="website"><link rel="stylesheet" href="/guides/style.css"></head><body><a class="skip" href="#main">Skip to content</a><header class="top"><a class="brand" href="/">Sarah Forrest<span>AI · work · things worth building</span></a><nav aria-label="Main"><a href="/guides/">Free guides</a><a href="https://sarforre.substack.com/">Newsletter ↗</a></nav></header>{body}<footer><span>© 2026 Sarah Forrest</span><a href="/">Back to my website ↗</a></footer><script src="/guides/script.js" defer></script></body></html>'''
def card(g,i):
 return f'''<a class="card" href="{g['slug']}.html"><div class="card-top"><span>{e(g['format'])}</span><span>{i:02}</span></div><h3>{e(g['title'])}</h3><p>{e(g['outcome'])}</p><span class="card-bottom">Read the guide <span aria-hidden="true">↗</span></span></a>'''
body='''<main id="main"><section class="library-hero"><p class="eyebrow">THE FREE GUIDE LIBRARY</p><h1>Learn, work<br>and <em>build with AI.</em></h1><p class="intro">Practical guides for a changing working life. Start with a question, try something small, and make it your own.</p><div class="hero-bottom"><span>By Sarah Forrest · Computer scientist & educator</span><a href="#start-here">Find your starting point ↓</a></div></section><div class="library-content"><nav class="categories" aria-label="Guide categories"><a href="#start-here">01 / Start here</a><a href="#build-something">02 / Build something</a><a href="#understand">03 / Understand what’s changing</a></nav>'''
for cat,anchor,desc in [('Start here','start-here','One useful task. A clear place to begin.'),('Build something','build-something','Turn a recurring problem or a small idea into an experiment.'),('Understand what’s changing','understand','Read the evidence. Ask questions that connect things.')]:
 body+=f'<section class="collection" id="{anchor}"><div class="section-title"><h2>{e(cat)}</h2><p>{e(desc)}</p></div><div class="cards">'+''.join(card(g,i+1) for i,g in enumerate(data) if g['category']==cat)+'</div></section>'
body+='''<section class="newsletter"><p class="eyebrow">KEEP EXPLORING</p><h2>A field note for your inbox.</h2><p>Follow my experiments with AI, tiny tech and the future of work on Substack.</p><a class="button" href="https://sarforre.substack.com/">Explore the newsletter ↗</a><p class="small">Every guide here is free to read and download. No signup needed.</p></section></div></main>'''
(OUT/'index.html').write_text(shell('Free guides','Practical guides to AI, building useful tools and understanding the future of work.',body))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='GuideTitle',fontName='Times-Roman',fontSize=30,leading=34,spaceAfter=18,textColor=HexColor('#151b25')))
styles.add(ParagraphStyle(name='GuideBody',fontName='Helvetica',fontSize=10,leading=15,spaceAfter=10,textColor=HexColor('#303d4c')))
styles.add(ParagraphStyle(name='GuideHead',fontName='Times-Roman',fontSize=18,leading=22,spaceBefore=12,spaceAfter=8,keepWithNext=True))
styles.add(ParagraphStyle(name='GuidePrompt',fontName='Courier',fontSize=8,leading=12,backColor=HexColor('#edf3fc'),borderPadding=10,spaceBefore=8,spaceAfter=14))
def pdftext(s):
 return e(s).replace('’',"'").replace('“','&quot;').replace('”','&quot;').replace('–','-').replace('—','-')
def footer(c,doc):
 c.setStrokeColor(HexColor('#b8c9df'));c.line(48,42,564,42);c.setFont('Helvetica',8);c.setFillColor(HexColor('#42546b'));c.drawString(48,28,'SARAH FORREST / FREE GUIDES');c.drawRightString(564,28,str(doc.page))
for idx,g in enumerate(data):
 meta=f'{g["category"]} · {g["format"]}'
 b=f'<main id="main" class="article"><a class="back" href="/guides/">← All guides</a><header class="article-head"><p class="eyebrow">{e(meta)}</p><h1>{e(g["title"])}</h1><p class="intro">{e(g["intro"])}</p><p class="byline">By Sarah Forrest · Updated {DATE}</p><a class="button" href="downloads/{g["slug"]}.pdf" download>Download the PDF ↓</a></header><aside class="takeaway"><strong>What you’ll leave with</strong><p>{e(g["outcome"])}</p></aside><div class="article-body">'
 flow=[Paragraph('SARAH FORREST / '+e(g['format'].upper()),styles['GuideBody']),Paragraph(pdftext(g['title']),styles['GuideTitle']),Paragraph(pdftext(g['intro']),styles['GuideBody']),Paragraph('Updated '+DATE,styles['GuideBody']),Paragraph('<b>What you will leave with</b><br/>'+pdftext(g['outcome']),styles['GuideBody'])]
 for s in g['sections']:
  b+=f'<section><h2>{e(s["title"])}</h2>'
  flow.append(Paragraph(pdftext(s['title']),styles['GuideHead']))
  if s.get('text'):
   b+='<p>'+e(s['text'])+'</p>';flow.append(Paragraph(pdftext(s['text']),styles['GuideBody']))
  if s.get('bullets'):
   b+='<ul>'+''.join('<li>'+e(x)+'</li>' for x in s['bullets'])+'</ul>'
   flow.extend(Paragraph('• '+pdftext(x),styles['GuideBody']) for x in s['bullets'])
  if s.get('prompt'):
   b+='<div class="prompt"><button type="button" class="copy">Copy text</button><pre>'+e(s['prompt'])+'</pre></div>'
   flow.append(Paragraph(pdftext(s['prompt']).replace('\n','<br/>'),styles['GuidePrompt']))
  b+='</section>'
 if g.get('sources'):
  b+='<section class="sources"><h2>Sources & further reading</h2><ul>'
  flow.append(Paragraph('Sources & further reading',styles['GuideHead']))
  for label,url in g['sources']:
   b+=f'<li><a href="{e(url)}">{e(label)} ↗</a></li>'
   flow.append(Paragraph(f'<link href="{e(url)}" color="#285392">{pdftext(label)}</link>',styles['GuideBody']))
  b+='</ul></section>'
 nextg=data[(idx+1)%len(data)]
 b+=f'</div><aside class="next"><p class="eyebrow">KEEP GOING</p><a href="{nextg["slug"]}.html">{e(nextg["title"])} →</a></aside></main>'
 (OUT/(g['slug']+'.html')).write_text(shell(g['title'],g['intro'],b,g['slug']+'.html'))
 flow.extend([Spacer(1,4),Paragraph(f'<link href="https://sarahforrestai.com/guides/{g["slug"]}.html" color="#285392">Read this guide online</link> | sarahforrestai.com/guides',styles['GuideBody'])])
 SimpleDocTemplate(str(OUT/'downloads'/(g['slug']+'.pdf')),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=48,bottomMargin=60,title=g['title'],author='Sarah Forrest').build(flow,onFirstPage=footer,onLaterPages=footer)
print('Built',len(data),'guides, PDFs and library index')
