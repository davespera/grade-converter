<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { client } from '$lib/api/client.gen'

	let { children } = $props();

	// Point to backend
	client.setConfig({
    baseUrl: 'http://localhost:8000'
  });
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>
{@render children()}
