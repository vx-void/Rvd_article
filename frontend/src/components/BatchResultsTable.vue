<<template>
  <div class="results">
    <div class="table-header">
      <h3>Результаты поиска ({{ totalMatches }} позиций)</h3>
      <button 
        @click="handleDownloadExcel" 
        class="btn-download-excel"
        :disabled="downloading || !hasResults"
        :title="hasResults ? 'Скачать результаты в Excel' : 'Нет данных для экспорта'"
      >
        <span v-if="downloading">
          <span class="spinner"></span> Генерация...
        </span>
        <span v-else>
          📥 Скачать Excel
        </span>
      </button>
    </div>

    <div class="table-container" v-if="hasResults">
      <table class="results-table">
        <thead>
          <tr>
            <th class="col-query">Запрос</th>
            <th class="col-name">Наименование</th>
            <th class="col-article">Артикул</th>
            <th class="col-quantity">Кол-во</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="(result, resultIndex) in results" :key="resultIndex">
            <!-- Если есть найденные совпадения -->
            <template v-if="result.matches && result.matches.length > 0">
              <tr v-for="(match, matchIndex) in result.matches" 
                  :key="`${resultIndex}-${matchIndex}`"
                  class="result-row"
                  :class="{ 'alternate-row': matchIndex % 2 === 0 }">
                <td v-if="matchIndex === 0" 
                    :rowspan="result.matches.length" 
                    class="cell cell-query">
                  {{ result.original_query }}
                  <div class="query-info" v-if="result.component_type">
                    <small>Тип: {{ result.component_type }}</small>
                  </div>
                </td>
                <td class="cell cell-name">{{ match.name || 'Не указано' }}</td>
                <td class="cell cell-article">{{ match.article || 'Не указан' }}</td>
                <td v-if="matchIndex === 0" 
                    :rowspan="result.matches.length" 
                    class="cell cell-quantity">
                  {{ result.quantity || 1 }}
                </td>
              </tr>
            </template>
            <!-- Если ничего не найдено -->
            <template v-else>
              <tr class="result-row not-found">
                <td class="cell cell-query">
                  {{ result.original_query }}
                  <div class="query-info" v-if="result.component_type">
                    <small>Тип: {{ result.component_type }}</small>
                  </div>
                </td>
                <td class="cell cell-name" colspan="2">
                  <span class="not-found-text">Компонент не найден</span>
                </td>
                <td class="cell cell-quantity">
                  {{ result.quantity || 1 }}
                </td>
              </tr>
            </template>
          </template>
        </tbody>
      </table>
    </div>

    <div class="summary" v-if="hasResults">
      <div class="summary-item">
        <span class="summary-label">Всего запросов:</span>
        <span class="summary-value">{{ results.length }}</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">Найдено компонентов:</span>
        <span class="summary-value">{{ totalMatches }}</span>
      </div>
      <div class="summary-item" v-if="notFoundCount > 0">
        <span class="summary-label">Не найдено:</span>
        <span class="summary-value warning">{{ notFoundCount }}</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref } from 'vue'
import useExcelGenerator from '@/composables/useExcelGenerator'

export default {
  name: 'BatchResultsTable',
  
  props: {
    results: {
      type: Array,
      default: () => [],
      required: true
    },
    downloading: {
      type: Boolean,
      default: false
    }
  },

  setup(props) {
    const { generateAndDownloadExcel } = useExcelGenerator()
    const isGenerating = ref(false)
    
    // Вычисляемые свойства
    const totalMatches = computed(() => {
      return props.results.reduce((total, result) => {
        return total + (result.matches?.length || 0)
      }, 0)
    })

    const notFoundCount = computed(() => {
      return props.results.filter(result => 
        !result.matches || result.matches.length === 0
      ).length
    })

    const hasResults = computed(() => {
      return props.results.length > 0
    })
    
    // Генерация Excel
    const handleDownloadExcel = async () => {
      if (!hasResults.value) {
        alert('Нет данных для экспорта')
        return
      }
      
      isGenerating.value = true
      
      try {
        await generateAndDownloadExcel(props.results)
      } catch (error) {
        console.error('Ошибка генерации Excel:', error)
        alert(`Ошибка: ${error.message}`)
      } finally {
        isGenerating.value = false
      }
    }

    return {
      totalMatches,
      notFoundCount,
      hasResults,
      handleDownloadExcel,
      isGenerating
    }
  }
}
</script>
<style scoped>
.results {
  background-color: #fff;
  border-radius: 12px;
  padding: 25px;
  margin-top: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  animation: fadeIn 0.5s ease;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #4562e4;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 22px;
  font-weight: 600;
}

