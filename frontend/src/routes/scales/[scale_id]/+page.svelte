<script lang="ts">
	import { resolve } from '$app/paths';
	import type { PageData } from './$types';

	let { data, form }: { data: PageData; form?: { success?: string; error?: string } } = $props();
	const scale = $derived(data.scale);

	function confirmDelete(event: SubmitEvent, message: string) {
		if (!confirm(message)) {
			event.preventDefault();
		}
	}
</script>

<section class="page-intro">
	<div>
		<p class="eyebrow">Scale Detail</p>
		<h1>{scale?.country_name ?? 'Scale'}</h1>
		<p class="lead">{scale?.scale_description ?? 'Review and manage equivalences.'}</p>
	</div>
	<div class="actions">
		<a href={resolve('/scales')} class="btn-secondary">Back to Scales</a>
		<a href={resolve(`/scales/${scale?.id}/equivalences/new`)} class="btn-tertiary">Add equivalence</a>
		<form
			method="POST"
			action="?/deleteScale"
			onsubmit={(event) =>
				confirmDelete(
					event,
					`Delete ${scale?.country_name} scale? This removes all equivalences.`
				)
			}>
			<button type="submit" class="btn-danger">Delete scale</button>
		</form>
	</div>
</section>

{#if form?.error}
	<div class="form-errors">{form.error}</div>
{/if}
{#if form?.success}
	<div class="success-banner">{form.success}</div>
{/if}

<section class="card">
	<h2>Scale summary</h2>
	<p class="muted">Overview of the grading scale and its equivalences.</p>
	<div class="stats">
		<div class="stat">
			<strong>{scale?.total_grades ?? '-'}</strong>
			<span>Total grades</span>
		</div>
		<div class="stat">
			<strong>{scale?.equivalences?.length ?? 0}</strong>
			<span>Equivalences</span>
		</div>
	</div>
</section>

<section class="card">
	<h2>Equivalences</h2>
	{#if scale?.equivalences && scale.equivalences.length > 0}
		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>Origin</th>
						<th>Spanish 1-4</th>
						<th>Spanish 5-10</th>
						<th>Literal</th>
						<th class="action-col">Actions</th>
					</tr>
				</thead>
				<tbody>
					{#each scale.equivalences as equivalence (equivalence.id)}
						<tr>
							<td>{equivalence.origin_grade}</td>
							<td>{equivalence.spanish_1_4 ?? '-'}</td>
							<td>{equivalence.spanish_5_10 ?? '-'}</td>
							<td>{equivalence.spanish_literal ?? '-'}</td>
							<td class="action-col">
								<form
									method="POST"
									action="?/deleteEquivalence"
									onsubmit={(event) =>
										confirmDelete(
											event,
											`Delete ${equivalence.origin_grade} equivalence?`
										)
									}>
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
</section>
