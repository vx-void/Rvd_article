<template>
  <div class="search-form">
    <div class="input-container">
      <label for="search-text" class="input-label">
        Введите текст с запросами гидравлических компонентов
        <span class="hint">(можно несколько запросов в одном тексте)</span>
      </label>
      
      <textarea 
        id="search-text"
        ref="textareaRef"
        v-model="localText"
        class="search-textarea"
        placeholder="Пример: Фитинг 1/2 BSP x2, Переходник 3/4 JIC, Заглушка M16"
        rows="8"
        @keydown.ctrl.enter="handleSearch"
        @keydown.meta.enter="handleSearch"
      ></textarea>
      
      <div class="textarea-footer">
        <div class="char-count">
          Символов: {{ localText.length }} / 5000
        </div>
        <div class="textarea-actions">
          <button 
            v-if="localText.length > 0"
            @click="clearText"
            class="btn-clear"
            title="Очистить поле"
          >
            ✕ Очистить
          </button>
        </div>
      </div>
    </div>
    
    <div class="form-actions">
      <button 
        @click="handleSearch" 
        class="btn-search"
        :disabled="!canSearch"
        :title="canSearch ? 'Начать поиск компонентов' : 'Введите текст для поиска'"
      >
        🔍 Найти компоненты
      </button>
      
      <button 
        @click="handleClearAll" 
        class="btn-clear-all"
        title="Очистить все поля и результаты"
      >
        🗑️ Очистить все
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  inputText: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:inputText', 'search', 'clear'])
const textareaRef = ref(null)

const localText = ref(props.inputText)

// Следим за изменениями в родительском компоненте
watch(() => props.inputText, (newValue) => {
  localText.value = newValue
})

// Следим за изменениями локального текста
watch(localText, (newValue) => {
  emit('update:inputText', newValue)
})

const canSearch = computed(() => {
  return localText.value.trim().length > 0
})

const handleSearch = () => {
  if (canSearch.value) {
    emit('search')
  }
}

const handleClearAll = () => {
  emit('clear')
}

const clearText = () => {
  localText.value = ''
}

// Автофокус на textarea при монтировании
onMounted(() => {
  if (textareaRef.value) {
    textareaRef.value.focus()
  }
})
</script>

<style scoped>
.search-form {
  margin-bottom: 30px;
}

.input-container {
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  margin-bottom: 25px;
}

.input-label {
  display: block;
  margin-bottom: 12px;
  font-weight: 600;
  color: #2c3e50;
  font-size: 16px;
}

.input-label .hint {
  font-weight: normal;
  color: #6c757d;
  font-size: 14px;
  margin-left: 8px;
}

.search-textarea {
  width: 100%;
  min-height: 180px;
  padding: 16px;
  font-size: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  resize: vertical;
  box-sizing: border-box;
  transition: all 0.3s ease;
  line-height: 1.6;
  background-color: #fff;
  color: #495057;
}

.search-textarea:focus {
  outline: none;
  border-color: #4562e4;
  box-shadow: 0 0 0 3px rgba(69, 98, 228, 0.15);
}

.search-textarea::placeholder {
  color: #adb5bd;
  font-style: italic;
}

.textarea-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding: 0 5px;
}

.char-count {
  font-size: 13px;
  color: #6c757d;
}

.textarea-actions {
  display: flex;
  gap: 10px;
}

.btn-clear {
  background: none;
  border: 1px solid #dc3545;
  color: #dc3545;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-clear:hover {
  background-color: #dc3545;
  color: white;
}

.form-actions {
  display: flex;
  gap: 20px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-search {
  background: linear-gradient(135deg, #0004ff, #4562e4);
  color: white;
  padding: 14px 32px;
  font-size: 17px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 6px rgba(0, 4, 255, 0.2);
}

.btn-search:hover:not(:disabled) {
  background: linear-gradient(135deg, #0077ff, #ff5a00);
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(255, 140, 0, 0.25);
}

.btn-search:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

.btn-clear-all {
  background: linear-gradient(135deg, #6c757d, #495057);
  color: white;
  padding: 14px 32px;
  font-size: 17px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 180px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-clear-all:hover {
  background: linear-gradient(135deg, #5a6268, #343a40);
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(108, 117, 125, 0.3);
}

/* Горячие клавиши подсказка */
.search-textarea::after {
  content: "Ctrl+Enter для быстрого поиска";
  font-size: 12px;
  color: #6c757d;
  position: absolute;
  bottom: 10px;
  right: 10px;
}

@media (max-width: 768px) {
  .input-container {
    padding: 15px;
  }
  
  .input-label {
    font-size: 15px;
  }
  
  .search-textarea {
    font-size: 15px;
    padding: 12px;
    min-height: 150px;
  }
  
  .form-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .btn-search,
  .btn-clear-all {
    width: 100%;
    padding: 12px 24px;
    font-size: 16px;
  }
  
  .textarea-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .input-label {
    font-size: 14px;
  }
  
  .input-label .hint {
    display: block;
    margin-left: 0;
    margin-top: 4px;
  }
  
  .search-textarea {
    font-size: 14px;
    min-height: 120px;
  }
  
  .btn-search,
  .btn-clear-all {
    font-size: 15px;
    padding: 10px 20px;
  }
}
</style>