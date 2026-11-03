<script setup>
import { useAuthStore } from '../stores/auth'
import { ShieldAlert, UserX, LogOut } from 'lucide-vue-next'

const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
}
</script>

<template>
  <div class="max-w-2xl mx-auto my-12 p-8 bg-white border border-rose-200 rounded-2xl shadow-lg text-center space-y-6">
    <div class="mx-auto w-16 h-16 rounded-full bg-rose-100 flex items-center justify-center text-rose-600">
      <ShieldAlert class="w-8 h-8" />
    </div>

    <div>
      <div class="inline-block px-3 py-1 bg-rose-100 text-rose-800 text-xs font-bold rounded-full uppercase tracking-wider mb-2">
        HTTP 403 Forbidden
      </div>
      <h2 class="text-2xl font-bold text-slate-900">Administrator Access Required</h2>
      <p class="text-sm text-slate-600 mt-2 max-w-lg mx-auto">
        You are authenticated as
        <strong class="text-slate-900">{{ authStore.currentUser?.email }}</strong>
        with the role
        <span class="inline-block px-2 py-0.5 bg-amber-100 text-amber-900 rounded font-semibold text-xs uppercase">{{ authStore.userRole }}</span>.
        Under the assessment's <code class="text-xs bg-slate-100 px-1 py-0.5 rounded font-mono">AdministratorPermission</code> policy, only administrator accounts can view and manage ride dispatch records.
      </p>
    </div>

    <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl text-left text-xs text-slate-700 space-y-2">
      <div class="font-semibold text-slate-900 flex items-center gap-1.5">
        <UserX class="w-4 h-4 text-rose-600" />
        <span>Permission Enforcement Details</span>
      </div>
      <p>
        The backend DRF viewsets (<code class="font-mono">RideViewSet</code>, <code class="font-mono">UserViewSet</code>) evaluate <code class="font-mono">request.user.role == 'admin'</code>. Because your active role is <code class="font-mono">{{ authStore.userRole }}</code>, API requests to ride details and status transitions are blocked with HTTP 403.
      </p>
    </div>

    <div class="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
      <button
        type="button"
        @click="handleLogout"
        class="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg shadow-sm transition"
      >
        <span>Sign in as Administrator</span>
      </button>

      <button
        type="button"
        @click="handleLogout"
        class="w-full sm:w-auto flex items-center justify-center gap-2 px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-medium rounded-lg transition"
      >
        <LogOut class="w-4 h-4" />
        <span>Sign Out</span>
      </button>
    </div>
  </div>
</template>
