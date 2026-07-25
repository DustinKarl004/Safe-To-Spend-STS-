<script setup>
import { RouterView, useRoute } from 'vue-router'
import AppShell from './components/AppShell.vue'

const route = useRoute()
</script>

<template>
  <AppShell v-if="!route.meta.public && !route.meta.standalone" />
  <RouterView v-else />
</template>
