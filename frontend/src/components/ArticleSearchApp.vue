<template>
  <div class="app">
    <header class="header">
      <h1>Поиск гидравлических компонентов</h1>
    </header>

    <main class="main-content">
      <InstructionsPanel 
        :is-expanded="isExpanded"
        @toggle="toggleInstructions"
      />

      <SearchForm 
        v-model:input-text="inputText"
        @search="startBatchSearch"
        @clear="clearAll"
      />

      <Loader 
        v-if="loading"
        :message="loadingMessage"
      />

      <BatchResultsTable 
        v-if="batchResults.length > 0"
        :results="batchResults"
        :downloading="downloadingExcel"
        @download-excel="downloadExcelFromBackend"
      />

      <div v-else-if="searchPerformed && !loading" class="no-results">
        <p>Компоненты не найдены. Попробуйте другой запрос.</p>
      </div>
    </main>
  </div>
</template>
<script>
import { ref, onUnmounted } from 'vue'
import InstructionsPanel from './InstructionsPanel.vue'
import SearchForm from './SearchForm.vue'
import BatchResultsTable from './BatchResultsTable.vue'
import Loader from './Loader.vue'

export default {
  name: 'ArticleSearchApp',
  
  components: {
    InstructionsPanel,
    SearchForm,
    BatchResultsTable,
    Loader
  },

  setup() {
    // Конфигурация API
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

    // Состояние
    const inputText = ref('')
    const batchResults = ref([])
    const searchPerformed = ref(false)
    const isExpanded = ref(false)
    const loading = ref(false)
    const downloadingExcel = ref(false)
    const loadingMessage = ref('Идет поиск компонентов...')
    const currentTaskId = ref(null)
    const pollInterval = ref(null)

    // Очистка интервала при уходе со страницы
    onUnmounted(() => {
      stopPolling()
    })

    // Запуск пакетного поиска
    const startBatchSearch = async () => {
      const text = inputText.value.trim()
      if (!text) {
        alert('Введите текст для поиска')
        return
      }

      // Сброс предыдущих результатов
      clearResults()
      searchPerformed.value = true
      loading.value = true
      loadingMessage.value = 'Анализ текста...'

      try {
        // Отправляем batch запрос на бекенд
        const response = await fetch(`${API_BASE_URL}/api/batch`, {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          },
          body: JSON.stringify({ 
            text: text,
            priority: 5 
          })
        })

        // Отладка
        console.log('Отправка запроса на:', `${API_BASE_URL}/api/batch`)
        console.log('Текст запроса:', text)

        // Обработка ответа
        if (!response.ok) {
          let errorData = {}
          try {
            errorData = await response.json()
          } catch (e) {
            // Если не удалось распарсить JSON
          }
          const errorMessage = errorData.error && errorData.error.message 
            ? errorData.error.message 
            : `Ошибка сервера: ${response.status} ${response.statusText}`
          throw new Error(errorMessage)
        }

        const result = await response.json()
        
        console.log('Полный ответ от сервера:', result)

        // Проверяем структуру ответа
        if (!result.success) {
          const errorMsg = result.error && result.error.message 
            ? result.error.message 
            : 'Неизвестная ошибка бекенда'
          throw new Error(errorMsg)
        }

        // Ищем task_id в разных местах ответа
        let taskId = null
        
        // Сначала проверяем data.task_id
        if (result.data && result.data.task_id) {
          taskId = result.data.task_id
        } 
        // Затем проверяем task_id на верхнем уровне
        else if (result.task_id) {
          taskId = result.task_id
        }
        // Ищем в других возможных местах
        else if (result.data && result.data.data && result.data.data.task_id) {
          taskId = result.data.data.task_id
        }

        if (!taskId) {
          console.warn('Не найден task_id в ответе. Структура ответа:', result)
          throw new Error('Бекенд не вернул идентификатор задачи')
        }

        currentTaskId.value = taskId

        // Проверяем статус задачи
        let status = null
        let resultData = null
        
        // Получаем статус
        if (result.data && result.data.status) {
          status = result.data.status
          resultData = result.data.result
        } else if (result.status) {
          status = result.status
          resultData = result.result
        } else if (result.data) {
          status = result.data
          resultData = result
        }

        // Если результат сразу готов (из кэша)
        if (status === 'completed') {
          if (resultData && resultData.results) {
            batchResults.value = resultData.results
          } else if (resultData && resultData.matches) {
            // Для обратной совместимости с single запросами
            batchResults.value = [{
              original_query: text,
              matches: resultData.matches,
              quantity: 1
            }]
          }
          loading.value = false
          loadingMessage.value = ''
        } else if (status === 'processing') {
          // Запускаем polling для отслеживания статуса
          loadingMessage.value = 'Поиск компонентов в базе данных...'
          startPolling()
        } else {
          throw new Error(`Неожиданный статус задачи: ${status}`)
        }

      } catch (error) {
        console.error('Ошибка запуска поиска:', error)
        alert(`Не удалось запустить поиск: ${error.message}`)
        loading.value = false
        loadingMessage.value = ''
      }
    }


// Polling статуса задачи - МАКСИМУМ 5 попыток
const startPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
  }

  let attempts = 0
  const maxAttempts = 5  // ТОЛЬКО 5 ПОПЫТОК!
  const pollIntervalMs = 5000  // Каждые 5 секунд

  pollInterval.value = setInterval(async () => {
    attempts++
    
    console.log(`Polling попытка ${attempts}/${maxAttempts} для задачи ${currentTaskId.value}`)
    
    // Проверка максимального количества попыток
    if (attempts >= maxAttempts) {
      stopPolling()
      loading.value = false
      
      // Пытаемся отменить задачу на сервере
      try {
        await fetch(`${API_BASE_URL}/api/task/${currentTaskId.value}/cancel`, {
          method: 'POST'
        }).catch(() => {})  // Игнорируем ошибки
      } catch (e) {}
      
      alert('Сервер не обработал задачу за 25 секунд. Возможно worker не запущен. Попробуйте позже.')
      return
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/task/${currentTaskId.value}`)
      
      if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`)
      }

      const result = await response.json()
      
      console.log('Polling результат:', result)
      
      if (!result.success) {
        throw new Error('Ошибка получения статуса')
      }

      const responseData = result.data || result
      const status = responseData.status
      const taskResult = responseData.result
      
      if (status === 'completed') {
        // Задача завершена успешно
        stopPolling()
        if (taskResult && taskResult.results) {
          batchResults.value = taskResult.results
        } else if (taskResult && taskResult.matches) {
          batchResults.value = [{
            original_query: inputText.value.trim(),
            matches: taskResult.matches,
            quantity: 1
          }]
        }
        loading.value = false
        loadingMessage.value = ''
        
      } else if (status === 'error' || status === 'failed' || status === 'timeout') {
        // Задача завершилась с ошибкой
        stopPolling()
        loading.value = false
        const errorMsg = (taskResult && taskResult.error) 
          ? taskResult.error 
          : (responseData.error && responseData.error.message)
            ? responseData.error.message
            : 'Неизвестная ошибка'
        alert(`Ошибка обработки: ${errorMsg}`)
        
      } else if (status === 'partial') {
        // Частичный результат
        stopPolling()
        if (taskResult && taskResult.results) {
          batchResults.value = taskResult.results
        }
        loading.value = false
        loadingMessage.value = ''
        alert('Внимание: некоторые компоненты не были найдены из-за ошибки БД')
        
      } else if (status === 'cached') {
        // Результат из кэша
        stopPolling()
        if (taskResult && taskResult.results) {
          batchResults.value = taskResult.results
        }
        loading.value = false
        loadingMessage.value = ''
        
      }
      // status === 'processing' - продолжаем ждать

    } catch (error) {
      console.error('Ошибка опроса статуса:', error)
      // Не останавливаем polling при временных ошибках
    }
  }, pollIntervalMs)
}
    const stopPolling = () => {
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
        pollInterval.value = null
      }
    }

    // Скачивание Excel с бекенда
    const downloadExcelFromBackend = async () => {
      if (!currentTaskId.value) {
        alert('Нет активной задачи для экспорта')
        return
      }

      if (batchResults.value.length === 0) {
        alert('Нет данных для экспорта')
        return
      }

      downloadingExcel.value = true

      try {
        // Запрашиваем Excel файл с бекенда
        const response = await fetch(`${API_BASE_URL}/api/download/${currentTaskId.value}`, {
          method: 'GET',
          headers: {
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          }
        })

        if (!response.ok) {
          const errorText = await response.text()
          throw new Error(`Ошибка сервера: ${response.status}. ${errorText}`)
        }

        // Получаем бинарные данные файла
        const blob = await response.blob()
        
        // Создаем URL для скачивания
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        
        // Получаем имя файла из заголовков или генерируем
        const contentDisposition = response.headers.get('Content-Disposition')
        let filename = `результаты_поиска_${currentTaskId.value.slice(0, 8)}.xlsx`
        
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
          if (filenameMatch && filenameMatch[1]) {
            filename = decodeURIComponent(filenameMatch[1].replace(/['"]/g, ''))
          }
        }
        
        link.href = url
        link.download = filename
        document.body.appendChild(link)
        link.click()
        
        // Очистка
        setTimeout(() => {
          window.URL.revokeObjectURL(url)
          document.body.removeChild(link)
        }, 100)

      } catch (error) {
        console.error('Ошибка скачивания Excel:', error)
        alert(`Не удалось скачать Excel файл: ${error.message}`)
      } finally {
        downloadingExcel.value = false
      }
    }

    // Очистка результатов
    const clearResults = () => {
      batchResults.value = []
      currentTaskId.value = null
      stopPolling()
    }

    // Полная очистка
    const clearAll = () => {
      inputText.value = ''
      clearResults()
      searchPerformed.value = false
      loading.value = false
      loadingMessage.value = 'Идет поиск компонентов...'
    }

    const toggleInstructions = () => {
      isExpanded.value = !isExpanded.value
    }

    return {
      // Данные
      inputText,
      batchResults,
      searchPerformed,
      isExpanded,
      loading,
      downloadingExcel,
      loadingMessage,
      
      // Методы
      startBatchSearch,
      downloadExcelFromBackend,
      clearAll,
      toggleInstructions
    }
  }
}
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  background: linear-gradient(135deg, #390bdd, #4562e4);
  height: 80px;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header h1 {
  margin: 0;
  color: white;
  font-size: 28px;
  font-weight: 600;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
}

.main-content {
  flex: 1;
  padding: 30px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

.no-results {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 10px;
  padding: 30px;
  text-align: center;
  margin-top: 30px;
  color: #856404;
  font-size: 18px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 22px;
  }
  
  .main-content {
    padding: 15px;
  }
  
  .no-results {
    padding: 20px;
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .header {
    height: 70px;
  }
  
  .header h1 {
    font-size: 20px;
  }
  
  .no-results {
    padding: 15px;
    font-size: 15px;
  }
}
</style>