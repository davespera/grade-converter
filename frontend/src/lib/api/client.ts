import createClient from "openapi-fetch";
import type { paths } from "./schema";
import { browser } from '$app/environment';

// Import the public one for the browser, and the private one for the server
import { env as publicEnv } from '$env/dynamic/public';
import { env as privateEnv } from '$env/dynamic/private'; 

const baseUrl = browser 
  ? (publicEnv.PUBLIC_CLIENT_API_URL || "http://localhost:8000") // Browser (PUBLIC_ variable as required by SvelteKit)
  : (privateEnv.API_URL || "http://backend:8000");        // Docker server (private)

export const api = createClient<paths>({ baseUrl });