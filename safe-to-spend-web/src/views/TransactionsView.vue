<script setup>
import { computed, onMounted, ref } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { expenseCategory } from '@/lib/expenseCategories'
import { incomeCategory } from '@/lib/incomeCategories'
import { providerIcon } from '@/lib/walletProviders'
import CategoryIcon from '@/components/CategoryIcon.vue'
import ProviderIcon from '@/components/ProviderIcon.vue'
import DonutChart from '@/components/DonutChart.vue'
import MonthPicker from '@/components/MonthPicker.vue'
import ExpenseLogSheet from '@/components/ExpenseLogSheet.vue'
import IncomeLogSheet from '@/components/IncomeLogSheet.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import LoadingState from '@/components/LoadingState.vue'

const dashboard = useDashboardStore()

onMounted(() => {
  console.log('[TransactionsView] mounted, hasLoaded =', dashboard.hasLoaded)
  dashboard.refresh()
  dashboard.fetchAllExpenses()
  dashboard.fetchIncomes()
})

function money(n) {
  return Number(n).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString('en-PH', { hour: 'numeric', minute: '2-digit' })
}

// ---- month/year filter ----
const today = new Date()
const viewMonth = ref({ year: today.getFullYear(), month: today.getMonth() })
const currentMonthMax = { year: today.getFullYear(), month: today.getMonth() }

const monthLabel = computed(() =>
  new Date(viewMonth.value.year, viewMonth.value.month, 1).toLocaleDateString('en-PH', { month: 'long', year: 'numeric' }),
)

function inViewMonth(iso) {
  const d = new Date(iso)
  return d.getFullYear() === viewMonth.value.year && d.getMonth() === viewMonth.value.month
}

const entries = computed(() => {
  const expenseEntries = dashboard.allExpenses
    .filter((e) => inViewMonth(e.created_at))
    .map((e) => ({ type: 'expense', ...e }))
  const incomeEntries = dashboard.incomes
    .filter((i) => inViewMonth(i.created_at))
    .map((i) => ({ type: 'income', ...i }))
  return [...expenseEntries, ...incomeEntries].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at),
  )
})

const groupedEntries = computed(() => {
  const byDay = new Map()
  for (const entry of entries.value) {
    const day = new Date(entry.created_at).toLocaleDateString('en-PH', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    })
    if (!byDay.has(day)) byDay.set(day, [])
    byDay.get(day).push(entry)
  }
  return Array.from(byDay.entries())
})

const totalIncome = computed(() =>
  entries.value.filter((e) => e.type === 'income').reduce((sum, e) => sum + Number(e.amount), 0),
)
const totalExpense = computed(() =>
  entries.value.filter((e) => e.type === 'expense').reduce((sum, e) => sum + Number(e.amount), 0),
)

function categoryInfo(entry) {
  return entry.type === 'income' ? incomeCategory(entry.category) : expenseCategory(entry.category)
}

const categoryBreakdown = computed(() => {
  const totals = new Map()
  for (const entry of entries.value) {
    if (entry.type !== 'expense') continue
    totals.set(entry.category, (totals.get(entry.category) || 0) + Number(entry.amount))
  }
  return Array.from(totals.entries())
    .map(([value, amount]) => ({
      label: expenseCategory(value).label,
      color: expenseCategory(value).color,
      icon: expenseCategory(value).icon,
      value: amount,
    }))
    .sort((a, b) => b.value - a.value)
})

function subtitle(entry) {
  const parts = []
  if (entry.note) parts.push(categoryInfo(entry).label)
  if (entry.wallet_label) parts.push(entry.wallet_label)
  parts.push(formatTime(entry.created_at))
  return parts.join(' · ')
}

// ---- edit ----
const expenseSheetOpen = ref(false)
const editingExpense = ref(null)
const incomeSheetOpen = ref(false)
const editingIncome = ref(null)

function startEdit(entry) {
  if (entry.type === 'expense') {
    editingExpense.value = entry
    expenseSheetOpen.value = true
  } else {
    editingIncome.value = entry
    incomeSheetOpen.value = true
  }
}

function openAddExpense() {
  editingExpense.value = null
  expenseSheetOpen.value = true
}

function openAddIncome() {
  editingIncome.value = null
  incomeSheetOpen.value = true
}

function closeExpenseSheet() {
  expenseSheetOpen.value = false
  editingExpense.value = null
}

function closeIncomeSheet() {
  incomeSheetOpen.value = false
  editingIncome.value = null
}

function handleExpenseSubmit(payload) {
  const editing = editingExpense.value
  closeExpenseSheet()
  if (editing) {
    dashboard.updateExpense(editing.id, payload).catch(() => {
      window.alert('Something went wrong saving that expense. Please try again.')
    })
  } else {
    dashboard.logExpense(payload).catch(() => {
      window.alert('Something went wrong logging that expense. Please try again.')
    })
  }
}

function handleIncomeSubmit(payload) {
  const editing = editingIncome.value
  closeIncomeSheet()
  if (editing) {
    dashboard.updateIncome(editing.id, payload).catch(() => {
      window.alert('Something went wrong saving that income. Please try again.')
    })
  } else {
    dashboard.logIncome(payload).catch(() => {
      window.alert('Something went wrong logging that income. Please try again.')
    })
  }
}

// ---- delete (with confirmation) ----
const deleteTarget = ref(null)
const deleting = ref(false)

function askDelete(entry) {
  deleteTarget.value = entry
}

function cancelDelete() {
  deleteTarget.value = null
}

