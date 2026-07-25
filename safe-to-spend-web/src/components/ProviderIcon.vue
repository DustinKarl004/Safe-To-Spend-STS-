<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  color: { type: String, required: true },
  initials: { type: String, required: true },
  logo: { type: String, default: null },
  icon: { type: String, default: null },
  size: { type: [Number, String], default: 36 },
})

// Minimal line icons for cash-style wallets with no official logo asset.
const PATHS = {
  cash: 'M3 7h18v10H3V7Z M12 9.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z M6 7v10M18 7v10',
  wallet:
    'M3 7a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2v1h1a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7Z M16 12.5a1.3 1.3 0 1 0 0 2.6 1.3 1.3 0 0 0 0-2.6Z',
  piggy_bank:
    'M4 12.5c0-3.6 3.4-6.5 8-6.5 3.6 0 6.6 1.8 7.7 4.3H21a1 1 0 0 1 1 1v2.4a1 1 0 0 1-1 1h-1.3c-.5 1-1.4 1.9-2.7 2.5V19h-2.5v-1.1a10 10 0 0 1-1.5.1c-.7 0-1.4-.05-2-.15V19H8.5v-1.6C5.8 16.2 4 14.5 4 12.5Z M9 8.5V6M15 8.5V6M7.5 12h.01',
  petty_cash: 'M4 6h16v12H4V6Z M4 10h16 M8 14h3',
}

const path = computed(() => (props.icon ? PATHS[props.icon] : null))
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full"
    :class="logo ? 'bg-white' : ''"
    :style="{
      width: `${size}px`,
      height: `${size}px`,
      background: logo ? '#ffffff' : color,
    }"
    :title="name"
  >
    <img v-if="logo" :src="logo" :alt="name" class="h-[78%] w-[78%] object-contain" />
    <svg v-else-if="path" :width="Math.round(Number(size) * 0.52)" :height="Math.round(Number(size) * 0.52)" viewBox="0 0 24 24" fill="none">
      <path :d="path" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    <span v-else class="font-bold text-white" :style="{ fontSize: `${Math.max(10, Number(size) * 0.34)}px` }">
      {{ initials }}
    </span>
  </span>
</template>
