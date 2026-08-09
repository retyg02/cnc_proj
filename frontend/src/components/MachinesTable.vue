<script setup>
defineProps({
  machines: {
    type: Array,
    required: true
  }
})
</script>

<template>
  <div class="bg-slate-900 border border-slate-800 rounded-xl shadow-lg overflow-hidden">
    <div class="px-6 py-4 border-b border-slate-800">
      <h2 class="text-lg font-bold text-white">Monitoring</h2>
    </div>

    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-950/50 text-slate-400 text-xs font-semibold uppercase tracking-wider border-b border-slate-800">
            <th class="px-6 py-3">ID</th>
            <th class="px-6 py-3">Machine Name</th>
            <th class="px-6 py-3">Status</th>
            <th class="px-6 py-3">Load Rate</th>
            <th class="px-6 py-3">Current Command</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800 text-sm">
          <tr v-for="machine in machines" :key="machine.id" class="hover:bg-slate-800/30 transition">
            <td class="px-6 py-4 font-mono text-slate-500">#{{ machine.id }}</td>
            <td class="px-6 py-4 font-semibold text-white">{{ machine.name }}</td>
            <td class="px-6 py-4">
              <span 
                class="px-2.5 py-1 rounded-full text-xs font-medium"
                :class="{
                  'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20': machine.status === 'working',
                  'bg-amber-500/10 text-amber-400 border border-amber-500/20': machine.status === 'idle',
                  'bg-rose-500/10 text-rose-400 border border-rose-500/20': machine.status === 'error',
                }">
                {{ machine.status }}
              </span>
            </td>
            <td class="px-6 py-4 w-1/4">
              <div class="flex items-center space-x-3">
                <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div 
                    class="h-full rounded-full transition-all duration-500"
                    :class="machine.load_percent > 80 ? 'bg-amber-500' : 'bg-emerald-500'"
                    :style="{ width: machine.load_percent + '%' }"
                  ></div>
                </div>
                <span class="font-mono text-xs text-slate-400">{{ machine.load_percent }}%</span>
              </div>
            </td>
            <td class="px-6 py-4">
              <span class="font-mono bg-slate-950 px-2 py-1 rounded border border-slate-800 text-slate-300">
                {{ machine.current_command }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
