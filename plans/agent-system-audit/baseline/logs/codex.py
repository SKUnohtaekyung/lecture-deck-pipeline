import glob,os,json,collections,re
for f in sorted(glob.glob(r"C:\Users\miso\.codex\sessions\**\*.jsonl",recursive=True)):
    cwd=None
    with open(f,encoding="utf-8",errors="replace") as fh:
        for i,line in enumerate(fh):
            if i>3: break
            if '"cwd"' in line:
                try:
                    d=json.loads(line); cwd=str(d.get("payload",d).get("cwd"))
                except: pass
                break
    if not cwd or not cwd.replace("\\","/").startswith("C:/Users/miso/Desktop/Project/template"): continue
    c=collections.Counter(); model=collections.Counter(); um=0
    for line in open(f,encoding="utf-8",errors="replace"):
        for k,v in(("AI_에이전트_실습워크숍","FRAME"),("바이브코딩_온라인","VO"),("AI_코딩_에이전트_입문","AC3")):
            if k in line: c[v]+=1
        m=re.search(r'"model":\s*"([^"]+)"',line)
        if m: model[m.group(1)]+=1
        if '"type":"user_message"' in line: um+=1
    print(os.path.basename(f)[8:27],os.path.getsize(f)//1024,"KB","userMsg",um,dict(c),model.most_common(2))
