import json,numpy as np,runpy,sys
sys.argv=['x']
src=open('probe_minilm.py').read().split('d=json.load')[0]
exec(src)
P=[ # (a,b,same_intent)
("what are the symptoms of type 1 diabetes","what are the symptoms of type 2 diabetes",0),
("can i take ibuprofen while on warfarin","can i take acetaminophen while on warfarin",0),
("what is the adult dose of amoxicillin","what is the child dose of amoxicillin",0),
("is it safe to take aspirin during pregnancy","is it safe to take aspirin while breastfeeding",0),
("how long does the flu vaccine last","how long does the shingles vaccine last",0),
("what should i do if my blood pressure is too high","what should i do if my blood pressure is too low",0),
("when should i take metformin, before meals","when should i take metformin, after meals",0),
("how do i treat a first degree burn","how do i treat a third degree burn",0),
("what are the side effects of lisinopril","what are the side effects of losartan",0),
("is it normal to have a fever after a covid vaccine","is it normal to have a fever after a flu vaccine",0),
("what are the symptoms of type 2 diabetes","which signs show that someone has type 2 diabetes",1),
("can i take ibuprofen while on warfarin","is ibuprofen safe together with warfarin",1),
("what is the adult dose of amoxicillin","how much amoxicillin should a grown up take",1),
("how long does the flu vaccine last","how long am i protected after a flu shot",1),
("how do i treat a first degree burn","what is the first aid for a mild first degree burn",1),
("what are the side effects of lisinopril","which side effects can lisinopril cause",1),
("what should i do if my blood pressure is too high","my blood pressure is high, what do i do",1),
("how do i stop smoking","what is the best way to quit smoking",1),
]
A=emb([a for a,_,_ in P]);Bm=emb([b for _,b,_ in P])
c=(A*Bm).sum(1)
out=[(float(c[i]),P[i][2],P[i][0],P[i][1]) for i in range(len(P))]
json.dump(out,open('pairs_minilm.json','w'),indent=1)
for o in out: print("%.3f same=%d | %s || %s"%(o[0],o[1],o[2],o[3]))
neg=[o[0] for o in out if not o[1]];pos=[o[0] for o in out if o[1]]
print("neg mean %.3f min %.3f max %.3f | pos mean %.3f min %.3f max %.3f"%(np.mean(neg),min(neg),max(neg),np.mean(pos),min(pos),max(pos)))
