const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

// Простой API клиент
export const api = {
  // Поиск компонентов
  async search(text) {
    console.log('Отправка запроса на:', `${API_URL}/api/search`)
    console.log('Текст запроса:', text.substring(0, 100) + '...')
    
    const response = await fetch(`${API_URL}/api/search`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        query: text.trim(),
        priority: 1 
      })
    })
    
    if (!response.ok) {
      let errorMessage = `Ошибка сервера: ${response.status}`
      try {
        const errorData = await response.json()
        errorMessage = errorData.error?.message || errorMessage
      } catch (e) {}
      throw new Error(errorMessage)
    }
    
    return await response.json()
  },
  
  // Проверка статуса задачи
  async checkTask(taskId) {
    if (!taskId) {
      throw new Error('Не указан ID задачи')
    }
    
    const response = await fetch(`${API_URL}/api/task/${taskId}`)
    
    if (!response.ok) {
      throw new Error(`Ошибка статуса: ${response.status}`)
    }
    
    return await response.json()
  },
  
  // Проверка здоровья сервера
  async health() {
    try {
      const response = await fetch(`${API_URL}/api/health`)
      return response.ok
    } catch (error) {
      console.error('Ошибка проверки здоровья:', error)
      return false
    }
  }
}

export default api