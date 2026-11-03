import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { getUsers } from '../api/users.js'
import { parseApiError, setApiAuth } from '../api/client.js'

export const useUserStore = defineStore('user', () => {
  const users = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const authEmail = ref('admin@test.com')
  const authPassword = ref('123')

  const drivers = computed(() => users.value.filter((user) => user.role === 'driver'))
  const riders = computed(() => users.value.filter((user) => user.role === 'rider'))
  const userMap = computed(() => new Map(users.value.map((user) => [user.id, user])))

  async function loadUsers() {
    isLoading.value = true
    error.value = null
    try {
      const result = await getUsers()
      users.value = Array.isArray(result) ? result : result?.results || []
      return users.value
    } catch (requestError) {
      error.value = parseApiError(requestError).message
      return []
    } finally {
      isLoading.value = false
    }
  }

  function updateAuth(email, password) {
    authEmail.value = email
    authPassword.value = password
    setApiAuth(email, password)
  }

  return {
    users,
    isLoading,
    error,
    authEmail,
    authPassword,
    drivers,
    riders,
    userMap,
    loadUsers,
    updateAuth,
  }
})
