import {mkdir,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
const origin='https://www.beyondallreason.info';
async function read(path){const r=await fetch(origin+path);if(!r.ok)throw Error(`${path}: ${r.status}`);return r.text()}
const home=await read('/units/armada-bots');
const cats=[...new Set([...home.matchAll(/href="(\/units\/[^"#]+)"/g)].map(m=>m[1]))].filter(p=>!p.includes('alien'));
const catalogue={};
for(const path of cats){
 const queue=[path],seen=new Set();
 while(queue.length){
  const page=queue.shift();if(seen.has(page))continue;seen.add(page);
  if(seen.size>100)throw Error('Unexpected pagination count: '+path);
  const html=await read(page);
  for(const m of html.matchAll(/href="\/unit\/([^"#?]+)"/g)){
   const id=m[1];catalogue[id]={id,faction:path.includes('armada')?'Armada':path.includes('cortex')?'Cortex':'Legion',category:path.split('/').pop().replace(/^(armada|cortex|legion|green)-/,'')};
  }
  // Each Webflow collection has its own pager. Traverse them independently.
  for(const tag of html.matchAll(/<a\b[^>]*class="[^"]*w-pagination-next[^>]*>/g)){
   const href=tag[0].match(/href="([^"]+)"/)?.[1];if(!href)continue;
   const nextURL=new URL(href.replaceAll('&amp;','&'),origin+page);
   for(const [key,value] of nextURL.searchParams)if(key.endsWith('_page')){
    const next=path+'?'+key+'='+value;if(!seen.has(next)&&!queue.includes(next))queue.push(next);
   }
  }
 }
 console.log(path+': checked '+seen.size+' pages');
}
await mkdir('raw',{recursive:true});await writeFile('catalogue.json',JSON.stringify(catalogue));
const ids=Object.keys(catalogue);for(let i=0;i<ids.length;i+=6){await Promise.all(ids.slice(i,i+6).map(async id=>writeFile(`raw/${id}.html`,await read('/unit/'+id))));console.log(`Fetched ${Math.min(i+6,ids.length)} / ${ids.length}`)}
const p=spawnSync('python',['parse.py'],{stdio:'inherit'});if(p.status!==0)process.exit(p.status||1);
console.log('Data refreshed. Update the displayed snapshot date, run node test.cjs, and republish.');
