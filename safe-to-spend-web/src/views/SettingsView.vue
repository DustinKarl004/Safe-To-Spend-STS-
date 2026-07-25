<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import PasswordField from '@/components/PasswordField.vue'

const auth = useAuthStore()
const router = useRouter()

// ---- change password ----
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordError = ref('')
const savingPassword = ref(false)

const passwordsMismatch = computed(
  () => confirmPassword.value.length > 0 && confirmPassword.value !== newPassword.value,
)
const canSavePassword = computed(
  () => currentPassword.value.length > 0 && newPassword.value.length >= 8 && newPassword.value === confirmPassword.value,
)

async function savePassword() {
  if (!canSavePassword.value) return
  passwordError.value = ''
  savingPassword.value = true
  try {
    await auth.changePassword(currentPassword.value, newPassword.value)
    auth.logout()
    router.push({ name: 'login', query: { passwordChanged: '1' } })
  } catch (err) {
    passwordError.value = err.response?.data?.detail || 'Could not change your password. Try again.'
    savingPassword.value = false
  }
}

// ---- 2FA ----
const twoFaStep = ref('idle') // 'idle' | 'setup' | 'disable'
const setupInfo = ref(null)
const setupCode = ref('')
const setupError = ref('')
const settingUp = ref(false)
const disablePassword = ref('')
const disableError = ref('')
const disabling = ref(false)

const secretGrouped = computed(() => {
  if (!setupInfo.value?.secret) return ''
  return setupInfo.value.secret.match(/.{1,4}/g).join(' ')
})

async function startSetup2fa() {
  setupError.value = ''
  setupCode.value = ''
  twoFaStep.value = 'setup'
  try {
    setupInfo.value = await auth.setup2fa()
  } catch {
    setupError.value = 'Could not start 2FA setup. Try again.'
  }
}

function cancelSetup2fa() {
  twoFaStep.value = 'idle'
  setupInfo.value = null
  setupCode.value = ''
  setupError.value = ''
}

async function confirmSetup2fa() {
  if (setupCode.value.length !== 6) return
  setupError.value = ''
  settingUp.value = true
  try {
    await auth.verify2fa(setupCode.value)
    twoFaStep.value = 'idle'
    setupInfo.value = null
  } catch (err) {
    setupError.value = err.response?.data?.detail || 'Incorrect code. Try again.'
  } finally {
    settingUp.value = false
  }
}

function startDisable2fa() {
  disableError.value = ''
  disablePassword.value = ''
  twoFaStep.value = 'disable'
}

function cancelDisable2fa() {
  twoFaStep.value = 'idle'
  disablePassword.value = ''
  disableError.value = ''
}

async function confirmDisable2fa() {
  if (!disablePassword.value) return
  disableError.value = ''
  disabling.value = true
  try {
    await auth.disable2fa(disablePassword.value)
    twoFaStep.value = 'idle'
  } catch (err) {
    disableError.value = err.response?.data?.detail || 'Incorrect password.'
  } finally {
    disabling.value = false
  }
}
</script>

