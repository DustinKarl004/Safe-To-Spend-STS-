<script setup>
import { RouterView, useRoute } from 'vue-router'
import { watchEffect } from 'vue'
import AppShell from './components/AppShell.vue'

const route = useRoute()

watchEffect(() => {
  console.log('[App] route =', route.name, 'meta =', route.meta, '-> showShell =', !route.meta.public && !route.meta.standalone)
})
</script>

<template>
  <AppShell v-if="!route.meta.public && !route.meta.standalone" />
  <RouterView v-else />
</template>
