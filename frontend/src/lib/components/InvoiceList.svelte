<script lang="ts">
  import type { InvoiceDraft, InvoiceSummary } from '$lib/types/invoice';

  export let invoices: InvoiceSummary[] = [];
  export let selected: InvoiceDraft | null = null;
  export let onOpen: (id: string) => void;
</script>

<div class="list">
  {#each invoices as invoice}
    <button
      class:active={selected?.id === invoice.id}
      class="invoice-row"
      on:click={() => onOpen(invoice.id)}
    >
      <span>{invoice.vendor_name || invoice.filename}</span>
      <small>{invoice.invoice_number || invoice.status}</small>
      <strong>{invoice.total === null ? '-' : `${invoice.currency} ${invoice.total}`}</strong>
    </button>
  {:else}
    <p class="empty">No drafts yet.</p>
  {/each}
</div>

