<script setup>
import { ref, watch } from 'vue'
import ProviderIcon from './ProviderIcon.vue'
import { providerIcon } from '@/lib/walletProviders'

const props = defineProps({
  open: { type: Boolean, default: false },
  wallet: { type: Object, default: null },
  saving: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save', 'remove'])

const balanceInput = ref('')

watch(
  () => props.wallet,
  (wallet) => {
    balanceInput.value = wallet ? String(wallet.balance) : ''
  },
  { immediate: true },
)

function handleSave() {
  if (!props.wallet || balanceInput.value === '' || props.saving) return
  emit('save', props.wallet.id, Number(balanceInput.value))
}

function handleRemove() {
  if (!props.wallet) return
  emit('remove', props.wallet.id)
}
</script>

<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-30 bg-black/40" @click="emit('close')" />
  </Transition>

  <Transition name="pop">
    <div
      v-if="open && wallet"
      class="fixed inset-x-4 top-1/2 z-40 mx-auto max-w-sm -translate-y-1/2 rounded-2xl border border-border bg-bg-raised p-6 shadow-2xl sm:inset-x-0"
      role="dialog"
      aria-label="Edit wallet"
    >
      <div class="flex items-center gap-3">
        <ProviderIcon v-bind="providerIcon(wallet.label)" :size="44" />
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-bold">{{ wallet.label }}</p>
          <p class="text-xs text-text-dim">Current balance: ₱{{ Number(wallet.balance).toLocaleString('en-PH', { minimumFractionDigits: 2 }) }}</p>
        </div>
        <button
          type="button"
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-text-dim hover:bg-bg-sunken hover:text-text"
          aria-label="Close"
          @click="emit('close')"
        >
          ✕
        </button>
      </div>

      <label class="mt-5 flex flex-col gap-1.5 text-sm font-semibold">
        New balance
        <span class="relative flex items-center">
          <span class="pointer-events-none absolute left-3.5 text-text-dim">₱</span>
          <input
            v-model="balanceInput"
            type="number"
            min="0"
            step="0.01"
            class="w-full rounded-xl border border-border bg-bg-sunken py-2.5 pl-8 pr-3.5 text-sm font-semibold outline-none focus:border-accent"
          />
        </span>
      </label>
      <p class="mt-1.5 text-xs text-text-dim">Got paid? Just type your new total here.</p>

      <div class="mt-5 flex gap-3">
        <button
          type="button"
          class="rounded-xl border border-border px-4 py-3 text-sm font-bold text-danger disabled:opacity-40"
          :disabled="saving"
          @click="handleRemove"
        >
          Remove
        </button>
        <button
          type="button"
          class="flex-1 rounded-xl bg-accent py-3 text-sm font-bold text-accent-text disabled:opacity-60"
          :disabled="saving || balanceInput === ''"
          @click="handleSave"
        >
          {{ saving ? 'Saving…' : 'Save' }}
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: translateY(-45%);
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
  .pop-enter-active,
  .pop-leave-active,
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>
