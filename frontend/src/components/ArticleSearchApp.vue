<template>
  <div class="app">
    <header class="header">
      <h1>Поиск артикулов</h1>
    </header>

    <main class="main-content">
      <InstructionsPanel 
        :is-expanded="isExpanded"
        @toggle="toggleInstructions"
      />

      <SearchForm 
        v-model:input-text="inputText"
        @search="startSearch"
        @clear="clearAll"
      />

      <Loader 
        v-if="loading"
        :message="loadingMessage"
      />

      <section v-if="foundArticles.length > 0" class="results">
        <ResultsTable :found-articles="foundArticles">
          <template #export-button>
            <button @click="downloadExcel" class="btn btn-export">Скачать XLSX</button>
          </template>
        </ResultsTable>
      </section>

      <div v-else-if="searchPerformed && !loading" class="no-results">
        <p>Артикулы не найдены.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue'
import InstructionsPanel from './InstructionsPanel.vue'
import SearchForm from './SearchForm.vue'
import ResultsTable from './ResultsTable.vue'
import Loader from './Loader.vue'

// === Состояние ===
const inputText = ref('')
const foundArticles = ref([])
const searchPerformed = ref(false)
const isExpanded = ref(false)
const loading = ref(false)
const loadingMessage = ref('Идет поиск артикулов...')
const currentTaskId = ref(null)
const pollInterval = ref(null)

// === Очистка интервала при уходе со страницы ===
onUnmounted(() => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
})

// === Запуск поиска ===
const startSearch = async () => {
  const query = inputText.value.trim()
  if (!query) return

  clearAll()
  searchPerformed.value = true
  loading.value = true

  try {
    const response = await fetch('/api/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })

    // 🔑 Читаем тело ОДИН РАЗ
    const result = await response.json()

    if (!response.ok) {
      throw new Error(result.message || `Ошибка ${response.status}`)
    }

    if (!result.task_id) {
      throw new Error('Бэкенд не вернул task_id')
    }

    currentTaskId.value = result.task_id

    if (result.source === 'cache') {
      foundArticles.value = result.matches || []
      loading.value = false
    } else {
      loadingMessage.value = 'Обработка запроса...'
      startPolling()
    }
  } catch (error) {
    console.error('Ошибка поиска:', error)
    alert(`Не удалось запустить поиск: ${error.message}`)
    loading.value = false
  }
}

// === Опрос статуса задачи ===
const startPolling = () => {
  if (pollInterval.value) clearInterval(pollInterval.value)

  pollInterval.value = setInterval(async () => {
    try {
      const res = await fetch(`/api/task/${currentTaskId.value}`)
      const status = await res.json()

      if (status.status === 'completed') {
        stopPolling()
        foundArticles.value = status.result?.matches || []
        loading.value = false
      } else if (status.status === 'failed') {
        stopPolling()
        loading.value = false
        alert('Задача завершилась с ошибкой')
      }
    } catch (err) {
      console.error('Ошибка опроса статуса:', err)
    }
  }, 1000)
}

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

// === Скачивание Excel ===
const downloadExcel = () => {
  if (!currentTaskId.value) return
  const url = `/download/${currentTaskId.value}`
  const a = document.createElement('a')
  a.href = url
  a.download = `результаты_${currentTaskId.value.slice(0, 8)}.xlsx`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

// === Полная очистка ===
const clearAll = () => {
  inputText.value = ''
  foundArticles.value = []
  searchPerformed.value = false
  loading.value = false
  stopPolling()
  currentTaskId.value = null
}

const toggleInstructions = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
/* Стили можно оставить как есть или добавить при необходимости */
.btn-export {
  padding: 8px 16px;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.btn-export:hover {
  background-color: #218838;
}
.no-results {
  text-align: center;
  margin-top: 1.5rem;
  color: #666;
}
</style>