<script lang="ts">
    import type { PageData } from "./$types";
    import { resolve } from "$app/paths";

    let { data }: { data: PageData } = $props();
    const scales = $derived(data.scales ?? []);
    const scaleCount = $derived(scales.length);
    const equivalenceCount = $derived(
        scales.reduce((total, scale) => total + (scale.equivalences?.length ?? 0), 0)
    );
    const countryCount = $derived(
        new Set(scales.map((scale) => scale.country_name).filter(Boolean)).size
    );
</script>

<section class="page-hero">
    <div class="hero-copy">
        <p class="eyebrow">Scale Library</p>
        <h1>Academic Scales</h1>
        <p class="lead">Browse, review, and refine equivalences with confidence.</p>
        <div class="hero-actions">
            <a href={resolve("/scales/new")} class="btn-primary">Create New Scale</a>
            <a href={resolve("/")} class="btn-secondary">Back to Home</a>
        </div>
    </div>
    <div class="hero-panel card">
        <h2>At a glance</h2>
        <div class="stat-grid">
            <div class="stat-card">
                <p class="stat-label">Total scales</p>
                <p class="stat-value">{scaleCount}</p>
            </div>
            <div class="stat-card">
                <p class="stat-label">Equivalences</p>
                <p class="stat-value">{equivalenceCount}</p>
            </div>
            <div class="stat-card">
                <p class="stat-label">Countries</p>
                <p class="stat-value">{countryCount}</p>
            </div>
        </div>
        <p class="muted">Keep your grade mappings consistent across regions and programs.</p>
    </div>
</section>

{#if scales.length === 0}
    <section class="empty-card">
        <h2>No scales yet</h2>
        <p class="lead">Create your first scale to start converting grades.</p>
        <div class="hero-actions">
            <a href={resolve("/scales/new")} class="btn-primary">Create New Scale</a>
        </div>
    </section>
{:else}
    <div class="scale-grid">
        {#each scales as scale (scale.id)}
            <article class="card scale-card">
                <header class="scale-header">
                    <div>
                        <h3>{scale.country_name}</h3>
                        <p class="muted">{scale.scale_description ?? "No description provided yet."}</p>
                    </div>
                    <div class="tags">
                        {#if scale.total_grades}
                            <span class="tag">{scale.total_grades} grades</span>
                        {/if}
                        <span class="tag">{scale.equivalences?.length ?? 0} equivalences</span>
                    </div>
                </header>

                {#if scale.equivalences && scale.equivalences.length > 0}
                    <div class="table-wrap">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Origin</th>
                                    <th>Spanish 1-4</th>
                                    <th>Spanish 5-10</th>
                                    <th>Literal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each scale.equivalences as equivalence (equivalence.id)}
                                    <tr>
                                        <td>{equivalence.origin_grade}</td>
                                        <td>{equivalence.spanish_1_4 ?? "-"}</td>
                                        <td>{equivalence.spanish_5_10 ?? "-"}</td>
                                        <td>{equivalence.spanish_literal ?? "-"}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {:else}
                    <p class="muted">No equivalences added yet.</p>
                {/if}
            </article>
        {/each}
    </div>
{/if}
