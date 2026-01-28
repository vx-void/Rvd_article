<template>
  <section class="instructions-panel" :class="{ expanded: isExpanded }">
    <div class="instructions-header" @click="$emit('toggle')">
      <div class="header-content">
        <h2>
          Инструкция
        </h2>
      </div>
      <button class="toggle-button" :aria-expanded="isExpanded">
        <span class="toggle-icon">{{ isExpanded ? '▼' : '▶' }}</span>
      </button>
    </div>
    
    <div v-if="isExpanded" class="instructions-content">
      <div class="steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>Введите текст</h3>
            <p>Вставьте или введите текст с одним или несколькими запросами гидравлических компонентов в поле ввода.</p>
            <div class="example">
              <strong>Пример:</strong>
              <code>Фитинг 1/2 BSP x2, Переходник 3/4 JIC, Заглушка M16</code>
            </div>
          </div>
        </div>
        
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>AI анализ</h3>
            <p>Система автоматически определит:</p>
            <ul>
              <li>Отдельные запросы в тексте</li>
              <li>Тип каждого компонента (фитинг, переходник, заглушка и т.д.)</li>
              <li>Технические параметры (диаметр, стандарт, резьбу)</li>
              <li>Количество (по умолчанию 1)</li>
            </ul>
          </div>
        </div>
        
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>Поиск в базе данных</h3>
            <p>Для каждого запроса система ищет соответствующие компоненты в базе данных и возвращает:</p>
            <ul>
              <li><strong>Наименование</strong> компонента</li>
              <li><strong>Артикул</strong> для заказа</li>
              <li><strong>Количество</strong> из запроса</li>
            </ul>
          </div>
        </div>
        
        <div class="step">
          <div class="step-number">4</div>
          <div class="step-content">
            <h3>Экспорт результатов</h3>
            <p>Используйте кнопку <strong>"Скачать Excel"</strong> для получения файла с результатами.</p>
            <p>Excel файл содержит таблицу с колонками: <em>Запрос, Наименование, Артикул, Количество</em></p>
          </div>
        </div>
      </div>
      
    </div>
  </section>
</template>

<script setup>
defineProps({
  isExpanded: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle'])
</script>

<style scoped>
.instructions-panel {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  border-radius: 12px;
  margin-bottom: 30px;
  overflow: hidden;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
}

.instructions-panel.expanded {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

.instructions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  cursor: pointer;
  background: white;
  transition: background-color 0.3s ease;
}

.instructions-header:hover {
  background-color: #f8f9fa;
}

.header-content h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content h2 .icon {
  font-size: 24px;
}

.header-subtitle {
  margin: 6px 0 0 0;
  color: #6c757d;
  font-size: 14px;
  font-weight: 400;
}

.toggle-button {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
}

.toggle-button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.toggle-icon {
  font-size: 18px;
  color: #4562e4;
  font-weight: bold;
  transition: transform 0.3s ease;
}

.instructions-content {
  padding: 25px;
  background: white;
  border-top: 1px solid #dee2e6;
}

.steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
}

.step {
  display: flex;
  gap: 15px;
  align-items: flex-start;
}

.step-number {
  background: linear-gradient(135deg, #4562e4, #390bdd);
  color: white;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
  flex-shrink: 0;
}

.step-content h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.step-content p {
  margin: 0 0 10px 0;
  color: #495057;
  line-height: 1.6;
  font-size: 15px;
}

.step-content ul {
  margin: 10px 0;
  padding-left: 20px;
  color: #495057;
  font-size: 14px;
  line-height: 1.5;
}

.step-content li {
  margin-bottom: 6px;
}

.example {
  background-color: #f8f9fa;
  border-left: 4px solid #4562e4;
  padding: 12px 15px;
  margin-top: 12px;
  border-radius: 0 6px 6px 0;
}

.example code {
  display: block;
  margin-top: 5px;
  font-family: 'Consolas', monospace;
  color: #dc3545;
  background-color: #fff;
  padding: 8px;
  border-radius: 4px;
  font-size: 14px;
  border: 1px solid #dee2e6;
}

.tips {
  background-color: #e7f4ff;
  border-radius: 10px;
  padding: 20px;
  border: 1px solid #b3d7ff;
}

.tips h4 {
  margin: 0 0 15px 0;
  color: #0056b3;
  font-size: 17px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 10px;
}

.tips ul {
  margin: 0;
  padding-left: 20px;
  color: #004085;
}

.tips li {
  margin-bottom: 8px;
  line-height: 1.5;
}

kbd {
  background-color: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 2px 6px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  color: #495057;
  box-shadow: 0 1px 1px rgba(0, 0, 0, 0.1);
}

@media (max-width: 992px) {
  .steps {
    grid-template-columns: 1fr;
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .instructions-header {
    padding: 15px 20px;
  }
  
  .header-content h2 {
    font-size: 20px;
  }
  
  .instructions-content {
    padding: 20px;
  }
  
  .step {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .step-number {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }
  
  .step-content h3 {
    font-size: 17px;
  }
  
  .step-content p,
  .step-content ul {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .instructions-header {
    padding: 12px 15px;
  }
  
  .header-content h2 {
    font-size: 18px;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .instructions-content {
    padding: 15px;
  }
  
  .example code {
    font-size: 12px;
    padding: 6px;
  }
}
</style>