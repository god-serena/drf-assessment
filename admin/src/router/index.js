import { createRouter, createWebHistory } from 'vue-router'
import RideView from '../views/RideView.vue'

const routes = [
  {
    path: '/',
    redirect: '/rides/1',
  },
  {
    path: '/rides/:id',
    name: 'ride-detail',
    component: RideView,
    props: true,
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
