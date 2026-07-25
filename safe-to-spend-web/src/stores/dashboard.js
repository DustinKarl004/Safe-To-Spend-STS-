import { defineStore } from 'pinia'
import api from '@/lib/api'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    loading: false,
    safeToSpendToday: 0,
    totalWalletBalance: 0,
    totalReserved: 0,
    daysRemaining: 0,
    nextPayday: null,
    spentToday: 0,
    wallets: [],
    obligations: [],
    recentExpenses: [],
    allExpenses: [],
    walletAdjustments: [],
    incomes: [],
  }),

  actions: {
    async refresh() {
      this.loading = true
      try {
        const { data } = await api.get('/api/dashboard')
        this.safeToSpendToday = data.safe_to_spend_today
        this.totalWalletBalance = data.total_wallet_balance
        this.totalReserved = data.total_reserved
        this.daysRemaining = data.days_remaining
        this.nextPayday = data.next_payday
        this.spentToday = data.spent_today
        this.wallets = data.wallets
        this.obligations = data.obligations
        this.recentExpenses = data.recent_expenses
      } finally {
        this.loading = false
      }
    },

    async addWallet(wallet) {
      await api.post('/api/wallets', wallet)
      await this.refresh()
    },

    async updateWallet(id, patch) {
      await api.patch(`/api/wallets/${id}`, patch)
      await Promise.all([this.refresh(), this.fetchWalletAdjustments()])
    },

    async fetchWalletAdjustments() {
      const { data } = await api.get('/api/wallets/adjustments')
      this.walletAdjustments = data
    },

    async deleteWallet(id) {
      await api.delete(`/api/wallets/${id}`)
      await this.refresh()
    },

    async fetchIncomes() {
      const { data } = await api.get('/api/income')
      this.incomes = data
    },

    async logIncome(income) {
      await api.post('/api/income', income)
      await Promise.all([this.refresh(), this.fetchIncomes()])
    },

    async deleteIncome(id) {
      await api.delete(`/api/income/${id}`)
      await Promise.all([this.refresh(), this.fetchIncomes()])
    },

    async addObligation(obligation) {
      await api.post('/api/obligations', obligation)
      await this.refresh()
    },

    async deleteObligation(id) {
      await api.delete(`/api/obligations/${id}`)
      await this.refresh()
    },

    async logExpense(expense) {
      await api.post('/api/expenses', expense)
      await this.refresh()
    },

    async fetchAllExpenses() {
      const { data } = await api.get('/api/expenses')
      this.allExpenses = data
    },

    async updateExpense(id, patch) {
      await api.patch(`/api/expenses/${id}`, patch)
      await Promise.all([this.refresh(), this.fetchAllExpenses()])
    },

    async deleteExpense(id) {
      await api.delete(`/api/expenses/${id}`)
      await Promise.all([this.refresh(), this.fetchAllExpenses()])
    },
  },
})
