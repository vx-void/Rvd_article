<template>
  <div class="search-form">
    <div class="form-group">
      <label for="search-text">Введите список компонентов:</label>
      <textarea
        id="search-text"
        v-model="localText"
        placeholder="Пример: Фитинг 1/2 BSP, Переходник 3/4 JIC, Заглушка M16"
        rows="5"
        :disabled="loading"
        @keydown.enter.ctrl="handleSearch"
        @keydown.enter.meta="handleSearch"
      ></textarea>
      <p class="hint">Используйте запятые или новые строки для разделения запросов</p>
    </div>
    
    <div class="buttons">
      <button 
        @click="handleSearch" 
        class="btn-primary"
        :disabled="!localText.trim() || loading"
      >
        {{ loading ? 'Поиск...' : 'Найти компоненты' }}
      </button>
      
      <button 
        @click="clear" 
        class="btn-secondary"
        :disabled="loading"
      >
        Очистить
      </button>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'

export default {
  name: 'SearchForm',
  
  props: {
    text: {
      type: String,
      default: ''
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  
  emits: ['update:text', 'search', 'clear'],
  
  setup(props, { emit }) {
    const localText = ref(props.text)
    
    // Отслеживаем изменения родителя
    watch(() => props.text, (newText) => {
      localText.value = newText
    })
    
    // Отслеживаем локальные изменения
    watch(localText, (newText) => {
      emit('update:text', newText)
    })
    
    // Обработчики
    const handleSearch = () => {
      if (localText.value.trim() && !props.loading) {
        emit('search')
      }
    }
    
    const clear = () => {
      localText.value = ''
      emit('clear')
    }
    
    return {
      localText,
      handleSearch,
      clear
    }
  }
}
</script>

<style scoped>
.search-form {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

textarea {
  width: 100%;
  padding: 15px;
  border: 2px solid #ddd;
  border-radius: 5px;
  font-size: 16px;
  font-family: inherit;
  resize: vertical;
  min-height: 120px;
}

textarea:focus {
  outline: none;
  border-color: #4562e4;
}

.hint {
  margin-top: 5px;
  color: #666;
  font-size: 14px;
}

.buttons {
  display: flex;
  gap: 10px;
}

button {
  padding: 12px 24px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  flex: 1;
  background: linear-gradient(135deg, #390bdd, #4562e4);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #4562e4, #390bdd);
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #5a6268;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>