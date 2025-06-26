import axios from 'axios'
import { ElNotification } from 'element-plus'
import { useUserStore } from '@/stores/UserStore'

export async function jwt_refresh(router: any) {
  const userStore = useUserStore()
  const { refresh_token } = userStore
  const headers = {
    Authorization: 'Bearer ' + refresh_token,
  }

  let base_url = import.meta.env.VITE_APP_HOST

  await axios
    .post(base_url + '/user/refresh', {}, { headers })
    .then((res) => {
      userStore.setAccessToken(res.data.data.access_token)
    })
    .catch(() => {
      ElNotification.error({ title: 'token已经失效', message: '请重新登陆！' })

      router.push('/login')
    })
}
