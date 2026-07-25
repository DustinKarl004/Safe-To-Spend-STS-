<script setup>
import { computed, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import AppLogo from '@/components/AppLogo.vue'
import PasswordField from '@/components/PasswordField.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

const passwordsMismatch = computed(
  () => confirmPassword.value.length > 0 && confirmPassword.value !== password.value,
)
const canSubmit = computed(
  () => password.value.length >= 8 && confirmPassword.value === password.value,
)

async function onSubmit() {
  error.value = ''
  if (!canSubmit.value) {
    error.value = 'Passwords do not match.'
    return
  }
  loading.value = true
  try {
    await auth.register(email.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = err.response?.data?.detail || 'Could not create your account. Try a different email.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-svh items-center justify-center px-4 py-10">
    <div class="w-full max-w-sm">
      <div class="mb-8 flex flex-col items-center gap-3 text-center">
        <AppLogo :size="52" />
        <div>
          <h1 class="font-display text-xl font-extrabold">Create your account</h1>
          <p class="mt-1 text-sm text-text-dim">Free, forever. No card needed.</p>
        </div>
      </div>

      <form class="flex flex-col gap-3 rounded-2xl border border-border bg-bg-raised p-6 shadow-sm" @submit.prevent="onSubmit">
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

        <PasswordField
          v-model="password"
          minlength="8"
          autocomplete="new-password"
          placeholder="At least 8 characters"
        />

        <div>
          <PasswordField
            v-model="confirmPassword"
            label="Confirm password"
            autocomplete="new-password"
            placeholder="Re-enter your password"
          />
          <p v-if="passwordsMismatch" class="mt-1.5 text-xs font-medium text-danger">Passwords don't match.</p>
        </div>

        <p v-if="error" class="text-sm font-medium text-danger">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading || !canSubmit"
          class="mt-2 rounded-xl bg-accent py-3 text-sm font-bold text-accent-text transition disabled:opacity-60"
        >
          {{ loading ? 'Creating…' : 'Create account' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm text-text-dim">
        Already have an account?
        <RouterLink :to="{ name: 'login' }" class="font-semibold text-accent">Log in</RouterLink>
      </p>
    </div>
  </div>
</template>
