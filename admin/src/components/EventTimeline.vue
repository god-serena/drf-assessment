<script setup>
import { computed, reactive, ref } from 'vue'
import { Clock3, Pencil, CheckCircle2, LoaderCircle, History, X } from 'lucide-vue-next'
import { useRideStore } from '../stores/ride.js'

const rideStore = useRideStore()
const editingEventId = ref(null)
const historyEvent = ref(null)
const form = reactive({ occurredAt: '', reason: '' })
const events = computed(() => {
  const rawEvents = rideStore.currentRide?.events || rideStore.currentRide?.todays_ride_events || []
  return [...rawEvents].sort((a, b) => new Date(a.occurred_at || a.effective_time || a.created_at) - new Date(b.occurred_at || b.effective_time || b.created_at))
})
function formatTime(value) {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? 'Time unavailable' : date.toLocaleString()
}
function localDateTime(value) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const pad = (part) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}
function openHistory(event) {
  historyEvent.value = event
}
function closeHistory() {
  historyEvent.value = null
}
function startEditing(event) {
  rideStore.clearAlerts()
  editingEventId.value = event.id
  form.occurredAt = localDateTime(event.occurred_at || event.effective_time || event.created_at)
  form.reason = ''
}
function cancelEditing() {
  editingEventId.value = null
  rideStore.clearAlerts()
}
async function saveCorrection(event) {
  if (await rideStore.correctEvent(event.id, { occurred_at: new Date(form.occurredAt).toISOString(), reason: form.reason })) {
    editingEventId.value = null
  }
}
</script>

<template>
  <section class="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
    <h2 class="flex items-center gap-2 text-lg font-bold text-slate-900"><Clock3 class="h-5 w-5 text-blue-600" />Ride event timeline</h2>
    <p v-if="!events.length" class="mt-6 rounded-lg bg-slate-50 p-5 text-center text-sm text-slate-500">No events recorded for this ride.</p>
    <ol v-else class="mt-6 space-y-5">
      <li v-for="(event, index) in events" :key="event.id || `${event.effective_time}-${index}`" class="relative border-l-2 border-slate-200 pl-5">
        <span class="absolute -left-[5px] top-1 h-2 w-2 rounded-full bg-blue-600" />
        <div class="flex flex-wrap items-center gap-x-2 gap-y-1">
          <time class="text-xs font-medium text-slate-500">{{ formatTime(event.occurred_at || event.effective_time || event.created_at) }}</time>
          <span v-if="event.occurred_at && event.created_at && new Date(event.occurred_at).getTime() !== new Date(event.created_at).getTime()" class="text-xs text-slate-400">(Recorded: {{ formatTime(event.created_at) }})</span>
        </div>
        <p class="mt-1 text-sm text-slate-800">{{ event.description }}</p>
        <button v-if="event.corrections?.length" type="button" @click="openHistory(event)" class="mt-2 inline-flex items-center gap-1.5 rounded-full bg-amber-100 hover:bg-amber-200 px-2.5 py-1 text-xs font-medium text-amber-800 transition">
          <History class="h-3.5 w-3.5" />
          <span>Corrected ({{ event.corrections.length }}x) — View History</span>
        </button>
        <div v-if="editingEventId !== event.id" class="mt-2">
          <button type="button" class="inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium text-blue-700 hover:bg-blue-50" @click="startEditing(event)"><Pencil class="h-3.5 w-3.5" />Edit Time</button>
        </div>
        <form v-else class="mt-3 space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4" @submit.prevent="saveCorrection(event)">
          <div>
            <label :for="`event-time-${event.id}`" class="mb-1 block text-xs font-medium text-slate-700">Correct occurrence time</label>
            <input :id="`event-time-${event.id}`" v-model="form.occurredAt" type="datetime-local" required class="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" />
          </div>
          <div>
            <label :for="`event-reason-${event.id}`" class="mb-1 block text-xs font-medium text-slate-700">Reason</label>
            <textarea :id="`event-reason-${event.id}`" v-model="form.reason" required rows="3" placeholder="Explain reason for correction e.g. Driver connectivity delay" class="w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200" />
          </div>
          <div class="flex flex-wrap gap-2">
            <button type="submit" :disabled="rideStore.isUpdating" class="inline-flex items-center gap-2 rounded-md bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"><LoaderCircle v-if="rideStore.isUpdating" class="h-4 w-4 animate-spin" /><CheckCircle2 v-else class="h-4 w-4" />Save Correction</button>
            <button type="button" :disabled="rideStore.isUpdating" class="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-60" @click="cancelEditing"><X class="h-4 w-4" />Cancel</button>
          </div>
        </form>
      </li>
    </ol>
  </section>

  <div v-if="historyEvent" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4" @click.self="closeHistory">
    <section role="dialog" aria-modal="true" aria-labelledby="history-title" class="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white p-6 shadow-xl">
      <div class="flex items-start justify-between gap-4">
        <div>
          <h2 id="history-title" class="text-lg font-bold text-slate-900">Correction Audit History</h2>
          <p class="mt-1 text-sm text-slate-600">{{ historyEvent.description }}</p>
        </div>
        <button type="button" aria-label="Close history" class="rounded-md p-1 text-slate-500 hover:bg-slate-100 hover:text-slate-700" @click="closeHistory"><X class="h-5 w-5" /></button>
      </div>
      <ol class="mt-5 space-y-4">
        <li v-for="(correction, index) in historyEvent.corrections" :key="correction.id || index" class="rounded-lg border border-slate-200 p-4">
          <dl class="grid gap-3 text-sm sm:grid-cols-2">
            <div><dt class="font-medium text-slate-500">Corrected by</dt><dd class="mt-1 text-slate-900">{{ correction.corrected_by_email || correction.editor_email || 'Unknown' }}</dd></div>
            <div><dt class="font-medium text-slate-500">Corrected at</dt><dd class="mt-1 text-slate-900">{{ formatTime(correction.created_at) }}</dd></div>
            <div><dt class="font-medium text-slate-500">Previous occurrence</dt><dd class="mt-1 text-slate-900">{{ formatTime(correction.previous_occurred_at) }}</dd></div>
            <div><dt class="font-medium text-slate-500">New occurrence</dt><dd class="mt-1 text-slate-900">{{ formatTime(correction.new_occurred_at) }}</dd></div>
            <div class="sm:col-span-2"><dt class="font-medium text-slate-500">Reason</dt><dd class="mt-1 text-slate-900">{{ correction.reason }}</dd></div>
          </dl>
        </li>
      </ol>
      <div class="mt-6 flex justify-end">
        <button type="button" class="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700" @click="closeHistory">Close</button>
      </div>
    </section>
  </div>
</template>
