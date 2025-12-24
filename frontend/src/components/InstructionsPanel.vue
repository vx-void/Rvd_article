<template>
  <section class="instruction-container">
    <div class="instructions" @click="$emit('toggle')">
      <h2 class="instruction-title">Инструкция</h2>
      <span class="toggle-icon">{{ isExpanded ? '▼' : '▶' }}</span>
    </div>
    <div v-if="isExpanded" class="instruction-content">
      <ul class="instruction-list">
        <li>Вставьте текст в поле ввода ниже</li>
        <li>Нажмите кнопку "Найти артикулы" для поиска</li>
        <li>Используйте "Очистить Ввод" для очистки поля</li>
        <li>Найденные артикулы будут отображены в списке</li>
      </ul>
    </div>
  </section>
</template>

<script setup>
defineProps({
  isExpanded: Boolean
})

defineEmits(['toggle'])
</script>