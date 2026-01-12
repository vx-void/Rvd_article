<template>
  <div class="search-form">
    <section class="input-section">
      <textarea 
        :value="inputText"
        @input="onInput"
        name="inputText" 
        id="inputText"
        class="input-text"
        placeholder="Введите запрос"
        rows="10">
      </textarea>
    </section>
    
    <section class="button-area">
      <button @click="findArticles" class="btn btn-primary">Найти артикулы</button>
      <button @click="clearInput" class="btn btn-secondary">Очистить Ввод</button>
    </section>
  </div>
</template>

<script setup>
const props = defineProps({
  inputText: String
})

const emit = defineEmits(['update:inputText', 'search', 'clear'])

const onInput = (event) => {
  emit('update:inputText', event.target.value)
}

const findArticles = () => emit('search')
const clearInput = () => emit('clear')
</script>

<style scoped>
.search-form {
  margin-bottom: 2rem;
}
</style>