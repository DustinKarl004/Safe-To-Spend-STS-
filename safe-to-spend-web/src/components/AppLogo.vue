<script setup>
defineProps({
  size: { type: [Number, String], default: 40 },
  withWordmark: { type: Boolean, default: false },
})
</script>

<template>
  <div class="inline-flex items-center gap-2.5">
    <svg :width="size" :height="size" viewBox="0 0 88 88" aria-hidden="true">
      <circle cx="44" cy="44" r="34" fill="none" style="stroke: var(--bg-sunken)" stroke-width="8" />
      <path
        d="M 68.8 63.7 A 34 34 0 1 1 68.8 24.3"
        fill="none"
        stroke="url(#sts-gauge-gradient)"
        stroke-width="8"
        stroke-linecap="round"
      />
      <circle cx="68.8" cy="24.3" r="4.5" style="fill: var(--accent)" />
      <text
        x="44"
        y="53"
        text-anchor="middle"
        font-family="ui-rounded, -apple-system, system-ui, sans-serif"
        font-size="34"
        font-weight="800"
        style="fill: var(--text)"
      >
        ₱
      </text>
      <defs>
        <linearGradient id="sts-gauge-gradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" style="stop-color: var(--amber)" />
          <stop offset="1" style="stop-color: var(--accent)" />
        </linearGradient>
      </defs>
    </svg>
    <span v-if="withWordmark" class="font-display text-2xl font-extrabold tracking-tight">
      safe<span style="color: var(--accent)">:</span><span class="text-text-dim font-bold">spend</span>
    </span>
  </div>
</template>
