<script setup>
import { reactive, ref, watch } from 'vue'
import { WALLET_GROUPS } from '@/lib/walletProviders'
import ProviderIcon from './ProviderIcon.vue'
import ConfirmModal from './ConfirmModal.vue'
import CurrencySelect from './CurrencySelect.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  selectedNames: { type: Array, default: () => [] },
  wallets: { type: Array, default: () => [] },
  saving: { type: Boolean, default: false },
  addingForeignMoney: { type: Boolean, default: false },
})
const emit = defineEmits(['close', 'save', 'remove-now', 'add-foreign-money'])

const newForeignCurrency = ref('USD')

function foreignMoneyWallets(provider) {
  return props.wallets.filter((w) => w.label.startsWith(`${provider.name} (`))
}

function addForeignMoney(group, provider) {
  if (props.addingForeignMoney) return
  const code = newForeignCurrency.value
  const label = `${provider.name} (${code})`
  if (props.wallets.some((w) => w.label === label)) return
  emit('add-foreign-money', { kind: group.kind, label, currency: code })
}

function removeForeignMoney(wallet) {
  if (Number(wallet.balance_php ?? wallet.balance) !== 0) {
    removalTarget.value = wallet.label
    return
  }
  emit('remove-now', [wallet.id])
}

const pending = reactive(new Set())
const removalTarget = ref(null)
const removalGroup = ref(null)
const expandedParents = reactive(new Set())

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      pending.clear()
      props.selectedNames.forEach((name) => pending.add(name))
      removalTarget.value = null
      removalGroup.value = null
      expandedParents.clear()
      WALLET_GROUPS.forEach((group) =>
        group.providers.forEach((p) => {
          if (p.children?.some((c) => pending.has(c.name))) expandedParents.add(p.name)
        }),
      )
    }
  },
)

function leafProviders(group) {
  return group.providers.flatMap((p) => {
    if (p.perCurrency) return []
    return p.children ? p.children : [p]
  })
}

function isSelected(name) {
  return pending.has(name)
}

function isExpanded(name) {
  return expandedParents.has(name)
}

function toggleExpanded(name) {
  if (expandedParents.has(name)) expandedParents.delete(name)
  else expandedParents.add(name)
}

function selectedChildCount(provider) {
  return provider.children.filter((c) => isSelected(c.name)).length
}

function hasSelection(group) {
  return leafProviders(group).some((p) => isSelected(p.name))
}

function existingWallet(name) {
  return props.wallets.find((w) => w.label === name) || null
}

function walletBalance(name) {
  const wallet = existingWallet(name)
  if (!wallet) return 0
  return Number(wallet.balance_php ?? wallet.balance) || 0
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
  const withBalance = leafProviders(group).find((p) => pending.has(p.name) && walletBalance(p.name) !== 0)
  if (withBalance) {
    removalGroup.value = group
    return
  }
  leafProviders(group).forEach((p) => pending.delete(p.name))
}

function confirmGroupRemoval() {
  const group = removalGroup.value
  if (group) {
    const ids = []
    leafProviders(group).forEach((p) => {
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
    leafProviders(group)
      .filter((p) => pending.has(p.name))
      .map((p) => ({ kind: group.kind, name: p.name })),
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
      <div class="border-b border-border px-5 py-4">
        <div class="flex items-center justify-between">
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
        <p class="mt-1.5 text-[11px] leading-relaxed text-text-dim">
          Bank and e-wallet logos are the property of their respective owners.
          Safe To Spend is not affiliated with or endorsed by these institutions.
        </p>
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
            <template v-for="provider in group.providers" :key="provider.name">
              <div v-if="provider.perCurrency" class="col-span-2 flex flex-col gap-2.5">
                <div
                  v-for="wallet in foreignMoneyWallets(provider)"
                  :key="wallet.id"
                  class="flex items-center gap-3 rounded-xl border border-border bg-bg-sunken p-3"
                >
                  <ProviderIcon v-bind="provider" :name="wallet.label" :size="44" />
                  <div class="min-w-0 flex-1">
                    <p class="truncate text-sm font-semibold">{{ wallet.label }}</p>
                    <p class="text-xs text-text-dim">{{ formatPeso(walletBalance(wallet.label)) }}</p>
                  </div>
                  <button
                    type="button"
                    class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-text-dim transition hover:bg-danger/10 hover:text-danger"
                    aria-label="Remove"
                    @click="removeForeignMoney(wallet)"
                  >
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none">
                      <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
                    </svg>
                  </button>
                </div>

                <div class="flex flex-col gap-2 rounded-xl border border-dashed border-border p-2.5">
                  <div class="flex items-center gap-2">
                    <ProviderIcon v-bind="provider" :size="32" />
                    <span class="min-w-0 flex-1 truncate text-sm font-semibold">{{ provider.name }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <CurrencySelect v-model="newForeignCurrency" compact class="min-w-0 flex-1" />
                    <button
                      type="button"
                      class="shrink-0 rounded-lg bg-accent px-3 py-1.5 text-xs font-bold text-accent-text disabled:opacity-60"
                      :disabled="addingForeignMoney"
                      @click="addForeignMoney(group, provider)"
                    >
                      {{ addingForeignMoney ? 'Adding…' : 'Add' }}
                    </button>
                  </div>
                </div>
              </div>

              <button
                v-else-if="!provider.children"
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
                  {{ formatPeso(walletBalance(provider.name)) }}
                </span>
              </button>

              <template v-else>
                <button
                  type="button"
                  class="relative flex flex-col items-center gap-2 rounded-xl border p-3.5 text-center text-sm font-semibold transition"
                  :class="
                    selectedChildCount(provider) > 0
                      ? 'border-accent bg-accent/10 text-text'
                      : 'border-border bg-bg-sunken text-text hover:border-accent/50'
                  "
                  @click="toggleExpanded(provider.name)"
                >
                  <span
                    v-if="selectedChildCount(provider) > 0"
                    class="absolute right-2 top-2 rounded-full bg-accent px-1.5 text-[10px] font-bold text-accent-text"
                  >
                    {{ selectedChildCount(provider) }}
                  </span>
                  <ProviderIcon v-bind="provider" :size="64" />
                  <span class="leading-tight">{{ provider.name }}</span>
                  <span class="text-xs font-semibold text-text-dim">{{ isExpanded(provider.name) ? 'Hide' : 'Show all' }} ▾</span>
                </button>

                <template v-if="isExpanded(provider.name)">
                  <button
                    v-for="child in provider.children"
                    :key="child.name"
                    type="button"
                    class="relative flex flex-col items-center gap-2 rounded-xl border p-3.5 text-center text-sm font-semibold transition"
                    :class="
                      isSelected(child.name)
                        ? 'border-accent bg-accent/10 text-text'
                        : 'border-border bg-bg-sunken text-text hover:border-accent/50'
                    "
                    @click="toggle(child.name)"
                  >
                    <span v-if="isSelected(child.name)" class="absolute right-2 top-2 text-accent">✓</span>
                    <ProviderIcon v-bind="child" :size="64" />
                    <span class="leading-tight">{{ child.name }}</span>
                    <span v-if="existingWallet(child.name)" class="text-xs font-semibold text-text-dim">
                      {{ formatPeso(walletBalance(child.name)) }}
                    </span>
                  </button>
                </template>
              </template>
            </template>
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