<template>
  <div class="mx-auto flex w-full max-w-lg flex-col gap-6">
    <div>
      <h1 class="font-display text-2xl font-extrabold">Settings</h1>
      <p class="mt-1 text-sm text-text-dim">Manage your account security.</p>
    </div>

    <!-- Change password -->
    <div class="rounded-2xl border border-border bg-bg-raised p-5 shadow-sm sm:p-6">
      <h2 class="font-display text-base font-bold">Change password</h2>
      <p class="mt-1 text-sm text-text-dim">Requires your current password. You'll be logged out afterward.</p>

      <form class="mt-4 flex flex-col gap-3" @submit.prevent="savePassword">
        <PasswordField v-model="currentPassword" label="Current password" autocomplete="current-password" />
        <PasswordField v-model="newPassword" label="New password" minlength="8" autocomplete="new-password" placeholder="At least 8 characters" />
        <div>
          <PasswordField v-model="confirmPassword" label="Confirm new password" autocomplete="new-password" />
          <p v-if="passwordsMismatch" class="mt-1.5 text-xs font-medium text-danger">Passwords don't match.</p>
        </div>

        <p v-if="passwordError" class="text-sm font-medium text-danger">{{ passwordError }}</p>

        <button
          type="submit"
          :disabled="!canSavePassword || savingPassword"
          class="mt-1 w-full rounded-xl bg-accent py-3 text-sm font-bold text-accent-text disabled:opacity-40"
        >
          {{ savingPassword ? 'Saving…' : 'Save password' }}
        </button>
      </form>
    </div>

    <!-- Two-factor authentication -->
    <div class="rounded-2xl border border-border bg-bg-raised p-5 shadow-sm sm:p-6">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h2 class="font-display text-base font-bold">Two-factor authentication</h2>
        <span
          v-if="auth.user?.totp_enabled"
          class="shrink-0 rounded-full px-3 py-1 text-xs font-semibold"
          style="background: color-mix(in srgb, var(--safe) 16%, transparent); color: var(--safe)"
        >
          Enabled
        </span>
        <span v-else class="shrink-0 rounded-full bg-bg-sunken px-3 py-1 text-xs font-semibold text-text-dim">Disabled</span>
      </div>
      <p class="mt-1 text-sm text-text-dim">
        Use an authenticator app like Google Authenticator or Authy for an extra layer of login security.
      </p>

      <!-- idle: enabled -->
      <button
        v-if="twoFaStep === 'idle' && auth.user?.totp_enabled"
        type="button"
        class="mt-4 w-full rounded-xl border border-border px-4 py-2.5 text-sm font-bold text-danger sm:w-auto"
        @click="startDisable2fa"
      >
        Disable 2FA
      </button>

      <!-- idle: disabled -->
      <button
        v-else-if="twoFaStep === 'idle'"
        type="button"
        class="mt-4 w-full rounded-xl bg-accent py-3 text-sm font-bold text-accent-text"
        @click="startSetup2fa"
      >
        Enable 2FA
      </button>

      <!-- setup flow -->
      <div v-if="twoFaStep === 'setup'" class="mt-4 flex flex-col gap-3">
        <p class="text-sm text-text-dim">Scan this into your authenticator app:</p>

        <div v-if="setupInfo?.qr_code_data_uri" class="flex justify-center">
          <div class="rounded-2xl bg-white p-4">
            <img :src="setupInfo.qr_code_data_uri" alt="2FA QR code" class="h-40 w-40 sm:h-48 sm:w-48" />
          </div>
        </div>

        <p class="text-center text-xs text-text-dim">Can't scan? Enter this key manually:</p>
        <p
          v-if="secretGrouped"
          class="select-all break-all rounded-xl border border-dashed border-border bg-bg-sunken px-3.5 py-3 text-center font-mono text-sm font-bold tracking-wider"
        >
          {{ secretGrouped }}
        </p>

        <label class="mt-2 flex flex-col gap-1.5 text-sm font-semibold">
          Enter the 6-digit code to confirm
          <input
            v-model="setupCode"
            type="text"
            inputmode="numeric"
            pattern="[0-9]*"
            maxlength="6"
            placeholder="123456"
            class="w-full rounded-xl border border-border bg-bg-sunken px-3.5 py-2.5 text-center text-lg font-bold tracking-[0.3em] outline-none focus:border-accent"
          />
        </label>

        <p v-if="setupError" class="text-sm font-medium text-danger">{{ setupError }}</p>

        <div class="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            class="rounded-xl border border-border px-4 py-2.5 text-sm font-bold text-text-dim"
            @click="cancelSetup2fa"
          >
            Cancel
          </button>
          <button
            type="button"
            :disabled="setupCode.length !== 6 || settingUp"
            class="flex-1 rounded-xl bg-accent py-2.5 text-sm font-bold text-accent-text disabled:opacity-40"
            @click="confirmSetup2fa"
          >
            {{ settingUp ? 'Confirming…' : 'Confirm' }}
          </button>
        </div>
      </div>

      <!-- disable flow -->
      <div v-if="twoFaStep === 'disable'" class="mt-4 flex flex-col gap-3">
        <PasswordField v-model="disablePassword" label="Confirm your password" autocomplete="current-password" />

        <p v-if="disableError" class="text-sm font-medium text-danger">{{ disableError }}</p>

        <div class="flex flex-col gap-3 sm:flex-row">
          <button
            type="button"
            class="rounded-xl border border-border px-4 py-2.5 text-sm font-bold text-text-dim"
            @click="cancelDisable2fa"
          >
            Cancel
          </button>
          <button
            type="button"
            :disabled="!disablePassword || disabling"
            class="flex-1 rounded-xl bg-danger py-2.5 text-sm font-bold text-white disabled:opacity-40"
            @click="confirmDisable2fa"
          >
            {{ disabling ? 'Disabling…' : 'Disable 2FA' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
