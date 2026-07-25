<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, required: true }, // { year, month }
  max: { type: Object, default: null }, // { year, month }
})
const emit = defineEmits(['update:modelValue'])

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const open = ref(false)
const viewYear = ref(props.modelValue.year)

watch(open, (isOpen) => {
  if (isOpen) viewYear.value = props.modelValue.year
})

const label = computed(() => `${MONTHS[props.modelValue.month]} ${props.modelValue.year}`)

const isMaxYear = computed(() => props.max && viewYear.value >= props.max.year)

function prevYear() {
  viewYear.value -= 1
}
function nextYear() {
  if (props.max && viewYear.value >= props.max.year) return
  viewYear.value += 1
}

function isDisabled(monthIdx) {
  if (!props.max) return false
  return viewYear.value > props.max.year || (viewYear.value === props.max.year && monthIdx > props.max.month)
}

function isSelected(monthIdx) {
  return viewYear.value === props.modelValue.year && monthIdx === props.modelValue.month
}

function pick(monthIdx) {
  if (isDisabled(monthIdx)) return
  emit('update:modelValue', { year: viewYear.value, month: monthIdx })
  open.value = false
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      class="flex items-center gap-1 rounded-full px-2 py-1 text-xs font-semibold text-text-dim transition hover:bg-bg-sunken hover:text-text"
      @click="open = !open"
    >
      {{ label }}
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
        <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <div v-if="open" class="fixed inset-0 z-30" @click="open = false" />

    <Transition name="pop">
      <div
        v-if="open"
        class="absolute right-0 z-40 mt-2 w-64 rounded-2xl border border-border bg-bg-raised p-4 shadow-xl"
      >
        <div class="flex items-center justify-between">
          <button
            type="button"
            class="flex h-8 w-8 items-center justify-center rounded-full text-text-dim transition hover:bg-bg-sunken hover:text-text"
            aria-label="Previous year"
            @click="prevYear"
          >
            ‹
          </button>
          <span class="text-sm font-bold">{{ viewYear }}</span>
          <button
            type="button"
            class="flex h-8 w-8 items-center justify-center rounded-full text-text-dim transition hover:bg-bg-sunken hover:text-text disabled:cursor-not-allowed disabled:opacity-30"
            aria-label="Next year"
            :disabled="isMaxYear"
            @click="nextYear"
          >
            ›
          </button>
        </div>

        <div class="mt-3 grid grid-cols-3 gap-1.5">
          <button
            v-for="(m, idx) in MONTHS"
            :key="m"
            type="button"
            :disabled="isDisabled(idx)"
            class="rounded-lg py-2 text-xs font-semibold transition disabled:cursor-not-allowed disabled:text-text-dim/30"
            :class="isSelected(idx) ? 'bg-accent text-accent-text' : 'text-text hover:bg-bg-sunken'"
            @click="pick(idx)"
          >
            {{ m.slice(0, 3) }}
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (prefers-reduced-motion: reduce) {
  .pop-enter-active,
  .pop-leave-active {
    transition: none;
  }
}
</style>
