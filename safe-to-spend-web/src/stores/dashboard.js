import { defineStore } from 'pinia'
import api from '@/lib/api'

function isToday(dateStr) {
  if (!dateStr) return true
  const d = new Date()
  const localToday = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  return dateStr === localToday
}

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    loading: false,
    hasLoaded: false,
    safeToSpendToday: 0,
    totalWalletBalance: 0,
    daysRemaining: 0,
    nextPayday: null,
    spentToday: 0,
    wallets: [],
    recentExpenses: [],
    allExpenses: [],
    walletAdjustments: [],
    incomes: [],
  }),

  actions: {
    async refresh() {
      console.log('[dashboard] refresh start, hasLoaded =', this.hasLoaded)
      this.loading = true
      try {
        const { data } = await api.get('/api/dashboard')
        this.safeToSpendToday = data.safe_to_spend_today
        this.totalWalletBalance = data.total_wallet_balance
        this.daysRemaining = data.days_remaining
        this.nextPayday = data.next_payday
        this.spentToday = data.spent_today
        this.wallets = data.wallets
        this.recentExpenses = data.recent_expenses
      } finally {
        this.loading = false
        this.hasLoaded = true
        console.log('[dashboard] refresh done, hasLoaded =', this.hasLoaded)
      }
    },

    async addWallet(wallet, { silent = false } = {}) {
      await api.post('/api/wallets', wallet)
      if (!silent) await this.refresh()
    },

    async updateWallet(id, patch) {
      await api.patch(`/api/wallets/${id}`, patch)
      this.refresh()
      this.fetchWalletAdjustments()
    },

    async fetchWalletAdjustments() {
      const { data } = await api.get('/api/wallets/adjustments')
      this.walletAdjustments = data
    },

    async deleteWallet(id, { silent = false } = {}) {
      await api.delete(`/api/wallets/${id}`)
      if (!silent) await this.refresh()
    },

    async fetchIncomes() {
      const { data } = await api.get('/api/income')
      this.incomes = data
    },

    async logIncome(income) {
      const tempId = `temp-${Math.random().toString(36).slice(2)}`
      const wallet = this.wallets.find((w) => w.id === income.wallet_id)
      this.incomes.unshift({ ...income, id: tempId, wallet_label: wallet?.label ?? null, created_at: new Date().toISOString() })

      const amount = Number(income.amount)
      if (wallet) wallet.balance = Number(wallet.balance) + amount
      this.totalWalletBalance += amount

      try {
        const { data } = await api.post('/api/income', income)
        const idx = this.incomes.findIndex((i) => i.id === tempId)
        if (idx !== -1) this.incomes[idx] = data
      } catch (err) {
        this.incomes = this.incomes.filter((i) => i.id !== tempId)
        throw err
      } finally {
        this.refresh()
      }
    },

    async updateIncome(id, patch) {
      const walletLabel = patch.wallet_id ? this.wallets.find((w) => w.id === patch.wallet_id)?.label ?? null : null
      const applyPatch = walletLabel ? { ...patch, wallet_label: walletLabel } : patch
      const idx = this.incomes.findIndex((i) => i.id === id)
      const prev = idx !== -1 ? { ...this.incomes[idx] } : null
      if (idx !== -1) this.incomes[idx] = { ...this.incomes[idx], ...applyPatch }
      try {
        const { data } = await api.patch(`/api/income/${id}`, patch)
        if (idx !== -1) this.incomes[idx] = data
      } catch (err) {
        if (prev && idx !== -1) this.incomes[idx] = prev
        throw err
      } finally {
        this.refresh()
      }
    },

    async deleteIncome(id) {
      const income = this.incomes.find((i) => i.id === id)
      this.incomes = this.incomes.filter((i) => i.id !== id)

      if (income) {
        const amount = Number(income.amount)
        const wallet = this.wallets.find((w) => w.id === income.wallet_id)
        if (wallet) wallet.balance = Number(wallet.balance) - amount
        this.totalWalletBalance -= amount
      }

      try {
        await api.delete(`/api/income/${id}`)
      } catch (err) {
        this.fetchIncomes()
        throw err
      } finally {
        this.refresh()
      }
    },

    async logExpense(expense) {
      const tempId = `temp-${Math.random().toString(36).slice(2)}`
      const wallet = this.wallets.find((w) => w.id === expense.wallet_id)
      const optimistic = { ...expense, id: tempId, wallet_label: wallet?.label ?? null, created_at: new Date().toISOString() }
      this.allExpenses.unshift(optimistic)
      this.recentExpenses.unshift(optimistic)

      const amount = Number(expense.amount)
      if (wallet) wallet.balance = Number(wallet.balance) - amount
      this.totalWalletBalance -= amount
      if (isToday(expense.entry_date)) {
        this.spentToday += amount
        this.safeToSpendToday -= amount
      }

      try {
        const { data } = await api.post('/api/expenses', expense)
        const i1 = this.allExpenses.findIndex((e) => e.id === tempId)
        if (i1 !== -1) this.allExpenses[i1] = data
        const i2 = this.recentExpenses.findIndex((e) => e.id === tempId)
        if (i2 !== -1) this.recentExpenses[i2] = data
      } catch (err) {
        this.allExpenses = this.allExpenses.filter((e) => e.id !== tempId)
        this.recentExpenses = this.recentExpenses.filter((e) => e.id !== tempId)
        throw err
      } finally {
        this.refresh()
      }
    },

    async fetchAllExpenses() {
      const { data } = await api.get('/api/expenses')
      this.allExpenses = data
    },

    async updateExpense(id, patch) {
      const walletLabel = patch.wallet_id ? this.wallets.find((w) => w.id === patch.wallet_id)?.label ?? null : null
      const applyPatch = walletLabel ? { ...patch, wallet_label: walletLabel } : patch
      const idxAll = this.allExpenses.findIndex((e) => e.id === id)
      const idxRecent = this.recentExpenses.findIndex((e) => e.id === id)
      const prevAll = idxAll !== -1 ? { ...this.allExpenses[idxAll] } : null
      const prevRecent = idxRecent !== -1 ? { ...this.recentExpenses[idxRecent] } : null
      if (idxAll !== -1) this.allExpenses[idxAll] = { ...this.allExpenses[idxAll], ...applyPatch }
      if (idxRecent !== -1) this.recentExpenses[idxRecent] = { ...this.recentExpenses[idxRecent], ...applyPatch }
      try {
        const { data } = await api.patch(`/api/expenses/${id}`, patch)
        if (idxAll !== -1) this.allExpenses[idxAll] = data
        if (idxRecent !== -1) this.recentExpenses[idxRecent] = data
      } catch (err) {
        if (prevAll && idxAll !== -1) this.allExpenses[idxAll] = prevAll
        if (prevRecent && idxRecent !== -1) this.recentExpenses[idxRecent] = prevRecent
        throw err
      } finally {
        this.refresh()
      }
    },

    async deleteExpense(id) {
      const expense = this.allExpenses.find((e) => e.id === id) || this.recentExpenses.find((e) => e.id === id)
      this.allExpenses = this.allExpenses.filter((e) => e.id !== id)
      this.recentExpenses = this.recentExpenses.filter((e) => e.id !== id)

      if (expense) {
        const amount = Number(expense.amount)
        const wallet = this.wallets.find((w) => w.id === expense.wallet_id)
        if (wallet) wallet.balance = Number(wallet.balance) + amount
        this.totalWalletBalance += amount
        if (isToday(expense.created_at?.slice(0, 10))) {
          this.spentToday -= amount
          this.safeToSpendToday += amount
        }
      }

      try {
        await api.delete(`/api/expenses/${id}`)
      } catch (err) {
        this.fetchAllExpenses()
        throw err
      } finally {
        this.refresh()
      }
    },
  },
})
