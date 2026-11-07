import { defineConfig, globalIgnores } from 'eslint/config';
import next from 'eslint-config-next/core-web-vitals';
import typescript from 'eslint-config-next/typescript';

export default defineConfig([
  ...next,
  ...typescript,
  { settings: { next: { rootDir: 'apps/web/' } } },
  globalIgnores(['**/.next/**', '**/schema.d.ts']),
]);
