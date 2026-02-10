<template>
  <div class="results">
    <div class="results-header">
      <h3>Результаты поиска ({{ totalFound }})</h3>
      <button 
        @click="exportExcel" 
        class="btn-excel"
        :disabled="exporting"
      >
        {{ exporting ? 'Генерация...' : '📥 Excel' }}
      </button>
    </div>
    
    <div class="table-container" v-if="hasResults">
      <table class="results-table">
        <thead>
          <tr>
            <th>Запрос</th>
            <th>Наименование</th>
            <th>Артикул</th>
            <th>Кол-во</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(result, index) in results" :key="index">
            <!-- Если есть найденные компоненты -->
            <template v-if="result.matches?.length > 0">
              <tr v-for="(match, matchIndex) in result.matches" 
                  :key="`${index}-${matchIndex}`"
                  :class="{ 'alternate': matchIndex % 2 === 0 }">
                <td v-if="matchIndex === 0" :rowspan="result.matches.length">
                  {{ result.original_query }}
                </td>
                <td>{{ match.name || 'Не указано' }}</td>
                <td class="article">{{ match.article || 'Не указан' }}</td>
                <td v-if="matchIndex === 0" :rowspan="result.matches.length">
                  {{ result.quantity || 1 }}
                </td>
              </tr>
            </template>
            <!-- Если не найдено -->
            <template v-else>
              <tr class="not-found">
                <td>{{ result.original_query }}</td>
                <td colspan="2">Компонент не найден</td>
                <td>{{ result.quantity || 1 }}</td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>
    
    <!-- Сводка -->
    <div class="summary" v-if="hasResults">
      <div class="summary-item">
        <span>Запросов:</span>
        <strong>{{ results.length }}</strong>
      </div>
      <div class="summary-item">
        <span>Найдено:</span>
        <strong>{{ totalFound }}</strong>
      </div>
      <div class="summary-item" v-if="notFoundCount > 0">
        <span>Не найдено:</span>
        <strong class="warning">{{ notFoundCount }}</strong>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'

export default {
  name: 'SearchResults',
  
  props: {
    results: {
      type: Array,
      default: () => []
    }
  },
  
  setup(props) {
    const exporting = ref(false)
    
    // Вычисляемые свойства
    const hasResults = computed(() => props.results.length > 0)
    const totalFound = computed(() => {
      return props.results.reduce((total, result) => 
        total + (result.matches?.length || 0), 0
      )
    })
    const notFoundCount = computed(() => {
      return props.results.filter(result => 
        !result.matches || result.matches.length === 0
      ).length
    })
    
    // Экспорт в Excel
    const exportExcel = () => {
      if (!hasResults.value) return
      
      exporting.value = true
      
      try {
        // Подготовка данных
        const data = []
        
        // Заголовки
        data.push(['Запрос', 'Наименование', 'Артикул', 'Количество'])
        
        // Данные
        props.results.forEach(result => {
          if (result.matches?.length > 0) {
            result.matches.forEach(match => {
              data.push([
                result.original_query,
                match.name || 'Не указано',
                match.article || 'Не указан',
                result.quantity || 1
              ])
            })
          } else {
            data.push([
              result.original_query,
              'Компонент не найден',
              '',
              result.quantity || 1
            ])
          }
        })
        
        // Создание Excel
        const workbook = XLSX.utils.book_new()
        const worksheet = XLSX.utils.aoa_to_sheet(data)
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Результаты')
        
        // Скачивание
        const filename = `гидравлика_${new Date().toISOString().slice(0,10)}.xlsx`
        XLSX.writeFile(workbook, filename)
        
      } catch (error) {
        console.error('Ошибка экспорта:', error)
        alert('Ошибка при создании Excel файла')
      } finally {
        exporting.value = false
      }
    }
    
    return {
      hasResults,
      totalFound,
      notFoundCount,
      exporting,
      exportExcel
    }
  }
}
</script>

<style scoped>
.results {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-top: 20px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #4562e4;
}

.results-header h3 {
  margin: 0;
  color: #333;
}

.btn-excel {
  background: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
}

.btn-excel:hover:not(:disabled) {
  background: #218838;
}

.btn-excel:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.table-container {
  overflow-x: auto;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.results-table th {
  background: #f8f9fa;
  padding: 15px;
  text-align: left;
  font-weight: bold;
  color: #333;
  border-bottom: 2px solid #dee2e6;
}

.results-table td {
  padding: 12px 15px;
  border-bottom: 1px solid #eee;
}

.results-table tr:hover {
  background: #f8f9fa;
}

.results-table tr.alternate {
  background: #fcfcfc;
}

.results-table tr.not-found {
  background: #fff3cd;
}

.results-table tr.not-found:hover {
  background: #ffeaa7;
}

.article {
  color: #007bff;
  font-weight: bold;
}

.summary {
  display: flex;
  gap: 30px;
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
  border: 1px solid #dee2e6;
}

.summary-item {
  display: flex;
  gap: 10px;
  color: #666;
}

.summary-item .warning {
  color: #dc3545;
}
</style>