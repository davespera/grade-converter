<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { resolve } from '$app/paths';
	import { onMount } from 'svelte';

	let { children } = $props();
	let theme = $state('dark');

	const applyTheme = (value: string) => {
		document.documentElement.dataset.theme = value;
		document.documentElement.style.colorScheme = value;
	};

	onMount(() => {
		const stored = localStorage.getItem('theme');
		const preferred = stored === 'light' || stored === 'dark' ? stored : 'dark';
		theme = preferred;
		applyTheme(preferred);
	});

	const toggleTheme = () => {
		const next = theme === 'dark' ? 'light' : 'dark';
		theme = next;
		applyTheme(next);
		localStorage.setItem('theme', next);
	};
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="viewport" content="width=device-width, initial-scale=1" />
	<meta name="description" content="Modern grade conversion and academic scale management." />
</svelte:head>

<div class="page-shell">
	<a href="#main-content" class="skip-link">Skip to main content</a>
	<header class="top-nav">
		<div class="nav-inner">
			<a class="brand" href={resolve('/')}
				><span class="brand-mark">GC</span>
				<span>Grade Converter</span></a
			>
			<nav class="nav-links">
				<a class="btn-secondary" href={resolve('/scales')}>Scales</a>
				<a class="btn-primary" href={resolve('/scales/new')}>New Scale</a>
				<button
					class="btn-ghost theme-toggle"
					type="button"
					aria-pressed={theme === 'dark'}
					onclick={toggleTheme}
				>
					{theme === 'dark' ? 'Light mode' : 'Dark mode'}
				</button>
			</nav>
		</div>
	</header>

	<main id="main-content" class="content">
		{@render children()}
	</main>

	<footer class="site-footer">
		Built for fast, reliable grade conversions with clear equivalence mapping.
	</footer>
</div>
