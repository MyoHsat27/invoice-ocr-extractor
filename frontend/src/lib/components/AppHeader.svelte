<script lang="ts">
  import type { InvoiceDraft } from '$lib/types/invoice';

  export let invoiceCount = 0;
  export let selected: InvoiceDraft | null = null;
</script>

<section class="topbar">
  <div>
    <h1>Invoice Review Agent</h1>
  </div>
  <div class="status-strip">
    <span>{invoiceCount} drafts</span>
    <span>{selected?.provider.model || 'model not run'}</span>
  </div>
</section>

