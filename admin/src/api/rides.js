import client from './client.js'

export async function getRides(params = {}) {
  return client.get('/rides/', { params }).then((response) => response.data)
}

export async function getRide(id) {
  return client.get(`/rides/${id}/`).then((response) => response.data)
}

export async function updateRideStatus(id, payload) {
  return client.post(`/rides/${id}/status/`, payload).then((response) => response.data)
}

export async function correctRideEvent(eventId, payload) {
  return client.post(`/ride-events/${eventId}/correct/`, payload).then((response) => response.data)
}
