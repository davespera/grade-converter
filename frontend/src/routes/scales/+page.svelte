<script lang="ts">
    import type { PageData } from "./$types";

    let { data }: { data : PageData } = $props();
</script>

<h1>Scales</h1>

<ul>
    {#each data.scales as scale (scale.id)}
    <li><strong>{scale.country_name}</strong></li>
    <li>{scale.scale_description}</li>
        {#each scale.equivalences as equivalence (equivalence.id)}
        <li>{equivalence.origin_grade}</li>
        <li>{equivalence?.spanish_1_4}</li> <!-- 1-4 grade is optional -->
        <li>{equivalence.spanish_5_10}</li>
        <li>{equivalence.spanish_literal}</li>
        {/each}
    {/each}
</ul>