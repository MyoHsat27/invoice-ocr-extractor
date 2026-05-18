<script lang="ts">
  export let warnings: string[] = [];
</script>

<div>
  <h3>Warnings</h3>
  {#each warnings as warning}
    <p class="warning">{warning}</p>
  {:else}
    <p class="quiet">No validation warnings.</p>
  {/each}
</div>

