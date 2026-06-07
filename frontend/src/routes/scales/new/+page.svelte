<script lang="ts">
    import { enhance } from '$app/forms';
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
        'MATRICULA'
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
        equivalences = equivalences.filter((_, i) => i !== index);
    }
</script>

<svelte:head>
    <title>New Scale | Grade Converter</title>
</svelte:head>

<div class="page">
    <div class="page-header">
        <div>
            <h1 class="page-title">Create a new scale</h1>
            <p class="page-subtitle">
                Capture the grading structure and map each origin grade to its Spanish
                equivalence.
            </p>
        </div>
    </div>

    {#if form?.success}
        <div class="status status-success" role="status">Saved: {form.success}</div>
    {/if}
    {#if form?.error}
        <div class="status status-error" role="alert">Error: {form.error}</div>
    {/if}

    <form
        method="POST"
        action="?/createScale"
        class="form-stack"
        use:enhance={() => {
            isSubmitting = true;
            return async ({ update }) => {
                await update();
                isSubmitting = false;
            };
        }}>
        <section class="card">
            <header class="card-header">
                <div>
                    <h2 class="card-title">Scale details</h2>
                    <p class="card-subtitle">Describe the origin grading system.</p>
                </div>
            </header>
            <div class="card-body form-grid">
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

        <section class="card">
            <header class="card-header">
                <div>
                    <h2 class="card-title">Scale equivalences</h2>
                    <p class="card-subtitle">Add as many equivalences as necessary.</p>
                </div>
            </header>
            <div class="card-body">
                {#each equivalences as eq, index (index)}
                    <div class="equivalence-row">
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
                    <div class="equivalence-actions">
                        <button type="button" class="btn btn-ghost" onclick={() => removeEquivalence(index)}>
                            Remove row
                        </button>
                    </div>
                {/each}

                <div class="equivalence-actions">
                    <button type="button" class="btn btn-secondary" onclick={addEquivalence}>
                        Add equivalence
                    </button>
                </div>
            </div>
        </section>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Saving...' : 'Save scale'}
            </button>
        </div>
        <br>
        <button type="submit" class="submit-btn" disabled={isSubmitting}>
            Save Scale
        </button>
</form>

</div>
