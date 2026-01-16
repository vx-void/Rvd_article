import { createApp } from 'vue'
import App from './App.vue'
import './assets/css/styles.css'

// Создание приложения
const app = createApp(App)

// Глобальная обработка ошибок
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Component:', vm)
  console.error('Info:', info)
  
  // Можно добавить отправку ошибок на сервер
  // или показать уведомление пользователю
}

// Глобальные свойства (если нужны)
app.config.globalProperties.$filters = {
  formatDate(value) {
    if (!value) return ''
    return new Date(value).toLocaleDateString('ru-RU')
  },
  truncate(text, length = 50) {
    if (!text || text.length <= length) return text
    return text.substring(0, length) + '...'
  }
}

// Монтируем приложение
app.mount('#app')

// Обработка глобальных ошибок
window.addEventListener('error', (event) => {
  console.error('Global Error:', event.error)
  event.preventDefault()
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  event.preventDefault()
})

// Отладка в разработке
if (import.meta.env.DEV) {
  console.log('🚀 Приложение запущено в режиме разработки')
  console.log('🌐 API URL:', import.meta.env.VITE_API_URL || 'http://localhost:5000')
}