<script lang="ts">
  export let busy = false;
  export let selectedFile: File | null = null;
  export let onFileChange: (file: File | null) => void;
  export let onUpload: () => void;
</script>

<div class="upload-box">
  <label for="invoice-file">Upload invoice</label>
  <input
    id="invoice-file"
    type="file"
    accept=".txt,.pdf,.png,.jpg,.jpeg,.tif,.tiff,.bmp,text/plain,application/pdf,image/*"
    disabled={busy}
    on:change={(event) => onFileChange(event.currentTarget.files?.[0] || null)}
  />
  <button class="primary" disabled={busy || !selectedFile} on:click={onUpload}>
    {busy ? 'Working' : 'Extract'}
  </button>
</div>

