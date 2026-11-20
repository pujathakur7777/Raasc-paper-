import json, numpy as np, onnxruntime as ort
from tokenizers import Tokenizer
B="/tmp/claude-0/-home-claude/3d193717-eb3f-5d25-a3fd-e765519136bb/scratchpad/enc/package/"
tok=Tokenizer.from_file(B+"tokenizer.json"); tok.enable_padding(); tok.enable_truncation(128)
sess=ort.InferenceSession(B+"model.onnx",providers=["CPUExecutionProvider"])
names=[i.name for i in sess.get_inputs()]
def emb(txts):
    out=[]
    for i in range(0,len(txts),32):
        e=tok.encode_batch(txts[i:i+32])
        ids=np.array([x.ids for x in e],dtype=np.int64); m=np.array([x.attention_mask for x in e],dtype=np.int64)
        f={"input_ids":ids,"attention_mask":m}
        if "token_type_ids" in names: f["token_type_ids"]=np.zeros_like(ids)
        h=sess.run(None,f)[0]
        v=(h*m[...,None]).sum(1)/m.sum(1,keepdims=True)
        out.append(v/np.linalg.norm(v,axis=1,keepdims=True))
    return np.vstack(out)
d=json.load(open("ehealthforumQAs.json"))
q=[x["question"].strip() for x in d]
seen={};keep=[]
for i,t in enumerate(q):
    if t.lower() not in seen: seen[t.lower()]=1;keep.append(i)
d=[d[i] for i in keep]; q=[x["question"].strip() for x in d]
E=emb(q); S=E@E.T; np.fill_diagonal(S,-1)
nn=S.max(1)
res={"n":len(q),"median":float(np.median(nn)),"p90":float(np.percentile(nn,90)),"p99":float(np.percentile(nn,99))}
for t in (0.5,0.6,0.7,0.8,0.9): res[f"ge{t}"]=float((nn>=t).mean()*100)
# shared-tag pairs vs not
tags=[set(x.get("tags",[])) for x in d]
iu=np.triu_indices(len(q),1); s=S[iu]
sh=np.array([bool(tags[i]&tags[j]) for i,j in zip(*iu)])
for lo in (0.5,0.6,0.7,0.8):
    m=s>=lo; res[f"pairs_ge{lo}"]=int(m.sum()); res[f"pairs_ge{lo}_shared_tag"]=int((m&sh).sum())
order=np.argsort(-S.max(1))[:0]
# closest pairs
idx=np.dstack(np.unravel_index(np.argsort(-np.triu(np.where(S>-1,S,-1),1).ravel())[:12],S.shape))[0]
res["closest"]=[(round(float(S[i,j]),3),q[i],q[j]) for i,j in idx]
# paraphrase-order test
res["order_test"]=float((emb(["ibuprofen with warfarin"])@emb(["warfarin with ibuprofen"]).T)[0,0])
json.dump(res,open("probe_minilm.json","w"),indent=1)
print(json.dumps(res,indent=1))
