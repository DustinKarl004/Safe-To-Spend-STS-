<script setup>
import { reactive, ref, watch } from 'vue'
import { WALLET_GROUPS } from '@/lib/walletProviders'
import ProviderIcon from './ProviderIcon.vue'
import ConfirmModal from './ConfirmModal.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  selectedNames: { type: Array, default: () => [] },
  wallets: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save', 'remove-now'])

const pending = reactive(new Set())
const removalTarget = ref(null)
const removalGroup = ref(null)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      pending.clear()
      props.selectedNames.forEach((name) => pending.add(name))
      removalTarget.value = null
      removalGroup.value = null
    }
  },
)

function isSelected(name) {
  return pending.has(name)
}

function hasSelection(group) {
  return group.providers.some((p) => isSelected(p.name))
}

function existingWallet(name) {
  return props.wallets.find((w) => w.label === name) || null
}

function walletBalance(name) {
  return existingWallet(name)?.balance ? Number(existingWallet(name).balance) : 0
}

function formatPeso(value) {
  return `₱${Number(value || 0).toLocaleString('en-PH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function toggle(name) {
  if (pending.has(name)) {
    if (walletBalance(name) !== 0) {
      removalTarget.value = name
      return
    }
    pending.delete(name)
  } else {
    pending.add(name)
  }
}

function confirmRemoval() {
  const name = removalTarget.value
  if (name) {
    pending.delete(name)
    const wallet = existingWallet(name)
    if (wallet) emit('remove-now', [wallet.id])
  }
  removalTarget.value = null
}

function cancelRemoval() {
  removalTarget.value = null
}

function clearGroup(group) {
  const withBalance = group.providers.find((p) => pending.has(p.name) && walletBalance(p.name) !== 0)
  if (withBalance) {
    removalGroup.value = group
    return
  }
  group.providers.forEach((p) => pending.delete(p.name))
}

function confirmGroupRemoval() {
  const group = removalGroup.value
  if (group) {
    const ids = []
    group.providers.forEach((p) => {
      if (pending.has(p.name)) {
        pending.delete(p.name)
        const wallet = existingWallet(p.name)
        if (wallet) ids.push(wallet.id)
      }
    })
    if (ids.length) emit('remove-now', ids)
  }
  removalGroup.value = null
}

function cancelGroupRemoval() {
  removalGroup.value = null
}

function hasChanges() {
  if (pending.size !== props.selectedNames.length) return true
  return props.selectedNames.some((name) => !pending.has(name))
}

function finish() {
  if (props.saving) return
  if (!hasChanges()) {
    emit('close')
    return
  }
  const selected = WALLET_GROUPS.flatMap((group) =>
    group.providers.filter((p) => pending.has(p.name)).map((p) => ({ kind: group.kind, name: p.name })),
  )
  emit('save', selected)
}

function cancel() {
  if (props.saving) return
  emit('close')
}
</script>

<template>
  <Transition name="fade">
    <div v-if="open" class="fixed inset-0 z-30 bg-black/40" @click="cancel" />
  </Transition>

  <Transition name="slide">
    <aside
      v-if="open"
      class="fixed inset-y-0 right-0 z-40 flex w-full max-w-sm flex-col bg-bg-raised shadow-2xl sm:max-w-md"
      role="dialog"
      aria-label="Choose a wallet or bank"
    >
      <div class="flex items-center justify-between border-b border-border px-5 py-4">
        <h2 class="font-display text-base font-bold">Add a wallet or bank</h2>
        <button
          type="button"
          class="flex h-8 w-8 items-center justify-center rounded-full text-text-dim hover:bg-bg-sunken hover:text-text disabled:opacity-60"
          aria-label="Close"
          :disabled="saving"
          @click="cancel"
        >
          ✕
        </button>
      </div>

      <div class="flex-1 overflow-y-auto px-5 py-4">
        <div v-for="group in WALLET_GROUPS" :key="group.kind" class="mb-6 last:mb-0">
          <div class="mb-2.5 flex items-center justify-between">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-text-dim">{{ group.label }}</h3>
            <button
              v-if="hasSelection(group)"
              type="button"
              class="flex h-6 w-6 items-center justify-center rounded-full text-text-dim transition hover:bg-danger/10 hover:text-danger"
              :aria-label="`Clear ${group.label}`"
              :title="`Clear ${group.label}`"
              @click="clearGroup(group)"
            >
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="grid grid-cols-2 gap-2.5">
            <button
              v-for="provider in group.providers"
              :key="provider.name"
              type="button"
              class="relative flex flex-col items-center gap-2 rounded-xl border p-3.5 text-center text-sm font-semibold transition"
              :class="
                isSelected(provider.name)
                  ? 'border-accent bg-accent/10 text-text'
                  : 'border-border bg-bg-sunken text-text hover:border-accent/50'
              "
              @click="toggle(provider.name)"
            >
              <span v-if="isSelected(provider.name)" class="absolute right-2 top-2 text-accent">✓</span>
              <ProviderIcon v-bind="provider" :size="64" />
              <span class="leading-tight">{{ provider.name }}</span>
              <span v-if="existingWallet(provider.name)" class="text-xs font-semibold text-text-dim">
                {{ formatPeso(existingWallet(provider.name).balance) }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <div class="border-t border-border px-5 py-4">
        <button
          type="button"
          class="w-full rounded-xl bg-accent py-3 text-sm font-bold text-accent-text disabled:opacity-60"
          :disabled="saving"
          @click="finish"
        >
          {{ saving ? 'Saving…' : 'Done' }}
        </button>
      </div>
    </aside>
  </Transition>

  <ConfirmModal
    :open="Boolean(removalTarget)"
    title="Remove this wallet?"
    :message="`This will permanently delete ${removalTarget}, its current balance of ${formatPeso(walletBalance(removalTarget))}, and all its income and expense entries. This cannot be undone.`"
    @cancel="cancelRemoval"
    @confirm="confirmRemoval"
  />

  <ConfirmModal
    :open="Boolean(removalGroup)"
    title="Remove these wallets?"
    :message="`Some wallets in ${removalGroup?.label ?? 'this group'} still have a balance. Removing them will permanently delete their balances and all their income and expense entries. This cannot be undone.`"
    @cancel="cancelGroupRemoval"
    @confirm="confirmGroupRemoval"
  />
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.25s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateX(100%);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (prefers-reduced-motion: reduce) {
  .slide-enter-active,
  .slide-leave-active,
  .fade-enter-active,
  .fade-leave-active {
    transition: none;
  }
}
</style>
