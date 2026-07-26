import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './style.css'
import { useDashboardStore } from './stores/dashboard'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const DASHBOARD_ROUTES = new Set(['dashboard', 'balance', 'transactions'])

router.isReady().then(async () => {
  const routeName = router.currentRoute.value.name
  if (DASHBOARD_ROUTES.has(routeName)) {
    const dashboard = useDashboardStore()
    await dashboard.refresh().catch(() => {})
  }
  app.mount('#app')
})
