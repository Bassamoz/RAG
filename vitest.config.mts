import { defineConfig } from "vitest/config";

// Source snapshots in tmp are installation fixtures, not additional copies of the suite.
export default defineConfig({ test: { include: ["tests/web/**/*.test.ts"] } });
