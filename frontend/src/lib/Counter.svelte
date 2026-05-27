<script>
  // This is a normal JavaScript variable
  // but marked with $state so Svelte knows:
  // “when this changes, update the UI.”
  let count = $state(0);
</script>

<!-- Here we *use* that variable in the UI -->
<button onclick={() => count++}>
  Count: {count}
</button>