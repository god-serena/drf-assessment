<script setup>
import { AlertCircle, X } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'

const rideStore = useRideStore()
</script>

<template>
  <div v-if="rideStore.error" role="alert" class="flex items-start gap-3 rounded-lg border border-red-300 bg-red-50 p-4 text-red-900">
    <AlertCircle class="mt-0.5 h-5 w-5 shrink-0" />
    <div class="min-w-0 flex-1">
      <p class="font-semibold">{{ rideStore.error }}</p>
    </div>
    <button type="button" aria-label="Dismiss error" class="rounded p-1 hover:bg-red-100" @click="rideStore.clearAlerts()"><X class="h-4 w-4" /></button>
  </div>
</template>
