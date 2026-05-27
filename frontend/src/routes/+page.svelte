<script lang="ts">
	import { resolve } from '$app/paths';
</script>

<div class="page">
	<section class="hero">
		<div>
			<p class="eyebrow">Academic services</p>
			<h1 class="page-title">Grade Converter</h1>
			<p class="page-subtitle">
				Internal workspace for managing grading scales and translation rules with clear
				institutional oversight.
			</p>
			<div class="hero-actions">
				<a class="btn btn-primary" href={resolve('/scales')}>View scales</a>
				<a class="btn btn-secondary" href={resolve('/scales/new')}>Create scale</a>
			</div>
		</div>
		<div class="card hero-card">
			<div class="card-body">
				<h2 class="card-title">Quick start</h2>
				<p class="card-subtitle">Keep equivalence data clean and consistent.</p>
				<ul class="hero-list">
					<li>Review existing grading scales for clarity and coverage.</li>
					<li>Add new equivalences with origin and Spanish grade mapping.</li>
					<li>Keep descriptions short for faster cross-team review.</li>
				</ul>
			</div>
		</div>
	</section>
</div>
