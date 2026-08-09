<script setup>
defineProps({
  cards: {
    type: Array,
    required: true
  }
})
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <div 
      v-for="(card, index) in cards" 
      :key="index"
      class="bg-slate-900 border border-slate-800 p-6 rounded-xl flex items-center justify-between shadow-lg">
      <div>
        <p class="text-xs font-semibold tracking-wider text-slate-400 uppercase">{{ card.title }}</p>
        <h3 class="text-3xl font-bold mt-1" :class="card.textColor">{{ card.value }} machines</h3>
      </div>
      <div class="w-12 h-12 rounded-lg border flex items-center justify-center text-xl" :class="card.badgeColor">
        {{ card.icon }}
      </div>
    </div>
  </div>
</template>
