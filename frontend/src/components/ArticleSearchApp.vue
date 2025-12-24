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
        :input-text="inputText"
        @search="findArticles"
        @clear="clearInput"
      />
      
      <Loader 
        v-if="loading"
        :message="loadingMessage"
      />
      
      <section v-if="foundArticles.length > 0" class="results">
        <ResultsTable :found-articles="foundArticles">
          <template #export-button>
            <ExportButton @export="saveExcel" />
          </template>
        </ResultsTable>
      </section>
      
      <div v-if="searchPerformed && foundArticles.length === 0" class="no-results">
        <p>Артикулы не найдены. Попробуйте другой текст.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import InstructionsPanel from './InstructionsPanel.vue'
import SearchForm from './SearchForm.vue'
import ResultsTable from './ResultsTable.vue'
import Loader from './Loader.vue'
import ExportButton from './ExportButton.vue'

// Состояние
const inputText = ref('')
const foundArticles = ref([])
const searchPerformed = ref(false)
const isExpanded = ref(false)
const loading = ref(false)
const loadingMessage = ref('Идет поиск артикулов...')

// Методы
const findArticles = async () => {
  if (!inputText.value.trim()) return
  
  searchPerformed.value = true
  loading.value = true
  
  try {
    // TODO: Реализовать вызов API
    // const response = await searchApi(inputText.value)
    // foundArticles.value = response.data
    
    // Временная заглушка
    setTimeout(() => {
      foundArticles.value = [inputText.value, 'Пример артикула 2', 'Пример артикула 3']
      loading.value = false
    }, 1500)
    
  } catch (error) {
    console.error('Ошибка поиска:', error)
    loading.value = false
  }
}

const clearInput = () => {
  inputText.value = ''
  foundArticles.value = []
  searchPerformed.value = false
}

const toggleInstructions = () => {
  isExpanded.value = !isExpanded.value
}

const saveExcel = () => {
  // TODO: Реализовать экспорт в Excel через API
  console.log('Экспорт в Excel:', foundArticles.value)
}
</script>