import json, sys, urllib.request
d=json.load(open(sys.argv[1],encoding='utf-8')); want=dict(a.split('=') for a in sys.argv[2:])
cred=[]; done=set()
for rows in d.values():
    for v in rows:
        k=str(v['id'])
        if k in want and k not in done:
            done.add(k); name=want[k]+'.mp4'
            open('src_'+name,'wb').write(urllib.request.urlopen(urllib.request.Request(v['file'],headers={'User-Agent':'Mozilla/5.0'}),timeout=180).read())
            cred.append({'id':v['id'],'file':name,'author':v['user'],'page':v['page']}); print(name,v['w'],v['h'],v['dur'])
json.dump(cred,open('creditos_'+sys.argv[1],'w',encoding='utf-8'),indent=1,ensure_ascii=False)
