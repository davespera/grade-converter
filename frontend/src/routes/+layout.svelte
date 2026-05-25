<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { resolve } from '$app/paths';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="description" content="Modern grade conversion and academic scale management." />
</svelte:head>

<div class="page-shell">
	<header class="top-nav">
		<div class="nav-inner">
			<a class="brand" href={resolve('/')}
				><span class="brand-mark">GC</span>
				<span>Grade Converter</span></a
			>
			<nav class="nav-links">
				<a class="btn-secondary" href={resolve('/scales')}>Scales</a>
				<a class="btn-primary" href={resolve('/scales/new')}>New Scale</a>
			</nav>
		</div>
	</header>

	<main class="content">
		{@render children()}
	</main>

	<footer class="site-footer">
		Built for fast, reliable grade conversions with clear equivalence mapping.
	</footer>
</div>
