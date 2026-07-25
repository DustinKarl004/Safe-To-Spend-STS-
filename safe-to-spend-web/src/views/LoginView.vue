<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'
import PasswordField from '@/components/PasswordField.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const mfaToken = ref('')
const mfaCode = ref('')
const verifying2fa = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    const result = await auth.login(email.value, password.value)
    if (result.requires_2fa) {
      mfaToken.value = result.mfa_token
    } else {
      router.push({ name: 'dashboard' })
    }
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not log in. Check your details and try again.'
  } finally {
    loading.value = false
  }
}

const canVerify = computed(() => mfaCode.value.length === 6)

async function onVerify2fa() {
  if (!canVerify.value) return
  error.value = ''
  verifying2fa.value = true
  try {
    await auth.completeMfaLogin(mfaToken.value, mfaCode.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Incorrect code. Try again.'
  } finally {
    verifying2fa.value = false
  }
}

function backToLogin() {
  mfaToken.value = ''
  mfaCode.value = ''
  error.value = ''
}
</script>

<template>
  <div class="flex min-h-svh items-center justify-center px-4 py-10">
    <div class="w-full max-w-sm">
      <div class="mb-8 flex flex-col items-center gap-3 text-center">
        <AppLogo :size="52" />
        <div>
          <h1 class="font-display text-xl font-extrabold">{{ mfaToken ? 'Two-factor authentication' : 'Welcome back' }}</h1>
          <p class="mt-1 text-sm text-text-dim">
            {{ mfaToken ? 'Enter the 6-digit code from your authenticator app.' : "Log in to see today's safe-to-spend." }}
          </p>
        </div>
      </div>

      <p
        v-if="!mfaToken && route.query.passwordChanged"
        class="mb-4 rounded-xl px-3.5 py-2.5 text-center text-sm font-semibold"
        style="background: color-mix(in srgb, var(--safe) 14%, transparent); color: var(--safe)"
      >
        Password changed — log in with your new password.
      </p>

      <form
        v-if="!mfaToken"
        class="flex flex-col gap-3 rounded-2xl border border-border bg-bg-raised p-6 shadow-sm"
        @submit.prevent="onSubmit"
      >
        <label class="flex flex-col gap-1.5 text-sm font-semibold">
          Email
          <input
            v-model="email"
            type="email"
            required
            autocomplete="email"
            placeholder="you@email.com"
            class="rounded-xl border border-border bg-bg-sunken px-3.5 py-2.5 text-sm font-normal outline-none focus:border-accent"
          />
        </label>
        <PasswordField v-model="password" autocomplete="current-password" />

        <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="mt-2 rounded-xl bg-accent py-3 text-sm font-bold text-accent-text transition disabled:opacity-60"
        >
          {{ loading ? 'Logging in…' : 'Log in' }}
        </button>
      </form>

      <form v-else class="flex flex-col gap-3 rounded-2xl border border-border bg-bg-raised p-6 shadow-sm" @submit.prevent="onVerify2fa">
        <label class="flex flex-col gap-1.5 text-sm font-semibold">
          6-digit code
          <input
            v-model="mfaCode"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="6"
            autocomplete="one-time-code"
            placeholder="123456"
            class="rounded-xl border border-border bg-bg-sunken px-3.5 py-2.5 text-center text-lg font-bold tracking-[0.3em] outline-none focus:border-accent"
          />
        </label>

        <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>

        <button
          type="submit"
          :disabled="!canVerify || verifying2fa"
          class="mt-2 rounded-xl bg-accent py-3 text-sm font-bold text-accent-text transition disabled:opacity-60"
        >
          {{ verifying2fa ? 'Verifying…' : 'Verify' }}
        </button>
        <button type="button" class="text-sm font-semibold text-text-dim" @click="backToLogin">Back to log in</button>
      </form>

      <p v-if="!mfaToken" class="mt-6 text-center text-sm text-text-dim">
        New here?
        <RouterLink :to="{ name: 'register' }" class="font-semibold text-accent">Create an account</RouterLink>
      </p>
    </div>
  </div>
</template>
