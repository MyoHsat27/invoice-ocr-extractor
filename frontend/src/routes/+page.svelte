<script lang="ts">
  import { getInvoice, listInvoices, reprocessInvoice, saveInvoice, uploadInvoice } from '$lib/api/invoices';
  import AppHeader from '$lib/components/AppHeader.svelte';
  import InvoiceList from '$lib/components/InvoiceList.svelte';
  import InvoiceReview from '$lib/components/InvoiceReview.svelte';
  import UploadPanel from '$lib/components/UploadPanel.svelte';
  import type { InvoiceDraft, InvoiceSummary } from '$lib/types/invoice';

  let invoices: InvoiceSummary[] = [];
  let selected: InvoiceDraft | null = null;
  let selectedFile: File | null = null;
  let busy = false;
  let message = '';
  let error = '';

  async function loadInvoices() {
    error = '';
    invoices = await listInvoices();
    if (!selected && invoices.length > 0) {
      await openInvoice(invoices[0].id);
    }
  }

  async function openInvoice(id: string) {
    error = '';
    selected = await getInvoice(id);
  }

  async function handleUpload() {
    if (!selectedFile) {
      error = 'Choose an invoice file first.';
      return;
    }

    busy = true;
    error = '';
    message = 'Extracting invoice fields...';

    try {
      selected = await uploadInvoice(selectedFile);
      selectedFile = null;
      message = 'Draft created. Review the fields before saving.';
      await loadInvoices();
    } catch (caught) {
      error = caught instanceof Error ? caught.message : 'Upload failed.';
    } finally {
      busy = false;
    }
  }

  async function handleSave() {
    if (!selected) return;

    busy = true;
    error = '';
    message = 'Saving reviewed invoice...';

    try {
      selected = await saveInvoice(selected);
      message = 'Reviewed invoice saved.';
      await loadInvoices();
    } catch (caught) {
      error = caught instanceof Error ? caught.message : 'Save failed.';
    } finally {
      busy = false;
    }
  }

  async function handleReprocess() {
    if (!selected) return;

    busy = true;
    error = '';
    message = 'Reprocessing original document evidence...';

    try {
      selected = await reprocessInvoice(selected.id);
      message = 'Extraction refreshed from stored evidence.';
      await loadInvoices();
    } catch (caught) {
      error = caught instanceof Error ? caught.message : 'Reprocess failed.';
    } finally {
      busy = false;
    }
  }

  function refreshSelected() {
    selected = selected;
  }

  loadInvoices().catch((caught) => {
    error = caught instanceof Error ? caught.message : 'Could not load invoices.';
  });
</script>

<svelte:head>
  <title>Invoice Review Agent</title>
</svelte:head>

<main class="shell">
  <AppHeader invoiceCount={invoices.length} {selected} />

  <section class="workspace">
    <aside class="rail">
      <UploadPanel
        {busy}
        {selectedFile}
        onFileChange={(file) => (selectedFile = file)}
        onUpload={handleUpload}
      />
      <InvoiceList {invoices} {selected} onOpen={openInvoice} />
    </aside>

    <section class="review">
      {#if message}
        <p class="notice">{message}</p>
      {/if}
      {#if error}
        <p class="error">{error}</p>
      {/if}

      <InvoiceReview
        {selected}
        {busy}
        onReprocess={handleReprocess}
        onSave={handleSave}
        onChange={refreshSelected}
      />
    </section>
  </section>
</main>
