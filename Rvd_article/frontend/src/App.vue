<template>
  <div class="app">
    <!-- Заголовок -->
    <header class="header">
      <h1>Поиск гидравлических компонентов</h1>
      <div class="server-status" :class="{ online: store.serverOnline }">
        {{ store.serverOnline ? '✅ Сервер онлайн' : '❌ Сервер недоступен' }}
      </div>
    </header>

    <!-- Основной контент -->
    <main class="main">
      <!-- Инструкции -->
      <Instructions 
        v-if="store.showInstructions"
        @close="actions.toggleInstructions"
      />
      
      <!-- Кнопка показа инструкций -->
      <button 
        v-else
        @click="actions.toggleInstructions"
        class="btn-instructions"
      >
        📘 Показать инструкции
      </button>

      <!-- Форма поиска -->
      <SearchForm 
        v-model:text="searchText"
        :loading="store.loading"
        @search="handleSearch"
        @clear="actions.clearAll"
      />

      <!-- Загрузка -->
      <div v-if="store.loading" class="loading">
        <div class="spinner"></div>
        <p>{{ store.loadingMessage }}</p>
      </div>

      <!-- Ошибка -->
      <div v-if="store.error" class="error">
        <p>❌ {{ store.error }}</p>
        <button @click="actions.setError(null)">Закрыть</button>
      </div>

      <!-- Результаты -->
      <SearchResults 
        v-if="getters.hasResults"
        :results="store.results"
      />

      <!-- Нет результатов -->
      <div 
        v-else-if="store.results.length === 0 && store.searchText && !store.loading"
        class="no-results"
      >
        <p>Ничего не найдено. Попробуйте другой запрос.</p>
        
        <!-- Примеры запросов -->
        <div class="examples">
          <p>Примеры для теста:</p>
          <button @click="searchText = 'Фитинг 1/2 BSP'; handleSearch()">
            Фитинг 1/2 BSP
          </button>
          <button @click="searchText = 'Неизвестный компонент'; handleSearch()">
            Неизвестный компонент
          </button>
        </div>
      </div>
      
      <!-- История поисков -->
      <div v-if="store.searchHistory.length > 0 && !store.loading && !getters.hasResults" class="history">
        <h4>История поиска:</h4>
        <div class="history-items">
          <button 
            v-for="item in store.searchHistory.slice(0, 5)" 
            :key="item.id"
            @click="searchText = item.text; handleSearch()"
            class="history-item"
          >
            {{ item.text.substring(0, 30) }}{{ item.text.length > 30 ? '...' : '' }}
            <small>{{ new Date(item.date).toLocaleDateString() }}</small>
          </button>
        </div>
      </div>
    </main>

    <!-- Подвал -->
    <footer class="footer">
      <p>Всего найдено: {{ getters.totalFound }} | Не найдено: {{ getters.notFoundCount }}</p>
      <p v-if="store.searchHistory.length > 0">
        История: {{ store.searchHistory.length }} поисков
      </p>
    </footer>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { store, actions, getters } from './store.js'
import { api } from './api.js' // ✅ Импортируем api для прямого использования
import SearchForm from './components/SearchForm.vue'
import SearchResults from './components/SearchResults.vue'
import Instructions from './components/Instructions.vue'

