import client from './client.js'

export async function getUsers() {
  return client.get('/users/').then((response) => response.data)
}

export async function getDrivers() {
  return getUsers().then((users) =>
    (Array.isArray(users) ? users : users.results || []).filter((user) => user.role === 'driver'),
  )
}
