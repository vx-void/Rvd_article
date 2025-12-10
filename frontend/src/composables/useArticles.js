import { ref } from 'vue'

export function useArticles() {
  // Реактивные переменные
  const inputText = ref('')
  const foundArticles = ref([])
  const searchPerformed = ref(false)
  const isExpanded = ref(false)

  // Функция поиска артикулов
  const findArticles = async () => {
    if (!inputText.value.trim()) {
      alert('Введите текст')
      return
    }
    
    searchPerformed.value = true
    
    const patterns = [
      /[A-ZА-Я]{2,}[-_]\d{2,}/gi,
      /арт\.?\s*\d+/gi,
      /\b\d{6,}\b/g,
      /[A-ZА-Я0-9]{5,}/gi
    ]
    
    const allMatches = []
    
    patterns.forEach(pattern => {
      const matches = inputText.value.match(pattern)
      if (matches) {
        allMatches.push(...matches)
      }
    })
    
    foundArticles.value = [...new Set(allMatches)]
    
    if (foundArticles.value.length === 0) {
      console.log('Артикулы не найдены')
    }
  }

  // Очистка ввода
  const clearInput = () => {
    inputText.value = ''
    foundArticles.value = []
    searchPerformed.value = false
  }

  // Переключение инструкции
  const toggleInstructions = () => {
    isExpanded.value = !isExpanded.value
  }

  // Возвращаем все реактивные данные и функции
  return {
    // Данные
    inputText,
    foundArticles,
    searchPerformed,
    isExpanded,
    
    // Методы
    findArticles,
    clearInput,
    toggleInstructions
  }
}