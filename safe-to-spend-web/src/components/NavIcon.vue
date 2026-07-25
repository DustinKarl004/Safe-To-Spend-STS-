<script setup>
defineProps({
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
})
</script>

<template>
  <svg :width="size" :height="size" viewBox="0 0 24 24" fill="none">
    <template v-if="icon === 'gauge'">
      <path d="M4.5 16a7.5 7.5 0 1 1 15 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <path d="M12 16l3.2-3.6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      <circle cx="12" cy="16" r="1.3" fill="currentColor" />
    </template>
    <template v-else-if="icon === 'plus'">
      <circle cx="12" cy="12" r="8.5" stroke="currentColor" stroke-width="1.8" />
      <path d="M12 8v8M8 12h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>
    <template v-else-if="icon === 'wallet'">
      <path
        d="M4 7.5A2 2 0 0 1 6 5.5h11a2 2 0 0 1 2 2v1h.5a1.5 1.5 0 0 1 1.5 1.5v6.5a1.5 1.5 0 0 1-1.5 1.5H6a2 2 0 0 1-2-2v-8.5Z"
        stroke="currentColor"
        stroke-width="1.7"
        stroke-linejoin="round"
      />
      <circle cx="15.5" cy="13" r="1.4" fill="currentColor" />
    </template>
    <template v-else-if="icon === 'settings'">
      <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.7" />
      <path
        d="M19.4 13a7.5 7.5 0 0 0 0-2l1.9-1.5-2-3.4-2.3.7a7.6 7.6 0 0 0-1.7-1L14.9 3h-3.8l-.4 2.4a7.6 7.6 0 0 0-1.7 1l-2.3-.8-2 3.4L6.6 11a7.5 7.5 0 0 0 0 2l-1.9 1.5 2 3.4 2.3-.7a7.6 7.6 0 0 0 1.7 1l.4 2.4h3.8l.4-2.4a7.6 7.6 0 0 0 1.7-1l2.3.8 2-3.4Z"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linejoin="round"
      />
    </template>
    <template v-else>
      <path d="M4 6h16M4 12h16M4 18h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
    </template>
  </svg>
</template>
