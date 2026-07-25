<script setup>
import { OBLIGATION_GROUPS } from '@/lib/obligationCategories'
import ProviderIcon from './ProviderIcon.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  selectedNames: { type: Array, default: () => [] },
})
const emit = defineEmits(['close', 'toggle', 'clear-group'])

function isSelected(name) {
  return props.selectedNames.includes(name)
}

function hasSelection(group) {
  return group.items.some((item) => isSelected(item.name))
}
</script>

<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-30 bg-black/40" @click="emit('close')" />
  </Transition>

  <Transition name="slide">
    <aside
      v-if="open"
      class="fixed inset-y-0 right-0 z-40 flex w-full max-w-sm flex-col bg-bg-raised shadow-2xl sm:max-w-md"
      role="dialog"
      aria-label="Choose a reserved expense"
    >
      <div class="flex items-center justify-between border-b border-border px-5 py-4">
        <h2 class="font-display text-base font-bold">Add a reserved expense</h2>
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full text-text-dim hover:bg-bg-sunken hover:text-text"
          aria-label="Close"
          @click="emit('close')"
        >
          ✕
        </button>
      </div>

      <div class="flex-1 overflow-y-auto px-5 py-4">
        <div v-for="group in OBLIGATION_GROUPS" :key="group.kind" class="mb-6 last:mb-0">
          <div class="mb-2.5 flex items-center justify-between">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-text-dim">{{ group.label }}</h3>
            <button
              v-if="hasSelection(group)"
              type="button"
              class="flex h-6 w-6 items-center justify-center rounded-full text-text-dim transition hover:bg-danger/10 hover:text-danger"
              :aria-label="`Clear ${group.label}`"
              :title="`Clear ${group.label}`"
              @click="emit('clear-group', group.kind)"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2.5">
            <button
              v-for="item in group.items"
              :key="item.name"
              type="button"
              class="relative flex flex-col items-center gap-2 rounded-xl border p-3.5 text-center text-sm font-semibold transition"
              :class="
                isSelected(item.name)
                  ? 'border-accent bg-accent/10 text-text'
                  : 'border-border bg-bg-sunken text-text hover:border-accent/50'
              "
              @click="emit('toggle', { kind: group.kind, name: item.name })"
            >
              <span v-if="isSelected(item.name)" class="absolute right-2 top-2 text-accent">✓</span>
              <ProviderIcon :name="item.name" :color="item.color" :initials="item.icon" :size="64" />
              <span class="leading-tight">{{ item.name }}</span>
            </button>
          </div>
        </div>
      </div>

      <div class="border-t border-border px-5 py-4">
        <button
          type="button"
          class="w-full rounded-xl bg-accent py-3 text-sm font-bold text-accent-text"
          @click="emit('close')"
        >
          Done
        </button>
      </div>
    </aside>
  </Transition>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .slide-enter-active,
  .slide-leave-active,
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>
