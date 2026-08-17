from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
GRAPH=ROOT/'TASK_GRAPH.yaml'; STATE=ROOT/'project_state/PROJECT_STATUS.yaml'; SUCCESS={'APPROVED','CANON_APPROVED','FINAL'}
def load(p): return yaml.safe_load(p.read_text(encoding='utf-8'))
def save(p,d): p.write_text(yaml.safe_dump(d,allow_unicode=True,sort_keys=False,width=120),encoding='utf-8')
def validator_map(g): return {v['id']:v for v in g['spec'].get('custom_validators',[])}
def gate_states(g,states,validator_results):
    out={}
    for _ in range(len(g['spec']['gates'])+2):
        changed=False
        for gid,gd in g['spec']['gates'].items():
            req_ok=bool(gd.get('requires')) and all((out.get(x) if x in g['spec']['gates'] else states.get(x)) in SUCCESS for x in gd.get('requires',[]))
            if not req_ok: val='PENDING'
            else:
                vids=gd.get('custom_validators',[])
                statuses=[validator_results.get(v,{}).get('status') for v in vids]
                if any(x=='FAIL' for x in statuses): val='BLOCKED'
                elif vids and not all(x=='PASS' for x in statuses): val='VALIDATION_REQUIRED'
                elif gd.get('requires_human_approval') and not (ROOT/gd.get('approval_file','').lstrip('/')).exists():
                    # O motor nunca escreve este arquivo. E o unico ponto do
                    # pipeline em que a decisao e humana por desenho.
                    val='AWAITING_HUMAN_APPROVAL'
                else: val='APPROVED'
            if out.get(gid)!=val: out[gid]=val; changed=True
        if not changed: break
    return out
def compute(g,s):
    states={k:v.get('state','PENDING') for k,v in s.get('tasks',{}).items()}; results=s.get('validator_results',{}); gs=gate_states(g,states,results)
    for t in g['spec']['tasks']:
        tid=t['id']; cur=states.get(tid,'PENDING')
        if cur in SUCCESS|{'RUNNING','SPAWNING','UNDER_REVIEW','FAILED','BLOCKED','REVISION_REQUIRED'}: continue
        ok=all((gs.get(d) if d in g['spec']['gates'] else states.get(d)) in SUCCESS for d in t.get('depends_on',[]))
        states[tid]='READY' if ok else 'PENDING'
    return states,gate_states(g,states,results)
def init():
    g=load(GRAPH); s={'apiVersion':'pedroarte.livingbooks/v1','kind':'ProjectStatus','metadata':{'project_id':g['metadata']['project_id']},'project_state':'INITIALIZED','tasks':{t['id']:{'state':'PENDING'} for t in g['spec']['tasks']},'gates':{x:{'state':'PENDING'} for x in g['spec']['gates']},'validator_results':{},'active_locks':{},'blocking_findings':[]}
    st,gs=compute(g,s)
    for k,v in st.items(): s['tasks'][k]['state']=v
    for k,v in gs.items(): s['gates'][k]['state']=v
    save(STATE,s); print('Initialized',STATE.relative_to(ROOT)); return 0
def refresh():
    if not STATE.exists(): return init()
    g=load(GRAPH); s=load(STATE); st,gs=compute(g,s)
    for k,v in st.items(): s['tasks'].setdefault(k,{})['state']=v
    for k,v in gs.items(): s['gates'].setdefault(k,{})['state']=v
    save(STATE,s); return 0
def ready():
    refresh(); g=load(GRAPH); s=load(STATE)
    xs=[t['id'] for t in g['spec']['tasks'] if s['tasks'][t['id']]['state']=='READY']
    print('\n'.join(xs) if xs else 'NO_READY_TASKS'); return 0
SUCCESS_MARKS={'APPROVED','CANON_APPROVED','FINAL'}

def mark(a):
    if not STATE.exists(): init()
    s=load(STATE)
    if a.node not in s['tasks']: print('Unknown task',a.node,file=sys.stderr); return 2
    s['tasks'][a.node]['state']=a.state; save(STATE,s); refresh()
    if a.state in SUCCESS_MARKS:
        print(f'Lembrete: registre o custo real de {a.node} em logs/COST_LEDGER.md (ver logs/AGENTS.md).',file=sys.stderr)
    return 0
def validate_gate(a):
    if not STATE.exists(): init()
    g=load(GRAPH); s=load(STATE); refresh(); s=load(STATE)
    if a.gate not in g['spec']['gates']: print('Unknown gate',a.gate,file=sys.stderr); return 2
    gd=g['spec']['gates'][a.gate]
    if s['gates'][a.gate]['state']=='PENDING': print(f'{a.gate}: dependencies are not complete',file=sys.stderr); return 2
    validators=validator_map(g); failed=False
    for vid in gd.get('custom_validators',[]):
        cfg=validators.get(vid)
        if not cfg:
            s.setdefault('validator_results',{})[vid]={'status':'FAIL','error':'validator not registered'}; failed=True; continue
        # Um validador declarado como "python scripts/x.py" seria executado
        # pelo Python do PATH, que pode nao ter as dependencias do motor
        # (Pillow, PyYAML) instaladas. Usar sys.executable garante o mesmo
        # interpretador que esta rodando este script — tipicamente o venv.
        command=cfg['command']
        if command.startswith('python '):
            command=f'"{sys.executable}" '+command[len('python '):]
        r=subprocess.run(command,cwd=ROOT,shell=True,text=True,capture_output=True)
        status='PASS' if r.returncode==0 else 'FAIL'
        s.setdefault('validator_results',{})[vid]={'status':status,'command':cfg['command'],'stdout':r.stdout[-8000:],'stderr':r.stderr[-8000:]}
        print(f'{vid}: {status}')
        if r.stdout: print(r.stdout.rstrip())
        if r.stderr: print(r.stderr.rstrip(),file=sys.stderr)
        failed |= r.returncode!=0
    save(STATE,s); refresh()
    return 1 if failed else 0
def main():
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    sub.add_parser('init-state').set_defaults(fn=lambda a:init()); sub.add_parser('refresh').set_defaults(fn=lambda a:refresh()); sub.add_parser('ready').set_defaults(fn=lambda a:ready())
    q=sub.add_parser('mark'); q.add_argument('node'); q.add_argument('state'); q.set_defaults(fn=mark)
    q=sub.add_parser('validate-gate'); q.add_argument('gate'); q.set_defaults(fn=validate_gate)
    a=p.parse_args(); return a.fn(a)
if __name__=='__main__': raise SystemExit(main())