async function confirmDelete() {
  const target = deleteTarget.value
  if (!target) return
  deleting.value = true
  try {
    if (target.type === 'expense') {
      await dashboard.deleteExpense(target.id)
    } else {
      await dashboard.deleteIncome(target.id)
    }
    deleteTarget.value = null
  } catch {
    window.alert('Something went wrong removing that entry. Please try again.')
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <LoadingState v-if="!dashboard.hasLoaded" label="Loading your transactions..." />
  <div v-else class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="font-display text-2xl font-extrabold">Transactions</h1>
        <p class="mt-1 text-sm text-text-dim">Every income and expense, month by month.</p>
      </div>
      <MonthPicker v-model="viewMonth" :max="currentMonthMax" />
    </div>

    <div class="flex gap-3">
      <button
        type="button"
        class="flex flex-1 items-center justify-center gap-2 rounded-xl border border-dashed border-border py-2.5 text-sm font-semibold text-danger"
        @click="openAddExpense"
      >
        + Add expense
      </button>
      <button
        type="button"
        class="flex flex-1 items-center justify-center gap-2 rounded-xl border border-dashed border-border py-2.5 text-sm font-semibold text-safe"
        @click="openAddIncome"
      >
        + Add income
      </button>
    </div>

    <div class="grid grid-cols-2 gap-4">
      <div class="rounded-2xl border border-border bg-bg-raised p-5 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wide text-text-dim">Income</span>
        <p class="mt-1 font-display text-2xl font-extrabold tabular-nums tracking-tight text-safe">
          +₱{{ money(totalIncome) }}
        </p>
      </div>
      <div class="rounded-2xl border border-border bg-bg-raised p-5 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wide text-text-dim">Expenses</span>
        <p class="mt-1 font-display text-2xl font-extrabold tabular-nums tracking-tight text-danger">
          −₱{{ money(totalExpense) }}
        </p>
      </div>
    </div>

    <div v-if="categoryBreakdown.length" class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
      <h2 class="font-display text-base font-bold">Where it went</h2>
      <div class="mt-4 flex flex-col items-center gap-6 sm:flex-row sm:items-center sm:gap-8">
        <DonutChart :segments="categoryBreakdown" :size="168">
          <span class="text-[11px] font-semibold uppercase tracking-wide text-text-dim">Total</span>
          <span class="mt-1 font-display text-xl font-extrabold tabular-nums tracking-tight">₱{{ money(totalExpense) }}</span>
        </DonutChart>

        <ul class="flex w-full flex-col gap-2.5">
          <li v-for="cat in categoryBreakdown" :key="cat.label" class="flex items-center gap-3">
            <CategoryIcon :icon="cat.icon" :color="cat.color" :size="30" />
            <span class="min-w-0 flex-1 truncate text-sm font-semibold">{{ cat.label }}</span>
            <span class="shrink-0 text-xs font-semibold text-text-dim">{{ Math.round((cat.value / totalExpense) * 100) }}%</span>
            <span class="shrink-0 text-sm font-bold tabular-nums">₱{{ money(cat.value) }}</span>
          </li>
        </ul>
      </div>
    </div>

    <p v-if="!entries.length" class="rounded-2xl border border-border bg-bg-raised p-6 text-sm text-text-dim">
      No income or expenses logged in {{ monthLabel }}.
    </p>

    <div v-for="[day, dayEntries] in groupedEntries" :key="day" class="flex flex-col gap-2.5">
      <h2 class="text-xs font-semibold uppercase tracking-wide text-text-dim">{{ day }}</h2>
      <div class="overflow-hidden rounded-2xl border border-border bg-bg-raised shadow-sm">
        <div
          v-for="(entry, idx) in dayEntries"
          :key="`${entry.type}-${entry.id}`"
          :class="idx > 0 ? 'border-t border-border' : ''"
          class="flex flex-col gap-3 p-4 sm:flex-row sm:items-center"
        >
          <div class="flex min-w-0 flex-1 items-center gap-3">
            <CategoryIcon :icon="categoryInfo(entry).icon" :color="categoryInfo(entry).color" :size="36" />
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold">{{ entry.note || categoryInfo(entry).label }}</p>
              <p class="flex items-center gap-1 truncate text-xs text-text-dim">
                <ProviderIcon v-if="entry.wallet_label" v-bind="providerIcon(entry.wallet_label)" :size="14" />
                <span class="truncate">{{ subtitle(entry) }}</span>
              </p>
            </div>
          </div>

          <div class="flex items-center justify-between gap-3 sm:shrink-0 sm:justify-end">
            <span class="text-sm font-bold tabular-nums" :class="entry.type === 'income' ? 'text-safe' : 'text-danger'">
              {{ entry.type === 'income' ? '+' : '−' }}₱{{ money(entry.amount) }}
            </span>
            <div class="flex items-center gap-3">
              <button type="button" class="text-xs font-semibold text-accent" @click="startEdit(entry)">Edit</button>
              <button
                type="button"
                class="text-xs font-semibold text-danger"
                @click="askDelete(entry)"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ExpenseLogSheet
      :open="expenseSheetOpen"
      :wallets="dashboard.wallets"
      :expense="editingExpense"
      @close="closeExpenseSheet"
      @submit="handleExpenseSubmit"
    />

    <IncomeLogSheet
      :open="incomeSheetOpen"
      :wallets="dashboard.wallets"
      :income="editingIncome"
      @close="closeIncomeSheet"
      @submit="handleIncomeSubmit"
    />

    <ConfirmModal
      :open="Boolean(deleteTarget)"
      title="Delete this entry?"
      :message="`This will permanently remove this ${deleteTarget?.type === 'income' ? 'income' : 'expense'} entry. This cannot be undone.`"
      :busy="deleting"
      @cancel="cancelDelete"
      @confirm="confirmDelete"
    />
  </div>
</template>
