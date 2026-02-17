<template>
  <div class="results">
    <div class="header">
      <h2>Найдено {{ results.length }} совпадений</h2>
      <div class="stats">
        <span v-if="metrics">Время: {{ formatTime(metrics.processing_time_ms) }}</span>
        <button @click="$emit('export')">Скачать Excel</button>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Артикул</th>
          <th>Наименование</th>
          <th>Описание</th>
          <th>Уверенность</th>
          <th>Параметры</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="result in results" :key="result.article">
          <td class="article">{{ result.article }}</td>
          <td class="name">{{ result.name }}</td>
          <td class="desc">{{ result.description || '-' }}</td>
          <td :class="['confidence', getConfidenceClass(result.confidence)]">
            {{ Math.round(result.confidence * 100) }}%
          </td>
          <td class="params">
            <span v-if="result.standard">{{ result.standard }}</span>
            <span v-if="result.thread">/ {{ result.thread }}</span>
            <span v-if="result.angle !== null">/ {{ result.angle }}°</span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  results: Array,
  metrics: Object
});

defineEmits(['export']);

const formatTime = (ms) => {
  if (ms < 1000) return Math.round(ms) + ' мс';
  return (ms / 1000).toFixed(2) + ' с';
};

const getConfidenceClass = (val) => {
  if (val >= 0.8) return 'high';
  if (val >= 0.5) return 'medium';
  return 'low';
};
</script>

<style scoped>
.results {
  background: white;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.08);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.header h2 { color: #333; font-size: 20px; }

.stats {
  display: flex;
  gap: 20px;
  align-items: center;
  color: #666;
  font-size: 14px;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

th {
  background: #f8f9fa;
  padding: 14px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e0e0e0;
}

td {
  padding: 14px;
  border-bottom: 1px solid #eee;
  vertical-align: top;
}

tr:hover { background: #f8f9fa; }

.article {
  font-family: monospace;
  color: #390bdd;
  font-weight: 600;
}

.name { font-weight: 500; color: #333; }
.desc { color: #666; max-width: 300px; }

.confidence { font-weight: 600; }
.confidence.high { color: #28a745; }
.confidence.medium { color: #ffc107; }
.confidence.low { color: #dc3545; }

.params { color: #666; font-size: 12px; }
.params span { margin-right: 4px; }

button {
  padding: 8px 16px;
  font-size: 14px;
}
</style>