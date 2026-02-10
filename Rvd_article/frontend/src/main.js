import { createApp } from 'vue'
import App from './App.vue'
import './styles.css'

// Создаем приложение
const app = createApp(App)

// Глобальная обработка ошибок
app.config.errorHandler = (err, vm, info) => {
  console.error('Ошибка Vue:', err)
}

// Монтируем приложение
app.mount('#app')

console.log('Приложение запущено')