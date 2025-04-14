import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Introduction from '@/views/Introduction.vue'
import FeatureDetection from '@/views/FeatureDetection.vue'
import FeatureMatching from '@/views/FeatureMatching.vue'
import Mosaic from '@/views/Mosaic.vue'
import PoseEstimation from '@/views/PoseEstimation.vue'
import Comparison from '@/views/Comparison.vue'
import TestAxios from '@/test/testAxios.vue'
import UserHome from '@/views/User/UserHome.vue'
import MainLayout from '@/layouts/MainLayout.vue'
import UserLayout from '@/layouts/UserLayout.vue'
import UserLogin from '@/views/User/UserLogin.vue'
import UserRegister from '@/views/User/UserRegister.vue'
import UserModify from '@/views/User/UserModify.vue'
import UserDetection from '@/views/User/UserDetection.vue'
import UserMosaic from '@/views/User/UserMosaic.vue'
import UserMatching from '@/views/User/UserMatching.vue'
import UserManage from '@/views/User/UserManage.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      name: '主布局',
      path: '/',
      component: MainLayout,
      children: [
        {
          name: '首页',
          path: '',
          component: Home,
        },
        {
          name: '模型简介',
          path: '/introduction',
          component: Introduction,
        },
        {
          name: '特征检测',
          path: '/detection',
          component: FeatureDetection,
        },
        {
          name: '特征匹配',
          path: '/matching',
          component: FeatureMatching,
        },
        {
          name: '图像拼接',
          path: '/mosaic',
          component: Mosaic,
        },
        {
          name: '位姿估计',
          path: '/PoseEstimation',
          component: PoseEstimation,
        },
        {
          name: '模型比较',
          path: '/Comparison',
          component: Comparison,
        },
      ],
    },
    {
      name: '用户布局',
      path: '/user',
      component: UserLayout,
      children: [
        {
          name: '用户首页',
          path: '',
          component: UserHome,
        },
        {
          name: '修改个人信息',
          path: 'modify',
          component: UserModify,
        },
        {
          name: '特征检测记录',
          path: 'detection',
          component: UserDetection,
        },
        {
          name: '特征匹配记录',
          path: 'matching',
          component: UserMatching,
        },
        {
          name: '图像拼接记录',
          path: 'mosaic',
          component: UserMosaic,
        },
        {
          name: '',
          path: 'testAxios',
          component: TestAxios,
        },
        {
          name: '管理用户信息',
          path: 'manage',
          component: UserManage,
        },
      ],
    },
    {
      name: '登陆',
      path: '/login',
      component: UserLogin,
    },
    {
      name: '注册',
      path: '/register',
      component: UserRegister,
    },
  ],
})

export default router
