<script setup>
import { computed } from 'vue'

const props = defineProps({
  segments: { type: Array, required: true }, // [{ label, color, value }]
  size: { type: [Number, String], default: 168 },
})

const RADIUS = 72
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

const total = computed(() => props.segments.reduce((sum, s) => sum + s.value, 0))

const arcs = computed(() => {
  let cumulative = 0
  return props.segments
    .filter((s) => s.value > 0)
    .map((s) => {
      const fraction = total.value > 0 ? s.value / total.value : 0
      const arcLength = fraction * CIRCUMFERENCE
      const arc = {
        ...s,
        fraction,
        dasharray: `${arcLength} ${CIRCUMFERENCE - arcLength}`,
        dashoffset: -cumulative,
      }
      cumulative += arcLength
      return arc
    })
})
</script>

<template>
  <div class="relative inline-flex shrink-0 items-center justify-center" :style="{ width: `${size}px`, height: `${size}px` }">
    <svg class="-rotate-90" width="100%" height="100%" viewBox="0 0 160 160">
      <circle cx="80" cy="80" :r="RADIUS" fill="none" stroke="var(--bg-sunken)" stroke-width="16" />
      <circle
        v-for="arc in arcs"
        :key="arc.label"
        cx="80"
        cy="80"
        :r="RADIUS"
        fill="none"
        :stroke="arc.color"
        stroke-width="16"
        :stroke-dasharray="arc.dasharray"
        :stroke-dashoffset="arc.dashoffset"
      />
    </svg>
    <div class="absolute inset-0 flex flex-col items-center justify-center px-3 text-center">
      <slot />
    </div>
  </div>
</template>
