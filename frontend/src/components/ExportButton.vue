<template>
  <button @click="downloadExcel" class="btn btn-excel">Скачать .xlsx</button>
</template>

<script setup>

import * as XLSX from 'xlsx'

// Пример данных — замените на ваши
const articles = [
  'Артикул-001',
  'Артикул-002',
  'Артикул-ABC123'
]

const downloadExcel = () => {
  // 1. Преобразуем массив артикулов в массив объектов (для удобства таблицы)
  const data = articles.map(article => ({ Артикул: article }))

  // 2. Создаём рабочую книгу (workbook)
  const workbook = XLSX.utils.book_new()

  // 3. Преобразуем данные в worksheet
  const worksheet = XLSX.utils.json_to_sheet(data)

  // 4. Добавляем лист в книгу
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Артикулы')

  // 5. Генерируем бинарный файл и скачиваем
  XLSX.writeFile(workbook, 'артикулы.xlsx')
}
</script>


<style scoped>
.btn-excel {
  background-color: #28a745;
  color: white;
  padding: 1rem 2.5rem;
  border-radius: 5px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-excel:hover {
  background-color: #218838;
}

.excel-icon {
  font-size: 1.2rem;
}
</style>