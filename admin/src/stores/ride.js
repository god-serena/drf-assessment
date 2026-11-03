import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { correctRideEvent, getRide, getRides, updateRideStatus } from '../api/rides.js'
import { parseApiError } from '../api/client.js'

export const useRideStore = defineStore('ride', () => {
  const currentRide = ref(null)
  const rides = ref([])
  const isLoading = ref(false)
  const isUpdating = ref(false)
  const error = ref(null)
  const fieldErrors = ref({})
  const successNotification = ref(null)

  const currentStatus = computed(() => currentRide.value?.status || null)
  const allowedNextStatuses = computed(() => currentRide.value?.allowed_next_statuses || [])
  const isTerminalState = computed(() => ['COMPLETED', 'CANCELLED'].includes(currentStatus.value))

  async function loadRide(id) {
    isLoading.value = true
    error.value = null
    fieldErrors.value = {}
    successNotification.value = null
    try {
      currentRide.value = await getRide(id)
      return currentRide.value
    } catch (requestError) {
      const parsed = parseApiError(requestError)
      error.value = parsed.message
      fieldErrors.value = parsed.fieldErrors
      return null
    } finally {
      isLoading.value = false
    }
  }

  async function loadRidesList() {
    try {
      const result = await getRides({ ps: 20 })
      const list = Array.isArray(result) ? result : result?.results || []
      rides.value = [...list].sort((a, b) => a.id - b.id)
      return rides.value
    } catch (requestError) {
      const parsed = parseApiError(requestError)
      error.value = parsed.message
      fieldErrors.value = parsed.fieldErrors
      return []
    }
  }

  async function submitStatusUpdate(payload) {
    if (!currentRide.value) return false

    isUpdating.value = true
    error.value = null
    fieldErrors.value = {}
    successNotification.value = null
    try {
      const updatedRide = await updateRideStatus(currentRide.value.id, payload)
      currentRide.value = updatedRide
      successNotification.value = `Ride status updated to ${updatedRide.status.replace('_', ' ')}.`
      await loadRidesList()
      return true
    } catch (requestError) {
      const parsed = parseApiError(requestError)
      error.value = parsed.message
      fieldErrors.value = parsed.fieldErrors
      return false
    } finally {
      isUpdating.value = false
    }
  }

  async function correctEvent(eventId, payload) {
    if (!currentRide.value) return false

    isUpdating.value = true
    error.value = null
    fieldErrors.value = {}
    successNotification.value = null
    try {
      await correctRideEvent(eventId, payload)
      successNotification.value = 'Event timestamp corrected successfully.'
      await loadRide(currentRide.value.id)
      return true
    } catch (requestError) {
      const parsed = parseApiError(requestError)
      error.value = parsed.message
      fieldErrors.value = parsed.fieldErrors
      return false
    } finally {
      isUpdating.value = false
    }
  }

  function clearAlerts() {
    error.value = null
    fieldErrors.value = {}
    successNotification.value = null
  }

  return {
    currentRide,
    rides,
    isLoading,
    isUpdating,
    error,
    fieldErrors,
    successNotification,
    currentStatus,
    allowedNextStatuses,
    isTerminalState,
    loadRide,
    loadRidesList,
    submitStatusUpdate,
    correctEvent,
    clearAlerts,
  }
})
