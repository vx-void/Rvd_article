import { ref } from 'vue';
import { healthService } from '../services/api.js';

export function useApi() {
  const isOnline = ref(false);
  const serverStats = ref(null);

  const checkHealth = async () => {
    try {
      const data = await healthService.check();
      isOnline.value = data.status === 'healthy';
      serverStats.value = data.stats;
    } catch {
      isOnline.value = false;
      serverStats.value = null;
    }
  };

  return {
    isOnline,
    serverStats,
    checkHealth
  };
}