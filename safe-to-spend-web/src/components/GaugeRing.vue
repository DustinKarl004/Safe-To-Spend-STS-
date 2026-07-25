<script setup>
import { computed } from 'vue'

const props = defineProps({
  spent: { type: Number, default: 0 },
  allowance: { type: Number, default: 0 },
  size: { type: [Number, String], default: 176 },
})

const RADIUS = 78
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const percent = computed(() => {
  if (props.allowance <= 0) return 0
  return Math.min(props.spent / props.allowance, 1)
})

const overBudget = computed(() => props.allowance > 0 && props.spent > props.allowance)

const strokeColor = computed(() => {
  if (overBudget.value) return 'var(--danger)'
  if (percent.value > 0.8) return 'var(--amber)'
  return 'var(--accent)'
})

const dashOffset = computed(() => CIRCUMFERENCE * (1 - percent.value))
</script>

<template>
  <div class="relative inline-flex shrink-0 items-center justify-center" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg class="-rotate-90" width="100%" height="100%" viewBox="0 0 180 180">
      <circle cx="90" cy="90" :r="RADIUS" fill="none" stroke="var(--bg-sunken)" stroke-width="14" />
      <circle
        cx="90"
        cy="90"
        :r="RADIUS"
        fill="none"
        :stroke="strokeColor"
        stroke-width="14"
        stroke-linecap="round"
        :stroke-dasharray="CIRCUMFERENCE"
        :stroke-dashoffset="dashOffset"
        style="transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease"
      />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center px-4 text-center">
      <slot />
    </div>
  </div>
</template>
