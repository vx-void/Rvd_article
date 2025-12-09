<template>
  <div class="app">
    <header class="header">
      <h1>Поиск артикулов</h1>
    </header>
    
    <main class="main-content">
      <div class="instruction-container">
        
        
        <div class="instructions" @click="toggleInstructions">
          <h2 class="instruction-title">Инструкция</h2>
          <span class="toggle-icon">{{ isExplanded ? '▼' : '▶' }}</span>
        </div>
        <div v-if="isExplanded" class="instruction-content">
          <ul class="instruction-list">
            <li>Вставьте текст в поле ввода ниже</li>
            <li>Нажмите кнопку "Найти артикулы" для поиска</li>
            <li>Используйте "Очистить Ввод" для очистки поля</li>
            <li>Найденные артикулы будут отображены в списке</li>
          </ul>
        </div>
      </div>
      
      <div class="input-section">
        <textarea 
          v-model="inputText"
          name="inputText" 
          id="inputText"
          class="input-text"
          placeholder="Вставьте ваш текст..."
          rows="10">
        </textarea>
      </div>
      
      <section class="button-area">
        <button @click="findArticles" class="btn btn-primary">Найти артикулы</button>
        <button @click="clearInput" class="btn btn-secondary">Очистить Ввод</button>
      </section>
      
      <!-- Результаты поиска -->
      <div v-if="foundArticles.length > 0" class="results">
        <h3>Найденные артикулы ({{ foundArticles.length }}):</h3>
        <ul class="articles-list">
          <li v-for="(article, index) in foundArticles" :key="index" class="article-item">
            {{ article }}
          </li>
        </ul>
      </div>
      
      <!-- Сообщение если ничего не найдено -->
      <div v-if="searchPerformed && foundArticles.length === 0" class="no-results">
        <p>Артикулы не найдены. Попробуйте другой текст.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const inputText = ref('')
const foundArticles = ref([])
const searchPerformed = ref(false)

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

const clearInput = () => {
  inputText.value = ''
  foundArticles.value = []
  searchPerformed.value = false
}

const isExplanded = ref(true)

const toggleInstructions = () => {
  isExplanded.value = !isExplanded.value;
}


</script>
