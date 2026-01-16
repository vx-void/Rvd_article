<template>
  <ArticleSearchApp />
</template>

<script setup>
import ArticleSearchApp from './components/ArticleSearchApp.vue'
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
  line-height: 1.6;
  color: #333;
  background-color: #f8f9fa;
}

#app {
  min-height: 100vh;
}

/* Утилиты */
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* Плавная прокрутка */
html {
  scroll-behavior: smooth;
}

/* Выделение текста */
::selection {
  background-color: rgba(69, 98, 228, 0.2);
  color: #2c3e50;
}

/* Убрать outline для навигации клавиатурой */
:focus-visible {
  outline: 2px solid #4562e4;
  outline-offset: 2px;
}
</style>