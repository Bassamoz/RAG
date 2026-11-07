import createClient from "openapi-fetch";
import type { paths } from "./schema";

/** Generated types constrain calls; the runtime guard treats JSON as untrusted data. */
export async function checkService(baseUrl: string): Promise<boolean> {
  const client = createClient<paths>({ baseUrl });
  const { data, response } = await client.GET("/api/v1/ready", {
    signal: AbortSignal.timeout(5_000),
  });
  return response.ok && typeof data === "object" && data?.status === "ok";
}
