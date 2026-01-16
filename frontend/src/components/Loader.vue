<template>
  <div v-if="loading" class="loader-container">
    <div class="loader-card">
      <div class="loader-spinner">
        <div class="spinner"></div>
        <div class="spinner-ring"></div>
      </div>
      <div class="loader-content">
        <h3 class="loader-title">Идет обработка...</h3>
        <p class="loader-message">{{ message }}</p>
        <div class="loader-progress">
          <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>
        <div class="loader-hint">
          <small>Это может занять несколько минут в зависимости от количества запросов</small>
        </div>
      </div>
    </div>
    <div class="loader-backdrop"></div>
  </div>
</template>

<script setup>
defineProps({
  loading: {
    type: Boolean,
    default: false,
    required: true
  },
  message: {
    type: String,
    default: 'Пожалуйста, подождите'
  },
  progress: {
    type: Number,
    default: 0
  }
})
</script>

<style scoped>
.loader-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loader-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(4px);
}

.loader-card {
  position: relative;
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  max-width: 500px;
  width: 90%;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  z-index: 1001;
  animation: slideIn 0.4s ease-out;
  border: 1px solid #e9ecef;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loader-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin-bottom: 25px;
}

.spinner {
  width: 100%;
  height: 100%;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4562e4;
  border-radius: 50%;
  animation: spin 1.2s linear infinite;
}

.spinner-ring {
  position: absolute;
  top: -8px;
  left: -8px;
  right: -8px;
  bottom: -8px;
  border: 4px solid rgba(69, 98, 228, 0.1);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    opacity: 0.1;
  }
  50% {
    transform: scale(1.05);
    opacity: 0.2;
  }
}

.loader-content {
  width: 100%;
}

.loader-title {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 22px;
  font-weight: 600;
}

.loader-message {
  margin: 0 0 20px 0;
  color: #6c757d;
  font-size: 16px;
  line-height: 1.5;
}

.loader-progress {
  width: 100%;
  height: 8px;
  background-color: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 15px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4562e4, #390bdd);
  border-radius: 4px;
  transition: width 0.3s ease;
  animation: progressShimmer 2s infinite linear;
  background-size: 200% 100%;
}

@keyframes progressShimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

.loader-hint {
  margin-top: 15px;
}

.loader-hint small {
  color: #adb5bd;
  font-size: 13px;
  font-style: italic;
}

@media (max-width: 768px) {
  .loader-card {
    padding: 30px 25px;
    width: 95%;
  }
  
  .loader-spinner {
    width: 60px;
    height: 60px;
  }
  
  .spinner {
    border-width: 3px;
  }
  
  .loader-title {
    font-size: 20px;
  }
  
  .loader-message {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .loader-card {
    padding: 25px 20px;
  }
  
  .loader-spinner {
    width: 50px;
    height: 50px;
  }
  
  .loader-title {
    font-size: 18px;
  }
  
  .loader-message {
    font-size: 14px;
  }
  
  .loader-hint small {
    font-size: 12px;
  }
}
</style>