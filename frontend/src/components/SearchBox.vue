<template>
  <div class="search-box">
    <label>Опишите нужный компонент:</label>
    <p class="hint">Примеры: "уголок 1/2 BSP папа", "фитинг DKOL M18 гайка"</p>

    <textarea
      v-model="query"
      placeholder="Введите описание компонента..."
      :disabled="loading"
      @keydown.ctrl.enter="submit"
    ></textarea>

    <div class="actions">
      <button
        @click="submit"
        :disabled="loading || !query.trim()"
        class="primary"
      >
        {{ loading ? 'Поиск...' : 'Найти компоненты' }}
      </button>
      <button @click="clear" :disabled="loading">Очистить</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  loading: Boolean
});

const emit = defineEmits(['search']);

const query = ref('');

const submit = () => {
  if (!query.value.trim() || props.loading) return;
  emit('search', query.value);
};

const clear = () => {
  query.value = '';
};
</script>

<style scoped>
.search-box {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.hint {
  color: #888;
  font-size: 13px;
  margin-bottom: 12px;
}

textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  resize: vertical;
  min-height: 120px;
  font-family: inherit;
}

textarea:focus {
  outline: none;
  border-color: #4562e4;
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 15px;
}

.primary {
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
}

button:not(.primary) {
  background: #f0f0f0;
  color: #555;
}
</style>