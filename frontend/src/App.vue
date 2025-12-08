<template>
  <div id="app">
    <!-- Основной компонент приложения -->
    <ArticleSearchApp />
  </div>
</template>

<script setup>
// Импорт основного компонента
import ArticleSearchApp from './components/ArticleSearchApp.vue'
</script>

<style>
/* Глобальные стили */
#app {
  font-family: Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
}
</style>