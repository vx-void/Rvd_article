const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function search(query, top_k = 10) {
  const response = await fetch(`${API_URL}/api/v1/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Ошибка ${response.status}`);
  }

  return response.json();
}

export function exportToExcel(results, query) {
  import('xlsx').then(XLSX => {
    const data = results.map(r => ({
      'Артикул': r.article,
      'Наименование': r.name,
      'Описание': r.description || '',
      'Уверенность': Math.round(r.confidence * 100) + '%',
      'Стандарт': r.standard || '',
      'Резьба': r.thread || '',
      'Тип': r.armature === 'male' ? 'папа' : r.armature === 'female' ? 'мама' : '',
      'Угол': r.angle !== null ? r.angle + '°' : '',
    }));

    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Результаты');

    const filename = `hydro-search-${new Date().toISOString().slice(0, 10)}.xlsx`;
    XLSX.writeFile(wb, filename);
  });
}