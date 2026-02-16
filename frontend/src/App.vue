<template>
  <div class="app">
    <!-- Header -->
    <header class="header">
      <div class="container">
        <h1>Hydro Search</h1>
        <p>Поиск гидравлических компонентов</p>
      </div>
    </header>

    <!-- Main -->
    <main class="container">
      <!-- API Key Input -->
      <div v-if="!apiKey" class="card">
        <h3>Введите API ключ</h3>
        <input
          v-model="tempApiKey"
          type="password"
          placeholder="API ключ..."
          @keyup.enter="saveApiKey"
        >
        <button @click="saveApiKey" :disabled="!tempApiKey">
          Сохранить
        </button>
        <p class="error" v-if="keyError">{{ keyError }}</p>
      </div>

      <!-- Search Interface -->
      <template v-else>
        <SearchBox
          @search="handleSearch"
          :loading="loading"
        />

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
          @export="exportToExcel"
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
      </template>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>Backend: FastAPI + ChromaDB | Frontend: Vue 3</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SearchBox from './components/SearchBox.vue';
import SearchResults from './components/SearchResults.vue';
import ExtractedParams from './components/ExtractedParams.vue';
import { useSearch } from './composables/useSearch.js';
import { useStorage } from './composables/useStorage.js';
import { useApi } from './composables/useApi.js';
import { exportToExcel } from './utils/formatters.js';

const API_KEY = useStorage('api-key', '');
const apiKey = ref(API_KEY.value);
const tempApiKey = ref('');
const keyError = ref('');

const { isOnline, serverStats, checkHealth } = useApi();
const { loading, error, results, metrics, extractedParams, searched, search } = useSearch(apiKey);

const examples = [
  'уголок 1/2 BSP папа',
  'фитинг DKOL M18 гайка',
  'переходник BSP-DKOS 1/2-M22',
];

onMounted(() => {
  checkHealth();
  setInterval(checkHealth, 30000);
});

const saveApiKey = () => {
  if (tempApiKey.value.length < 16) {
    keyError.value = 'Ключ слишком короткий';
    return;
  }
  API_KEY.value = tempApiKey.value;
  apiKey.value = tempApiKey.value;
  keyError.value = '';
};

const handleSearch = (query) => {
  search(query);
};

const searchExample = (ex) => {
  search(ex);
};
</script>

<style scoped>
.app { min-height: 100vh; display: flex; flex-direction: column; }

.header {
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
  padding: 0px;
  text-align: center;
}

.header h1 { font-size: 20px; margin-bottom: 0px; }
.header p { opacity: 0.9; }

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  flex: 1;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
  max-width: 500px;
  margin: 0 auto;
}

.card h3 { margin-bottom: 15px; color: #555; }

input {
  width: 100%;
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  margin-bottom: 12px;
}

input:focus {
  outline: none;
  border-color: #4562e4;
}

button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
  transition: transform 0.2s;
}

button:hover:not(:disabled) { transform: translateY(-2px); }
button:disabled { opacity: 0.6; cursor: not-allowed; }

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

@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

.error-box {
  background: #ffebee;
  border: 1px solid #ffcdd2;
  color: #c62828;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.error { color: #c62828; font-size: 14px; margin-top: 8px; }

.no-results {
  text-align: center;
  padding: 50px;
  color: #888;
}

.examples { margin-top: 20px; }
.examples p { margin-bottom: 10px; color: #666; }
.examples button {
  display: inline-block;
  margin: 5px;
  padding: 10px 15px;
  background: #f0f0f0;
  color: #555;
  font-size: 14px;
}

.footer {
  text-align: center;
  padding: 30px;
  color: #888;
  font-size: 14px;
}
</style>