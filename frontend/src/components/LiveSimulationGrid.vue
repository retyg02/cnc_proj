<script setup>
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import axios from 'axios'

const props = defineProps({
  machines: {
    type: Array,
    required: true
  }
})

// Фильтруем список машин: берем только те, у которых статус "working"
const workingMachines = computed(() => {
  return props.machines.filter(m => m.status === 'working')
})

// Хранилище массивов точек для каждого активного станка { [machineId]: [{x, y}, ...] }
const trajectories = ref({})
let pollInterval = null

// Функция загрузки координат из MongoDB для конкретной сессии конкретной машины
const fetchCoordinates = async (machineId, sessionId) => {
  if (!sessionId) return
  try {
    // Наш новый эндпоинт, который мы дописали во FastAPI
    const response = await axios.get(`http://127.0.0.1:8000/telemetry/coordinates/${sessionId}`)
    
    // Сохраняем точки. Если массив пустой, инициализируем дефолтным пустым списком
    trajectories.value[machineId] = response.data || []
  } catch (error) {
    console.error(`Ошибка забора координат для станка ${machineId}:`, error)
  }
}

// Запускаем периодический опрос MongoDB для всех активных в данный момент станков
const startPolling = () => {
  if (pollInterval) clearInterval(pollInterval)
  
  pollInterval = setInterval(() => {
    workingMachines.value.forEach(machine => {
      // Подставляем session_id, который привязан к текущей строке станка в Postgres
      fetchCoordinates(machine.id, machine.session_id)
    })
  }, 500) // Такт опроса совпадает с C# шлюзом — 500 мс (2 Гц)
}

// Следим за списком работающих машин. Если кто-то ушел в IDLE — зачищаем его массив из памяти
watch(workingMachines, (newWorking) => {
  const activeIds = newWorking.map(m => m.id)
  Object.keys(trajectories.value).forEach(id => {
    if (!activeIds.includes(Number(id))) {
      delete trajectories.value[id]
    }
  })
}, { deep: true })

// Вспомогательная функция генерации строки для SVG-полилинии (перевод координат станка в пиксели экрана)
const generateSvgPath = (points) => {
  if (!points || points.length === 0) return ''
  
  // Координаты C++ ядра масштабируются под размер нашего SVG контейнера (300х300)
  // Центр сетки смещаем в середину (150, 150)
  const scale = 3.0 
  const center = 150

  return points.map(p => {
    const screenX = center + (p.x * scale)
    const screenY = center - (p.y * scale) // Инвертируем Y для соответствия декартовой сетке
    return `${screenX},${screenY}`
  }).join(' ')
}

// Получаем координаты последней точки фрезы, чтобы отрисовать режущий маркер
const getLastPoint = (points) => {
  if (!points || points.length === 0) return { x: 150, y: 150, is_cutting: false }
  const scale = 3.0
  const center = 150
  const last = points[points.length - 1]
  return {
    x: center + (last.x * scale),
    y: center - (last.y * scale),
    is_cutting: last.is_cutting
  }
}

onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>

<template>
  <!-- Компонент рендерится на экране ТОЛЬКО если есть хотя бы один работающий комплекс -->
  <div v-if="workingMachines.length > 0" class="space-y-3 animate-fade-in">
    <div class="flex items-center space-x-2">
      <span class="text-sm">👁️‍🗨️</span>
      <h2 class="text-sm font-bold text-slate-400 tracking-wider uppercase">Мониторинг траектории резки (NoSQL Real-Time)</h2>
    </div>

    <!-- ДИНАМИЧЕСКИЙ GRID: 
         Если работает 1 станок — растягивается на всю ширину (grid-cols-1).
         Если 2 и более — перестраивается в сетку (md:grid-cols-2, lg:grid-cols-3) -->
    <div :class="[
      'grid gap-6 transition-all duration-500',
      workingMachines.length === 1 ? 'grid-cols-1' : 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3'
    ]">
      <div v-for="machine in workingMachines" :key="machine.id" 
           class="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-2xl relative overflow-hidden flex flex-col items-center">
        
        <!-- Шапка индивидуальной карточки симуляции -->
        <div class="w-full flex justify-between items-center mb-4 border-b border-slate-800 pb-2">
          <div>
            <h3 class="text-base font-bold text-white">{{ machine.name }}</h3>
            <p class="text-2xs font-mono text-slate-500">Сессия: {{ machine.session_id || 'нет данных' }}</p>
          </div>
          <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full text-2xs font-mono uppercase tracking-wider animate-pulse">
            обработка
          </span>
        </div>

        <!-- ГРАФИЧЕСКИЙ SVG-КОНТЕЙНЕР ДЛЯ ОТРИСОВКИ СЛЕДА -->
        <div class="w-[300px] h-[300px] bg-black rounded-lg border border-slate-800 relative shadow-inner overflow-hidden">
          
          <!-- Промышленная Декартова сетка (векторные направляющие) -->
          <svg class="absolute inset-0 w-full h-full pointer-events-none opacity-20">
            <defs>
              <pattern id="grid-pattern" width="30" height="30" patternUnits="userSpaceOnUse">
                <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#475569" stroke-width="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid-pattern)" />
            <!-- Осевые линии центра -->
            <line x1="150" y1="0" x2="150" y2="300" stroke="#94a3b8" stroke-width="1" />
            <line x1="0" y1="150" x2="300" y2="150" stroke="#94a3b8" stroke-width="1" />
          </svg>

          <!-- Слой отрисовки честной траектории G-кода -->
          <svg class="absolute inset-0 w-full h-full">
            <!-- Динамическая полилиния следа движения фрезы -->
            <polyline
              fill="none"
              stroke="#10b981"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
              :points="generateSvgPath(trajectories[machine.id])"
              class="transition-all duration-300"
            />

            <!-- Пульсирующая точка — текущее положение фрезы (резец) -->
            <circle
              :cx="getLastPoint(trajectories[machine.id]).x"
              :cy="getLastPoint(trajectories[machine.id]).y"
              :r="getLastPoint(trajectories[machine.id]).is_cutting ? '5' : '3'"
              :fill="getLastPoint(trajectories[machine.id]).is_cutting ? '#ef4444' : '#eab308'"
              class="animate-ping opacity-75"
            />
            <circle
              :cx="getLastPoint(trajectories[machine.id]).x"
              :cy="getLastPoint(trajectories[machine.id]).y"
              :r="getLastPoint(trajectories[machine.id]).is_cutting ? '4' : '2.5'"
              :fill="getLastPoint(trajectories[machine.id]).is_cutting ? '#ef4444' : '#eab308'"
            />
          </svg>

          <!-- Цифровой индикатор координат в углу экрана симулятора -->
          <div class="absolute bottom-2 left-2 bg-slate-950/80 backdrop-blur-sm border border-slate-800 rounded px-2 py-1 text-3xs font-mono text-emerald-400 space-y-0.5">
            <div v-if="trajectories[machine.id] && trajectories[machine.id].length > 0">
              X: {{ trajectories[machine.id][trajectories[machine.id].length - 1].x.toFixed(1) }} |
              Y: {{ trajectories[machine.id][trajectories[machine.id].length - 1].y.toFixed(1) }}
            </div>
            <div v-else class="text-slate-500">Синхронизация буфера...</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.text-2xs { font-size: 0.65rem; }
.text-3xs { font-size: 0.55rem; }
.animate-fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
