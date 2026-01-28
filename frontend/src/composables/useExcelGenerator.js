// src/composables/useExcelGenerator.js
import { utils, writeFileXLSX } from 'xlsx'


export const useExcelGenerator = () => {

    const formatResultsForExcel = (results) => {
    const excelData = []
    
    excelData.push([
    'Запрос',
    'Наименование',
    'Артикул',
    'Количество'
    ])
    
    results.forEach((result) => {
    if (result.matches && result.matches.length > 0) {
        // Для найденных компонентов
        result.matches.forEach((match) => {
        excelData.push([
            result.original_query || '',
            match.name || 'Не указано',
            match.article || 'Не указан',
            result.quantity || 1
        ])
        })
    } else {
        // Для ненайденных компонентов
        excelData.push([
        result.original_query || '',
        'Компонент не найден',
        '',
        result.quantity || 1
        ])
    }
    })
    

    const totalFound = results.reduce((sum, result) =>
    sum + (result.matches?.length || 0), 0
    )
    const totalRequests = results.length
    
рока
   

    
    return excelData
  }
  

  const applyExcelStyles = (worksheet, excelData) => {
    
    const colWidths = [
      { wch: 40 },  // Запрос
      { wch: 50 },  // Наименование
      { wch: 25 },  // Артикул
      { wch: 12 }   // Количество
    ]
    worksheet['!cols'] = colWidths
    
    // Определяем диапазон ячеек
    const range = utils.decode_range(worksheet['!ref'])
    
    // Стили для заголовков (строка 1)
    for (let col = range.s.c; col <= range.e.c; col++) {
    const cellAddress = utils.encode_cell({ r: 0, c: col })
    if (!worksheet[cellAddress]) continue
    
    if (!worksheet[cellAddress].s) worksheet[cellAddress].s = {}
    Object.assign(worksheet[cellAddress].s, {
        font: { 
        bold: true, 
        color: { rgb: "FFFFFF" },
        sz: 12
        },
        fill: { 
        fgColor: { rgb: "4562E4" },
        patternType: "solid"
        },
        alignment: { 
        vertical: "center",
        horizontal: "center",
        wrapText: true
        }
    })
    }
    
    // Стили для данных
    for (let row = 1; row < excelData.length - 3; row++) {
    const isNotFound = excelData[row][1] === '❌ Компонент не найден в базе'
    
    for (let col = 0; col < excelData[row].length; col++) {
        const cellAddress = utils.encode_cell({ r: row, c: col })
        if (!worksheet[cellAddress]) continue
        
        if (!worksheet[cellAddress].s) worksheet[cellAddress].s = {}
        
        const baseStyle = {
        alignment: { 
            vertical: "top",
            wrapText: true
        }
        }
        
        // Специфические стили
        if (col === 0) { // Запрос
        Object.assign(baseStyle, {
            font: { bold: true, color: { rgb: "2C3E50" } }
        })
        } else if (col === 1 && isNotFound) { // Наименование (не найдено)
        Object.assign(baseStyle, {
            font: { color: { rgb: "DC3545" }, italic: true },
            fill: { fgColor: { rgb: "FFF5F5" }, patternType: "solid" }
        })
        } else if (col === 2) { // Артикул
        Object.assign(baseStyle, {
            font: { bold: true, color: { rgb: "007BFF" } }
        })
        } else if (col === 3) { // Количество
        Object.assign(baseStyle, {
            alignment: { horizontal: "center", vertical: "center" },
            font: { bold: true, color: { rgb: "28A745" } }
        })
        }
        
        // Чередование цвета строк
        if (row % 2 === 1 && !isNotFound) {
        baseStyle.fill = baseStyle.fill || { fgColor: { rgb: "F8F9FA" }, patternType: "solid" }
        }
        
        Object.assign(worksheet[cellAddress].s, baseStyle)
    }
    }
    
    // Стили для итоговых строк
    const lastRow = excelData.length - 1
    const secondLastRow = excelData.length - 2
    
    // "ИТОГО:" строка
    for (let col = 0; col < excelData[secondLastRow].length; col++) {
    const cellAddress = utils.encode_cell({ r: secondLastRow, c: col })
    if (!worksheet[cellAddress]) continue
    
    if (!worksheet[cellAddress].s) worksheet[cellAddress].s = {}
    Object.assign(worksheet[cellAddress].s, {
        font: { bold: true, sz: 12 },
        fill: { fgColor: { rgb: "E9ECEF" }, patternType: "solid" }
    })
    }
    
    // Итоговая статистика
    for (let col = 0; col < excelData[lastRow].length; col++) {
    const cellAddress = utils.encode_cell({ r: lastRow, c: col })
    if (!worksheet[cellAddress]) continue
    
    if (!worksheet[cellAddress].s) worksheet[cellAddress].s = {}
    Object.assign(worksheet[cellAddress].s, {
        font: { bold: true, color: { rgb: "6C757D" } }
    })
    }
}


const generateFilename = (results) => {
    const now = new Date()
    const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
    const timeStr = now.toTimeString().slice(0, 8).replace(/:/g, '')
    
    const totalFound = results.reduce((sum, result) => 
    sum + (result.matches?.length || 0), 0
    )
    
    return `гидравлика_${dateStr}_${totalFound}шт.xlsx`
}

const generateAndDownloadExcel = (results) => {
    try {
      // Валидация
    if (!results || !Array.isArray(results) || results.length === 0) {
        throw new Error('Нет данных для экспорта')
    }
    
      // Форматируем данные
    const excelData = formatResultsForExcel(results)
    
      // Создаем worksheet
    const worksheet = utils.aoa_to_sheet(excelData)
    
      // Применяем стили
    applyExcelStyles(worksheet, excelData)
    
      // Создаем workbook
    const workbook = utils.book_new()
    utils.book_append_sheet(workbook, worksheet, 'Результаты поиска')
    
      // Свойства документа
    workbook.Props = {
        Title: 'Результаты поиска гидравлических компонентов',
        Author: 'Гидравлика Поиск',
        CreatedDate: new Date()
    }

      // Генерируем и скачиваем файл
    const filename = generateFilename(results)
    writeFileXLSX(workbook, filename)
    
    console.log(`Excel файл "${filename}" успешно сгенерирован`)
    return true
    
    } catch (error) {
    console.error('Ошибка генерации Excel:', error)
    throw new Error(`Не удалось сгенерировать Excel файл: ${error.message}`)
    }
}

return {
    generateAndDownloadExcel,
    generateFilename
}
}

export default useExcelGenerator