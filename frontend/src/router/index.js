import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import ProjectList from '../views/ProjectList.vue'
import ProjectDetail from '../views/ProjectDetail.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/projects',
    name: 'ProjectList',
    component: ProjectList,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects/:id',
    name: 'ProjectDetail',
    component: ProjectDetail,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const currentUser = localStorage.getItem('currentUser')

  if (to.meta.requiresAuth && !currentUser) {
    next('/login')
    return
  }

  if (to.path === '/login' && currentUser) {
    next('/projects')
    return
  }

  next()
})

export default router