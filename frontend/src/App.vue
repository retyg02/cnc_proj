<script setup>
import { ref } from 'vue'

import AnalyticsCards from './components/AnalyticsCards.vue'
import MachinesTable from './components/MachinesTable.vue'
import GcodeUpload from './components/GcodeUpload.vue'

const factory_name = ref("Factory")

const stats_cards = ref([
  { title: "Total Fleet", value: 3, icon: "🎛️", textColor: "text-white", badgeColor: "bg-blue-500/10 border-blue-500/20 text-blue-400" },
  { title: "In Production", value: 1, icon: "🟢", textColor: "text-emerald-400", badgeColor: "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" },
  { title: "Emergency Stop", value: 1, icon: "🚨", textColor: "text-rose-500", badgeColor: "bg-rose-500/10 border-rose-500/20 text-rose-500" }
])

const machines_list = ref([
  { id: 1, name: "CNC Turning Center", status: "working", load_percent: 75, current_command: "RESET" },
  { id: 2, name: "Milling Machine Router", status: "idle", load_percent: 0, current_command: "RESET" },
  { id: 3, name: "Laser Cutting System", status: "error", load_percent: 95, current_command: "STOP" }
])
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
      <MachinesTable :machines="machines_list" />

    </main>

  </div>
</template>
