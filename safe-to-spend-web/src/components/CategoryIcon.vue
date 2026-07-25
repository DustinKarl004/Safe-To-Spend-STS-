<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, required: true },
  color: { type: String, default: '#5A6178' },
  size: { type: [Number, String], default: 36 },
})

// Minimal, consistent 24x24 line icons — no emoji, no third-party icon set.
const PATHS = {
  food: 'M6 3v7a2 2 0 0 0 2 2v9M6 3v6M8 3v6M10 3v6M10 3v18M18 3c-2 0-3 2-3 5s1 4 1 6v9',
  groceries: 'M4 8h16l-1.5 11a2 2 0 0 1-2 1.8H7.5a2 2 0 0 1-2-1.8L4 8Z M8 8V6a4 4 0 0 1 8 0v2',
  transpo: 'M4 16V9a2 2 0 0 1 2-2h4l3-3h3l1 3h1a2 2 0 0 1 2 2v7M4 16h16M4 16v2a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-1h10v1a1 1 0 0 0 1 1h1a1 1 0 0 0 1-1v-2M7.5 16a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3ZM16.5 16a1.5 1.5 0 1 1 0 3 1.5 1.5 0 0 1 0-3Z',
  shopping: 'M6 8h12l1 12.2a1.8 1.8 0 0 1-1.8 1.8H6.8A1.8 1.8 0 0 1 5 20.2L6 8Z M9 8V6a3 3 0 0 1 6 0v2',
  bills: 'M6 3h9l4 4v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Z M14 3v4a1 1 0 0 0 1 1h4 M8 12h8M8 15.5h8M8 19h5',
  home: 'M4 11.5 12 4l8 7.5V20a1 1 0 0 1-1 1h-4v-6H9v6H5a1 1 0 0 1-1-1v-8.5Z',
  health: 'M12 21s-7.5-4.6-10-9.3C.6 8.6 2.3 5 5.7 5c2 0 3.4 1.1 4.3 2.6C11 6.1 12.3 5 14.3 5c3.4 0 5.1 3.6 3.7 6.7C15.5 16.4 12 21 12 21Z',
  subscriptions: 'M4 12a8 8 0 0 1 13.3-6M20 12a8 8 0 0 1-13.3 6 M17 3v4h-4 M7 21v-4h4',
  entertainment: 'M4 5h16a1 1 0 0 1 1 1v11a1 1 0 0 1-1 1h-6l1.5 3h-7L9 18H4a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z M10 8.3v5.4l4.5-2.7L10 8.3Z',
  games: 'M7 8h10a4 4 0 0 1 4 4.5l-.7 4a2 2 0 0 1-3.5 1L15 15.5H9L7.2 17.5a2 2 0 0 1-3.5-1l-.7-4A4 4 0 0 1 7 8Z M9 11v3M7.5 12.5h3M15.5 11.5h.01M17.5 13.5h.01',
  travel: 'M11 5 3 9.5v1.7l7.4-2v4.9L8 15.6v1.6l3.5-1 .5 2.8 1-.6.5-2.6 3.5 1v-1.6l-2.4-1.5v-4.9L21 11.2V9.5L13 5h-2Z',
  personal_care: 'M12 3c2 2.6 4 5.6 4 8.6a4 4 0 1 1-8 0C8 8.6 10 5.6 12 3Z M8.5 19.5h7',
  gifts: 'M4 9h16v3H4V9Z M5 12h14v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9Z M12 9v13 M12 9c-1.3 0-3.5-.6-3.5-2.8A2.2 2.2 0 0 1 10.7 4c1.7 0 2.7 2.2 3.3 5 0.6-2.8 1.6-5 3.3-5a2.2 2.2 0 0 1 2.2 2.2C19.5 8.4 17.3 9 16 9',
  pets: 'M8 10.5a2 2 0 1 1-3-1.7A2 2 0 0 1 8 10.5Z M13.5 8.5a2 2 0 1 1-3-1.7 2 2 0 0 1 3 1.7Z M19 10.5a2 2 0 1 1-3-1.7 2 2 0 0 1 3 1.7Z M17 15a2 2 0 1 1-2.6-1.9A2 2 0 0 1 17 15Z M12 14c-2.8 0-5.5 1.7-5.5 4.3 0 1.5 1.3 2.7 2.9 2.4l1.8-.4a3.6 3.6 0 0 1 1.6 0l1.8.4c1.6.3 2.9-.9 2.9-2.4C17.5 15.7 14.8 14 12 14Z',
  education: 'M12 4 2 9l10 5 8-4v6M6 11.5V17c0 1.4 2.7 3 6 3s6-1.6 6-3v-5.5',
  tithes: 'M12 5.5c1-1.6 2.7-2.5 4.3-2.5 2.6 0 4.7 2.1 4.7 4.8 0 3.7-4.3 6.8-9 10.9-4.7-4.1-9-7.2-9-10.9 0-2.7 2.1-4.8 4.7-4.8 1.6 0 3.3.9 4.3 2.5Z M9 21h6 M9 21v-2.5a3 3 0 0 1 3-3 3 3 0 0 1 3 3V21',
  other: 'M5 5h6l9 9-6 6-9-9V5Z M9 9a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z',

  // income
  salary: 'M4 8.5A1.5 1.5 0 0 1 5.5 7h13A1.5 1.5 0 0 1 20 8.5v9a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 4 17.5v-9Z M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7 M4 12h16',
  bonus: 'M4 9h16v3H4V9Z M5 12h14v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9Z M12 9v13 M12 9c-1.3 0-3.5-.6-3.5-2.8A2.2 2.2 0 0 1 10.7 4c1.7 0 2.7 2.2 3.3 5 0.6-2.8 1.6-5 3.3-5a2.2 2.2 0 0 1 2.2 2.2C19.5 8.4 17.3 9 16 9',
  allowance: 'M5 9a7 3.2 0 1 0 14 0 7 3.2 0 1 0-14 0Z M5 9v5.5a7 3.2 0 0 0 14 0V9',
  interest: 'M18.5 5.5 5.5 18.5 M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z M16 13.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5Z',
  investment: 'M4 17l5.5-5.5 3.5 3.5L21 7 M14.5 7H21v6.5',
  cashback: 'M4 12a8 8 0 0 1 13.3-6M20 12a8 8 0 0 1-13.3 6 M17 3v4h-4 M7 21v-4h4',
}

const path = computed(() => PATHS[props.icon] || PATHS.other)
</script>

<template>
  <span
    class="inline-flex shrink-0 items-center justify-center rounded-full"
    :style="{ width: `${size}px`, height: `${size}px`, background: color }"
  >
    <svg
      :width="Math.round(Number(size) * 0.52)"
      :height="Math.round(Number(size) * 0.52)"
      viewBox="0 0 24 24"
      fill="none"
    >
      <path :d="path" stroke="#fff" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  </span>
</template>
