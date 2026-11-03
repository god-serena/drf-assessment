<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { Shield, LogIn, AlertCircle } from 'lucide-vue-next'

const authStore = useAuthStore()
const email = ref('admin@test.com')
const password = ref('123')

async function handleLogin() {
  if (!email.value || !password.value) return
  await authStore.login(email.value, password.value)
}

</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/70 backdrop-blur-sm p-4">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden">
      <!-- Header -->
      <div class="bg-gradient-to-r from-blue-600 to-indigo-700 px-6 py-6 text-white text-center">
        <div class="mx-auto w-12 h-12 rounded-full bg-white/20 flex items-center justify-center mb-3">
          <Shield class="w-6 h-6 text-white" />
        </div>
        <h2 class="text-xl font-bold">Wingz Admin Dispatch</h2>
        <p class="text-sm text-blue-100 mt-1">Sign in with an Administrator account to manage rides</p>
      </div>

      <!-- Form Body -->
      <div class="p-6 space-y-5">
        <div v-if="authStore.authError" class="flex items-start gap-3 p-3 text-sm text-rose-800 bg-rose-50 border border-rose-200 rounded-lg">
          <AlertCircle class="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>{{ authStore.authError }}</div>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Email Address</label>
            <input
              v-model="email"
              type="email"
              required
              class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              placeholder="admin@test.com"
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-1">Password</label>
            <input
              v-model="password"
              type="password"
              required
              class="w-full px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm text-slate-900 focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            :disabled="authStore.isLoading"
            class="w-full flex items-center justify-center gap-2 py-2.5 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg shadow-sm hover:shadow transition"
          >
            <LogIn class="w-4 h-4" />
            <span v-if="authStore.isLoading">Signing in...</span>
            <span v-else>Sign In</span>
          </button>
        </form>

      </div>
    </div>
  </div>
</template>
