<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

import AnalyticsCards from './components/AnalyticsCards.vue'
import MachinesTable from './components/MachinesTable.vue'
import GcodeUpload from './components/GcodeUpload.vue'
import LiveSimulationGrid from './components/LiveSimulationGrid.vue'

const factory_name = ref("Factory")
let updateInterval = null 

const stats_cards = ref([
  { title: "Total Fleet", value: 0, icon: "🎛️", textColor: "text-white", badgeColor: "bg-blue-500/10 border-blue-500/20 text-blue-400" },
  { title: "In Production", value: 0, icon: "🟢", textColor: "text-emerald-400", badgeColor: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" },
  { title: "Emergency Stop", value: 0, icon: "🚨", textColor: "text-rose-500", badgeColor: "bg-rose-500/10 border-rose-500/20 text-rose-500" }
])

// Опрос аналитики
const fetch_analytics = async () => {
  try {
    const response = await axios.get('http://127.0.0.1:8000/telemetry/analytics')
    const data = response.data
    
    stats_cards.value[0].value = data.total
    stats_cards.value[1].value = data.working
    stats_cards.value[2].value = data.error
  } catch (error) {
    console.error("[❌ FASTAPI ANALYTICS ERROR]: ", error)
  }
}

const machines_list = ref([])

const fetch_machines = async () => {
  try {
    const response = await axios.get('http://localhost:8000/telemetry/machines')
    machines_list.value = response.data
  } catch (error) {
    console.error("[❌ FASTAPI MACHINES ERROR]: ", error)
  }
}

const startLiveSync = () => {
  fetch_analytics()
  fetch_machines()

  
  updateInterval = setInterval(() => {
    fetch_analytics()
    fetch_machines()
  }, 500)
}

onMounted(() => {
  startLiveSync() 
})

onUnmounted(() => {
  if (updateInterval) clearInterval(updateInterval) 
})
</script>


<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
    
    <header class="bg-slate-900 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
      <div class="flex items-center space-x-3">
        <span class="text-2xl">🏭</span>
        <div>
          <h1 class="text-xl font-bold tracking-tight text-white">{{ factory_name }}</h1>
          <p class="text-xs text-slate-400">Observing system • Dispatcher panel</p>
        </div>
      </div>
      <div class="text-sm text-slate-400 bg-slate-950 px-3 py-1.5 rounded-md border border-slate-800">
        ⏱️ Sync: <span class="text-emerald-400 font-mono">ONLINE</span>
      </div>
    </header>

    <main class="max-w-7xl mx-auto p-6 space-y-6">
      
      <AnalyticsCards :cards="stats_cards" />
      <GcodeUpload />
      <MachinesTable :machines="machines_list" @refresh="fetch_machines" />
      <LiveSimulationGrid :machines="machines_list" />
    </main>

  </div>
</template>
