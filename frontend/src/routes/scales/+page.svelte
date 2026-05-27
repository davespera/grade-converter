<script lang="ts">
    import type { PageData } from "./$types";
    import { resolve } from '$app/paths';

    let { data }: { data : PageData } = $props();
</script>

<div class="page">
    <div class="page-header">
        <div>
            <h1 class="page-title">Scales</h1>
            <p class="page-subtitle">
                Review grading scales and ensure equivalence rules remain current across
                institutional partners.
            </p>
        </div>
        <a href={resolve('/scales/new')} class="btn btn-primary">Create new scale</a>
    </div>

    {#if data.scales?.length}
        <div class="card-grid">
            {#each data.scales as scale (scale.id)}
                <article class="card">
                    <header class="card-header">
                        <div>
                            <h2 class="card-title">{scale.country_name}</h2>
                            <p class="card-subtitle">{scale.scale_description}</p>
                        </div>
                        {#if scale.total_grades}
                            <span class="badge">{scale.total_grades} grades</span>
                        {:else}
                            <span class="badge">Flexible scale</span>
                        {/if}
                    </header>
                    <div class="card-body">
                        {#if scale.equivalences?.length}
                            <table class="table">
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
                                            <td>{equivalence.spanish_1_4 || '-'}</td>
                                            <td>{equivalence.spanish_5_10}</td>
                                            <td>{equivalence.spanish_literal}</td>
                                        </tr>
                                    {/each}
                                </tbody>
                            </table>
                        {:else}
                            <div class="status">No equivalences added yet.</div>
                        {/if}
                    </div>
                </article>
            {/each}
        </div>
    {:else}
        <div class="card">
            <div class="card-body">
                <h2 class="card-title">No scales yet</h2>
                <p class="card-subtitle">Create the first scale to start mapping equivalences.</p>
                <a href={resolve('/scales/new')} class="btn btn-primary">Create a scale</a>
            </div>
        </div>
    {/if}
</div>