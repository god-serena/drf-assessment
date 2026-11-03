import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getCurrentUser, setApiAuth, parseApiError } from '../api/client'

const STORAGE_KEY_AUTH = 'wingz_auth_credentials'

export const useAuthStore = defineStore('auth', () => {
  const currentUser = ref(null)
  const authEmail = ref('')
  const authPassword = ref('')
  const isLoading = ref(false)
  const authError = ref(null)

  const isAuthenticated = computed(() => Boolean(currentUser.value))
  const isAdmin = computed(() => currentUser.value?.role === 'admin')
  const userRole = computed(() => currentUser.value?.role || 'anonymous')

  async function login(email, password) {
    isLoading.value = true
    authError.value = null
    try {
      setApiAuth(email, password)
      const user = await getCurrentUser()
      currentUser.value = user
      authEmail.value = email
      authPassword.value = password
      try {
        localStorage.setItem(
          STORAGE_KEY_AUTH,
          JSON.stringify({ email, password })
        )
      } catch {
        // localStorage non-blocking
      }
      return true
    } catch (err) {
      const parsed = parseApiError(err)
      authError.value = parsed.status === 401
        ? 'Invalid email or password.'
        : parsed.message || 'Login failed.'
      currentUser.value = null
      setApiAuth(null, null)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function logout() {
    currentUser.value = null
    authEmail.value = ''
    authPassword.value = ''
    authError.value = null
    setApiAuth(null, null)
    try {
      localStorage.removeItem(STORAGE_KEY_AUTH)
    } catch {
      // ignore
    }
  }

  async function initializeAuth() {
    let saved = null
    try {
      const raw = localStorage.getItem(STORAGE_KEY_AUTH)
      if (raw) saved = JSON.parse(raw)
    } catch {
      // ignore
    }

    const email = saved?.email || 'admin@test.com'
    const password = saved?.password || '123'
    await login(email, password)
  }

  return {
    currentUser,
    authEmail,
    authPassword,
    isLoading,
    authError,
    isAuthenticated,
    isAdmin,
    userRole,
    login,
    logout,
    initializeAuth,
  }
})
