import { createServer, type Server } from "node:http";
import { afterEach, expect, test } from "vitest";
import { checkService } from "../../packages/api-client/src/index";

let server: Server | undefined;
afterEach(async () => {
  if (server) await new Promise<void>((resolve) => server!.close(() => resolve()));
  server = undefined;
});

async function serve(status: number, body: unknown) {
  server = createServer((request, response) => {
    expect(request.url).toBe("/api/v1/ready");
    response.writeHead(status, { "content-type": "application/json" });
    response.end(JSON.stringify(body));
  });
  await new Promise<void>((resolve) => server!.listen(0, "127.0.0.1", resolve));
  const address = server.address();
  if (!address || typeof address === "string") throw new Error("No listener");
  return `http://127.0.0.1:${address.port}`;
}

test("reads a ready response over an actual local HTTP connection", async () => {
  expect(await checkService(await serve(200, { status: "ok" }))).toBe(true);
});

test.each([null, { status: true }, { status: "broken" }])(
  "rejects invalid provider data %j",
  async (body) => {
    expect(await checkService(await serve(200, body))).toBe(false);
  },
);

test("a failed readiness response cannot be reported ready", async () => {
  expect(await checkService(await serve(503, { status: "ok" }))).toBe(false);
});
