<script setup>
import { computed, ref, watch } from 'vue'
import { INCOME_CATEGORIES } from '@/lib/incomeCategories'
import { providerIcon } from '@/lib/walletProviders'
import ProviderIcon from './ProviderIcon.vue'
import CategoryIcon from './CategoryIcon.vue'
import DatePicker from './DatePicker.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  wallets: { type: Array, default: () => [] },
  todayIso: { type: String, required: true },
  initialDate: { type: String, default: '' },
  initialCategory: { type: String, default: 'salary' },
  initialWalletId: { type: Number, default: null },
  initialAmount: { type: Number, default: null },
  initialNote: { type: String, default: '' },
  hasExpectedInfo: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save', 'remove'])

const date = ref('')
const category = ref('salary')
const walletId = ref(null)
const amountStr = ref('')
const note = ref('')
const saving = ref(false)
const removing = ref(false)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      date.value = props.initialDate || props.todayIso
      category.value = props.initialCategory
      walletId.value = props.initialWalletId ?? props.wallets[0]?.id ?? null
      amountStr.value = props.initialAmount ? String(props.initialAmount) : ''
      note.value = props.initialNote || ''
    }
  },
)

const canSave = computed(() => Boolean(date.value) && Number(amountStr.value) > 0 && walletId.value)

async function handleSave() {
  if (!canSave.value) return
  saving.value = true
  try {
    await emit('save', {
      next_payday: date.value,
      category: category.value,
      wallet_id: walletId.value,
      amount: amountStr.value === '' ? null : Number(amountStr.value),
      note: note.value.trim() || null,
    })
  } finally {
    saving.value = false
  }
}

async function handleRemove() {
  removing.value = true
  try {
    await emit('remove')
  } finally {
    removing.value = false
  }
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
      aria-label="Edit payday"
    >
      <div class="flex items-center justify-between border-b border-border px-5 py-4">
        <h2 class="font-display text-base font-bold">Payday</h2>
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
        <h3 class="mb-2.5 text-xs font-semibold uppercase tracking-wide text-text-dim">Category</h3>
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="cat in INCOME_CATEGORIES"
            :key="cat.value"
            type="button"
            class="flex flex-col items-center gap-1.5 rounded-xl border p-2 text-center transition"
            :class="category === cat.value ? 'border-accent bg-accent/10' : 'border-border bg-bg-sunken hover:border-accent/50'"
            @click="category = cat.value"
          >
            <CategoryIcon :icon="cat.icon" :color="cat.color" :size="34" />
            <span class="text-[11px] font-semibold leading-tight">{{ cat.label }}</span>
          </button>
        </div>

        <h3 class="mb-2.5 mt-5 text-xs font-semibold uppercase tracking-wide text-text-dim">Wallet</h3>
        <div class="flex flex-col gap-2">
          <button
            v-for="wallet in wallets"
            :key="wallet.id"
            type="button"
            class="flex items-center gap-3 rounded-xl border p-2.5 text-left transition"
            :class="walletId === wallet.id ? 'border-accent bg-accent/10' : 'border-border bg-bg-sunken hover:border-accent/50'"
            @click="walletId = wallet.id"
          >
            <ProviderIcon v-bind="providerIcon(wallet.label)" :size="34" />
            <span class="min-w-0 flex-1 truncate text-sm font-semibold">{{ wallet.label }}</span>
            <span v-if="walletId === wallet.id" class="shrink-0 text-accent">✓</span>
          </button>
        </div>

        <label class="mt-5 flex flex-col gap-1.5 text-sm font-semibold">
          Amount
          <span class="relative flex items-center">
            <span class="pointer-events-none absolute left-3.5 text-text-dim">₱</span>
            <input
              v-model="amountStr"
              type="number"
              min="0.01"
              step="0.01"
              placeholder="0.00"
              class="w-full rounded-xl border border-border bg-bg-sunken py-2.5 pl-8 pr-3.5 text-sm font-semibold outline-none focus:border-accent"
            />
          </span>
        </label>

        <label class="mt-4 flex flex-col gap-1.5 text-sm font-semibold">
          Date
          <DatePicker v-model="date" :min="todayIso" placeholder="Select your payday" />
        </label>

        <label class="mt-4 flex flex-col gap-1.5 text-sm font-semibold">
          Note (optional)
          <input
            v-model="note"
            type="text"
            maxlength="140"
            placeholder="e.g. July payroll"
            class="rounded-xl border border-border bg-bg-sunken px-3.5 py-2.5 text-sm font-normal outline-none focus:border-accent"
          />
        </label>
      </div>

      <div class="flex gap-3 border-t border-border px-5 py-4">
        <button
          v-if="hasExpectedInfo"
          type="button"
          :disabled="removing"
          class="rounded-xl border border-border px-4 py-3 text-sm font-bold text-danger disabled:opacity-40"
          @click="handleRemove"
        >
          Remove
        </button>
        <button
          type="button"
          :disabled="!canSave || saving"
          class="flex-1 rounded-xl bg-accent py-3 text-sm font-bold text-accent-text disabled:opacity-60"
          @click="handleSave"
        >
          {{ saving ? 'Saving…' : 'Save' }}
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
