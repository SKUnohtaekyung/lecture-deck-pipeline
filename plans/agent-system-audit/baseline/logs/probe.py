import json,os,collections
P=r"C:\Users\miso\.claude\projects\C--Users-miso-Desktop-Project-template"
f=os.path.join(P,"6b29a7ad-5602-404e-bb51-06ddbfc864b2.jsonl")
types=collections.Counter(); att=collections.Counter(); shown=set()
for line in open(f,encoding="utf-8",errors="replace"):
    d=json.loads(line); t=d.get("type"); types[t]+=1
    if t=="attachment":
        a=d.get("attachment",{}); att[a.get("type")]+=1
        k=("att",a.get("type"))
        if k not in shown:
            shown.add(k); print("ATT",a.get("type"),list(a.keys())[:10], len(json.dumps(a,ensure_ascii=False)))
    if t=="user":
        m=d.get("message",{}); c=m.get("content")
        kind="str" if isinstance(c,str) else "+".join(sorted({x.get("type") for x in c if isinstance(x,dict)}))
        k=("user",kind,json.dumps(d.get("origin"),ensure_ascii=False),d.get("isMeta"),d.get("isSidechain"))
        if k not in shown:
            shown.add(k); print("USER",k,[x for x in d.keys() if x not in("message",)], (c if isinstance(c,str) else json.dumps(c,ensure_ascii=False))[:160].replace("\n"," "))
    if t not in("user","assistant","attachment") and ("t",t) not in shown:
        shown.add(("t",t)); print("OTHER",t,list(d.keys())[:14], json.dumps(d,ensure_ascii=False)[:200].replace("\n"," "))
print(types); print(att)
print(os.listdir(P)[:40])
