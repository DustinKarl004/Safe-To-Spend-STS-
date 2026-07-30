<script setup>
import { computed, ref, watch } from 'vue'
import { INCOME_CATEGORIES } from '@/lib/incomeCategories'
import { providerIcon } from '@/lib/walletProviders'
import ProviderIcon from './ProviderIcon.vue'
import CategoryIcon from './CategoryIcon.vue'
import DatePicker from './DatePicker.vue'

const RECURRENCE_OPTIONS = [
  { value: 'one_time', label: 'One-time' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'biweekly', label: 'Biweekly' },
  { value: 'semi_monthly', label: 'Semi-monthly' },
  { value: 'monthly', label: 'Monthly' },
]

// Digital banks (Maya, MariBank, etc.) accrue interest daily off the end-of-day
// balance: daily interest = balance x (annual rate / 365). We approximate the
// number of days covered by each payout using calendar-day period lengths.
const DAYS_PER_PERIOD = {
  one_time: 1,
  daily: 1,
  weekly: 7,
  biweekly: 14,
  semi_monthly: 15,
  monthly: 30,
}

const props = defineProps({
  open: { type: Boolean, default: false },
  wallets: { type: Array, default: () => [] },
  todayIso: { type: String, required: true },
  source: { type: Object, default: null },
  saving: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save', 'remove'])

const isEditing = computed(() => Boolean(props.source))

const label = ref('')
const date = ref('')
const category = ref('salary')
const recurrence = ref('one_time')
const walletId = ref(null)
const amountStr = ref('')
const note = ref('')

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      label.value = props.source?.label || ''
      date.value = props.source?.next_date || props.todayIso
      category.value = props.source?.category || 'salary'
      recurrence.value = props.source?.recurrence || 'one_time'
      walletId.value = props.source?.wallet_id ?? props.wallets[0]?.id ?? null
      amountStr.value = props.source?.amount ? String(props.source.amount) : ''
      note.value = props.source?.note || ''
    }
  },
)

const canSave = computed(() => Boolean(date.value))

// BIR final withholding tax on Philippine bank/e-wallet interest income.
const WITHHOLDING_TAX_RATE = 0.2

function maybeAutofillInterest() {
  if (category.value !== 'interest') return
  const wallet = props.wallets.find((w) => w.id === walletId.value)
  if (!wallet?.interest_rate) return
  const days = DAYS_PER_PERIOD[recurrence.value] ?? 1
  const dailyRate = Number(wallet.interest_rate) / 100 / 365
  const grossInterest = Number(wallet.balance_php ?? wallet.balance) * dailyRate * days
  const netInterest = grossInterest * (1 - WITHHOLDING_TAX_RATE)
  amountStr.value = netInterest.toFixed(2)
}

function handleSave() {
  if (!canSave.value || props.saving) return
  emit('save', {
    label: label.value.trim() || null,
    next_date: date.value,
    category: category.value,
    recurrence: recurrence.value,
    wallet_id: walletId.value,
    amount: amountStr.value === '' ? null : Number(amountStr.value),
    note: note.value.trim() || null,
  })
}

function handleRemove() {
  emit('remove')
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
      aria-label="Edit payday source"
    >
      <div class="flex items-center justify-between border-b border-border px-5 py-4">
        <h2 class="font-display text-base font-bold">{{ isEditing ? 'Edit payday source' : 'Add payday source' }}</h2>
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
        <label class="flex flex-col gap-1.5 text-sm font-semibold">
          Label
          <input
            v-model="label"
            type="text"
            maxlength="50"
            placeholder="e.g. Allowance, TikTok affiliate"
            class="rounded-xl border border-border bg-bg-sunken px-3.5 py-2.5 text-sm font-normal outline-none focus:border-accent"
          />
        </label>

        <h3 class="mb-2.5 mt-5 text-xs font-semibold uppercase tracking-wide text-text-dim">Category</h3>
        <div class="grid grid-cols-4 gap-2">
          <button
            v-for="cat in INCOME_CATEGORIES"
            :key="cat.value"
            type="button"
            class="flex flex-col items-center gap-1.5 rounded-xl border p-2 text-center transition"
            :class="category === cat.value ? 'border-accent bg-accent/10' : 'border-border bg-bg-sunken hover:border-accent/50'"
            @click="category = cat.value; maybeAutofillInterest()"
          >
            <CategoryIcon :icon="cat.icon" :color="cat.color" :size="34" />
            <span class="text-[11px] font-semibold leading-tight">{{ cat.label }}</span>
          </button>
        </div>

        <h3 class="mb-2.5 mt-5 text-xs font-semibold uppercase tracking-wide text-text-dim">Repeats</h3>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in RECURRENCE_OPTIONS"
            :key="opt.value"
            type="button"
            class="rounded-full border px-3.5 py-2 text-xs font-semibold transition"
            :class="recurrence === opt.value ? 'border-accent bg-accent/10 text-accent' : 'border-border bg-bg-sunken hover:border-accent/50'"
            @click="recurrence = opt.value; maybeAutofillInterest()"
          >
            {{ opt.label }}
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
            @click="walletId = wallet.id; maybeAutofillInterest()"
          >
            <ProviderIcon v-bind="providerIcon(wallet.label)" :size="34" />
            <span class="min-w-0 flex-1 truncate text-sm font-semibold">{{ wallet.label }}</span>
            <span v-if="walletId === wallet.id" class="shrink-0 text-accent">✓</span>
          </button>
        </div>

        <label class="mt-5 flex flex-col gap-1.5 text-sm font-semibold">
          Expected amount (optional)
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
          <DatePicker v-model="date" :min="todayIso" placeholder="Select the payday" />
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
          v-if="isEditing"
          type="button"
          :disabled="saving"
          class="rounded-xl border border-border px-4 py-3 text-sm font-bold text-danger disabled:opacity-40"
          @click="handleRemove"
        >
          Delete
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
