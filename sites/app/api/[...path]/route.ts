import {env} from 'cloudflare:workers';
import {handleAPI} from '../../../lib/api.mjs';
export const dynamic='force-dynamic';
export function GET(request:Request){return handleAPI(request,env);}
export function POST(request:Request){return handleAPI(request,env);}
