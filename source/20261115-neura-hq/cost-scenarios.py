from decimal import Decimal,ROUND_CEILING
from pathlib import Path
import json
plans=[('Starter',99,2000),('Growth',249,6000),('Scale',499,15000)]
def addon(n):
 opts=[]
 for big in range((n+4999)//5000+1):
  small=max(0,(n-big*5000+999)//1000);opts.append((big*249+small*59,big,small))
 return min(opts)
r=[]
for name,price,inc in plans:
 extra=max(0,8400-inc);fee,big,small=addon(extra)
 r.append({'plan':name,'price':price,'includedCredits':inc,'fullUseUsdPerCredit':str(Decimal(price)/Decimal(inc)),'sixReplyTextSessions':inc//6,'sixReply20PercentMediaSessions':inc*5//42,'scenario8400Credits':{'additionalNeeded':extra,'packs5000':big,'packs1000':small,'totalUsdBeforeOtherFees':price+fee}})
assert [x['scenario8400Credits']['totalUsdBeforeOtherFees']for x in r]==[466,426,499]
Path(__file__).with_name('cost-scenarios.json').write_text(json.dumps({'assumptions':'1000sessions*6AIreplies;20% of replies triggered by media consume3credits, others1.8400credits. Hypothetical, not real usage. Discrete additive packs, no tax/WhatsApp/labor/integration cost, no rollover assumption.','plans':r},indent=2));print(json.dumps(r))
