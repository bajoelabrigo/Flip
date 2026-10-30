import json, urllib.request, io, sys
from PIL import Image, ImageDraw, ImageFont
d=json.load(open(sys.argv[1],encoding='utf-8')); W,H=(int(sys.argv[3]),int(sys.argv[4]))
qs=list(d.keys()); sheet=Image.new('RGB',(W*8,(H+18)*len(qs)),(20,20,20)); dr=ImageDraw.Draw(sheet); f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13)
for r,q in enumerate(qs):
    for c,v in enumerate(d[q][:8]):
        try:
            data=urllib.request.urlopen(urllib.request.Request(v['img'],headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
            sheet.paste(Image.open(io.BytesIO(data)).convert('RGB').resize((W,H)),(c*W,r*(H+18)+18))
        except Exception: pass
        dr.text((c*W+3,r*(H+18)+1),f"{r}{c} {v['id']} {v['dur']}s",fill=(255,255,0),font=f)
sheet.save(sys.argv[2],quality=80)
