import axios from 'axios'
import { config } from '@/config/index.ts'
const http = axios.create({
  // baseURL 需要设置为反向代理前缀，不能设置绝对路径URL
  baseURL: config.baseUrl,
  // timeout: 5000,
})

export default http
