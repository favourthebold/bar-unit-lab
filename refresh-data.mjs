import {mkdir,writeFile} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
const origin='https://www.beyondallreason.info';
async function read(path){const r=await fetch(origin+path);if(!r.ok)throw Error(`${path}: ${r.status}`);return r.text()}
const home=await read('/units/armada-bots');
const cats=[...new Set([...home.matchAll(/href="(\/units\/[^"#]+)"/g)].map(m=>m[1]))].filter(p=>!p.includes('alien'));
const catalogue={};
for(const path of cats){const html=await read(path);for(const m of html.matchAll(/href="\/unit\/([^"#]+)"/g)){const id=m[1];catalogue[id]={id,faction:path.includes('armada')?'Armada':path.includes('cortex')?'Cortex':'Legion',category:path.split('/').pop().replace(/^(armada|cortex|legion|green)-/,'')}}}
await mkdir('raw',{recursive:true});await writeFile('catalogue.json',JSON.stringify(catalogue));
const ids=Object.keys(catalogue);for(let i=0;i<ids.length;i+=6){await Promise.all(ids.slice(i,i+6).map(async id=>writeFile(`raw/${id}.html`,await read('/unit/'+id))));console.log(`Fetched ${Math.min(i+6,ids.length)} / ${ids.length}`)}
const p=spawnSync('python',['parse.py'],{stdio:'inherit'});if(p.status!==0)process.exit(p.status||1);
console.log('Data refreshed. Update the displayed snapshot date, run node test.cjs, and republish.');