.btn-download-excel {
  background: linear-gradient(135deg, #28a745, #20c997);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 16px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
}

.btn-download-excel:hover:not(:disabled) {
  background: linear-gradient(135deg, #218838, #1aa179);
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
}

.btn-download-excel:disabled {
  background: #6c757d;
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

.btn-download-excel .spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  margin-bottom: 20px;
}

.results-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.results-table thead {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  position: sticky;
  top: 0;
}

.results-table th {
  padding: 16px 12px;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #dee2e6;
  font-size: 15px;
}

.results-table td {
  padding: 14px 12px;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: top;
}

/* Ширины колонок */
.col-query { width: 40%; min-width: 300px; }
.col-name { width: 35%; min-width: 250px; }
.col-article { width: 15%; min-width: 150px; }
.col-quantity { width: 10%; min-width: 80px; }

/* Стили ячеек */
.cell {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.cell-query {
  background-color: #f8f9fa;
  font-weight: 500;
  color: #2c3e50;
}

.cell-name {
  color: #495057;
}

.cell-article {
  color: #007bff;
  font-weight: 500;
}

.cell-quantity {
  text-align: center;
  font-weight: 600;
  color: #28a745;
}

/* Строки таблицы */
.result-row:hover {
  background-color: #f8f9fa;
}

.alternate-row {
  background-color: #fcfcfc;
}

.result-row.not-found {
  background-color: #fff3cd;
}

.result-row.not-found:hover {
  background-color: #ffeaa7;
}

.not-found-text {
  color: #856404;
  font-style: italic;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Информация о запросе */
.query-info {
  margin-top: 6px;
  font-size: 12px;
  color: #6c757d;
  font-weight: normal;
}

.query-info small {
  background-color: #e9ecef;
  padding: 2px 6px;
  border-radius: 4px;
}

/* Сводка */
.summary {
  display: flex;
  gap: 30px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  font-size: 14px;
  color: #495057;
  flex-wrap: wrap;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary-label {
  font-weight: 500;
  color: #6c757d;
}

.summary-value {
  font-weight: 600;
  color: #2c3e50;
  background-color: white;
  padding: 4px 12px;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.summary-value.warning {
  color: #dc3545;
  background-color: #fff5f5;
  border-color: #f5c6cb;
}

/* Анимации */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Адаптивность */
@media (max-width: 992px) {
  .results {
    padding: 20px;
  }
  
  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .table-header h3 {
    font-size: 20px;
  }
  
  .col-query { min-width: 250px; }
  .col-name { min-width: 200px; }
  .col-article { min-width: 120px; }
  
  .summary {
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .results {
    padding: 15px;
    margin-top: 20px;
  }
  
  .table-header h3 {
    font-size: 18px;
  }
  
  .btn-download-excel {
    padding: 10px 20px;
    font-size: 14px;
    width: 100%;
    justify-content: center;
  }
  
  .results-table th,
  .results-table td {
    padding: 10px 8px;
    font-size: 13px;
  }
  
  .cell {
    font-size: 13px;
  }
  
  .summary {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .results {
    padding: 12px;
  }
  
  .table-header h3 {
    font-size: 16px;
  }
  
  .results-table th,
  .results-table td {
    padding: 8px 6px;
    font-size: 12px;
  }
  
  .cell {
    font-size: 12px;
  }
  
  .query-info {
    font-size: 10px;
  }
}
</style>