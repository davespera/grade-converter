<script lang="ts">
    import { enhance } from '$app/forms';
    //import type { components } from '$lib/api/schema'
    let { form } = $props();
    let isSubmitting = false;

    let equivalences = $state([
        {
            origin_grade: '',
            spanish_grade_1_4: '',
            spanish_grade_5_10: '',
            spanish_literal: ''
        }
    ]);

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

<h1>Create New Scale & Associated Equivalences</h1>

{#if form?.success}
    <p class="success">OK {form.success}</p>
{/if}

<form method="POST" action="?/createScale" use:enhance={() => {
    isSubmitting = true;
    return async ({ update }) => {
      await update();
      isSubmitting = false;
    };
  }}>

    <div class="form-select">
        <label>
            Country Name
            <input name="country_name" required />
        </label>

        <label>
            Scale Description
            <input name="scale_description" placeholder="e.g., Min Grade - Max Grade" required />
        </label>
            
        <label>
            Total Number of Grades
            <input name="total_grades" />
        </label>
    </div>

    <div class="form-select">
        <h2>Scale Equivalences</h2>
        <p class="subtitle">Add as many equivalences as necessary</p>

        <div class="row-container">
            {#each equivalences as eq, index (index)}
                <div class="equivalence-row">
                    <label>
                        Origin Grade
                        <input name="origin_grade" bind:value={eq.origin_grade} required>
                    </label>

                    <label>
                        Spanish Grade (1-4)
                        <input name="spanish_grade_1_4" bind:value={eq.spanish_grade_1_4} required>
                    </label>

                    <label>
                        Sapnish Grade (5-10)
                        <input name="spanish_grade_5_10" bind:value={eq.spanish_grade_5_10} required>
                    </label>

                    <label>
                        Spanish Literal
                        <input name="spanish_literal" bind:value={eq.spanish_literal} required>
                    </label>
                </div>

                <button
                    type="button"
                    class="delete-btn"
                    onclick={() => removeEquivalence(index)}>
                    Remove Row
                </button>
            {/each}

            <button
                type="button"
                class="add-btn"
                onclick={addEquivalence}>
                Add Equivalence
            </button>
        </div>
        <br>
        <button type="submit" class="submit-btn" disabled={isSubmitting}>
            Save Scale
        </button>
    </div>

</form>    

<style>
  form { display: grid; gap: 0.6rem; max-width: 40rem; }
  label { display: grid; gap: 0.25rem; }
  .success { color: #0a7; }
</style>