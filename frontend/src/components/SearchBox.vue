<template>
  <div class="search-box">
    <label>Опишите нужный компонент:</label>
    <p class="hint">Примеры: "уголок 1/2 BSP", "фитинг DKOL M18 гайка"</p>

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
        {{ loading ? 'Поиск...' : 'Найти' }}
      </button>
      <button @click="clear" :disabled="loading">Очистить</button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  loading: Boolean
});

const emit = defineEmits(['search']);

const query = ref('');

const submit = () => {
  if (!query.value.trim()) return;
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
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
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
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 18px;
  resize: vertical;
  min-height: 200px;
  max-height: 400px;
  font-family: inherit;
  box-sizing: border-box;
  line-height: 1.5;
}

textarea:focus {
  outline: none;
  border-color: #4562e4;
  box-shadow: 0 0 0 3px rgba(69, 98, 228, 0.1);
}

.actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.primary {
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
  flex: 1 1 auto;
  min-width: 180px;
}

button:not(.primary) {
  background: #f0f0f0;
  color: #555;
  flex: 0 1 auto;
}

button {
  padding: 14px 28px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.2s ease, box-shadow 0.2s ease;
}

button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Адаптивность для мобильных устройств */
@media (max-width: 600px) {
  .search-box {
    padding: 15px;
  }

  textarea {
    min-height: 150px;
    font-size: 16px;
    padding: 15px;
  }

  .actions {
    flex-direction: column;
  }

  .primary, button:not(.primary) {
    width: 100%;
    flex: none;
    padding: 12px 20px;
  }
}
</style>