<script setup>
import { LoaderCircle } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'
import RideDetailCard from '../components/RideDetailCard.vue'
import StatusTransitionCard from '../components/StatusTransitionCard.vue'
import EventTimeline from '../components/EventTimeline.vue'

const rideStore = useRideStore()
</script>

<template>
  <div v-if="rideStore.isLoading && !rideStore.currentRide" class="flex min-h-64 items-center justify-center gap-3 text-slate-600">
    <LoaderCircle class="h-6 w-6 animate-spin text-blue-600" />
    <span class="text-sm font-medium">Loading ride dispatch data...</span>
  </div>

  <div v-else-if="rideStore.currentRide" class="grid gap-6 lg:grid-cols-2">
    <div class="space-y-6">
      <RideDetailCard />
      <StatusTransitionCard />
    </div>
    <div>
      <EventTimeline />
    </div>
  </div>

  <div v-else class="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-600 text-sm">
    No ride details available. Please select a ride from the header selector.
  </div>
</template>
