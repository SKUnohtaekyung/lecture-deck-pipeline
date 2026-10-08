import pickle,os,collections
out=pickle.load(open(os.path.join(os.path.dirname(__file__),"measure.pkl"),"rb"))
print("sid|start|model|first|humanN|slash|mainCalls|mainIn(M)|subN|subCalls|subIn(M)|Agent|Skill|course|rereadMain|rereadSub|compact")
for (tag,sid),(M,S) in out.items():
    if tag!="NEW": continue
    c=M["course"].most_common(2)
    print("|".join(map(str,[sid,(min(M["ts"]) if M["ts"] else "")[:10],(M["model"] or "").replace("claude-",""),M["first"],len(M["human"]),dict(M["slash"]),M["calls"],round(M["inp"]/1e6,1),S["n"],S["calls"],round(S["inp"]/1e6,1),sum(M["agent"].values()),dict(M["skill"]),c,sum(1 for p,k in M["reads"].items() if k>=3),S["rereads"],M["compact"]])))
print("\n== Agent types per session")
for (tag,sid),(M,S) in out.items():
    if tag=="NEW" and M["agent"]: print(sid,dict(M["agent"]))
print("\n== hook ctx (count/chars) & hook_success by (event,mode,hasStdout)")
for (tag,sid),(M,S) in out.items():
    if tag=="NEW": print(sid,dict(M["hookctx"]),dict(M["hookchars"]),"|",{f"{k[0][:4]}:{k[1]}:{'out' if k[2] else 'empty'}":v for k,v in M["hooksucc"].items()})
print("\n== start attachments chars")
for (tag,sid),(M,S) in out.items():
    if tag=="NEW": print(sid,M["start_att"],"instr:",M["instr_files"])
print("\n== sub skills / sub Skill tool")
for (tag,sid),(M,S) in out.items():
    if tag=="NEW" and (S["skill"] or S["n"]): print(sid,"subSkill",dict(S["skill"]),"subFirst median",sorted(S["first"])[len(S["first"])//2] if S["first"] else None)
