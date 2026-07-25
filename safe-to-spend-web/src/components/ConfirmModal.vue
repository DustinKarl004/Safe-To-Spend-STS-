<script setup>
const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Are you sure?' },
  message: { type: String, default: 'This cannot be undone.' },
  confirmLabel: { type: String, default: 'Delete' },
  cancelLabel: { type: String, default: 'Cancel' },
  busy: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" @click.self="emit('cancel')">
      <div class="w-full max-w-sm rounded-2xl bg-bg-raised p-6 shadow-2xl" role="alertdialog" aria-modal="true">
        <h2 class="font-display text-base font-bold">{{ title }}</h2>
        <p class="mt-2 text-sm text-text-dim">{{ message }}</p>
        <div class="mt-6 flex justify-end gap-3">
          <button
            type="button"
            class="rounded-xl px-4 py-2.5 text-sm font-semibold text-text-dim hover:bg-bg-sunken"
            @click="emit('cancel')"
          >
            {{ cancelLabel }}
          </button>
          <button
            type="button"
            class="rounded-xl bg-danger px-4 py-2.5 text-sm font-bold text-white disabled:opacity-50"
            :disabled="busy"
            @click="emit('confirm')"
          >
            {{ busy ? 'Please wait…' : confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>
