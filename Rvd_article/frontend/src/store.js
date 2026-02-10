import { reactive, readonly } from 'vue'
import { api } from './api.js' // ✅ Добавляем импорт

// Создаем глобальное состояние
const state = reactive({
  // Данные поиска
  searchText: '',
  results: [],
  searchHistory: [],
  
  // Состояние UI
  loading: false,
  loadingMessage: '',
  error: null,
  showInstructions: false,
  
  // Текущая задача
  taskId: null,
  
  // Статус сервера
  serverOnline: true
})

// Геттеры
export const getters = {
  hasResults: () => state.results.length > 0,
  totalFound: () => {
    return state.results.reduce((total, result) => 
      total + (result.matches?.length || 0), 0
    )
  },
  notFoundCount: () => {
    return state.results.filter(result => 
      !result.matches || result.matches.length === 0
    ).length
  }
}

// Действия
export const actions = {
  // Установить текст поиска
  setSearchText(text) {
    state.searchText = text
  },
  
  // Начать поиск
  async startSearch(text) {
    if (!text?.trim()) {
      state.error = 'Введите текст для поиска'
      return
    }
    
    try {
      state.loading = true
      state.loadingMessage = 'Анализ текста...'
      state.error = null
      state.searchText = text
      state.results = []
      
      // Сохраняем в историю
      state.searchHistory.unshift({
        text,
        date: new Date().toISOString(),
        id: Date.now()
      })
      
      const response = await api.search(text) // ✅ Используем импортированный api
      
      // Сохраняем ID задачи
      state.taskId = response.data?.task_id || response.task_id
      
      return response
    } catch (error) {
      state.error = error.message
      state.loading = false
      throw error
    }
  },
  
  // Проверить статус задачи
  async checkTaskStatus() {
    if (!state.taskId) return
    
    try {
      state.loadingMessage = 'Поиск в базе данных...'
      const response = await api.checkTask(state.taskId) // ✅ Используем импортированный api
      
      if (response.data?.status === 'completed') {
        state.results = response.data?.result?.results || []
        state.loading = false
        state.taskId = null
      } else if (response.data?.status === 'error') {
        state.error = response.data?.result?.error || 'Ошибка обработки'
        state.loading = false
        state.taskId = null
      }
      
      return response
    } catch (error) {
      console.error('Ошибка проверки статуса:', error)
      state.error = 'Ошибка при проверке статуса задачи'
      state.loading = false
    }
  },
  
  // Очистить все
  clearAll() {
    state.searchText = ''
    state.results = []
    state.error = null
    state.taskId = null
    state.loading = false
  },
  
  // Показать/скрыть инструкции
  toggleInstructions() {
    state.showInstructions = !state.showInstructions
  },
  
  // Установить ошибку
  setError(message) {
    state.error = message
  },
  
  // Проверить доступность сервера
  async checkServer() {
    try {
      state.serverOnline = await api.health()
      return state.serverOnline
    } catch (error) {
      state.serverOnline = false
      return false
    }
  },
  
  // Загрузить историю из localStorage
  loadHistory() {
    try {
      const saved = localStorage.getItem('searchHistory')
      if (saved) {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          state.searchHistory = parsed.slice(0, 10)
        }
      }
    } catch (error) {
      console.error('Ошибка загрузки истории:', error)
    }
  },
  
  // Сохранить историю в localStorage
  saveHistory() {
    try {
      localStorage.setItem('searchHistory', 
        JSON.stringify(state.searchHistory.slice(0, 10))
      )
    } catch (error) {
      console.error('Ошибка сохранения истории:', error)
    }
  }
}

// Экспортируем состояние только для чтения
export const store = readonly(state)