export default {
  name: 'App',
  
  components: {
    SearchForm,
    SearchResults,
    Instructions
  },
  
  setup() {
    const searchText = ref('')
    let pollInterval = null
    
    // При монтировании
    onMounted(async () => {
      console.log('Приложение запущено')
      
      // Проверяем доступность сервера
      await actions.checkServer()
      
      // Загружаем историю
      actions.loadHistory()
      
      // Автозагрузка истории поиска из localStorage
      const savedText = localStorage.getItem('lastSearch')
      if (savedText) {
        searchText.value = savedText
      }
    })
    
    // При размонтировании
    onUnmounted(() => {
      if (pollInterval) clearInterval(pollInterval)
      
      // Сохраняем историю
      actions.saveHistory()
    })
    
    // Обработчик поиска
    const handleSearch = async () => {
      // Сохраняем текст поиска
      localStorage.setItem('lastSearch', searchText.value)
      
      try {
        const response = await actions.startSearch(searchText.value)
        
        // Если задача выполняется асинхронно
        if (response?.data?.status === 'processing' || response?.status === 'processing') {
          startPolling(store.taskId)
        } else if (response?.data?.status === 'completed' || response?.status === 'completed') {
          // Результат уже готов
          const resultData = response.data?.result || response.result
          store.results = resultData?.results || []
          store.loading = false
        }
      } catch (error) {
        console.error('Ошибка поиска:', error)
      }
    }
    
    // Polling статуса задачи
    const startPolling = (taskId) => {
      if (pollInterval) clearInterval(pollInterval)
      
      let attempts = 0
      const maxAttempts = 30 // 60 секунд при интервале 2 секунды
      
      pollInterval = setInterval(async () => {
        attempts++
        
        if (attempts > maxAttempts) {
          clearInterval(pollInterval)
          actions.setError('Время ожидания истекло (60 секунд)')
          store.loading = false
          return
        }
        
        try {
          const response = await api.checkTask(taskId) // ✅ Используем импортированный api
          
          if (response.data?.status === 'completed') {
            clearInterval(pollInterval)
            store.results = response.data.result?.results || []
            store.loading = false
            store.taskId = null
          } else if (response.data?.status === 'error' || response.data?.status === 'failed') {
            clearInterval(pollInterval)
            actions.setError(response.data.result?.error || 'Ошибка обработки')
            store.loading = false
            store.taskId = null
          }
        } catch (error) {
          console.error('Ошибка polling:', error)
          // Не останавливаем polling при временных ошибках
        }
      }, 2000) // Каждые 2 секунды
    }
    
    return {
      store,
      actions,
      getters,
      searchText,
      handleSearch
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: linear-gradient(135deg, #390bdd, #4562e4);
  padding: 15px 20px;
  color: white;
  position: relative;
}

.header h1 {
  margin: 0;
  font-size: 24px;
  text-align: center;
}

.server-status {
  position: absolute;
  top: 15px;
  right: 20px;
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 4px;
  background: rgba(255,255,255,0.2);
}

.server-status.online {
  background: rgba(40, 167, 69, 0.2);
}

.main {
  flex: 1;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.btn-instructions {
  background: #4562e4;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 20px;
  font-size: 16px;
  display: block;
  width: 100%;
}

.loading {
  text-align: center;
  padding: 30px;
  background: white;
  border-radius: 10px;
  margin: 20px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4562e4;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background: #ffebee;
  border: 1px solid #ffcdd2;
  color: #c62828;
  padding: 15px;
  border-radius: 5px;
  margin: 15px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error button {
  background: none;
  border: 1px solid #c62828;
  color: #c62828;
  padding: 5px 10px;
  border-radius: 3px;
  cursor: pointer;
}

.no-results {
  text-align: center;
  padding: 30px;
  background: white;
  border-radius: 10px;
  margin: 20px 0;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  color: #666;
}

.examples {
  margin-top: 20px;
}

.examples p {
  margin-bottom: 10px;
  font-weight: bold;
}

.examples button {
  background: #f0f0f0;
  border: 1px solid #ddd;
  padding: 8px 15px;
  margin: 5px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.2s;
}

.examples button:hover {
  background: #e0e0e0;
}

.history {
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.history h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.history-items {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 5px;
  padding: 10px 15px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-item:hover {
  background: #e9ecef;
}

.history-item small {
  color: #6c757d;
  font-size: 12px;
}

.footer {
  background: #f8f9fa;
  padding: 15px;
  text-align: center;
  border-top: 1px solid #dee2e6;
  color: #666;
  font-size: 14px;
}

.footer p {
  margin: 5px 0;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 20px;
    padding-right: 120px;
  }
  
  .server-status {
    position: static;
    margin-top: 10px;
    text-align: center;
    display: inline-block;
  }
  
  .history-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>