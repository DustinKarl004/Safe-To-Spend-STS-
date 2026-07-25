<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(false)

function apply(theme) {
  document.documentElement.setAttribute('data-theme', theme)
  localStorage.setItem('sts_theme', theme)
  isDark.value = theme === 'dark'
}

function toggle() {
  apply(isDark.value ? 'light' : 'dark')
}

onMounted(() => {
  const saved = localStorage.getItem('sts_theme')
  if (saved) {
    apply(saved)
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
})
</script>

<template>
  <button
    type="button"
    class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-border bg-bg-raised text-text-dim transition hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
    :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    @click="toggle"
  >
    <svg v-if="isDark" width="16" height="16" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="4.5" fill="currentColor" />
      <g stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
        <path d="M12 2v2.4M12 19.6V22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M2 12h2.4M19.6 12H22M4.9 19.1l1.7-1.7M17.4 6.6l1.7-1.7" />
      </g>
    </svg>
    <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
      <path
        d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.4 5.4 0 0 1-7.54-7.54c-.44-.06-.9-.1-1.36-.1Z"
        fill="currentColor"
      />
    </svg>
  </button>
</template>
