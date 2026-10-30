"""Search Pexels for portrait clips; prints id, size, duration, url of the best HD file and a preview image."""
import json, re, sys, os, urllib.request, urllib.parse
ORIENT=os.environ.get('ORIENT','landscape')
OUT=os.environ.get('OUT','res.json')
def OKSIZE(f):
    return (f['width']<=1920 and f['width']>=1280) if ORIENT=='landscape' else (f['width']<=1080 and f['height']>=1280)
key = re.search(r'PEXELS_API_KEY\s*=\s*(\S+)', open(r'C:/Users/bajoe/Downloads/FlipStudio/secretos/api-claves.txt', encoding='utf-8').read()).group(1)
out = {}
for q in sys.argv[1:]:
    url = 'https://api.pexels.com/videos/search?' + urllib.parse.urlencode({'query': q, 'orientation': ORIENT, 'per_page': 8, 'size': 'medium'})
    req = urllib.request.Request(url, headers={'Authorization': key, 'User-Agent': 'FlipStudio-sample/1.0'})
    data = json.load(urllib.request.urlopen(req, timeout=30))
    rows = []
    for v in data.get('videos', []):
        files = [f for f in v['video_files'] if f.get('width') and OKSIZE(f)]
        files.sort(key=lambda f: -f['height'])
        if not files: continue
        rows.append({'id': v['id'], 'dur': v['duration'], 'w': files[0]['width'], 'h': files[0]['height'], 'file': files[0]['link'], 'img': v['image'], 'user': v['user']['name'], 'page': v['url']})
    out[q] = rows
json.dump(out, open(OUT, 'w', encoding='utf-8'), indent=1)
for q, rows in out.items():
    print(q, len(rows), [(r['id'], r['dur']) for r in rows])
