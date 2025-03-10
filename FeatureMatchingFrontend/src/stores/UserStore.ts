import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    access_token: localStorage.getItem('access_token'),
    refresh_token: localStorage.getItem('refresh_token'),
    user_id: localStorage.getItem('user_id'),
    username: localStorage.getItem('username') || '登陆',
    gender: localStorage.getItem('gender') || 'male',
    role: localStorage.getItem('role') || 'guest',
  }),
  actions: {
    setAccessToken(access_token: string) {
      this.access_token = access_token
      localStorage.setItem('access_token', access_token)
    },
    setRefreshToken(refresh_token: string) {
      this.refresh_token = refresh_token
      localStorage.setItem('refresh_token', refresh_token)
    },
    setUserID(user_id: string) {
      this.user_id = user_id
      localStorage.setItem('user_id', user_id)
    },
    setUsername(username: string) {
      this.username = username
      localStorage.setItem('username', username)
    },
    setGender(gender: string) {
      this.gender = gender
      localStorage.setItem('gender', gender)
    },
    setRole(role: string) {
      this.role = role
      localStorage.setItem('role', role)
    },
    removeAccessToken() {
      this.access_token = ''
      localStorage.removeItem('access_token')
    },
    removeRefreshToken() {
      this.refresh_token = ''
      localStorage.removeItem('refresh_token')
    },
    removeUserID() {
      this.user_id = ''
      localStorage.removeItem('user_id')
    },
    removeUsername() {
      this.username = '登陆'
      localStorage.removeItem('username')
    },
    removeGender() {
      this.gender = 'male'
      localStorage.removeItem('gender')
    },
    removeRole() {
      this.role = 'guest'
      localStorage.removeItem('role')
    },
    logout() {
      this.removeAccessToken()
      this.removeRefreshToken()
      this.removeUserID()
      this.removeUsername()
      this.removeGender()
      this.removeRole()
    },
  },
  persist: true,
})
