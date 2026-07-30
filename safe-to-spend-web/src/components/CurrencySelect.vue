<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { CURRENCIES } from '@/lib/currencies'

const props = defineProps({
  modelValue: { type: String, required: true },
  compact: { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const triggerRef = ref(null)
const panelStyle = ref({})

function toggle() {
  if (open.value) {
    open.value = false
    return
  }
  const rect = triggerRef.value.getBoundingClientRect()
  const viewportH = window.innerHeight
  const panelHeight = 240
  const openUp = rect.bottom + panelHeight > viewportH && rect.top > panelHeight
  panelStyle.value = openUp
    ? { left: `${rect.left}px`, bottom: `${viewportH - rect.top + 4}px`, width: `${Math.max(rect.width, 180)}px` }
    : { left: `${rect.left}px`, top: `${rect.bottom + 4}px`, width: `${Math.max(rect.width, 180)}px` }
  open.value = true
}

function select(code) {
  emit('update:modelValue', code)
  open.value = false
}

function onClickOutside(e) {
  if (triggerRef.value?.contains(e.target)) return
  if (e.target.closest?.('.currency-select-panel')) return
  open.value = false
}

onMounted(() => document.addEventListener('mousedown', onClickOutside))
onUnmounted(() => document.removeEventListener('mousedown', onClickOutside))
</script>

<template>
  <div>
    <button
      ref="triggerRef"
      type="button"
      class="flex w-full items-center justify-between gap-1.5 rounded-xl border bg-bg-sunken font-semibold outline-none transition"
      :class="[compact ? 'px-2 py-1.5 text-xs' : 'px-3 py-2.5 text-sm', open ? 'border-accent' : 'border-border']"
      @click="toggle"
    >
      <span>{{ modelValue }}</span>
      <svg
        width="11"
        height="11"
        viewBox="0 0 24 24"
        fill="none"
        class="shrink-0 text-text-dim transition-transform"
        :class="open ? 'rotate-180' : ''"
      >
        <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </button>

    <Teleport to="body">
      <Transition name="fade">
        <ul
          v-if="open"
          class="currency-select-panel fixed z-50 max-h-60 overflow-y-auto rounded-xl border border-border bg-bg-raised p-1 shadow-2xl"
          :style="panelStyle"
        >
          <li v-for="c in CURRENCIES" :key="c.code">
            <button
              type="button"
              class="flex w-full items-center justify-between gap-3 rounded-lg px-2.5 py-2 text-left text-sm transition"
              :class="c.code === modelValue ? 'bg-accent/10 font-semibold text-accent' : 'text-text hover:bg-bg-sunken'"
              @click="select(c.code)"
            >
              <span class="font-semibold">{{ c.code }}</span>
              <span class="truncate text-xs text-text-dim">{{ c.name }}</span>
            </button>
          </li>
        </ul>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
