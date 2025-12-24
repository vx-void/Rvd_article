<template>
  <button @click="exportToExcel" class="btn btn-excel">
    <span class="excel-icon">📊</span>
    скачать .xlsx
  </button>
</template>

<script setup>
const emit = defineEmits(['export'])

const exportToExcel = () => {
  emit('export')
}
</script>

<style scoped>
.btn-excel {
  background-color: #28a745;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-excel:hover {
  background-color: #218838;
}

.excel-icon {
  font-size: 1.2rem;
}
</style>