const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(url, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  };

  const response = await fetch(`${API_URL}${url}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || `Ошибка ${response.status}`);
  }

  return response.json();
}

export const healthService = {
  check: () => request('/api/v1/health')
};

export const searchService = {
  search: (query, apiKey) => request('/api/v1/search', {
    method: 'POST',
    headers: { 'X-API-Key': apiKey },
    body: JSON.stringify({ query, top_k: 10 })
  })
};