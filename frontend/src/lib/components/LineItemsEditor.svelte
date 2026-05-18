<script lang="ts">
  import type { InvoiceLineItem } from '$lib/types/invoice';

  export let items: InvoiceLineItem[] = [];
  export let onChange: () => void;

  function toNumber(value: string): number | null {
    if (value.trim() === '') return null;
    const numberValue = Number(value);
    return Number.isFinite(numberValue) ? numberValue : null;
  }

  function addLineItem() {
    items.push({
      description: '',
      quantity: null,
      unit_price: null,
      amount: null
    });
    onChange();
  }

  function removeLineItem(index: number) {
    items.splice(index, 1);
    onChange();
  }
</script>

<section class="line-items">
  <div class="section-head">
    <h3>Line items</h3>
    <button on:click={addLineItem}>Add row</button>
  </div>
  {#each items as item, index}
    <div class="line-row">
      <input placeholder="Description" bind:value={item.description} on:input={onChange} />
      <input
        placeholder="Qty"
        value={item.quantity ?? ''}
        on:input={(event) => {
          item.quantity = toNumber(event.currentTarget.value);
          onChange();
        }}
      />
      <input
        placeholder="Unit"
        value={item.unit_price ?? ''}
        on:input={(event) => {
          item.unit_price = toNumber(event.currentTarget.value);
          onChange();
        }}
      />
      <input
        placeholder="Amount"
        value={item.amount ?? ''}
        on:input={(event) => {
          item.amount = toNumber(event.currentTarget.value);
          onChange();
        }}
      />
      <button class="icon" aria-label="Remove row" on:click={() => removeLineItem(index)}>×</button>
    </div>
  {/each}
</section>

