<script setup>
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth.js'
import { useRideStore } from './stores/ride.js'
import { useUserStore } from './stores/user.js'
import AppHeader from './components/AppHeader.vue'
import LoginModal from './components/LoginModal.vue'
import ForbiddenCard from './components/ForbiddenCard.vue'
import ErrorAlert from './components/ErrorAlert.vue'
import SuccessAlert from './components/SuccessAlert.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const rideStore = useRideStore()
const userStore = useUserStore()

async function loadDashboardData() {
  if (!authStore.isAdmin) return
  await userStore.loadUsers()
  await rideStore.loadRidesList()
  if (route.params.id) {
    await rideStore.loadRide(Number(route.params.id))
  } else if (rideStore.rides.length) {
    router.replace(`/rides/${rideStore.rides[0].id}`)
  } else {
    router.replace('/rides/1')
  }
}

watch(
  () => route.params.id,
  (newId) => {
    if (newId && authStore.isAdmin && rideStore.currentRide?.id !== Number(newId)) {
      rideStore.loadRide(Number(newId))
    }
  }
)

watch(
  () => authStore.isAdmin,
  (isAdmin) => {
    if (isAdmin) {
      loadDashboardData()
    } else {
      rideStore.currentRide = null
    }
  }
)

onMounted(async () => {
  await authStore.initializeAuth()
  if (authStore.isAdmin) {
    await loadDashboardData()
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-100 flex flex-col">
    <AppHeader />

    <!-- Unauthenticated Login Modal -->
    <LoginModal v-if="!authStore.isAuthenticated" />

    <!-- Authenticated but Non-Admin (403 Forbidden Screen) -->
    <main v-else-if="!authStore.isAdmin" class="flex-1 mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 w-full flex items-center justify-center">
      <ForbiddenCard />
    </main>

    <!-- Authorized Admin Console -->
    <main v-else class="flex-1 mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8 w-full">
      <div class="space-y-3 mb-6">
        <ErrorAlert />
        <SuccessAlert />
      </div>

      <router-view />
    </main>
  </div>
</template>
