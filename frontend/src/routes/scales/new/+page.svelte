<script lang="ts">
    import { enhance } from '$app/forms';
    import { resolve } from '$app/paths';
    //import type { components } from '$lib/api/schema'
    let { form } = $props();
    let isSubmitting = $state(false);

    let equivalences = $state([
        {
            origin_grade: '',
            spanish_grade_1_4: '',
            spanish_grade_5_10: '',
            spanish_literal: ''
        }
    ]);

    const spanishLiteralOptions = [
        'APROBADO',
        'NOTABLE',
        'SOBRESALIENTE',
        'MATRICULA DE HONOR'
    ];

    function addEquivalence() {
        equivalences = [...equivalences, {
            origin_grade: '',
            spanish_grade_1_4: '',
            spanish_grade_5_10: '',
            spanish_literal: ''
        }];
    }

    function removeEquivalence(index: number) {
        if (equivalences.length <= 1) {
            return;
        }
        equivalences = equivalences.filter((_, i) => i !== index);
    }
</script>

<svelte:head>
    <title>New Scale | Grade Converter</title>
</svelte:head>

<section class="page-intro">
    <div>
        <p class="eyebrow">New Scale</p>
        <h1>Create a new scale</h1>
        <p class="lead">
            Capture the grading structure and map each origin grade to its Spanish
            equivalence.
        </p>
    </div>
    <div class="actions">
        <a href={resolve('/scales')} class="btn-secondary">Back to Scales</a>
    </div>
</section>

{#if form?.success}
    <div class="save-confirm" role="status" aria-live="polite">
        <span class="save-confirm__icon" aria-hidden="true">✓</span>
        <div class="save-confirm__body">
            <h2 class="save-confirm__title">Scale saved</h2>
            <p class="save-confirm__text">
                {form.countryName} is ready with {form.equivalenceCount}
                {form.equivalenceCount === 1 ? 'equivalence' : 'equivalences'} mapped.
            </p>
            <div class="save-confirm__actions">
                <a class="btn-primary" href={resolve(`/scales/${form.scaleId}`)}>View scale</a>
                <a class="btn-secondary" href={resolve('/scales/new')} data-sveltekit-reload>
                    Create another
                </a>
            </div>
        </div>
    </div>
{/if}
{#if form?.error}
    <div class="form-errors" role="alert">{form.error}</div>
{/if}

<form
    method="POST"
    action="?/createScale"
    class="form-shell"
    use:enhance={() => {
        isSubmitting = true;
        return async ({ update }) => {
            await update();
            isSubmitting = false;
        };
    }}>
    <section class="card form-card">
        <header>
            <h2>Scale details</h2>
            <p class="lead">Describe the origin grading system.</p>
        </header>
        <div class="form-grid">
            <label class="field">
                <span>Country name</span>
                <input name="country_name" required placeholder="e.g., Chile" />
            </label>

            <label class="field">
                <span>Scale description</span>
                <input
                    name="scale_description"
                    placeholder="e.g., Min grade - max grade"
                    required />
            </label>
        </div>
    </section>

    <section class="card form-card">
        <header>
            <h2>Scale equivalences</h2>
            <p class="lead">Add as many equivalences as necessary.</p>
        </header>
        {#each equivalences as eq, index (index)}
            <div class="equivalence-row">
                <div class="row-header">
                    <strong>Equivalence {index + 1}</strong>
                    <button
                        type="button"
                        class="btn-danger"
                        onclick={() => removeEquivalence(index)}
                        disabled={equivalences.length <= 1}
                        aria-label={`Remove equivalence ${index + 1}`}>
                        Remove
                    </button>
                </div>
                <label class="field">
                    <span>Origin grade</span>
                    <input name="origin_grade" bind:value={eq.origin_grade} required />
                </label>

                <label class="field">
                    <span>Spanish grade (1-4)</span>
                    <input
                        name="spanish_grade_1_4"
                        bind:value={eq.spanish_grade_1_4}
                        placeholder="Optional" />
                </label>

                <label class="field">
                    <span>Spanish grade (5-10)</span>
                    <input name="spanish_grade_5_10" bind:value={eq.spanish_grade_5_10} required />
                </label>

                <label class="field">
                    <span>Spanish literal</span>
                    <select name="spanish_literal" bind:value={eq.spanish_literal} required>
                        <option value="" disabled>Select literal</option>
                        {#each spanishLiteralOptions as option (option)}
                            <option value={option}>{option}</option>
                        {/each}
                    </select>
                </label>
            </div>
        {/each}

        <div class="row-actions">
            <button type="button" class="btn-tertiary" onclick={addEquivalence}>
                Add equivalence
            </button>
        </div>
    </section>

    <div class="row-actions">
        <button type="submit" class="btn-primary" disabled={isSubmitting}>
            {isSubmitting ? 'Saving...' : 'Save scale'}
        </button>
        <a href={resolve('/scales')} class="btn-secondary">Cancel</a>
    </div>
</form>

<style>
    .save-confirm {
        display: flex;
        gap: 1rem;
        align-items: flex-start;
        padding: 1.2rem 1.4rem;
        margin-bottom: 1.6rem;
        border-radius: var(--radius-md);
        border: 1px solid color-mix(in srgb, var(--success) 45%, var(--border));
        background: color-mix(in srgb, var(--success) 12%, var(--surface));
        animation: fade-up 0.4s ease both;
    }

    .save-confirm__icon {
        flex: none;
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-weight: 700;
        color: var(--success);
        background: color-mix(in srgb, var(--success) 22%, transparent);
        border: 1px solid color-mix(in srgb, var(--success) 45%, var(--border));
    }

    .save-confirm__title {
        margin: 0 0 0.25rem;
        font-size: 1.25rem;
    }

    .save-confirm__text {
        margin: 0 0 0.95rem;
        color: var(--muted);
    }

    .save-confirm__actions {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
    }
</style>
