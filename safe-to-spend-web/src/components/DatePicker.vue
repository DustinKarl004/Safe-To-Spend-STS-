<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  min: { type: String, default: null },
  max: { type: String, default: null },
  placeholder: { type: String, default: 'Select a date' },
})
const emit = defineEmits(['update:modelValue'])

const WEEKDAYS = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa']
const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

const open = ref(false)

function parseIso(iso) {
  if (!iso) return null
  const [y, m, d] = iso.split('-').map(Number)
  return { year: y, month: m - 1, day: d }
}

const selected = computed(() => parseIso(props.modelValue))
const minParsed = computed(() => parseIso(props.min))

const today = new Date()
const view = ref({
  year: selected.value?.year ?? today.getFullYear(),
  month: selected.value?.month ?? today.getMonth(),
})

watch(open, (isOpen) => {
  if (isOpen) {
    view.value = {
      year: selected.value?.year ?? today.getFullYear(),
      month: selected.value?.month ?? today.getMonth(),
    }
  }
})

function pad(n) {
  return String(n).padStart(2, '0')
}

function isoOf(year, month, day) {
  return `${year}-${pad(month + 1)}-${pad(day)}`
}

const displayLabel = computed(() => {
  if (!selected.value) return props.placeholder
  const { year, month, day } = selected.value
  return `${MONTHS[month].slice(0, 3)} ${day}, ${year}`
})

const monthLabel = computed(() => `${MONTHS[view.value.month]} ${view.value.year}`)

const cells = computed(() => {
  const { year, month } = view.value
  const firstDow = new Date(year, month, 1).getDay()
  const daysInMonth = new Date(year, month + 1, 0).getDate()
  const result = []
  for (let i = 0; i < firstDow; i++) result.push(null)
  for (let day = 1; day <= daysInMonth; day++) result.push(day)
  return result
})

function isDisabled(day) {
  if (!day) return false
  const iso = isoOf(view.value.year, view.value.month, day)
  if (minParsed.value && iso <= props.min) return true
  if (props.max && iso > props.max) return true
  return false
}

function isSelected(day) {
  if (!day || !selected.value) return false
  return (
    view.value.year === selected.value.year &&
    view.value.month === selected.value.month &&
    day === selected.value.day
  )
}

function isToday(day) {
  if (!day) return false
  return (
    view.value.year === today.getFullYear() &&
    view.value.month === today.getMonth() &&
    day === today.getDate()
  )
}

function pick(day) {
  if (!day || isDisabled(day)) return
  emit('update:modelValue', isoOf(view.value.year, view.value.month, day))
  open.value = false
}

function prevMonth() {
  if (view.value.month === 0) {
    view.value = { year: view.value.year - 1, month: 11 }
  } else {
    view.value = { ...view.value, month: view.value.month - 1 }
  }
}
function nextMonth() {
  if (view.value.month === 11) {
    view.value = { year: view.value.year + 1, month: 0 }
  } else {
    view.value = { ...view.value, month: view.value.month + 1 }
  }
}
</script>

<template>
  <div class="relative">
    <button
      type="button"
      class="relative z-40 flex w-full items-center justify-between rounded-xl border border-border bg-bg-sunken px-4 py-3.5 text-left text-base font-semibold outline-none transition focus:border-accent"
      :class="selected ? 'text-text' : 'text-text-dim'"
      @click="open = !open"
    >
      {{ displayLabel }}
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" class="shrink-0 text-text-dim">
        <rect x="3.5" y="5" width="17" height="16" rx="2.5" stroke="currentColor" stroke-width="1.7" />
        <path d="M3.5 9.5h17M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
      </svg>
    </button>

    <div v-if="open" class="fixed inset-0 z-30" @click="open = false" />

    <Transition name="pop">
      <div
        v-if="open"
        class="absolute inset-x-0 z-40 mt-2 rounded-2xl border border-border bg-bg-raised p-5 shadow-xl"
      >
        <div class="flex items-center justify-between">
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-full text-text-dim transition hover:bg-bg-sunken hover:text-text"
            aria-label="Previous month"
            @click="prevMonth"
          >
            ‹
          </button>
          <span class="text-base font-bold">{{ monthLabel }}</span>
          <button
            type="button"
            class="flex h-9 w-9 items-center justify-center rounded-full text-text-dim transition hover:bg-bg-sunken hover:text-text"
            aria-label="Next month"
            @click="nextMonth"
          >
            ›
          </button>
        </div>

        <div class="mt-3 grid grid-cols-7 gap-y-1.5 text-center">
          <span v-for="d in WEEKDAYS" :key="d" class="py-1 text-xs font-semibold text-text-dim sm:text-sm">{{ d }}</span>

          <template v-for="(day, idx) in cells" :key="idx">
            <button
              v-if="day"
              type="button"
              :disabled="isDisabled(day)"
              class="mx-auto flex h-10 w-10 items-center justify-center rounded-full text-sm font-semibold transition disabled:cursor-not-allowed disabled:text-text-dim/30 sm:text-base"
              :class="[
                isSelected(day)
                  ? 'bg-accent text-accent-text'
                  : isToday(day)
                    ? 'text-accent'
                    : 'text-text hover:bg-bg-sunken',
              ]"
              @click="pick(day)"
            >
              {{ day }}
            </button>
            <span v-else />
          </template>
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
