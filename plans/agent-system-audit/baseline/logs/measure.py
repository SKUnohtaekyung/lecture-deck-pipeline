import json,os,glob,re,collections,sys
ROOT=r"C:\Users\miso\.claude\projects"
DIRS={"NEW":"C--Users-miso-Desktop-Project-template","OLD":"C--Users-miso-Desktop-template"}
COURSE={"AI_에이전트_실습워크숍_4시간":"FRAME","AI_코딩_에이전트_입문_3차시":"AC3","바이브코딩_온라인":"VO","바이브코딩":"VC"}
seen_msg=set(); seen_uuid=set()
def text_of(c):
    if isinstance(c,str): return c
    if isinstance(c,list): return "".join(x.get("text","") for x in c if isinstance(x,dict) and x.get("type")=="text")
    return ""
def scan(path,is_sub=False):
    R=dict(calls=0,inp=0,out=0,first=None,model=None,tools=collections.Counter(),skill=collections.Counter(),agent=collections.Counter(),
           reads=collections.Counter(),readfull=collections.Counter(),human=[],slash=collections.Counter(),hookctx=collections.Counter(),hookchars=collections.Counter(),
           hooksucc=collections.Counter(),start_att={},bash=collections.Counter(),course=collections.Counter(),edit=collections.Counter(),ts=[],compact=0,instr_files=None)
    msgs={}; order=[]; started=False
    for line in open(path,encoding="utf-8",errors="replace"):
        try:d=json.loads(line)
        except: continue
        t=d.get("type")
        if d.get("timestamp"): R["ts"].append(d["timestamp"])
        if t=="attachment":
            a=d.get("attachment",{}); at=a.get("type")
            if at=="hook_additional_context":
                c=json.dumps(a.get("content",a),ensure_ascii=False)
                key="course" if "과목 지침" in c else "checklist" if "사전 점검" in c else "generated" if "생성물" in c else "tmp" if ("저장소 밖" in c or "임시" in c) else "other"
                R["hookctx"][key]+=1; R["hookchars"][key]+=len(text_of(a.get("content")) or c)
            elif at=="hook_success":
                cmd=a.get("command","") or ""
                m=re.search(r"--mode (\S+)",cmd); R["hooksucc"][(a.get("hookEvent"),m.group(1) if m else "nonrepo",bool((a.get("stdout") or "").strip() not in("","{}")))]+=1
            elif not started and at in("instructions","skill_listing","agent_listing_delta","deferred_tools_delta","mcp_instructions_delta","prompt_snapshot","session_context","environment"):
                R["start_att"][at]=R["start_att"].get(at,0)+len(json.dumps(a,ensure_ascii=False))
                if at=="instructions":
                    fs=a.get("files"); 
                    try: R["instr_files"]=[(os.path.basename(str(x.get("path",x.get("file","?")))),len(json.dumps(x,ensure_ascii=False))) for x in fs]
                    except Exception as e: R["instr_files"]=str(type(fs))+str(fs)[:200]
            continue
        if t=="system" and "compact" in str(d.get("subtype","")): R["compact"]+=1
        m=d.get("message") or {}
        if t=="assistant" and m.get("usage"):
            started=True
            mid=m.get("id"); u=m["usage"]
            tot=u.get("input_tokens",0)+u.get("cache_creation_input_tokens",0)+u.get("cache_read_input_tokens",0)
            if mid in msgs:
                e=msgs[mid]; e[0]=max(e[0],tot); e[1]=max(e[1],u.get("output_tokens",0))
            else:
                msgs[mid]=[tot,u.get("output_tokens",0),m.get("model")]; order.append(mid)
            for c in m.get("content",[]) if isinstance(m.get("content"),list) else []:
                if c.get("type")!="tool_use": continue
                key=c.get("id")
                if key in seen_uuid: continue
                seen_uuid.add(key)
                n=c["name"]; i=c.get("input",{}) or {}
                R["tools"][n]+=1
                if n=="Skill": R["skill"][i.get("skill")]+=1
                if n in("Agent","Task"): R["agent"][(i.get("subagent_type") or "default", i.get("model") or "-")]+=1
                if n=="Read":
                    p=(i.get("file_path") or "").replace("\\","/"); R["reads"][p]+=1
                    if not(i.get("offset") or i.get("limit")): R["readfull"][p]+=1
                if n in("Edit","Write"): R["edit"][(i.get("file_path") or "").replace("\\","/")]+=1
                if n=="Bash":
                    cmd=i.get("command","")
                    for s in set(re.findall(r"([A-Za-z_][\w\-]*\.(?:py|js|sh))\b",cmd)): R["bash"][s]+=1
                    if re.search(r"python\d?\s+-\s*<<|python\d?\s+-c",cmd): R["bash"]["<inline python>"]+=1
                s=json.dumps(i,ensure_ascii=False)
                for k,v in COURSE.items():
                    if "courses/"+k+"/" in s.replace("\\\\","/").replace("\\","/"): R["course"][v]+=1; break
        elif t=="user" and not d.get("isSidechain") and not is_sub:
            if (d.get("origin") or {}).get("kind")=="human" and not d.get("isMeta"):
                if d.get("uuid") in seen_uuid: continue
                seen_uuid.add(d.get("uuid"))
                tx=text_of(m.get("content"))
                cm=re.search(r"<command-name>([^<]+)</command-name>",tx)
                if cm: R["slash"][cm.group(1).strip()]+=1
                elif tx.strip() and not tx.startswith("This session is being continued"): R["human"].append(tx)
    for mid in order:
        if mid in seen_msg: continue
        seen_msg.add(mid); e=msgs[mid]
        R["calls"]+=1; R["inp"]+=e[0]; R["out"]+=e[1]
    if order:
        R["first"]=msgs[order[0]][0]; R["model"]=msgs[order[0]][2]
    return R
out={}
for tag,dn in DIRS.items():
    base=os.path.join(ROOT,dn)
    files=sorted(glob.glob(os.path.join(base,"*.jsonl")),key=os.path.getmtime)
    for f in files:
        sid=os.path.basename(f)[:8]
        M=scan(f)
        subs=glob.glob(os.path.join(base,os.path.basename(f)[:-6],"subagents","*.jsonl"))
        S=dict(n=len(subs),calls=0,inp=0,out=0,rereads=0,tools=collections.Counter(),skill=collections.Counter(),reads=collections.Counter(),first=[])
        for sf in subs:
            r=scan(sf,True); S["calls"]+=r["calls"]; S["inp"]+=r["inp"]; S["out"]+=r["out"]
            S["rereads"]+=sum(1 for p,c in r["reads"].items() if c>=3); S["rf"]=S.get("rf",0)+sum(1 for p,c in r["readfull"].items() if c>=3); S["rf2"]=S.get("rf2",0)+sum(1 for p,c in r["readfull"].items() if c>=2); S["agentT"]=S.get("agentT",[])+[(r["calls"],r["inp"])]; S["tools"]+=r["tools"]; S["skill"]+=r["skill"]; S["reads"]+=r["reads"]
            if r["first"]: S["first"].append(r["first"])
        out[(tag,sid)]=(M,S)
import pickle; pickle.dump(out,open(os.path.join(os.path.dirname(__file__),"measure.pkl"),"wb"))
print("sessions",collections.Counter(k[0] for k in out))
