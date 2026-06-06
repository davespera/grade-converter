<script lang="ts">
    import type { PageData } from "./$types";
    import { resolve } from "$app/paths";

    let { data, form }: { data: PageData; form?: { success?: string; error?: string } } = $props();
    const scales = $derived(data.scales ?? []);
    const scaleCount = $derived(scales.length);
    const equivalenceCount = $derived(
        scales.reduce((total, scale) => total + (scale.equivalences?.length ?? 0), 0)
    );
    const countryCount = $derived(
        new Set(scales.map((scale) => scale.country_name).filter(Boolean)).size
    );

    let selectedScaleIds = $state<number[]>([]);
    let selectedEquivalenceIds = $state<string[]>([]);
    const selectedScaleCount = $derived(selectedScaleIds.length);
    const selectedEquivalenceCount = $derived(selectedEquivalenceIds.length);
    const totalSelected = $derived(selectedScaleCount + selectedEquivalenceCount);

    function confirmDelete(event: SubmitEvent, message: string) {
        if (!confirm(message)) {
            event.preventDefault();
        }
    }

    function confirmBulkDelete(event: SubmitEvent) {
        if (totalSelected === 0) {
            event.preventDefault();
            return;
        }
        const parts = [];
        if (selectedScaleCount > 0) {
            parts.push(`${selectedScaleCount} scale${selectedScaleCount === 1 ? "" : "s"}`);
        }
        if (selectedEquivalenceCount > 0) {
            parts.push(`${selectedEquivalenceCount} equivalence${selectedEquivalenceCount === 1 ? "" : "s"}`);
        }
        const message = `Delete ${parts.join(" and ")}?`;
        if (!confirm(message)) {
            event.preventDefault();
        }
    }
</script>

<svelte:head>
    <title>Scales Library | Grade Converter</title>
</svelte:head>

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
    {#if form?.error}
        <div class="form-errors" role="alert">{form.error}</div>
    {/if}
    {#if form?.success}
        <div class="success-banner" role="status">{form.success}</div>
    {/if}

    <form
        id="bulk-delete-form"
        method="POST"
        action="?/bulkDelete"
        class="bulk-bar"
        onsubmit={confirmBulkDelete}>
        <div>
            <strong>Bulk delete</strong>
            <p class="muted">Select scales or equivalences below to delete them in one action.</p>
        </div>
        <div class="bulk-meta">
            <span>{selectedScaleCount} scale{selectedScaleCount === 1 ? "" : "s"}</span>
            <span>{selectedEquivalenceCount} equivalence{selectedEquivalenceCount === 1 ? "" : "s"}</span>
        </div>
        <button type="submit" class="btn-danger" disabled={totalSelected === 0}>
            Delete selected
        </button>
    </form>

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
                    <div class="row-actions">
                        <label class="select-pill">
                            <input
                                type="checkbox"
                                name="scale_ids"
                                value={scale.id}
                                form="bulk-delete-form"
                                bind:group={selectedScaleIds}
                                aria-label={`Select ${scale.country_name} scale`} />
                            <span>Select scale</span>
                        </label>
                        <a href={resolve(`/scales/${scale.id}`)} class="btn-tertiary">View details</a>
                        <a
                            href={resolve(`/scales/${scale.id}/equivalences/new`)}
                            class="btn-tertiary">
                            Add equivalence
                        </a>
                        <form
                            method="POST"
                            action="?/deleteScale"
                            onsubmit={(event) =>
                                confirmDelete(
                                    event,
                                    `Delete ${scale.country_name} scale? This removes all associated equivalences.`
                                )
                            }>
                            <input type="hidden" name="scale_id" value={scale.id} />
                            <button type="submit" class="btn-danger">Delete scale</button>
                        </form>
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
                                    <th class="select-col">Select</th>
                                    <th class="action-col">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each scale.equivalences as equivalence (equivalence.id)}
                                    <tr>
                                        <td>{equivalence.origin_grade}</td>
                                        <td>{equivalence.spanish_1_4 ?? "-"}</td>
                                        <td>{equivalence.spanish_5_10 ?? "-"}</td>
                                        <td>{equivalence.spanish_literal ?? "-"}</td>
                                        <td class="select-col">
                                            <input
                                                type="checkbox"
                                                name="equivalence_ids"
                                                value={`${scale.id}:${equivalence.id}`}
                                                form="bulk-delete-form"
                                                bind:group={selectedEquivalenceIds}
                                                aria-label={`Select ${equivalence.origin_grade} equivalence`} />
                                        </td>
                                        <td class="action-col">
                                            <form
                                                method="POST"
                                                action="?/deleteEquivalence"
                                                onsubmit={(event) =>
                                                    confirmDelete(
                                                        event,
                                                        `Delete ${equivalence.origin_grade} equivalence from ${scale.country_name}?`
                                                    )
                                                }>
                                                <input type="hidden" name="scale_id" value={scale.id} />
                                                <input type="hidden" name="equivalence_id" value={equivalence.id} />
                                                <button type="submit" class="btn-danger btn-small">Delete</button>
                                            </form>
                                        </td>
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
