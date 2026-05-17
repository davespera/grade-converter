import { defineConfig } from '@hey-api/openapi-ts';

// Detect if we are running inside Docker or on the host machine
const openApiUrl = 'http://localhost:8000/openapi.json';
// process.env.OPENAPI_URL || 'http://localhost:8000/openapi.json';

export default defineConfig({
  input: openApiUrl,
  output: 'src/lib/client',
  plugins: [
    '@hey-api/client-fetch',
  ],
});