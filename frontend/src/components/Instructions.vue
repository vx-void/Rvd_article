<template>
  <div class="instructions">
    <div class="instructions-header">
      <h2>Как пользоваться поиском</h2>
      <button @click="$emit('close')" class="btn-close">✕</button>
    </div>
    
    <div class="instructions-content">
      <div class="step">
        <div class="step-number">1</div>
        <div class="step-text">
          <h3>Введите текст</h3>
          <p>Вставьте или введите список компонентов в поле ввода.</p>
          <p class="example">Пример: <code>Фитинг 1/2 BSP, Переходник 3/4 JIC</code></p>
        </div>
      </div>
      
      <div class="step">
        <div class="step-number">2</div>
        <div class="step-text">
          <h3>Нажмите "Найти компоненты"</h3>
          <p>Система автоматически определит:</p>
          <ul>
            <li>Отдельные запросы в тексте</li>
            <li>Типы компонентов</li>
            <li>Количество</li>
          </ul>
        </div>
      </div>
      
      <div class="step">
        <div class="step-number">3</div>
        <div class="step-text">
          <h3>Получите результаты</h3>
          <p>Найденные компоненты появятся в таблице.</p>
          <p>Используйте кнопку <strong>Excel</strong> для скачивания результатов.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Instructions',
  
  emits: ['close']
}
</script>

<style scoped>
.instructions {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  margin-bottom: 20px;
  overflow: hidden;
}

.instructions-header {
  background: linear-gradient(135deg, #4562e4, #390bdd);
  color: white;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.instructions-header h2 {
  margin: 0;
  font-size: 20px;
}

.btn-close {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  background: rgba(255,255,255,0.2);
}

.instructions-content {
  padding: 20px;
}

.step {
  display: flex;
  gap: 20px;
  margin-bottom: 25px;
  align-items: flex-start;
}

.step:last-child {
  margin-bottom: 0;
}

.step-number {
  background: #4562e4;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
  flex-shrink: 0;
}

.step-text h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.step-text p {
  margin: 0 0 10px 0;
  color: #666;
  line-height: 1.5;
}

.step-text ul {
  margin: 10px 0;
  padding-left: 20px;
  color: #666;
}

.step-text li {
  margin-bottom: 5px;
}

.example {
  margin-top: 15px !important;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 5px;
  border-left: 4px solid #4562e4;
}

.example code {
  font-family: monospace;
  color: #390bdd;
  font-weight: bold;
}
</style>