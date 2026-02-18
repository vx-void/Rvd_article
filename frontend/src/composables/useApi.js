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
  check: () => request('/api/health')
};

export const searchService = {
  search: (query) => request('/api/search', {
    method: 'POST',
    body: JSON.stringify({ query, top_k: 10 })
  })
};