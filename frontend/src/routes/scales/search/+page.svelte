<script lang="ts">
    import type { PageData } from "./$types";
    import { resolve } from "$app/paths";

    let { data }: { data: PageData } = $props();

    const results = $derived(data.results);
    const resultCount = $derived(results?.length ?? 0);
    const hasQuery = $derived(Boolean(data.country || data.scale));
</script>

<svelte:head>
    <title>Search Scales | Grade Converter</title>
</svelte:head>

<section class="page-hero">
    <div class="hero-copy">
        <p class="eyebrow">Scale Library</p>
        <h1>Search Scales by Country</h1>
        <p class="lead">
            Find every grading scale registered for a country, or narrow to a specific
            scale identifier.
        </p>
        <div class="hero-actions">
            <a href={resolve("/scales")} class="btn-secondary">Browse all scales</a>
            <a href={resolve("/")} class="btn-tertiary">Back to Home</a>
        </div>
    </div>
    <div class="hero-panel card">
        <form method="GET" class="search-form">
            <label class="field">
                <span>Country</span>
                <input
                    type="text"
                    name="country"
                    value={data.country}
                    placeholder="e.g. Alemania"
                    autocomplete="off" />
            </label>
            <label class="field">
                <span>Scale identifier <em class="muted">(optional)</em></span>
                <input
                    type="text"
                    name="scale"
                    value={data.scale}
                    placeholder="e.g. 1-6"
                    autocomplete="off" />
            </label>
            <button type="submit" class="btn-primary">Search</button>
        </form>
        <p class="muted">Matching is case-insensitive and matches partial text.</p>
    </div>
</section>

{#if data.error}
    <div class="form-errors" role="alert">Search failed. Please try again.</div>
{/if}

{#if !hasQuery}
    <section class="empty-card">
        <h2>Start a search</h2>
        <p class="lead">Enter a country to list all of its grading scales.</p>
    </section>
{:else if resultCount === 0}
    <section class="empty-card">
        <h2>No matching scales</h2>
        <p class="lead">No scales found for that search. Try a broader term.</p>
    </section>
{:else}
    <p class="muted">
        {resultCount} scale{resultCount === 1 ? "" : "s"} found.
    </p>
    <div class="scale-grid">
        {#each results ?? [] as scale (scale.id)}
            <article class="card scale-card">
                <header class="scale-header">
                    <div>
                        <h3>{scale.country_name}</h3>
                        <p class="muted">{scale.scale_description}</p>
                    </div>
                    <div class="row-actions">
                        <a href={resolve(`/scales/${scale.id}`)} class="btn-tertiary">View details</a>
                    </div>
                </header>
            </article>
        {/each}
    </div>
{/if}

<style>
    .search-form {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .search-form .btn-primary {
        align-self: flex-start;
    }
</style>
