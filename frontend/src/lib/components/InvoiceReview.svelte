<script lang="ts">
  import type { InvoiceDraft } from '$lib/types/invoice';
  import InvoiceFields from './InvoiceFields.svelte';
  import LineItemsEditor from './LineItemsEditor.svelte';
  import RawTextPanel from './RawTextPanel.svelte';
  import WarningsPanel from './WarningsPanel.svelte';

  export let selected: InvoiceDraft | null = null;
  export let busy = false;
  export let onReprocess: () => void;
  export let onSave: () => void;
  export let onChange: () => void;
</script>

{#if selected}
  <div class="review-header">
    <div>
      <p class="eyebrow">{selected.filename}</p>
      <h2>{selected.extracted.vendor_name || 'Unverified invoice'}</h2>
    </div>
    <div class="actions">
      <button disabled={busy} on:click={onReprocess}>Reprocess</button>
      <button class="primary" disabled={busy} on:click={onSave}>Save review</button>
    </div>
  </div>

  <InvoiceFields invoice={selected.extracted} {onChange} />
  <LineItemsEditor items={selected.extracted.line_items} {onChange} />

  <section class="split">
    <WarningsPanel warnings={selected.warnings} />
    <RawTextPanel rawText={selected.raw_text} />
  </section>
{:else}
  <div class="blank">
    <h2>Upload an invoice to start extraction.</h2>
  </div>
{/if}
