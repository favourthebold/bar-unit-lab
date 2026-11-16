import json,re
from datetime import date
from pathlib import Path
from html.parser import HTMLParser
class Node:
 def __init__(self,tag='',attrs=(),parent=None):self.tag=tag;self.a=dict(attrs);self.children=[];self.parent=parent
 def text(self):return ''.join(c if isinstance(c,str) else c.text() for c in self.children).strip()
 def find(self,cls):
  out=[]
  for c in self.children:
   if isinstance(c,Node):
    if cls in c.a.get('class','').split():out.append(c)
    out.extend(c.find(cls))
  return out
class Parser(HTMLParser):
 def __init__(self,s):super().__init__();self.root=Node();self.cur=self.root;self.feed(s)
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs,self.cur);self.cur.children.append(n)
  if tag not in ('img','input','br','hr','meta','link','source','embed','wbr','area','base','col','param'):self.cur=n
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs)
 def handle_endtag(self,tag):
  n=self.cur
  while n.parent:
   if n.tag==tag:self.cur=n.parent;return
   n=n.parent
 def handle_data(self,s):self.cur.children.append(s)
def number(s):
 try:return float(s.replace(',','').strip())
 except:return None
catalog=json.loads(Path('catalogue.json').read_text());units=[];keys={}
for id,u in catalog.items():
 root=Parser(Path('raw',id+'.html').read_text(encoding='utf8')).root
 def first(cls):
  a=root.find(cls);return a[0].text() if a else ''
 u.update(name=first('us-unitname'),role=first('us-text'),tier=first('techlevel'),stats={},weapons=[],url='https://www.beyondallreason.info/unit/'+id)
 if u['role']=='Commander':u['category']='commanders'
 elif u['role']=='Decoy Commander':u['category']='bots'
 imgs=root.find('unit-img-detail');u['image']=next((x.a.get('src','') for x in imgs if 'w-condition-invisible' not in x.a.get('class','')),'')
 for n in root.find('us-stats-item'):
  if 'w-condition-invisible' in n.a.get('class',''):continue
  names=n.find('us-stats-name');nums=n.find('us-stats-number')
  if names and nums:
   key=names[0].text().lower().strip();v=number(nums[0].text())
   if v is not None:u['stats'][key]=v;keys[key]=keys.get(key,0)+1
 u['ranges']={}
 for w in root.find('uw-item'):
  names=w.find('uw-weaponname');weapon={'name':names[0].text() if names else ''}
  for n in w.find('uw-weapon-stats'):
   if 'w-condition-invisible' in n.a.get('class',''):continue
   falloff=re.search(r'Weapon does\s+([\d.]+)% damage at max\. range',n.text())
   if falloff:weapon['range_damage_factor']=float(falloff.group(1))/100
   fields=n.find('uw-stats-text')
   if len(fields)>1:
    v=number(fields[0].text());key=fields[1].text().strip().lower()
    if v is not None:weapon[key]=v
  if len(weapon)>1:u['weapons'].append(weapon)
 damage_weapons=[w for w in u['weapons'] if w.get('dps',0)>0]
 if any(w.get('range_damage_factor',1)<1 for w in damage_weapons) and 'dps' in u['stats']:
  total=sum(w['dps'] for w in damage_weapons)
  low=sum(w['dps']*w.get('range_damage_factor',1) for w in damage_weapons)
  factors={w.get('range_damage_factor',1) for w in damage_weapons}
  u['ranges']['dps']={'min':u['stats']['dps']*low/total,'max':u['stats']['dps'],'estimated':len(factors)>1 or abs(total-u['stats']['dps'])>max(1,total*.01),'basis':'Published weapon falloff applied to unit DPS; mixed weapons weighted by published weapon DPS. Bounds are a weapon-output envelope, not damage at one shared distance.'}
 for w in u['weapons']:
  if w.get('range_damage_factor',1)<1:
   w['ranges']={k:{'min':w[k]*w['range_damage_factor'],'max':w[k]} for k in ('dps','alpha') if k in w}
 for key in ('reload','salvo','alpha','aoe'):
  vs=[w[key] for w in u['weapons'] if key in w]
  if vs:u['stats']['weapon_'+key]=max(vs)
  if key=='alpha' and vs and any('alpha' in w.get('ranges',{}) for w in u['weapons']):
   u['ranges']['weapon_alpha']={'min':max(w.get('ranges',{}).get('alpha',{}).get('min',w['alpha']) for w in u['weapons'] if 'alpha' in w),'max':max(vs),'estimated':False}
 if not u['name']:raise Exception('Missing name '+id)
 units.append(u)
Path('dist/data.json').write_text(json.dumps({'source':'https://www.beyondallreason.info','retrieved':date.today().isoformat(),'units':units},ensure_ascii=False),encoding='utf8')
print(json.dumps({'units':len(units),'fields':keys,'pawn':next(u for u in units if u['id']=='armpw')},indent=2))
