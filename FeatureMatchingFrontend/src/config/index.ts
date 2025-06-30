export interface IConfig {
  env: string // 开发环境
  mock?: boolean // mock数据
  title: string // 项目title
  baseUrl?: string // 项目地址
  baseApi?: string // api请求地址
}

const dev: IConfig = {
  env: 'development',
  mock: false,
  title: '开发环境',
  baseUrl: '/api',
  baseApi: 'http://127.0.0.1:5000/',
}

const prod: IConfig = {
  env: 'production',
  mock: false,
  title: '生产环境',
  baseUrl: '/api',
  baseApi: 'http://127.0.0.1:5000/',
}
export const config: IConfig = import.meta.env.MODE == 'development' ? dev : prod
