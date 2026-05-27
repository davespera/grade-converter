<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';
	import { resolve } from '$app/paths';

	let { children } = $props();
	let theme = $state('light');

	const navLinks = [
		{ label: 'Home', href: resolve('/') },
		{ label: 'Scales', href: resolve('/scales') },
		{ label: 'New Scale', href: resolve('/scales/new') }
	];

	const applyTheme = (value: string) => {
		document.documentElement.dataset.theme = value;
		document.documentElement.style.colorScheme = value;
	};

	onMount(() => {
		const stored = localStorage.getItem('theme');
		const preferred =
			stored ??
			(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
		theme = preferred;
		applyTheme(preferred);
	});

	const toggleTheme = () => {
		theme = theme === 'dark' ? 'light' : 'dark';
		applyTheme(theme);
		localStorage.setItem('theme', theme);
	};
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="color-scheme" content="light dark" />
</svelte:head>

<div class="app-shell">
	<header class="app-header">
		<div class="app-header-inner">
			<div class="brand">
				<div class="brand-mark"></div>
				<div>
					<div class="brand-title">Grade Converter</div>
					<div class="brand-subtitle">Academic equivalence workspace</div>
				</div>
			</div>
			<nav class="nav-links">
				{#each navLinks as link (link)}
					<a href={link.href}>{link.label}</a>
				{/each}
				<button
					type="button"
					class="btn btn-ghost theme-toggle"
					onclick={toggleTheme}
					aria-pressed={theme === 'dark'}>
					{theme === 'dark' ? 'Light mode' : 'Dark mode'}
				</button>
			</nav>
		</div>
	</header>
	<main class="app-main">{@render children()}</main>
</div>
