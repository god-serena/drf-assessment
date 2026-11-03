import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
})

export function setApiAuth(email, password) {
  if (email && password) {
    client.defaults.headers.common.Authorization = `Basic ${btoa(`${email}:${password}`)}`
  } else {
    delete client.defaults.headers.common.Authorization
  }
}

export async function getCurrentUser() {
  const response = await client.get('/users/me/')
  return response.data
}

function errorMessage(value) {
  if (Array.isArray(value)) return value.map(errorMessage).filter(Boolean).join(' ')
  if (typeof value === 'string') return value
  if (value && typeof value === 'object') {
    return Object.values(value).map(errorMessage).filter(Boolean).join(' ')
  }
  return value == null ? '' : String(value)
}

export function parseApiError(error) {
  const response = error?.response
  const status = response?.status || 0
  const data = response?.data
  const fieldErrors = {}

  if (data && typeof data === 'object' && !Array.isArray(data)) {
    for (const [field, value] of Object.entries(data)) {
      if (field === 'detail' || field === 'non_field_errors') continue
      const message = errorMessage(value)
      if (message) fieldErrors[field] = message
    }
  }

  const rawMessage = errorMessage(data?.detail)
    || errorMessage(data?.non_field_errors)
    || Object.values(fieldErrors)[0]
    || error?.message
    || 'An unexpected error occurred'

  let message = rawMessage
  if (!response) {
    message = 'Unable to connect to the server. Please check your network connection and try again.'
  } else if (status === 403) {
    message = /csrf|origin/i.test(rawMessage)
      ? 'Security validation failed. Please refresh the page or sign in again.'
      : 'You do not have permission to perform this action.'
  } else if (status === 401) {
    message = 'Authentication required. Please sign in with administrator credentials.'
  } else if (status >= 500) {
    message = 'A server error occurred while processing the request. Please try again later.'
  } else if (status === 400 && /json parse error/i.test(rawMessage)) {
    message = 'Invalid request format received by the server.'
  }

  return {
    status,
    message,
    rawMessage,
    fieldErrors,
  }
}

export default client
