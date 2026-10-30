import json, re, sys, urllib.request, urllib.parse
key = re.search(r'PEXELS_API_KEY\s*=\s*(\S+)', open(r'C:/Users/bajoe/Downloads/FlipStudio/secretos/api-claves.txt', encoding='utf-8').read()).group(1)
out = {}
for q in sys.argv[2:]:
    url = 'https://api.pexels.com/v1/search?' + urllib.parse.urlencode({'query': q, 'orientation': 'portrait', 'per_page': 8})
    data = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'Authorization': key, 'User-Agent': 'FlipStudio-sample/1.0'}), timeout=30))
    out[q] = [{'id': p['id'], 'dur': 0, 'img': p['src']['medium'], 'file': p['src']['large2x'], 'user': p['photographer'], 'page': p['url'], 'w': p['width'], 'h': p['height']} for p in data['photos']]
    print(q, len(out[q]))
json.dump(out, open(sys.argv[1], 'w', encoding='utf-8'), indent=1)
