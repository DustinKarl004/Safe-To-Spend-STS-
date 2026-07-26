<script setup>
defineProps({
  label: { type: String, default: 'Loading...' },
})
</script>

<template>
  <div class="loading-state">
    <span class="loading-spinner" aria-hidden="true"></span>
    <span class="loading-label">{{ label }}</span>
  </div>
</template>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  width: 100%;
  min-height: 50vh;
  padding: 2.5rem 1.5rem;
  text-align: center;
  color: var(--text-dim);
}

.loading-spinner {
  width: 28px;
  height: 28px;
  flex-shrink: 0;
  border-radius: 50%;
  border: 3px solid var(--border);
  border-top-color: var(--accent);
  animation: loading-spin 0.7s linear infinite;
}

.loading-label {
  font-size: 0.85rem;
  font-weight: 600;
  max-width: 20rem;
}

@media (min-width: 640px) {
  .loading-state {
    min-height: 60vh;
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
  }
}

@keyframes loading-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
