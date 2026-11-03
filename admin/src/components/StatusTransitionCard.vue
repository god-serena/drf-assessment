<script setup>
import { reactive, ref, watch } from 'vue'
import { LoaderCircle } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'
import { useUserStore } from '../stores/user.js'

const rideStore = useRideStore()
const userStore = useUserStore()
const selectedStatus = ref('')
const form = reactive({ id_driver: '', description: '', pickup_time: '' })
watch(() => rideStore.currentRide, () => {
  selectedStatus.value = ''
  Object.assign(form, { id_driver: '', description: '', pickup_time: '' })
})
function reset() {
  selectedStatus.value = ''
  Object.assign(form, { id_driver: '', description: '', pickup_time: '' })
}
async function submit() {
  if (!selectedStatus.value || rideStore.isUpdating) return
  const payload = { status: selectedStatus.value }
  if (selectedStatus.value === 'ASSIGNED') payload.id_driver = form.id_driver ? Number(form.id_driver) : null
  if (selectedStatus.value === 'CANCELLED') payload.description = form.description
  if (selectedStatus.value === 'PICKED_UP') payload.pickup_time = form.pickup_time ? new Date(form.pickup_time).toISOString() : null
  if (!['ASSIGNED', 'CANCELLED', 'PICKED_UP'].includes(selectedStatus.value) && form.description) payload.description = form.description
  if (await rideStore.submitStatusUpdate(payload)) reset()
}
</script>

<template>
  <section v-if="rideStore.currentRide" class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 class="text-lg font-bold text-slate-900">Update ride status</h2>
    <div v-if="rideStore.isTerminalState || rideStore.allowedNextStatuses.length === 0" class="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">This ride is {{ rideStore.currentStatus.toLowerCase() }}. No further transitions permitted.</div>
    <template v-else>
      <div class="mt-4 flex flex-wrap gap-2"><button v-for="status in rideStore.allowedNextStatuses" :key="status" type="button" class="rounded-lg border border-slate-300 px-3 py-2 text-sm font-semibold text-slate-700 hover:border-blue-400" :class="selectedStatus === status ? 'border-blue-600 bg-blue-600 text-white ring-4 ring-blue-100' : ''" @click="selectedStatus = status">{{ status }}</button></div>
      <form v-if="selectedStatus" class="mt-5 space-y-4" @submit.prevent="submit">
        <div v-if="selectedStatus === 'ASSIGNED'"><label class="mb-1 block text-sm font-medium" for="driver">Driver</label><select id="driver" v-model="form.id_driver" required class="w-full rounded-md border border-slate-300 px-3 py-2"><option value="" disabled>Select a driver</option><option v-for="driver in userStore.drivers" :key="driver.id" :value="driver.id">{{ [driver.first_name, driver.last_name].filter(Boolean).join(' ') || driver.name || driver.email }} — {{ driver.email }}</option></select></div>
        <div v-else-if="selectedStatus === 'CANCELLED'"><label class="mb-1 block text-sm font-medium" for="description">Cancellation reason</label><textarea id="description" v-model="form.description" required rows="3" class="w-full rounded-md border border-slate-300 px-3 py-2"/></div>
        <div v-else-if="selectedStatus === 'PICKED_UP'"><label class="mb-1 block text-sm font-medium" for="pickup-time">Pickup time</label><input id="pickup-time" v-model="form.pickup_time" required type="datetime-local" class="w-full rounded-md border border-slate-300 px-3 py-2"/></div>
        <div v-else><label class="mb-1 block text-sm font-medium" for="note">Optional note</label><input id="note" v-model="form.description" type="text" class="w-full rounded-md border border-slate-300 px-3 py-2" /></div>
        <div class="flex gap-3"><button type="submit" :disabled="!selectedStatus || rideStore.isUpdating" class="inline-flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"><LoaderCircle v-if="rideStore.isUpdating" class="h-4 w-4 animate-spin" />{{ rideStore.isUpdating ? 'Submitting…' : 'Submit Transition' }}</button><button type="button" class="rounded-md border border-slate-300 px-4 py-2 font-semibold text-slate-700 hover:bg-slate-50" @click="reset">Reset</button></div>
      </form>
    </template>
  </section>
</template>
