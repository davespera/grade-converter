<script lang="ts">
    import { enhance } from "$app/forms";
    import { resolve } from "$app/paths";
    import type { PageData } from "./$types";

    let { data, form }: { data: PageData; form?: { success?: number; error?: string } } = $props();
    let isSubmitting = $state(false);

    let equivalences = $state([
        {
            origin_grade: "",
            spanish_grade_1_4: "",
            spanish_grade_5_10: "",
            spanish_literal: ""
        }
    ]);

    const spanishLiteralOptions = [
        "APROBADO",
        "NOTABLE",
        "SOBRESALIENTE",
        "MATRICULA"
    ];

    function addEquivalence() {
        equivalences = [
            ...equivalences,
            {
                origin_grade: "",
                spanish_grade_1_4: "",
                spanish_grade_5_10: "",
                spanish_literal: ""
            }
        ];
    }

    function removeEquivalence(index: number) {
        if (equivalences.length <= 1) {
            return;
        }
        equivalences = equivalences.filter((_, i) => i !== index);
    }
</script>

<section class="page-intro">
    <div>
        <p class="eyebrow">Add Equivalence</p>
        <h1>{data?.scale?.country_name ?? "Scale"} equivalences</h1>
        <p class="lead">
            {data?.scale?.scale_description ?? "Add grade mappings to the selected scale."}
        </p>
    </div>
    <div class="actions">
        <a href={resolve("/scales")} class="btn-secondary">Back to Scales</a>
    </div>
</section>

{#if form?.error}
    <div class="form-errors">{form.error}</div>
{/if}
{#if form?.success}
    <div class="success-banner">
        Added {form.success} equivalence{form.success === 1 ? "" : "s"}.
    </div>
{/if}

<form
    method="POST"
    action="?/addEquivalences"
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
            <h2>Equivalences</h2>
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
                        disabled={equivalences.length <= 1}>
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
                    <input
                        name="spanish_grade_5_10"
                        bind:value={eq.spanish_grade_5_10}
                        required />
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
            {isSubmitting ? "Saving..." : "Save equivalences"}
        </button>
        <a href={resolve("/scales")} class="btn-secondary">Cancel</a>
    </div>
</form>
