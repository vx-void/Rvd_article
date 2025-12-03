<script setup>
  import './assets/css/styles.css'
</script>

<template>
  <div class="container">
  <header>
  <h1 class="header">Сервис подбора гидрокомпонента по описанию</h1>
  </header>
  
  <div class="content">
    <div class="instructions">
      <h2 class="instruction-header">Инструкция</h2>
    </div>


    <div class="search-container">
      <div class="input-with-hits">
        <label for="componentSearch" class="input-label">Поиск гидрокомпонентов</label>
        <textarea
          id="componentSearch"
          class="smart-textarea"
          placeholder="Введите текстовое описание или название необходимого компонента"
          rows="4"
          ></textarea>
      </div>
      <div class="input-status">
        <div class="processing-indicator hidden">
        <div class="spinner"></div>
        <span>Анализируем запрос...</span>
      </div>
    </div>
    <div id="loading" class="loading" style="display: none;"></div>
      Отправка запроса на сервер...
    </div>
    <div id="status" class="status"></div>

  <button class="search-btn" id="searchButton">Найти артикулы</button>
  
  <div class="results-section" id="resultsSection">
                <h2 class="results-title">Результаты поиска:</h2>

                <div id="articlesContainer" class="hidden">
                    <div class="articles-title">Найденные артикулы:</div>
                    <div class="articles-result" id="articlesResult"></div>
                </div>

                <div id="detailedResultsContainer">
                    <div id="resultsContainer">

                    </div>
    </div>

   
  </div>
   <div class="footer">
            <p>Система автоматической идентификации гидравлических компонентов © 2025</p>
    </div>   
  </div>
</div>
</template>

<style scoped></style>
