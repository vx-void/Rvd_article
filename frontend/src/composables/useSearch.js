import { ref } from 'vue';
import { searchService } from '../services/api.js';

export function useSearch() {
  const loading = ref(false);
  const error = ref(null);
  const results = ref([]);
  const metrics = ref(null);
  const extractedParams = ref(null);
  const searched = ref(false);

  const search = async (query) => {
    loading.value = true;
    error.value = null;
    searched.value = true;

    try {
      const response = await searchService.search(query);
      results.value = response.results;
      metrics.value = response.metrics;
      extractedParams.value = response.extracted_params;
    } catch (err) {
      error.value = err.message || 'Ошибка поиска';
      results.value = [];
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    error,
    results,
    metrics,
    extractedParams,
    searched,
    search
  };
}