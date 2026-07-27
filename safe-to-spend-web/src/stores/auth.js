import { defineStore } from 'pinia'
import api from '@/lib/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('sts_token') || null,
    user: null,
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },

  actions: {
    async register(email, password) {
      await api.post('/api/auth/register', { email, password })
      await this.login(email, password)
    },

    async login(email, password) {
      const form = new URLSearchParams()
      form.set('username', email)
      form.set('password', password)
      const { data } = await api.post('/api/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      if (data.requires_2fa) {
        return data
      }

      this.token = data.access_token
      localStorage.setItem('sts_token', this.token)
      await this.fetchMe()
      return data
    },

    async completeMfaLogin(mfaToken, code) {
      const { data } = await api.post('/api/auth/login/2fa', { mfa_token: mfaToken, code })
      this.token = data.access_token
      localStorage.setItem('sts_token', this.token)
      await this.fetchMe()
      return data
    },

    async fetchMe() {
      const { data } = await api.get('/api/auth/me')
      this.user = data
      return data
    },

    async changePassword(currentPassword, newPassword) {
      const { data } = await api.post('/api/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      })
      this.user = data
      return data
    },

    async setup2fa() {
      const { data } = await api.post('/api/auth/2fa/setup')
      return data
    },

    async verify2fa(code) {
      const { data } = await api.post('/api/auth/2fa/verify', { code })
      this.user = data
      return data
    },

    async disable2fa(password) {
      const { data } = await api.post('/api/auth/2fa/disable', { password })
      this.user = data
      return data
    },

    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('sts_token')
    },
  },
})
