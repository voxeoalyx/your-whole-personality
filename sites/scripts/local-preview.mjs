// Local-only launcher. Existing service keys stay in the child process environment.
import {readFileSync,existsSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {spawn} from 'node:child_process';
const root=fileURLToPath(new URL('../',import.meta.url));
const names=['QLOO_API_KEY','QLOO_BASE_URL','QLOO_CALL_LIMIT','NVIDIA_API_KEY','NVIDIA_MODEL','NVIDIA_CALL_LIMIT'];
const values={};
// Checkout-local values override the original Python checkout's local values.
for(const url of [new URL('../../.env',import.meta.url),new URL('../.env',import.meta.url)]){
 if(!existsSync(url))continue;
 for(let line of readFileSync(url,'utf8').replace(/^\uFEFF/,'').split(/\r?\n/)){
  line=line.trim().replace(/^export\s+/,'');if(!line||line.startsWith('#')||!line.includes('='))continue;
  const split=line.indexOf('='),name=line.slice(0,split).trim();if(!names.includes(name))continue;
  let value=line.slice(split+1).trim();value=/^["']/.test(value)?value.slice(1).split(value[0])[0]:value.split(/\s+#/)[0].trim();values[name]=value;
 }
}
const env=Object.fromEntries(['PATH','HOME','LANG','TMPDIR','SSL_CERT_FILE','SSL_CERT_DIR','NODE_EXTRA_CA_CERTS'].filter(k=>process.env[k]).map(k=>[k,process.env[k]]));
for(const name of names){const value=process.env[name]||values[name];if(value)env[name]=value;}
Object.assign(env,{CLOUDFLARE_INCLUDE_PROCESS_ENV:'true',WRANGLER_SEND_METRICS:'false',CLOUDFLARE_CF_FETCH_ENABLED:'false'});
const args=process.argv.slice(2);if(args.length&&(args.length!==2||args[0]!=='--port'||!/^\d+$/.test(args[1])||Number(args[1])<1024||Number(args[1])>65535))throw new Error('Only a local --port override is supported.');
const child=spawn(process.execPath,['--import','./scripts/sites-env.mjs','./node_modules/wrangler/bin/wrangler.js','dev','--config','dist/server/wrangler.json','--local','--persist-to','.wrangler/state','--ip','127.0.0.1','--inspector-port','0',...args],{cwd:root,env,stdio:'inherit'});
for(const signal of ['SIGINT','SIGTERM'])process.on(signal,()=>child.kill(signal));
child.on('exit',code=>process.exitCode=code??1);
