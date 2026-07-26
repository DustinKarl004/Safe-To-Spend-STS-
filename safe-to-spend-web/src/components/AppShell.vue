<script setup>
import { onMounted, onUnmounted } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import AppLogo from './AppLogo.vue'
import ThemeToggle from './ThemeToggle.vue'
import NavIcon from './NavIcon.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

onMounted(() => console.log('[AppShell] mounted, route =', route.name))
onUnmounted(() => console.log('[AppShell] unmounted, route =', route.name))

const navItems = [
  { name: 'dashboard', label: 'Overview', icon: 'gauge' },
  { name: 'transactions', label: 'Transactions', icon: 'receipt' },
  { name: 'balance', label: 'Balance', icon: 'wallet' },
]

function handleLogout() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="flex h-svh flex-col overflow-hidden md:flex-row">
    <!-- Sidebar: md and up -->
    <aside
      class="hidden md:flex md:w-60 md:shrink-0 md:flex-col md:justify-between md:border-r md:border-border md:bg-bg-raised md:px-5 md:py-6 lg:w-64"
    >
      <div>
        <AppLogo :size="34" with-wordmark class="px-1 pb-8" />
        <nav class="flex flex-col gap-1">
          <RouterLink
            v-for="item in navItems"
            :key="item.name"
            :to="{ name: item.name }"
            class="flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition"
            :class="
              route.name === item.name
                ? 'bg-accent text-accent-text'
                : 'text-text-dim hover:bg-bg-sunken hover:text-text'
            "
          >
            <NavIcon :icon="item.icon" :size="19" />
            {{ item.label }}
          </RouterLink>
        </nav>
      </div>
      <div class="flex items-center justify-between gap-2 px-1">
        <button
          type="button"
          class="text-xs font-semibold text-text-dim hover:text-danger"
          @click="handleLogout"
        >
          Log out
        </button>
        <div class="flex items-center gap-1.5">
          <RouterLink
            :to="{ name: 'settings' }"
            class="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-bg-raised transition"
            :class="route.name === 'settings' ? 'text-accent' : 'text-text-dim hover:text-text'"
            aria-label="Settings"
            title="Settings"
          >
            <NavIcon icon="settings" :size="17" />
          </RouterLink>
          <ThemeToggle />
        </div>
      </div>
    </aside>

    <!-- Mobile top bar -->
    <header
      class="flex items-center justify-between border-b border-border bg-bg-raised px-4 py-3 md:hidden"
    >
      <AppLogo :size="30" with-wordmark />
      <div class="flex items-center gap-2">
        <RouterLink
          :to="{ name: 'settings' }"
          class="flex h-8 w-8 items-center justify-center rounded-full"
          :class="route.name === 'settings' ? 'text-accent' : 'text-text-dim'"
          aria-label="Settings"
        >
          <NavIcon icon="settings" :size="18" />
        </RouterLink>
        <ThemeToggle />
        <button
          type="button"
          class="text-xs font-semibold text-text-dim"
          @click="handleLogout"
        >
          Log out
        </button>
      </div>
    </header>

    <!-- Main content -->
    <main class="flex-1 overflow-y-auto pb-28 md:pb-0">
      <div class="mx-auto w-full max-w-5xl px-4 py-6 sm:px-6 lg:px-10 lg:py-10">
        <RouterView />
      </div>
    </main>

    <!-- Mobile bottom nav -->
    <nav
      class="fixed inset-x-0 bottom-0 z-20 flex border-t border-border bg-bg-raised/95 backdrop-blur md:hidden"
      style="padding-bottom: env(safe-area-inset-bottom)"
    >
      <RouterLink
        v-for="item in navItems"
        :key="item.name"
        :to="{ name: item.name }"
        class="flex flex-1 flex-col items-center gap-1 py-2.5 text-[11px] font-semibold"
        :class="route.name === item.name ? 'text-accent' : 'text-text-dim'"
      >
        <NavIcon :icon="item.icon" :size="21" />
        {{ item.label }}
      </RouterLink>
    </nav>
  </div>
</template>
