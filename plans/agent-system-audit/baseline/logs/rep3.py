import json,os,glob,re,collections
ROOT=r"C:\Users\miso\.claude\projects"; P=os.path.join(ROOT,"C--Users-miso-Desktop-Project-template")
print("== MEMORY.md access per main session: (tool, offset, limit, result chars)")
for f in sorted(glob.glob(os.path.join(P,"*.jsonl")),key=os.path.getmtime):
    pend={}; rows=[]; skl=None; cmds=collections.Counter()
    for line in open(f,encoding="utf-8",errors="replace"):
        if "command-name" in line:
            for c in re.findall(r"<command-name>([^<]{1,40})</command-name>",line): cmds[c]+=1
        try:d=json.loads(line)
        except: continue
        if d.get("type")=="attachment" and d["attachment"].get("type")=="skill_listing" and skl is None:
            a=d["attachment"]; skl=(a.get("skillCount"),len(a.get("content","")),a.get("content",""),a.get("names"))
        m=d.get("message") or {}
        c=m.get("content")
        if not isinstance(c,list): continue
        for x in c:
            if x.get("type")=="tool_use":
                i=x.get("input",{}) or {}; s=json.dumps(i,ensure_ascii=False)
                if "MEMORY.md" in s and x["name"] in("Read","Grep","Bash"): pend[x["id"]]=(x["name"],i.get("offset"),i.get("limit"),(i.get("pattern") or i.get("command") or "")[:50])
            elif x.get("type")=="tool_result" and x.get("tool_use_id") in pend:
                t=x.get("content"); t="".join(y.get("text","") for y in t if isinstance(y,dict)) if isinstance(t,list) else (t or "")
                rows.append(pend[x["tool_use_id"]]+(len(t),))
    sid=os.path.basename(f)[:8]
    print(sid,"total chars",sum(r[-1] for r in rows),[(r[0],r[1],r[2],r[4]) for r in rows][:8], "| cmds",dict(cmds))
    last=skl
print("\n== skill_listing (last session): count,chars",last[0],last[1])
blocks=re.split(r"\n(?=- )",last[2]); sizes=[]
for b in blocks:
    nm=b[2:].split(":")[0][:40]; sizes.append((len(b),nm))
repo=[s for s in sizes if any(k in s[1] for k in("create-slides","리서치","검토","하네스","ui-ux-pro-max"))]
print(" repo skills:",repo,"sum",sum(s[0] for s in repo)); print(" top10:",sorted(sizes,reverse=True)[:10])
print("\n== 671720eb subs: skill-doc reads by path")
cnt=collections.Counter()
for sf in glob.glob(os.path.join(P,"671720eb*","subagents","*.jsonl")):
    for line in open(sf,encoding="utf-8",errors="replace"):
        if '"Read"' not in line: continue
        for p in re.findall(r'"file_path":\s*"([^"]+SKILL\.md)"',line): cnt[p.replace("\\\\","/")[-60:]]+=1
print(cnt.most_common(8))
print("\n== FRAME path hits in ALL project log dirs, 9/28~10/01")
for dn in os.listdir(ROOT):
    for f in glob.glob(os.path.join(ROOT,dn,"*.jsonl")):
        import datetime
        mt=datetime.datetime.fromtimestamp(os.path.getmtime(f))
        if datetime.datetime(2026,9,17)<=mt<=datetime.datetime(2026,10,1,12):
            n=0
            for line in open(f,encoding="utf-8",errors="replace"):
                if "FRAME-개편" in line or "AI_에이전트_실습워크숍" in line: n+=1
            print(dn[-40:],os.path.basename(f)[:8],mt.strftime("%m-%d %H:%M"),os.path.getsize(f)//1024,"KB FRAME-lines",n)
