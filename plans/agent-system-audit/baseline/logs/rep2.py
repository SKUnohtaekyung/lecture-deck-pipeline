import pickle,os,collections,re
out=pickle.load(open(os.path.join(os.path.dirname(__file__),"measure.pkl"),"rb"))
FR=("0b1569d9","c93120d9","b6e30e2b"); AC=("2f7e8a36","671720eb","32f8c13f","3ee8fe9a","b2dd90d0","44015b3c")
print("== re-reads: main(any>=3 / full>=3) ; sub(any>=3 / full>=3 / full>=2)")
for (tag,sid),(M,S) in out.items():
    if tag=="NEW": print(sid, sum(1 for p,k in M["reads"].items() if k>=3), sum(1 for p,k in M["readfull"].items() if k>=3), "|", S["rereads"], S.get("rf",0), S.get("rf2",0))
for name,grp in(("FRAME",FR),("AC3",AC)):
    b=collections.Counter(); ed=collections.Counter(); rd=collections.Counter(); tools=collections.Counter()
    for (tag,sid),(M,S) in out.items():
        if tag=="NEW" and sid in grp:
            b+=M["bash"]; tools+=M["tools"]
            for p,k in M["edit"].items():
                key="shard part-*" if re.search(r"강의덱\.초안/part-",p) else "shell.html" if p.endswith("shell.html") else "강의덱*.html" if re.search(r"/강의덱[^/]*\.html$",p) else "tmp/" if "/tmp/" in p else "plans/" if "/plans/" in p else "MEMORY" if "MEMORY.md" in p else "courses other" if "/courses/" in p else "other"
                ed[key]+=k
            for p,k in M["reads"].items():
                for key in("MEMORY.md","AGENTS.md","skills/하네스","skills/리서치","skills/검토","/SKILL.md","references/phases","검증-명령-지도","PLAN.md","PROGRESS.md","재개_인계","profile.md","kit/guide"):
                    if key in p: rd[key]+=k
    print("\n==",name,"tools:",tools.most_common(14))
    print(" bash scripts top:",b.most_common(28))
    print(" edit targets:",dict(ed)); print(" key reads(main):",dict(rd))
print("\n== MEMORY.md reads per session (main: total/full)")
for (tag,sid),(M,S) in out.items():
    if tag=="NEW":
        t=sum(k for p,k in M["reads"].items() if "MEMORY.md" in p); f=sum(k for p,k in M["readfull"].items() if "MEMORY.md" in p)
        st=sum(k for p,k in S["reads"].items() if "MEMORY.md" in p); sh=sum(k for p,k in S["reads"].items() if "skills/" in p and "SKILL.md" in p)
        print(sid,t,f,"sub MEMORY reads",st,"sub skill-doc reads",sh)
print("\n== OLD dir by month: sessions, human, mainCalls, Agent calls, Skill calls, slash, hookctx, harness/리서치/검토 SKILL reads")
agg=collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
for (tag,sid),(M,S) in out.items():
    if tag!="OLD" or not M["ts"]: continue
    mo=min(M["ts"])[:7]; a=agg[mo]
    a["n"]["sessions"]+=1; a["n"]["human"]+=len(M["human"]); a["n"]["calls"]+=M["calls"]; a["n"]["subcalls"]+=S["calls"]; a["n"]["agent"]+=sum(M["agent"].values())
    a["skill"]+=M["skill"]; a["skill"]+=collections.Counter({"(sub)"+str(k):v for k,v in S["skill"].items()}); a["slash"]+=M["slash"]; a["hook"]+=M["hookctx"]
    a["agentT"]+=collections.Counter({k[0]:v for k,v in M["agent"].items()})
    a["model"][(M["model"] or "").replace("claude-","")]+=1
    for src in(M["reads"],S["reads"]):
        for p,k in src.items():
            for key in("skills/하네스","skills/리서치","skills/검토","ui-ux-pro-max"):
                if key in p: a["docread"][key]+=k
    for s,k in M["bash"].items():
        if "search.py" in s: a["docread"]["bash search.py"]+=k
for mo in sorted(agg):
    a=agg[mo]; print(mo,dict(a["n"]),"\n   models",dict(a["model"]),"\n   skill",dict(a["skill"]),"\n   slash",dict(a["slash"]),"\n   hook",dict(a["hook"]),"\n   agents",a["agentT"].most_common(8),"\n   docreads",dict(a["docread"]))
