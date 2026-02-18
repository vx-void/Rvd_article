import * as XLSX from 'xlsx';

export function exportToExcel(results, query) {
  const data = results.map(r => ({
    'Артикул': r.article,
    'Наименование': r.name,
    'Описание': r.description || '',
    'Уверенность': Math.round(r.confidence * 100) + '%',
    'Стандарт': r.standard || '',
    'Резьба': r.thread || '',
    'Тип': r.armature || '',
    'Угол': r.angle !== null ? r.angle + '°' : '',
    'Dy': r.dy !== null ? r.dy + ' мм' : ''
  }));

  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Результаты');

  const filename = `hydro-search-${new Date().toISOString().slice(0,10)}.xlsx`;
  XLSX.writeFile(wb, filename);
}