<script setup>
import { computed } from 'vue'
import { MapPin, UserRound, Clock3 } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'
import { useUserStore } from '../stores/user.js'

const rideStore = useRideStore()
const userStore = useUserStore()
const statusClasses = {
  REQUESTED: 'bg-blue-100 text-blue-800 border-blue-300', SCHEDULED: 'bg-purple-100 text-purple-800 border-purple-300',
  ASSIGNED: 'bg-amber-100 text-amber-800 border-amber-300', ENROUTE: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  PICKED_UP: 'bg-teal-100 text-teal-800 border-teal-300', COMPLETED: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  CANCELLED: 'bg-rose-100 text-rose-800 border-rose-300',
}
const rider = computed(() => userStore.userMap.get(rideStore.currentRide?.id_rider) || (rideStore.currentRide?.rider_email ? { email: rideStore.currentRide.rider_email } : null))
const driver = computed(() => userStore.userMap.get(rideStore.currentRide?.id_driver))
const pickupTime = computed(() => {
  const value = rideStore.currentRide?.pickup_time
  if (!value) return 'Immediate / Not specified'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Immediate / Not specified' : date.toLocaleString()
})
function fullName(user) {
  return user ? [user.first_name, user.last_name].filter(Boolean).join(' ') || user.name || 'Name unavailable' : 'Unknown'
}
</script>

<template>
  <section v-if="rideStore.currentRide" class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
    <div class="flex items-start justify-between gap-3"><div><p class="text-sm font-medium text-slate-500">Ride details</p><h2 class="mt-1 text-2xl font-bold text-slate-900">Ride #{{ rideStore.currentRide.id }}</h2></div><span class="rounded-full border px-3 py-1 text-xs font-semibold" :class="statusClasses[rideStore.currentRide.status] || 'border-slate-300 bg-slate-100 text-slate-800'">{{ rideStore.currentRide.status.replace('_', ' ') }}</span></div>
    <div class="mt-6 grid gap-5 sm:grid-cols-2">
      <div class="rounded-lg bg-slate-50 p-4"><h3 class="flex items-center gap-2 font-semibold text-slate-800"><UserRound class="h-4 w-4" /> Rider</h3><template v-if="rider"><p class="mt-2 font-medium">{{ fullName(rider) }}</p><p class="text-sm text-slate-600">{{ rider.email || '—' }}</p><p class="text-sm text-slate-600">{{ rider.phone || rider.phone_number || '—' }}</p></template><p v-else class="mt-2 text-sm text-slate-500">Rider information unavailable</p></div>
      <div class="rounded-lg bg-slate-50 p-4"><h3 class="flex items-center gap-2 font-semibold text-slate-800"><UserRound class="h-4 w-4" /> Driver</h3><template v-if="driver"><p class="mt-2 font-medium">{{ fullName(driver) }}</p><p class="text-sm text-slate-600">{{ driver.email || '—' }}</p><p class="text-sm text-slate-600">{{ driver.phone || driver.phone_number || '—' }}</p></template><p v-else class="mt-2 text-sm text-slate-500">Unassigned</p></div>
    </div>
    <div class="mt-5 space-y-3"><div class="flex gap-3"><MapPin class="mt-0.5 h-5 w-5 shrink-0 text-emerald-600"/><div><p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Pickup coordinates</p><p class="text-sm text-slate-800">{{ rideStore.currentRide.pickup_latitude ?? rideStore.currentRide.pickup_lat ?? '—' }}, {{ rideStore.currentRide.pickup_longitude ?? rideStore.currentRide.pickup_lng ?? '—' }}</p></div></div><div class="flex gap-3"><MapPin class="mt-0.5 h-5 w-5 shrink-0 text-rose-600"/><div><p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Dropoff coordinates</p><p class="text-sm text-slate-800">{{ rideStore.currentRide.dropoff_latitude ?? rideStore.currentRide.dropoff_lat ?? '—' }}, {{ rideStore.currentRide.dropoff_longitude ?? rideStore.currentRide.dropoff_lng ?? '—' }}</p></div></div><div class="flex gap-3"><Clock3 class="mt-0.5 h-5 w-5 shrink-0 text-slate-500"/><div><p class="text-xs font-semibold uppercase tracking-wide text-slate-500">Pickup time</p><p class="text-sm text-slate-800">{{ pickupTime }}</p></div></div></div>
  </section>
</template>
