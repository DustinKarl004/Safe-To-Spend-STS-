<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { expenseCategory } from '@/lib/expenseCategories'
import CategoryIcon from '@/components/CategoryIcon.vue'
import GaugeRing from '@/components/GaugeRing.vue'
import DatePicker from '@/components/DatePicker.vue'

const dashboard = useDashboardStore()
const auth = useAuthStore()

onMounted(() => {
  dashboard.refresh()
  dashboard.fetchAllExpenses()
})

function money(n) {
  return Number(n).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-PH', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' })
}

function pad(n) {
  return String(n).padStart(2, '0')
}

const isOverBudget = computed(() => dashboard.safeToSpendToday < 0)
const dailyAllowance = computed(() => dashboard.safeToSpendToday + dashboard.spentToday)

const paydayLabel = computed(() => {
  if (!dashboard.nextPayday) return ''
  return new Date(dashboard.nextPayday).toLocaleDateString('en-PH', { month: 'short', day: 'numeric' })
})

// ---- browse recent transactions by day / month ----
const today = new Date()
const todayIso = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`

const txnView = ref('recent') // 'recent' | 'day' | 'month'
const selectedDay = ref(todayIso)
const selectedMonth = ref({ year: today.getFullYear(), month: today.getMonth() })

const isCurrentMonth = computed(
  () => selectedMonth.value.year === today.getFullYear() && selectedMonth.value.month === today.getMonth(),
)

const monthLabel = computed(() =>
  new Date(selectedMonth.value.year, selectedMonth.value.month, 1).toLocaleDateString('en-PH', {
    month: 'long',
    year: 'numeric',
  }),
)

function setTxnView(mode) {
  txnView.value = mode
}

function prevMonth() {
  const { year, month } = selectedMonth.value
  selectedMonth.value = month === 0 ? { year: year - 1, month: 11 } : { year, month: month - 1 }
}

function nextMonth() {
  if (isCurrentMonth.value) return
  const { year, month } = selectedMonth.value
  selectedMonth.value = month === 11 ? { year: year + 1, month: 0 } : { year, month: month + 1 }
}

const filteredExpenses = computed(() => {
  if (txnView.value === 'day') {
    return dashboard.allExpenses.filter((e) => e.created_at.slice(0, 10) === selectedDay.value)
  }
  if (txnView.value === 'month') {
    const { year, month } = selectedMonth.value
    return dashboard.allExpenses.filter((e) => {
      const d = new Date(e.created_at)
      return d.getFullYear() === year && d.getMonth() === month
    })
  }
  return dashboard.recentExpenses.slice(0, 5)
})

const filteredTotal = computed(() => filteredExpenses.value.reduce((sum, e) => sum + Number(e.amount), 0))

const emptyMessage = computed(() => {
  if (txnView.value === 'day') return "No expenses logged on this day."
  if (txnView.value === 'month') return 'No expenses logged this month.'
  return "Nothing logged yet — your first expense takes about 3 seconds."
})
</script>

<template>
  <div class="flex flex-col gap-6">
    <div>
      <p class="text-sm text-text-dim">
        Hey{{ auth.user?.email ? ',' : '' }} <span class="font-semibold text-text">{{ auth.user?.email }}</span>
      </p>
      <h1 class="font-display text-2xl font-extrabold">Today's safe-to-spend</h1>
    </div>

    <div class="grid grid-cols-1 gap-6 lg:grid-cols-[1.3fr_1fr]">
      <!-- Main gauge card -->
      <div class="flex flex-col gap-6">
        <div class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm sm:p-8">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wide text-text-dim">Safe to spend today</span>
            <span
              v-if="dashboard.nextPayday"
              class="rounded-full px-3 py-1 text-xs font-semibold"
              style="background: color-mix(in srgb, var(--accent) 14%, transparent); color: var(--accent)"
            >
              {{ dashboard.daysRemaining }}d to payday · {{ paydayLabel }}
            </span>
          </div>

          <div class="mt-5 flex flex-col items-center gap-5 sm:flex-row sm:items-center sm:gap-8">
            <GaugeRing :spent="dashboard.spentToday" :allowance="dailyAllowance" :size="188">
              <span class="text-[11px] font-semibold uppercase tracking-wide text-text-dim">Left today</span>
              <span
                class="mt-1 font-display text-2xl font-extrabold tabular-nums tracking-tight"
                :class="isOverBudget ? 'text-danger' : 'text-text'"
              >
                ₱{{ money(dashboard.safeToSpendToday) }}
              </span>
            </GaugeRing>

            <div class="flex w-full flex-col text-center sm:text-left">
              <p class="text-sm text-text-dim">
                ₱{{ money(dashboard.totalWalletBalance) }} left across wallets, after ₱{{ money(dashboard.totalReserved) }}
                reserved · ₱{{ money(dashboard.spentToday) }} spent today
              </p>

              <RouterLink
                :to="{ name: 'log' }"
                class="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-accent py-3.5 text-sm font-bold text-accent-text transition active:scale-[0.99]"
              >
                + Log an expense
              </RouterLink>
            </div>
          </div>
        </div>

        <!-- Recent transactions -->
        <div class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
          <div class="flex items-center justify-between">
            <h2 class="font-display text-base font-bold">Transactions</h2>
            <RouterLink :to="{ name: 'transactions' }" class="text-sm font-semibold text-accent">See all</RouterLink>
          </div>

          <div class="mt-3 flex items-center gap-2">
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-full transition"
              :class="txnView === 'recent' ? 'bg-accent text-accent-text' : 'bg-bg-sunken text-text-dim hover:text-text'"
              title="Recent"
              aria-label="Recent transactions"
              @click="setTxnView('recent')"
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.7" />
                <path d="M12 7v5l3.2 2" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </button>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-full transition"
              :class="txnView === 'day' ? 'bg-accent text-accent-text' : 'bg-bg-sunken text-text-dim hover:text-text'"
              title="By day"
              aria-label="Browse by day"
              @click="setTxnView('day')"
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                <rect x="3.5" y="5" width="17" height="16" rx="2.5" stroke="currentColor" stroke-width="1.7" />
                <path d="M3.5 9.5h17M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
                <circle cx="12" cy="15" r="1.8" fill="currentColor" />
              </svg>
            </button>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-full transition"
              :class="txnView === 'month' ? 'bg-accent text-accent-text' : 'bg-bg-sunken text-text-dim hover:text-text'"
              title="By month"
              aria-label="Browse by month"
              @click="setTxnView('month')"
            >
              <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                <rect x="3.5" y="5" width="17" height="16" rx="2.5" stroke="currentColor" stroke-width="1.7" />
                <path d="M3.5 9.5h17M8 3v4M16 3v4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
                <path d="M7.5 13.5h2M11 13.5h2M14.5 13.5h2M7.5 16.5h2M11 16.5h2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
            </button>
          </div>

          <DatePicker
            v-if="txnView === 'day'"
            v-model="selectedDay"
            :max="todayIso"
            placeholder="Pick a date"
            class="mt-3"
          />

          <div v-if="txnView === 'month'" class="mt-3 flex items-center justify-between rounded-xl border border-border bg-bg-sunken px-3 py-2">
            <button
              type="button"
              class="flex h-7 w-7 items-center justify-center rounded-full text-text-dim transition hover:bg-bg-raised hover:text-text"
              aria-label="Previous month"
              @click="prevMonth"
            >
              ‹
            </button>
            <span class="text-sm font-semibold">{{ monthLabel }}</span>
            <button
              type="button"
              class="flex h-7 w-7 items-center justify-center rounded-full text-text-dim transition hover:bg-bg-raised hover:text-text disabled:cursor-not-allowed disabled:opacity-30"
              aria-label="Next month"
              :disabled="isCurrentMonth"
              @click="nextMonth"
            >
              ›
            </button>
          </div>

          <p v-if="txnView !== 'recent' && filteredExpenses.length" class="mt-3 text-xs font-semibold text-text-dim">
            {{ filteredExpenses.length }} expense{{ filteredExpenses.length === 1 ? '' : 's' }} · ₱{{ money(filteredTotal) }} total
          </p>

          <p v-if="!filteredExpenses.length" class="mt-4 text-sm text-text-dim">
            {{ emptyMessage }}
          </p>
          <ul v-else class="mt-3 flex flex-col divide-y divide-border">
            <li v-for="expense in filteredExpenses" :key="expense.id" class="flex items-center gap-3 py-3">
              <CategoryIcon
                :icon="expenseCategory(expense.category).icon"
                :color="expenseCategory(expense.category).color"
                :size="34"
              />
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-semibold">{{ expense.note || expenseCategory(expense.category).label }}</p>
                <p class="text-xs text-text-dim">{{ expenseCategory(expense.category).label }} · {{ formatDate(expense.created_at) }}</p>
              </div>
              <span class="shrink-0 text-sm font-bold tabular-nums">−₱{{ money(expense.amount) }}</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Wallets & reserved -->
      <div class="flex flex-col gap-6">
        <RouterLink
          :to="{ name: 'balance' }"
          class="block rounded-2xl border border-border bg-bg-raised p-6 shadow-sm transition hover:border-accent/50"
        >
          <div class="flex items-center justify-between">
            <h2 class="font-display text-base font-bold">Balance</h2>
            <span class="text-sm font-semibold text-accent">Manage →</span>
          </div>
          <p class="mt-2 font-display text-3xl font-extrabold tabular-nums tracking-tight">
            ₱{{ money(dashboard.totalWalletBalance) }}
          </p>
          <p class="mt-1 text-sm text-text-dim">
            Across {{ dashboard.wallets.length }} wallet{{ dashboard.wallets.length === 1 ? '' : 's' }}
          </p>
        </RouterLink>

        <div v-if="dashboard.obligations.length" class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
          <h2 class="font-display text-base font-bold">Reserved</h2>
          <ul class="mt-3 flex flex-col gap-2.5">
            <li
              v-for="obligation in dashboard.obligations"
              :key="obligation.id"
              class="flex items-center justify-between rounded-xl px-3.5 py-2.5"
              style="background: color-mix(in srgb, var(--amber) 12%, transparent)"
            >
              <p class="text-sm font-semibold" style="color: var(--amber)">{{ obligation.label }}</p>
              <span class="text-sm font-bold tabular-nums" style="color: var(--amber)">₱{{ money(obligation.amount) }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
