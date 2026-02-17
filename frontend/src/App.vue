<template>
  <div class="app">
    <!-- Header -->
    <header class="header">
        <h1>Hydro Search</h1>
    </header>

    <!-- Main -->
    <main class="container">
      <!-- Сворачиваемое меню инструкции -->
      <div class="instruction-wrapper">
        <div class="instruction-header" @click="toggleInstructions">
          <h2>📋 Инструкция</h2>
          <span class="toggle-icon">{{ instructionsVisible ? '▼' : '▶' }}</span>
        </div>

        <Transition name="slide">
          <div v-if="instructionsVisible" class="instruction-content">
            <div class="instruction-item">
              <span class="bullet">•</span>
              <span>Вставьте текст в поле ввода ниже</span>
            </div>
            <div class="instruction-item">
              <span class="bullet">•</span>
              <span>Нажмите кнопку "Найти компоненты" для поиска</span>
            </div>
            <div class="instruction-item">
              <span class="bullet">•</span>
              <span>Используйте "Очистить" для очистки поля</span>
            </div>
            <div class="instruction-item">
              <span class="bullet">•</span>
              <span>Найденные компоненты будут отображены в списке</span>
            </div>
          </div>
        </Transition>
      </div>

      <!-- Блок поиска -->
      <div class="search-section">
        <div class="search-label">Введите запрос</div>
        <SearchBox
          @search="handleSearch"
          :loading="loading"
        />
      </div>

      <ExtractedParams
        v-if="extractedParams && !loading"
        :params="extractedParams"
      />

      <!-- Loading -->
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Обработка запроса...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="error-box">
        <p>{{ error }}</p>
        <button @click="error = null">Закрыть</button>
      </div>

      <!-- Results -->
      <SearchResults
        v-else-if="results.length"
        :results="results"
        :metrics="metrics"
        @export="exportResults"
      />

      <!-- No Results -->
      <div v-else-if="searched" class="no-results">
        <p>Ничего не найдено</p>
        <div class="examples">
          <p>Примеры:</p>
          <button
            v-for="ex in examples"
            :key="ex"
            @click="searchExample(ex)"
          >
            {{ ex }}
          </button>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>Created by S V A</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SearchBox from './components/SearchBox.vue';
import SearchResults from './components/SearchResults.vue';
import ExtractedParams from './components/ExtractedParams.vue';
import { search, exportToExcel } from './services/api.js';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const loading = ref(false);
const error = ref(null);
const results = ref([]);
const metrics = ref(null);
const extractedParams = ref(null);
const searched = ref(false);
const isOnline = ref(false);
const serverStats = ref(null);
const instructionsVisible = ref(true); // По умолчанию развернут

const examples = [
  'уголок 1/2 BSP папа',
  'фитинг DKOL M18 гайка',
  'переходник BSP-DKOS 1/2-M22',
  'заглушка 3/8 дюйма',
];


const toggleInstructions = () => {
  instructionsVisible.value = !instructionsVisible.value;
};

const handleSearch = async (query) => {
  loading.value = true;
  error.value = null;
  searched.value = true;

  try {
    const data = await search(query);
    results.value = data.results;
    metrics.value = data.metrics;
    extractedParams.value = data.extracted_params;
  } catch (err) {
    error.value = err.message;
    results.value = [];
  } finally {
    loading.value = false;
  }
};

const searchExample = (ex) => {
  handleSearch(ex);
};

const exportResults = () => {
  exportToExcel(results.value, metrics.value?.query || 'search');
};
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
  padding: 20px 0;
  text-align: center;
}

.header h1 {
  font-size: 32px;
  margin: 0;
}

.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 40px;
  flex: 1;
  box-sizing: border-box;
}

/* Стили для сворачиваемой инструкции */
.instruction-wrapper {
  margin-bottom: 25px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.instruction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #f5f5f5;
  cursor: pointer;
  user-select: none;
  transition: background 0.2s ease;
  border-bottom: 1px solid #e0e0e0;
}

.instruction-header:hover {
  background: #e8e8e8;
}

.instruction-header h2 {
  font-size: 18px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.toggle-icon {
  font-size: 14px;
  color: #666;
  transition: transform 0.2s ease;
}

.instruction-content {
  padding: 15px 20px;
  background: white;
}

.instruction-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  color: #555;
  font-size: 15px;
  line-height: 1.5;
}

.instruction-item:last-child {
  margin-bottom: 0;
}

.bullet {
  color: #4562e4;
  font-weight: bold;
  font-size: 18px;
  line-height: 1;
}

/* Стили для секции поиска */
.search-section {
  margin-bottom: 20px;
}

.search-label {
  font-size: 16px;
  font-weight: 500;
  color: #555;
  margin-bottom: 8px;
  padding-left: 5px;
}

/* Анимация сворачивания/разворачивания */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
  max-height: 200px;
  overflow: hidden;
}

.slide-enter-from,
.slide-leave-to {
  max-height: 0;
  opacity: 0;
  padding: 0 20px;
}

/* Адаптивность */
@media (min-width: 1600px) {
  .container {
    max-width: 1600px;
    padding: 20px 60px;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 15px 20px;
  }

  .header h1 {
    font-size: 28px;
  }

  .instruction-header h2 {
    font-size: 16px;
  }

  .instruction-item {
    font-size: 14px;
  }
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4562e4;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-box {
  background: #ffebee;
  border: 1px solid #ffcdd2;
  color: #c62828;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.no-results {
  text-align: center;
  padding: 50px;
  color: #888;
}

.examples {
  margin-top: 20px;
}

.examples p {
  margin-bottom: 10px;
  color: #666;
}

.examples button {
  display: inline-block;
  margin: 5px;
  padding: 10px 15px;
  background: #f0f0f0;
  color: #555;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.examples button:hover {
  transform: translateY(-2px);
}

.footer {
  text-align: center;
  padding: 30px;
  color: #888;
  font-size: 14px;
}

button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
  transition: transform 0.2s ease;
}

button:hover {
  transform: translateY(-2px);
}
</style>