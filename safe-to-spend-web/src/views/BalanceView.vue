<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useDashboardStore } from '@/stores/dashboard'
import { useAuthStore } from '@/stores/auth'
import { KIND_LABEL, providerIcon } from '@/lib/walletProviders'
import { incomeCategory } from '@/lib/incomeCategories'
import ProviderIcon from '@/components/ProviderIcon.vue'
import CategoryIcon from '@/components/CategoryIcon.vue'
import WalletPickerDrawer from '@/components/WalletPickerDrawer.vue'
import WalletEditSheet from '@/components/WalletEditSheet.vue'
import IncomeLogSheet from '@/components/IncomeLogSheet.vue'
import PaydayEditSheet from '@/components/PaydayEditSheet.vue'
import MonthPicker from '@/components/MonthPicker.vue'
import ConfirmModal from '@/components/ConfirmModal.vue'

const dashboard = useDashboardStore()
const auth = useAuthStore()

onMounted(() => {
  dashboard.refresh()
  dashboard.fetchAllExpenses()
  dashboard.fetchWalletAdjustments()
  dashboard.fetchIncomes()
})

function money(n) {
  return Number(n).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function pad(n) {
  return String(n).padStart(2, '0')
}

const addWalletOpen = ref(false)
const editingWallet = ref(null)
const confirmingWalletRemove = ref(false)
const removingWallet = ref(false)
const addIncomeOpen = ref(false)
const incomePrefill = ref({ category: 'salary', amount: null, walletId: null })

async function saveWalletSelection(selected) {
  const selectedNames = new Set(selected.map((s) => s.name))
  const toAdd = selected.filter((s) => !dashboard.wallets.some((w) => w.label === s.name))
  const toRemove = dashboard.wallets.filter((w) => !selectedNames.has(w.label))

  try {
    for (const s of toAdd) {
      await dashboard.addWallet({ kind: s.kind, label: s.name, balance: 0 })
    }
    for (const w of toRemove) {
      await dashboard.deleteWallet(w.id)
    }
  } catch {
    window.alert('Something went wrong saving your wallets. Please try again.')
  }
}

function openWalletEdit(wallet) {
  editingWallet.value = wallet
}

function saveWalletEdit(id, balance) {
  editingWallet.value = null
  dashboard.updateWallet(id, { balance }).catch(() => {
    window.alert('Something went wrong saving that wallet. Please try again.')
  })
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

function openIncomeForPayday() {
  incomePrefill.value = {
    category: auth.user?.payday_category || 'salary',
    amount: auth.user?.payday_amount ?? null,
    walletId: auth.user?.payday_wallet_id ?? null,
  }
  addIncomeOpen.value = true
}

function handleLogIncome(payload) {
  addIncomeOpen.value = false
  dashboard.logIncome(payload).catch(() => {
    window.alert('Something went wrong logging that income. Please try again.')
  })
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

// ---- payday ----
const todayIso = `${today.getFullYear()}-${pad(today.getMonth() + 1)}-${pad(today.getDate())}`
const editingPayday = ref(false)

const paydayLabel = computed(() => {
  if (!auth.user?.next_payday) return null
  return new Date(auth.user.next_payday).toLocaleDateString('en-PH', { month: 'long', day: 'numeric', year: 'numeric' })
})

const daysUntilPayday = computed(() => {
  if (!auth.user?.next_payday) return null
  return Math.ceil((new Date(auth.user.next_payday) - new Date(todayIso)) / (1000 * 60 * 60 * 24))
})

const paydayWallet = computed(() => dashboard.wallets.find((w) => w.id === auth.user?.payday_wallet_id) || null)
const paydayCategoryInfo = computed(() => incomeCategory(auth.user?.payday_category || 'salary'))
const hasExpectedInfo = computed(() => Boolean(auth.user?.payday_amount || auth.user?.payday_wallet_id))

async function savePayday(payload) {
  await auth.setPayday(payload)
  editingPayday.value = false
}

async function removeExpectedPayday() {
  await auth.setPayday({ amount: null, wallet_id: null, category: null, note: null })
  editingPayday.value = false
}
</script>

<template>
  <div class="flex flex-col gap-6">
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
        <h2 class="font-display text-base font-bold">Payday</h2>
        <button
          type="button"
          class="text-sm font-semibold text-accent"
          @click="editingPayday = true"
        >
          Edit
        </button>
      </div>

      <div v-if="paydayLabel" class="mt-3 flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <p class="font-display text-2xl font-extrabold tabular-nums tracking-tight">{{ paydayLabel }}</p>
          <span
            class="shrink-0 rounded-full px-3 py-1 text-xs font-semibold"
            style="background: color-mix(in srgb, var(--accent) 14%, transparent); color: var(--accent)"
          >
            {{ daysUntilPayday }}d away
          </span>
        </div>

        <div class="flex items-center gap-3 rounded-xl bg-bg-sunken p-3">
          <CategoryIcon :icon="paydayCategoryInfo.icon" :color="paydayCategoryInfo.color" :size="36" />
          <div class="min-w-0 flex-1">
            <p class="text-xs text-text-dim">Expected amount</p>
            <p class="truncate text-sm font-bold" :class="auth.user?.payday_amount ? 'text-text' : 'text-text-dim'">
              {{ auth.user?.payday_amount ? `₱${money(auth.user.payday_amount)}` : 'None' }}
            </p>
          </div>
        </div>

        <div class="flex items-center gap-3 rounded-xl bg-bg-sunken p-3">
          <ProviderIcon v-if="paydayWallet" v-bind="providerIcon(paydayWallet.label)" :size="36" />
          <span v-else class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-bg-raised text-text-dim">—</span>
          <div class="min-w-0 flex-1">
            <p class="text-xs text-text-dim">Goes to</p>
            <p class="truncate text-sm font-bold" :class="paydayWallet ? 'text-text' : 'text-text-dim'">
              {{ paydayWallet ? paydayWallet.label : 'None' }}
            </p>
          </div>
        </div>

        <button
          type="button"
          class="w-full rounded-xl border border-dashed border-border py-2.5 text-sm font-semibold text-accent"
          @click="openIncomeForPayday"
        >
          + Log this payday's income
        </button>
      </div>

      <p v-else class="mt-3 text-sm text-text-dim">No payday set yet.</p>
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
        <li v-for="wallet in dashboard.wallets" :key="wallet.id">
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
            <span class="shrink-0 text-sm font-bold tabular-nums">₱{{ money(wallet.balance) }}</span>
          </button>
        </li>
      </ul>
    </div>

    <WalletPickerDrawer
      :open="addWalletOpen"
      :selected-names="dashboard.wallets.map((w) => w.label)"
      @close="addWalletOpen = false"
      @save="saveWalletSelection"
    />

    <WalletEditSheet
      :open="Boolean(editingWallet)"
      :wallet="editingWallet"
      @close="editingWallet = null"
      @save="saveWalletEdit"
      @remove="askRemoveWallet"
    />

    <ConfirmModal
      :open="confirmingWalletRemove"
      title="Remove this wallet?"
      :message="`This will remove ${editingWallet?.label ?? 'this wallet'} from your list. Its expense and income history will be kept, just unlinked.`"
      :busy="removingWallet"
      @cancel="cancelRemoveWallet"
      @confirm="confirmRemoveWallet"
    />

    <IncomeLogSheet
      :open="addIncomeOpen"
      :wallets="dashboard.wallets"
      :default-category="incomePrefill.category"
      :default-amount="incomePrefill.amount"
      :default-wallet-id="incomePrefill.walletId"
      @close="addIncomeOpen = false"
      @submit="handleLogIncome"
    />

    <PaydayEditSheet
      :open="editingPayday"
      :wallets="dashboard.wallets"
      :today-iso="todayIso"
      :initial-date="auth.user?.next_payday || todayIso"
      :initial-category="auth.user?.payday_category || 'salary'"
      :initial-wallet-id="auth.user?.payday_wallet_id ?? null"
      :initial-amount="auth.user?.payday_amount ?? null"
      :initial-note="auth.user?.payday_note || ''"
      :has-expected-info="hasExpectedInfo"
      @close="editingPayday = false"
      @save="savePayday"
      @remove="removeExpectedPayday"
    />
  </div>
</template>
