import { handleAPI, SECURITY_HEADERS } from "../lib/api.mjs";
import handler from "vinext/server/fetch-handler";
import { runWithConnectorBinding } from "../lib/connector-context";
import type { ConnectorBinding } from "../lib/connector-contract.mjs";

const worker = {
  async fetch(request: Request, env: Cloudflare.Env, ctx: ExecutionContext<{ CONNECTORS?: ConnectorBinding }>) {
    let binding = ctx.props?.CONNECTORS;
    // Local preview emulates the same request-scoped capability. This branch and
    // the auxiliary service binding are absent from production builds.
    if (import.meta.env.DEV && !binding && env.CONNECTORS) {
      const preview = env.CONNECTORS;
      const expiresAt = Date.now() + 60_000;
      binding = {
        async getContext() {
          if (Date.now() >= expiresAt) return { status: "request_context_expired" };
          return preview.getContext?.() ?? { status: "binding_unavailable" };
        },
        async invoke(connectorId, actionName, args) {
          if (Date.now() >= expiresAt) {
            return { status: "request_context_expired", message: "This request has expired. Please try again." };
          }
          return preview.invoke(connectorId, actionName, args);
        },
      };
    }
    // Keep the native Request for API work: Vinext's dynamic-route Request
    // proxy uses the wrong receiver for workerd's native `cf` getter.
    // The edge metadata is required for shared visitor quota enforcement.
    const response=await runWithConnectorBinding(binding, () =>
      new URL(request.url).pathname.startsWith('/api/')
        ? handleAPI(request, env)
        : handler.fetch(request, env, ctx));
    const headers=new Headers(response.headers);
    for(const [key,value] of Object.entries(SECURITY_HEADERS))headers.set(key,value);
    return new Response(response.body,{status:response.status,statusText:response.statusText,headers});
  },
};

export default worker;
