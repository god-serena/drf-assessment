<script setup>
import { CheckCircle, X } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'

const rideStore = useRideStore()
</script>

<template>
  <div v-if="rideStore.successNotification" role="status" class="flex items-center gap-3 rounded-lg border border-emerald-300 bg-emerald-50 p-4 text-emerald-900">
    <CheckCircle class="h-5 w-5 shrink-0" />
    <p class="flex-1 font-medium">{{ rideStore.successNotification }}</p>
    <button type="button" aria-label="Dismiss success message" class="rounded p-1 hover:bg-emerald-100" @click="rideStore.clearAlerts()"><X class="h-4 w-4" /></button>
  </div>
</template>
