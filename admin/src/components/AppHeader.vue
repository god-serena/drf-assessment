<script setup>
import { ref, computed } from 'vue'
import { Car, Compass, UserCheck, ChevronDown, LogOut, Search } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'
import { useUserStore } from '../stores/user.js'
import { useAuthStore } from '../stores/auth.js'
import { useRoute, useRouter } from 'vue-router'

const rideStore = useRideStore()
const userStore = useUserStore()
const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isMenuOpen = ref(false)
const searchQuery = ref('')

const rideOptions = computed(() => (rideStore.rides.length
  ? rideStore.rides
  : Array.from({ length: 10 }, (_, index) => ({ id: index + 1, status: '' })))
  .map(ride => ({
    ...ride,
    rider_email: ride.rider_email || userStore.userMap.get(ride.id_rider)?.email,
  })))

const filteredRides = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return rideOptions.value

  return rideOptions.value.filter(ride =>
    [ride.id, ride.status, ride.rider_email]
      .some(value => String(value ?? '').toLowerCase().includes(query)),
  )
})

function truncateEmail(email, maxLength = 18) {
  if (!email) return ''
  return email.length > maxLength ? `${email.slice(0, maxLength - 1)}…` : email
}

function selectRide(event) {
  const id = Number(event.target.value)
  if (id) router.push(`/rides/${id}`)
}

function handleLogout() {
  isMenuOpen.value = false
  authStore.logout()
}
</script>

<template>
  <header class="border-b border-slate-200 bg-white sticky top-0 z-30 shadow-sm">
    <div class="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4 py-3.5 sm:px-6 lg:px-8">
      <div class="flex items-center gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
          <Car class="h-5 w-5" />
          <Compass class="-ml-1 h-4 w-4" />
        </div>
        <div>
          <h1 class="text-base font-bold text-slate-900 leading-tight">Wingz Ride Dispatch</h1>
          <p class="text-xs text-slate-500">Live Status & Event Management</p>
        </div>
      </div>

      <div class="flex flex-wrap items-center gap-4">
        <!-- Ride selector (Only shown if admin) -->
        <label v-if="authStore.isAdmin" class="flex items-center gap-2 text-xs font-semibold text-slate-600 uppercase tracking-wider">
          <span>Ride</span>
          <div class="relative normal-case font-normal">
            <Search class="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              v-model="searchQuery"
              type="search"
              placeholder="Search rider email, ID, status..."
              class="w-56 rounded-lg border border-slate-300 bg-white py-1.5 pl-8 pr-3 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              @search="searchQuery = $event.target.value"
            />
          </div>
          <select
            class="normal-case font-normal w-72 truncate rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-900 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            :value="Number(route.params.id) || rideStore.currentRide?.id || ''"
            @change="selectRide"
          >
            <option v-if="filteredRides.length === 0" value="" disabled>No matching rides</option>
            <option v-else value="" disabled>Select ride</option>
            <option v-for="ride in filteredRides" :key="ride.id" :value="ride.id">
              Ride #{{ ride.id }}<template v-if="ride.rider_email"> ({{ truncateEmail(ride.rider_email) }})</template><template v-if="ride.status"> — {{ ride.status }}</template>
            </option>
          </select>
        </label>

        <!-- User Profile & Switcher Dropdown -->
        <div class="relative">
          <button
            type="button"
            @click="isMenuOpen = !isMenuOpen"
            class="flex items-center gap-2.5 px-3 py-1.5 rounded-lg border border-slate-200 hover:border-slate-300 bg-slate-50 hover:bg-slate-100/80 transition text-sm text-slate-800"
          >
            <div class="w-6 h-6 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-xs uppercase">
              {{ authStore.currentUser?.email?.[0] || '?' }}
            </div>
            <div class="text-left hidden sm:block">
              <div class="text-xs font-semibold leading-tight text-slate-900">{{ authStore.currentUser?.email || 'Not Signed In' }}</div>
              <div class="text-[10px] uppercase font-bold tracking-wider" :class="{
                'text-emerald-700': authStore.userRole === 'admin',
                'text-amber-700': authStore.userRole === 'driver',
                'text-blue-700': authStore.userRole === 'rider',
                'text-slate-500': !authStore.isAuthenticated
              }">
                {{ authStore.userRole }}
              </div>
            </div>
            <ChevronDown class="w-3.5 h-3.5 text-slate-400" />
          </button>

          <!-- Dropdown Menu -->
          <div
            v-if="isMenuOpen"
            class="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-xl border border-slate-100 py-2 z-50 text-xs"
          >
            <div class="px-3 py-2 border-b border-slate-100 text-slate-500">
              Signed in as <strong class="text-slate-800">{{ authStore.currentUser?.email }}</strong>
            </div>

            <div class="border-t border-slate-100 mt-1 pt-1">
              <button
                type="button"
                @click="handleLogout"
                class="w-full text-left px-3 py-2 text-rose-600 hover:bg-rose-50 flex items-center gap-2 font-medium transition"
              >
                <LogOut class="w-3.5 h-3.5" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>
