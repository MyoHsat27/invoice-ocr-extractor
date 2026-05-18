<script lang="ts">
  import type { ExtractedInvoice } from '$lib/types/invoice';

  export let invoice: ExtractedInvoice;
  export let onChange: () => void = () => {};

  function toNumber(value: string): number | null {
    if (value.trim() === '') return null;
    const numberValue = Number(value);
    return Number.isFinite(numberValue) ? numberValue : null;
  }
</script>

<div class="grid">
  <label>
    Vendor
    <input bind:value={invoice.vendor_name} on:input={onChange} />
  </label>
  <label>
    Invoice #
    <input bind:value={invoice.invoice_number} on:input={onChange} />
  </label>
  <label>
    Invoice date
    <input bind:value={invoice.invoice_date} on:input={onChange} />
  </label>
  <label>
    Due date
    <input bind:value={invoice.due_date} on:input={onChange} />
  </label>
  <label>
    Currency
    <input bind:value={invoice.currency} on:input={onChange} />
  </label>
  <label>
    Subtotal
    <input
      value={invoice.subtotal ?? ''}
      on:input={(event) => {
        invoice.subtotal = toNumber(event.currentTarget.value);
        onChange();
      }}
    />
  </label>
  <label>
    Tax
    <input
      value={invoice.tax ?? ''}
      on:input={(event) => {
        invoice.tax = toNumber(event.currentTarget.value);
        onChange();
      }}
    />
  </label>
  <label>
    Total
    <input
      value={invoice.total ?? ''}
      on:input={(event) => {
        invoice.total = toNumber(event.currentTarget.value);
        onChange();
      }}
    />
  </label>
</div>
