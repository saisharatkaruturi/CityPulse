import { defineConfig } from 'vitest/config';

// Unit tests for pure logic (roles, localisation, ranking display, CSV helpers). No DOM is needed.
export default defineConfig({
  test: { include: ['src/**/*.test.ts'], environment: 'node' },
});
