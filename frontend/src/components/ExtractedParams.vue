<template>
  <div class="extracted">
    <h4>AI извлек из запроса:</h4>
    <div class="grid">
      <div class="item">
        <span class="label">Стандарт:</span>
        <span :class="['value', !params.standard && 'empty']">
          {{ params.standard || 'не указан' }}
        </span>
      </div>
      <div class="item">
        <span class="label">Резьба:</span>
        <span :class="['value', !params.thread && 'empty']">
          {{ params.thread || 'не указана' }}
        </span>
      </div>
      <div class="item">
        <span class="label">Тип:</span>
        <span :class="['value', !params.armature && 'empty']">
          {{ formatArmature(params.armature) }}
        </span>
      </div>
      <div class="item">
        <span class="label">Угол:</span>
        <span :class="['value', params.angle === null && 'empty']">
          {{ params.angle !== null ? params.angle + '°' : 'не указан' }}
        </span>
      </div>
      <div class="item">
        <span class="label">Dy:</span>
        <span :class="['value', params.dy === null && 'empty']">
          {{ params.dy !== null ? params.dy + ' мм' : 'не указан' }}
        </span>
      </div>
      <div class="item">
        <span class="label">Деталь:</span>
        <span :class="['value', !params.component_type && 'empty']">
          {{ params.component_type || 'не определен' }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  params: Object
});

const formatArmature = (val) => {
  if (val === 'male') return 'папа (штуцер)';
  if (val === 'female') return 'мама (гайка)';
  return 'не указан';
};
</script>

<style scoped>
.extracted {
  background: #e8f4f8;
  border-left: 4px solid #17a2b8;
  padding: 15px 20px;
  margin-bottom: 20px;
  border-radius: 0 8px 8px 0;
}

h4 {
  color: #17a2b8;
  font-size: 14px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 10px;
}

.item {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  font-size: 13px;
}

.label { color: #888; }
.value { font-weight: 600; color: #333; }
.value.empty { color: #bbb; font-style: italic; }
</style>