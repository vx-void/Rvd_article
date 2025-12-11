<template>
  <div class="app">
    <header class="header">
      <h1>Поиск артикулов</h1>
    </header>
    
    <main class="main-content">
      <section class="instruction-container">
        <div class="instructions" @click="toggleInstructions">
          <h2 class="instruction-title">Инструкция</h2>
          <span class="toggle-icon">{{ isExpanded ? '▼' : '▶' }}</span>
        </div>
        <div v-if="isExpanded" class="instruction-content">
          <ul class="instruction-list">
            <li>Вставьте текст в поле ввода ниже</li>
            <li>Нажмите кнопку "Найти артикулы" для поиска</li>
            <li>Используйте "Очистить Ввод" для очистки поля</li>
            <li>Найденные артикулы будут отображены в списке</li>
          </ul>
        </div>
      </section>
      
      <section class="input-section">
        <textarea 
          v-model="inputText"
          name="inputText" 
          id="inputText"
          class="input-text"
          placeholder="Вставьте ваш текст..."
          rows="10">
        </textarea>
      </section>
      
      <section class="button-area">
        <button @click="findArticles" class="btn btn-primary">Найти артикулы</button>
        <button @click="clearInput" class="btn btn-secondary">Очистить Ввод</button>
      </section>
      
      <!-- Результаты поиска -->
      <section v-if="foundArticles.length > 0" class="results">
        <div class="table-header-container">
          <h3>Найденные артикулы ({{ foundArticles.length }}):</h3>
          
          <button @click="saveExcel" class="btn btn-excel">скачать .xlsx</button>
        
        </div>
        
        <div class="table-container">
          <table class="articles-table">
            <thead>
              <tr>
                <th class="col-1">Запрос</th>
                <th class="col-2">Наименование</th>
                <th class="col-3">Артикул</th>
                <th class="col-4">Количество</th>
              </tr>
            </thead>
            <tbody>

              <!--вывести Результаты из back-end  -->
              <tr v-for="article in foundArticles" class="article-row">
                <td class="cell">{{ article}}</td>
                <td class="cell">Данные 2</td>
                <td class="cell">Данные 3</td>
                <td class="cell">Данные 4</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      
      <!-- Сообщение если ничего не найдено -->
      <div v-if="searchPerformed && foundArticles.length === 0" class="no-results">
        <p>Артикулы не найдены. Попробуйте другой текст.</p>
      </div>
    </main>
  </div>
</template>

<script setup>
  import { useArticles } from '@/composables/useArticles.js'
  const {
    inputText,
    foundArticles,
    searchPerformed,
    isExpanded,
    findArticles,
    clearInput,
    toggleInstructions,
    saveExcel
  } = useArticles()

</script>

<style scoped>

</style>