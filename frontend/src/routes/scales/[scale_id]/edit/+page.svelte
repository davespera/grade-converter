<script lang="ts">
	import { enhance } from '$app/forms';
	import { resolve } from '$app/paths';
	import type { PageData } from './$types';

	let { data, form }: { data: PageData; form?: { error?: string } } = $props();
	const scale = $derived(data.scale);
	let isSubmitting = $state(false);
</script>

<section class="page-intro">
	<div>
		<p class="eyebrow">Edit Scale</p>
		<h1>{scale?.country_name ?? 'Scale'}</h1>
		<p class="lead">Update the scale details without leaving the grading library.</p>
	</div>
	<div class="actions">
		<a href={resolve(`/scales/${scale?.id}`)} class="btn-secondary">Back to scale</a>
	</div>
</section>

{#if form?.error}
	<div class="form-errors">{form.error}</div>
{/if}

<form
	method="POST"
	action="?/updateScale"
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
			<p class="lead">Change the country name, description, or total grade count.</p>
		</header>
		<div class="form-grid">
			<label class="field">
				<span>Country name</span>
				<input name="country_name" value={scale?.country_name ?? ''} required />
			</label>

			<label class="field">
				<span>Scale description</span>
				<input name="scale_description" value={scale?.scale_description ?? ''} required />
			</label>

			<label class="field">
				<span>Total grades</span>
				<input
					name="total_grades"
					type="number"
					min="1"
					step="1"
					value={scale?.total_grades ?? ''}
					placeholder="Optional" />
			</label>
		</div>
	</section>

	<div class="row-actions">
		<button type="submit" class="btn-primary" disabled={isSubmitting}>
			{isSubmitting ? 'Saving...' : 'Save scale'}
		</button>
		<a href={resolve(`/scales/${scale?.id}`)} class="btn-secondary">Cancel</a>
	</div>
</form>