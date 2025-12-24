<template>
  <div class="results-table">
    <div class="table-header-container">
      <h3>Найденные артикулы ({{ foundArticles.length }}):</h3>
      <slot name="export-button"></slot>
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
          <tr v-for="(article, index) in foundArticles" :key="index" class="article-row">
            <td class="cell">{{ article }}</td>
            <td class="cell">Данные 2</td>
            <td class="cell">Данные 3</td>
            <td class="cell">Данные 4</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  foundArticles: {
    type: Array,
    default: () => []
  }
})
</script>