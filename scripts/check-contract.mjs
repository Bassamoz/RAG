import { execFileSync } from "node:child_process";
import { readFileSync, unlinkSync } from "node:fs";
import { fileURLToPath } from "node:url";
const target = new URL("../packages/api-client/src/schema.d.ts", import.meta.url);
const temporary = new URL("../packages/api-client/src/schema.check.d.ts", import.meta.url);
const cli = fileURLToPath(new URL("../node_modules/openapi-typescript/bin/cli.js", import.meta.url));
try {
  execFileSync(process.execPath, [cli, "packages/api-client/openapi.json", "-o", fileURLToPath(temporary)], { stdio: "inherit" });
  if (readFileSync(target, "utf8") !== readFileSync(temporary, "utf8"))
    throw new Error("Generated API client is stale; regenerate it from OpenAPI");
} finally {
  try { unlinkSync(temporary); } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
}
