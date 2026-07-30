<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { KIND_LABEL, providerIcon, isPerCurrencyLabel } from '@/lib/walletProviders'
import { incomeCategory } from '@/lib/incomeCategories'
import ProviderIcon from '@/components/ProviderIcon.vue'
import CategoryIcon from '@/components/CategoryIcon.vue'
import WalletPickerDrawer from '@/components/WalletPickerDrawer.vue'
import WalletEditSheet from '@/components/WalletEditSheet.vue'
import PaydayEditSheet from '@/components/PaydayEditSheet.vue'
import MonthPicker from '@/components/MonthPicker.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'
import LoadingState from '@/components/LoadingState.vue'

const dashboard = useDashboardStore()

onMounted(() => {
  dashboard.refresh()
  dashboard.fetchAllExpenses()
  dashboard.fetchWalletAdjustments()
  dashboard.fetchIncomes()
  dashboard.fetchPaydaySources()
})

function money(n) {
  return Number(n).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const sortedWallets = computed(() =>
  [...dashboard.wallets].sort((a, b) => Number(b.balance_php) - Number(a.balance_php))
)

function pad(n) {
  return String(n).padStart(2, '0')
}

const addWalletOpen = ref(false)
const editingWallet = ref(null)
const confirmingWalletRemove = ref(false)
const removingWallet = ref(false)
const savingWalletSelection = ref(false)
const savingWalletBalance = ref(false)
const addingForeignMoney = ref(false)

async function removeWalletsNow(ids) {
  try {
    await Promise.all(ids.map((id) => dashboard.deleteWallet(id, { silent: true })))
    await dashboard.refresh()
  } catch {
    window.alert('Something went wrong removing that wallet. Please try again.')
    await dashboard.refresh()
  }
}

async function saveWalletSelection(selected) {
  const selectedNames = new Set(selected.map((s) => s.name))
  const toAdd = selected.filter((s) => !dashboard.wallets.some((w) => w.label === s.name))
  const toRemove = dashboard.wallets.filter((w) => !selectedNames.has(w.label) && !isPerCurrencyLabel(w.label))

  savingWalletSelection.value = true
  try {
    await Promise.all([
      ...toAdd.map((s) => dashboard.addWallet({ kind: s.kind, label: s.name, balance: 0 }, { silent: true })),
      ...toRemove.map((w) => dashboard.deleteWallet(w.id, { silent: true })),
    ])
    await dashboard.refresh()
    addWalletOpen.value = false
  } catch {
    window.alert('Something went wrong saving your wallets. Please try again.')
  } finally {
    savingWalletSelection.value = false
  }
}

function openWalletEdit(wallet) {
  editingWallet.value = wallet
}

async function addForeignMoney({ kind, label, currency }) {
  addingForeignMoney.value = true
  try {
    await dashboard.addWallet({ kind, label, balance: 0, currency })
  } catch {
    window.alert('Something went wrong adding that wallet. Please try again.')
  } finally {
    addingForeignMoney.value = false
  }
}

async function saveWalletEdit(id, balance, interestRate, currency) {
  savingWalletBalance.value = true
  try {
    await dashboard.updateWallet(id, { balance, interest_rate: interestRate, currency })
    editingWallet.value = null
  } catch {
    window.alert('Something went wrong saving that wallet. Please try again.')
  } finally {
    savingWalletBalance.value = false
  }
}

function askRemoveWallet() {
  confirmingWalletRemove.value = true
}

function cancelRemoveWallet() {
  confirmingWalletRemove.value = false
}

async function confirmRemoveWallet() {
  if (!editingWallet.value) return
  removingWallet.value = true
  try {
    await dashboard.deleteWallet(editingWallet.value.id)
    confirmingWalletRemove.value = false
    editingWallet.value = null
  } catch {
    window.alert('Something went wrong removing that wallet. Please try again.')
  } finally {
    removingWallet.value = false
  }
}

// ---- net this month, with month/year navigation ----
const today = new Date()
const viewMonth = ref({ year: today.getFullYear(), month: today.getMonth() })

const currentMonthMax = { year: today.getFullYear(), month: today.getMonth() }

const netThisMonth = computed(() => {
  const inView = (iso) => {
    const d = new Date(iso)
    return d.getFullYear() === viewMonth.value.year && d.getMonth() === viewMonth.value.month
  }

  const incomeTotal = dashboard.incomes.filter((i) => inView(i.created_at)).reduce((sum, i) => sum + Number(i.amount), 0)
  const adjustments = dashboard.walletAdjustments
    .filter((a) => inView(a.created_at))
    .reduce((sum, a) => sum + Number(a.delta), 0)
  const spent = dashboard.allExpenses.filter((e) => inView(e.created_at)).reduce((sum, e) => sum + Number(e.amount), 0)

  return incomeTotal + adjustments - spent
})

const monthLabel = computed(() =>
  new Date(viewMonth.value.year, viewMonth.value.month, 1).toLocaleDateString('en-PH', { month: 'long', year: 'numeric' }),
)
const isNetPositive = computed(() => netThisMonth.value >= 0)

// ---- payday sources ----
const todayIso = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`
const editingPaydaySource = ref(null)
const addingPaydaySource = ref(false)

function daysUntil(dateStr) {
  return Math.ceil((new Date(dateStr) - new Date(todayIso)) / (1000 * 60 * 60 * 24))
}

function paydaySourceWallet(source) {
  return dashboard.wallets.find((w) => w.id === source.wallet_id) || null
}

function paydaySourceCategoryInfo(source) {
  return incomeCategory(source.category || 'salary')
}

const savingPaydaySource = ref(false)
const confirmingPaydaySourceRemove = ref(null)
const removingPaydaySource = ref(false)

function openAddPaydaySource() {
  editingPaydaySource.value = null
  addingPaydaySource.value = true
}

function openEditPaydaySource(source) {
  editingPaydaySource.value = source
  addingPaydaySource.value = true
}

function closePaydaySourceSheet() {
  addingPaydaySource.value = false
  editingPaydaySource.value = null
}

async function savePaydaySource(payload) {
  savingPaydaySource.value = true
  try {
    if (editingPaydaySource.value) {
      await dashboard.updatePaydaySource(editingPaydaySource.value.id, payload)
    } else {
      await dashboard.addPaydaySource(payload)
    }
    closePaydaySourceSheet()
  } catch {
    window.alert('Something went wrong saving that payday source. Please try again.')
  } finally {
    savingPaydaySource.value = false
  }
}

function askRemovePaydaySource() {
  confirmingPaydaySourceRemove.value = editingPaydaySource.value
}

function cancelRemovePaydaySource() {
  confirmingPaydaySourceRemove.value = null
}

async function confirmRemovePaydaySource() {
  if (!confirmingPaydaySourceRemove.value) return
  removingPaydaySource.value = true
  try {
    await dashboard.deletePaydaySource(confirmingPaydaySourceRemove.value.id)
    confirmingPaydaySourceRemove.value = null
    closePaydaySourceSheet()
  } catch {
    window.alert('Something went wrong removing that payday source. Please try again.')
  } finally {
    removingPaydaySource.value = false
  }
}
</script>

<template>
  <LoadingState v-if="!dashboard.hasLoaded" label="Loading your balance and wallets..." />
  <div v-else class="flex flex-col gap-6">
    <div>
      <h1 class="font-display text-2xl font-extrabold">Balance</h1>
      <p class="mt-1 text-sm text-text-dim">Every wallet you've added, and how this month's money moved.</p>
    </div>

    <div class="grid grid-cols-1 gap-6 sm:grid-cols-2">
      <div class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
        <span class="text-xs font-semibold uppercase tracking-wide text-text-dim">Total balance</span>
        <p class="mt-2 font-display text-4xl font-extrabold tabular-nums tracking-tight">
          ₱{{ money(dashboard.totalWalletBalance) }}
        </p>
        <p class="mt-1 text-sm text-text-dim">Across {{ dashboard.wallets.length }} wallet{{ dashboard.wallets.length === 1 ? '' : 's' }}</p>
      </div>

      <div class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold uppercase tracking-wide text-text-dim">Net</span>
          <MonthPicker v-model="viewMonth" :max="currentMonthMax" />
        </div>
        <p
          class="mt-2 font-display text-4xl font-extrabold tabular-nums tracking-tight"
          :class="isNetPositive ? 'text-safe' : 'text-danger'"
        >
          {{ isNetPositive ? '+' : '−' }}₱{{ money(Math.abs(netThisMonth)) }}
        </p>
        <p class="mt-1 text-sm text-text-dim">{{ monthLabel }} · income minus spending</p>
      </div>
    </div>

    <!-- Payday -->
    <div class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="font-display text-base font-bold">Payday sources</h2>
        <button
          type="button"
          class="text-sm font-semibold text-accent"
          @click="openAddPaydaySource"
        >
          Add
        </button>
      </div>

      <div v-if="dashboard.paydaySources.length" class="mt-3 flex flex-col gap-3">
        <button
          v-for="source in dashboard.paydaySources"
          :key="source.id"
          type="button"
          class="w-full rounded-xl bg-bg-sunken p-3 text-left transition hover:brightness-110"
          @click="openEditPaydaySource(source)"
        >
          <div class="flex items-center justify-between gap-3">
            <div class="flex min-w-0 items-center gap-3">
              <CategoryIcon :icon="paydaySourceCategoryInfo(source).icon" :color="paydaySourceCategoryInfo(source).color" :size="36" />
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-bold">{{ source.label || paydaySourceCategoryInfo(source).label }}</p>
                <p class="text-xs text-text-dim">
                  {{ new Date(source.next_date).toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' }) }}
                  <span v-if="source.wallet_label"> · {{ source.wallet_label }}</span>
                </p>
              </div>
            </div>
            <div class="flex shrink-0 flex-col items-end gap-1">
              <span
                class="rounded-full px-3 py-1 text-xs font-semibold"
                style="background: color-mix(in srgb, var(--accent) 14%, transparent); color: var(--accent)"
              >
                {{ daysUntil(source.next_date) }}d away
              </span>
              <span v-if="source.amount" class="text-xs font-semibold text-text-dim">₱{{ money(source.amount) }}</span>
            </div>
          </div>
        </button>
      </div>

      <p v-else class="mt-3 text-sm text-text-dim">No payday sources set yet — add your allowance, sideline, or any other income.</p>
    </div>

    <RouterLink
      :to="{ name: 'transactions' }"
      class="flex items-center justify-center rounded-xl border border-dashed border-border py-3 text-sm font-semibold text-accent"
    >
      View income &amp; expense history →
    </RouterLink>

    <!-- Wallets -->
    <div class="rounded-2xl border border-border bg-bg-raised p-6 shadow-sm">
      <div class="flex items-center justify-between">
        <h2 class="font-display text-base font-bold">Wallets</h2>
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full bg-bg-sunken text-text-dim transition hover:text-text"
          aria-label="Add a wallet or bank"
          title="Add a wallet or bank"
          @click="addWalletOpen = true"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          </svg>
        </button>
      </div>

      <p v-if="!dashboard.wallets.length" class="mt-4 text-sm text-text-dim">No wallets yet — add one to get started.</p>
      <ul v-else class="mt-4 flex flex-col gap-2.5">
        <li v-for="wallet in sortedWallets" :key="wallet.id">
          <button
            type="button"
            class="flex w-full items-center gap-3 rounded-xl bg-bg-sunken px-3.5 py-3 text-left transition hover:brightness-110"
            @click="openWalletEdit(wallet)"
          >
            <ProviderIcon v-bind="providerIcon(wallet.label)" :size="40" />
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-semibold">{{ wallet.label }}</p>
              <p class="text-xs text-text-dim">{{ KIND_LABEL[wallet.kind] }}</p>
            </div>
            <span v-if="wallet.currency !== 'PHP'" class="shrink-0 text-right">
              <span class="block text-sm font-bold tabular-nums">{{ wallet.currency }} {{ money(wallet.balance) }}</span>
              <span class="block text-xs font-semibold tabular-nums text-text-dim">≈ ₱{{ money(wallet.balance_php) }}</span>
            </span>
            <span v-else class="shrink-0 text-sm font-bold tabular-nums">₱{{ money(wallet.balance) }}</span>
          </button>
        </li>
      </ul>
    </div>

    <WalletPickerDrawer
      :open="addWalletOpen"
      :selected-names="dashboard.wallets.map((w) => w.label)"
      :wallets="dashboard.wallets"
      :saving="savingWalletSelection"
      :adding-foreign-money="addingForeignMoney"
      @close="addWalletOpen = false"
      @save="saveWalletSelection"
      @remove-now="removeWalletsNow"
      @add-foreign-money="addForeignMoney"
    />

    <WalletEditSheet
      :open="Boolean(editingWallet)"
      :wallet="editingWallet"
      :saving="savingWalletBalance"
      @close="editingWallet = null"
      @save="saveWalletEdit"
      @remove="askRemoveWallet"
    />

    <ConfirmModal
      :open="confirmingWalletRemove"
      title="Remove this wallet?"
      :message="`This will permanently delete ${editingWallet?.label ?? 'this wallet'}, its current balance of ₱${money(editingWallet?.balance ?? 0)}, and all its income and expense entries. This cannot be undone.`"
      :busy="removingWallet"
      @cancel="cancelRemoveWallet"
      @confirm="confirmRemoveWallet"
    />

    <PaydayEditSheet
      :open="addingPaydaySource"
      :wallets="dashboard.wallets"
      :today-iso="todayIso"
      :source="editingPaydaySource"
      :saving="savingPaydaySource"
      @close="closePaydaySourceSheet"
      @save="savePaydaySource"
      @remove="askRemovePaydaySource"
    />

    <ConfirmModal
      :open="Boolean(confirmingPaydaySourceRemove)"
      title="Remove this payday source?"
      :message="`This will delete ${confirmingPaydaySourceRemove?.label || 'this payday source'}. You can add it again anytime.`"
      :busy="removingPaydaySource"
      @cancel="cancelRemovePaydaySource"
      @confirm="confirmRemovePaydaySource"
    />
  </div>
</template>
