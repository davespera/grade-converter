<script lang="ts">
    import { resolve } from '$app/paths';
</script>

<svelte:head>
    <title>Home | Grade Converter</title>
</svelte:head>

<section class="hero">
    <div>
        <p class="eyebrow">Academic Conversion Suite</p>
        <h1>Make grade conversion clear, quick, and trustworthy.</h1>
        <p class="lead">
            Build and manage academic scales in one place. Review equivalences at a
            glance and keep conversions consistent across teams.
        </p>
        <div class="hero-actions">
            <a href={resolve('/scales')} class="btn-primary">Explore Scales</a>
            <a href={resolve('/scales/new')} class="btn-secondary">Create New Scale</a>
        </div>
    </div>

    <div class="hero-card">
        <h2>What you can do</h2>
        <div class="stats">
            <div class="stat">
                <strong>Centralize</strong>
                Keep all country scales and equivalences in one source of truth.
            </div>
            <div class="stat">
                <strong>Validate</strong>
                Catch missing grades with clearer inputs and inline feedback.
            </div>
            <div class="stat">
                <strong>Share</strong>
                Hand off clean mappings to automation flows without rework.
            </div>
        </div>
    </div>
</section>

<section class="card">
    <h2>Start with a new scale</h2>
    <p class="lead">
        Use guided inputs to add equivalences and ensure Spanish literal grades are
        consistent across the data set.
    </p>
    <div class="hero-actions">
        <a href={resolve('/scales/new')} class="btn-primary">Add Equivalences</a>
        <a href={resolve('/scales')} class="btn-secondary">Review Existing Scales</a>
    </div>
</section>

