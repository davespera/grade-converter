import { existsSync, writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const openApiPath = path.resolve(scriptDir, '..', '.openapi.json');

if (existsSync(openApiPath) && process.env.REFRESH_OPENAPI !== '1') {
  process.exit(0);
}

const baseUrl = process.env.API_URL || 'http://localhost:8000';
const response = await fetch(`${baseUrl}/openapi.json`);

if (!response.ok) {
  throw new Error(`Failed to fetch OpenAPI schema from ${baseUrl}/openapi.json (${response.status})`);
}

writeFileSync(openApiPath, await response.text(), 'utf8');