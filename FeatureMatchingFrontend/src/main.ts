import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate' // 持久化 pinia
import ElementPlus from 'element-plus' // 全局引入 ElementPlus
import 'element-plus/dist/index.css' // 引入 ElementPlus 样式
import '@/style/index.css' // 全局样式
import '@/assets/iconfont/iconfont.js' // iconfont
import SvgIcon from '@/components/SvgIcon.vue' // 全局引入自己封装的 SvgIcon 组件
import zhCn from 'element-plus/es/locale/lang/zh-cn' // elementPlus 使用中文

import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
app.use(pinia)
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.component('SvgIcon', SvgIcon)

app.mount('#app')
