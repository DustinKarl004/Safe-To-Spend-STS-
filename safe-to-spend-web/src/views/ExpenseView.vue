<script setup>
import { computed, onMounted, ref } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import { EXPENSE_CATEGORIES, expenseCategory } from '@/lib/expenseCategories'
import CategoryIcon from '@/components/CategoryIcon.vue'
import DonutChart from '@/components/DonutChart.vue'
import ExpenseLogSheet from '@/components/ExpenseLogSheet.vue'

const dashboard = useDashboardStore()

onMounted(() => {
  dashboard.refresh()
  dashboard.fetchAllExpenses()
})

const addExpenseOpen = ref(false)

async function handleLogExpense(payload) {
  await dashboard.logExpense(payload)
  addExpenseOpen.value = false
}

const editingId = ref(null)
const editForm = ref({ amount: '', category: 'other', note: '' })
const busyId = ref(null)

const groups = computed(() => {
  const byDay = new Map()
  for (const expense of dashboard.allExpenses) {
    const day = new Date(expense.created_at).toLocaleDateString('en-PH', {
      weekday: 'long',
      month: 'short',
      day: 'numeric',
    })
    if (!byDay.has(day)) byDay.set(day, [])
    byDay.get(day).push(expense)
  }
  return Array.from(byDay.entries())
})

function money(n) {
  return Number(n).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const totalSpent = computed(() => dashboard.allExpenses.reduce((sum, e) => sum + Number(e.amount), 0))

const categoryBreakdown = computed(() => {
  const totals = new Map()
  for (const expense of dashboard.allExpenses) {
    totals.set(expense.category, (totals.get(expense.category) || 0) + Number(expense.amount))
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

function formatTime(iso) {
  return new Date(iso).toLocaleTimeString('en-PH', { hour: 'numeric', minute: '2-digit' })
}

function categoryLabel(value) {
  return expenseCategory(value).label
}

function startEdit(expense) {
  editingId.value = expense.id
  editForm.value = { amount: expense.amount, category: expense.category, note: expense.note || '' }
}

function cancelEdit() {
  editingId.value = null
}

async function saveEdit(id) {
  busyId.value = id
  try {
    await dashboard.updateExpense(id, {
      amount: Number(editForm.value.amount),
      category: editForm.value.category,
      note: editForm.value.note.trim() || null,
    })
    editingId.value = null
  } finally {
    busyId.value = null
  }
}

async function removeExpense(id) {
  busyId.value = id
  try {
    await dashboard.deleteExpense(id)
  } finally {
    busyId.value = null
  }
}
</script>

<template>
  <div class="flex flex-col gap-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="font-display text-2xl font-extrabold">Expenses</h1>
        <p class="mt-1 text-sm text-text-dim">Where it went, and every expense you've logged.</p>
      </div>
      <button
        type="button"
        class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent text-accent-text"
        aria-label="Log an expense"
        title="Log an expense"
        @click="addExpenseOpen = true"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
      </button>
    </div>

    <ExpenseLogSheet
      :open="addExpenseOpen"
      :wallets="dashboard.wallets"
      @close="addExpenseOpen = false"
      @submit="handleLogExpense"
    />

    <p v-if="!dashboard.allExpenses.length" class="rounded-2xl border border-border bg-bg-raised p-6 text-sm text-text-dim">
      No expenses logged yet.
    </p>

    <div v-else class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
      <h2 class="font-display text-base font-bold">Where it went</h2>
      <div class="mt-4 flex flex-col items-center gap-6 sm:flex-row sm:items-center sm:gap-8">
        <DonutChart :segments="categoryBreakdown" :size="168">
          <span class="text-[11px] font-semibold uppercase tracking-wide text-text-dim">Total</span>
          <span class="mt-1 font-display text-xl font-extrabold tabular-nums tracking-tight">₱{{ money(totalSpent) }}</span>
        </DonutChart>

        <ul class="flex w-full flex-col gap-2.5">
          <li v-for="cat in categoryBreakdown" :key="cat.label" class="flex items-center gap-3">
            <CategoryIcon :icon="cat.icon" :color="cat.color" :size="30" />
            <span class="min-w-0 flex-1 truncate text-sm font-semibold">{{ cat.label }}</span>
            <span class="shrink-0 text-xs font-semibold text-text-dim">{{ Math.round((cat.value / totalSpent) * 100) }}%</span>
            <span class="shrink-0 text-sm font-bold tabular-nums">₱{{ money(cat.value) }}</span>
          </li>
        </ul>
      </div>
    </div>

    <div v-for="[day, expenses] in groups" :key="day" class="flex flex-col gap-2.5">
      <h2 class="text-xs font-semibold uppercase tracking-wide text-text-dim">{{ day }}</h2>
      <div class="overflow-hidden rounded-2xl border border-border bg-bg-raised shadow-sm">
        <div v-for="(expense, idx) in expenses" :key="expense.id" :class="idx > 0 ? 'border-t border-border' : ''">
          <div v-if="editingId !== expense.id" class="flex items-center justify-between gap-3 p-4">
            <div class="flex min-w-0 items-center gap-3">
              <CategoryIcon
                :icon="expenseCategory(expense.category).icon"
                :color="expenseCategory(expense.category).color"
                :size="36"
              />
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold">{{ expense.note || categoryLabel(expense.category) }}</p>
                <p class="text-xs text-text-dim">{{ categoryLabel(expense.category) }} · {{ formatTime(expense.created_at) }}</p>
              </div>
            </div>
            <div class="flex shrink-0 items-center gap-3">
              <span class="text-sm font-bold tabular-nums">−₱{{ money(expense.amount) }}</span>
              <button type="button" class="text-xs font-semibold text-accent" @click="startEdit(expense)">Edit</button>
              <button
                type="button"
                class="text-xs font-semibold text-danger disabled:opacity-40"
                :disabled="busyId === expense.id"
                @click="removeExpense(expense.id)"
              >
                Delete
              </button>
            </div>
          </div>

          <div v-else class="flex flex-col gap-2.5 p-4">
            <div class="flex flex-wrap gap-2.5">
              <select
                v-model="editForm.category"
                class="rounded-lg border border-border bg-bg-sunken px-2.5 py-2 text-sm font-semibold outline-none"
              >
                <option v-for="c in EXPENSE_CATEGORIES" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
              <div class="flex items-center gap-1.5">
                <span class="text-sm font-semibold text-text-dim">₱</span>
                <input
                  v-model="editForm.amount"
                  type="number"
                  min="0.01"
                  step="0.01"
                  class="w-24 rounded-lg border border-border bg-bg-sunken px-2.5 py-2 text-right text-sm font-semibold outline-none focus:border-accent"
                />
              </div>
              <input
                v-model="editForm.note"
                type="text"
                placeholder="Note"
                class="min-w-0 flex-1 rounded-lg border border-border bg-bg-sunken px-2.5 py-2 text-sm outline-none focus:border-accent"
              />
            </div>
            <div class="flex justify-end gap-3">
              <button type="button" class="text-xs font-semibold text-text-dim" @click="cancelEdit">Cancel</button>
              <button
                type="button"
                class="text-xs font-semibold text-accent disabled:opacity-40"
                :disabled="busyId === expense.id"
                @click="saveEdit(expense.id)"
              >
                {{ busyId === expense.id ? 'Saving…' : 'Save' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
