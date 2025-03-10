<template>
    <div class="common-layout">
        <el-container>
            <el-header style="height: 8vh;">
                <el-menu class="el-menu-demo" mode="horizontal" :ellipsis="false" router>
                    <el-menu-item index="/" id="home_title">
                        特征匹配
                    </el-menu-item>
                    <div class="title">
                        <div>
                            <el-text size="large">面向相对姿态估计的局部特征匹配算法设计与实现</el-text>
                        </div>
                        <div>
                            <el-text size="small">—— 21-大数据-张永锐</el-text>
                        </div>
                    </div>
                    <el-menu-item index="/user" class="userLogo">
                        <div class="avatar" v-if="username != '登陆'">
                            <el-icon>
                                <SvgIcon icon-name="icon-01" v-if="gender == 'male'" />
                                <SvgIcon icon-name="icon-34" v-if="gender == 'female'" />
                            </el-icon>
                        </div>
                        <div class="username">
                            <el-text>{{ username }}</el-text>
                        </div>
                        <div style="margin-right: 1rem;" v-if="username != '登陆'"></div>
                    </el-menu-item>
                </el-menu>
            </el-header>

            <el-container>
                <el-aside>
                    <el-menu class="el-menu-vertical-demo" :collapse="isCollapse" :ellipsis="false" router>
                        <el-menu-item index="/introduction">
                            <el-icon>
                                <Memo />
                            </el-icon>
                            <template #title>模型简介</template>
                        </el-menu-item>

                        <el-menu-item index="/detection">
                            <el-icon>
                                <SvgIcon iconName="icon-detection" />
                            </el-icon>
                            <template #title>特征点检测</template>
                        </el-menu-item>

                        <el-menu-item index="/matching">
                            <el-icon>
                                <SvgIcon iconName="icon-icon_Matching" />
                            </el-icon>
                            <template #title>特征匹配</template>
                        </el-menu-item>

                        <el-menu-item index="/Mosaic">
                            <el-icon>
                                <SvgIcon iconName="icon-matching" />
                            </el-icon>
                            <template #title>图像拼接</template>
                        </el-menu-item>

                        <el-menu-item index="/PoseEstimation">
                            <el-icon>
                                <View />
                            </el-icon>
                            <template #title>位姿估计</template>
                        </el-menu-item>

                        <el-menu-item index="/Comparison">
                            <el-icon>
                                <SvgIcon icon-name="icon-compare" />
                            </el-icon>
                            <template #title>模型比较</template>
                        </el-menu-item>

                        <hr style="margin-left: 10%; width: 80%; margin-top: 20px; margin-bottom: 20px;">

                        <el-menu-item index="/user/manage" v-if="role === 'admin'">
                            <el-icon>
                                <SvgIcon icon-name="icon-guanliyuan_jiaoseguanli" />
                            </el-icon>
                            <template #title>管理用户信息</template>
                        </el-menu-item>

                        <el-menu-item index="/user/modify" v-if="username != '登陆'">
                            <el-icon>
                                <SvgIcon icon-name="icon-essential-information" />
                            </el-icon>
                            <template #title>管理个人信息</template>
                        </el-menu-item>

                        <el-menu-item @click="logout" v-if="username != '登陆'">
                            <el-icon>
                                <SvgIcon icon-name="icon-dengchu" />
                            </el-icon>
                            <template #title>注销登陆</template>
                        </el-menu-item>

                        <el-menu-item index="" @click="openCollapse" v-if="isCollapse" class="fun">
                            <el-icon>
                                <SvgIcon icon-name="icon-xiangyouzhankai" />
                            </el-icon>
                            <template #title>展开导航栏</template>
                        </el-menu-item>
                        <el-menu-item index="" @click="closeCollapse" v-if="!isCollapse" class="fun">
                            <el-icon>
                                <SvgIcon icon-name="icon-Hdonghua-xiangzuozhankai" />
                            </el-icon>
                            <template #title>收起导航栏</template>
                        </el-menu-item>

                    </el-menu>
                </el-aside>

                <el-main>
                    <router-view></router-view>
                </el-main>
            </el-container>
        </el-container>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/UserStore';
import { storeToRefs } from 'pinia';
import { ElNotification } from 'element-plus';

const userStore = useUserStore();
let { username, gender, role } = storeToRefs(userStore);
userStore.$subscribe((mutation, state) => {
    username.value = state.username
    gender.value = state.gender
    role.value = state.role
})


const isCollapse = ref(true)

function openCollapse() {
    isCollapse.value = false
}

function closeCollapse() {
    isCollapse.value = true
}

function logout() {
    userStore.logout()
    ElNotification.success({
        title: '注销成功',
        message: '欢迎 ' + username.value + ' 下次使用！'
    })
}
</script>

<style scoped>
.el-menu--horizontal>.el-menu-item:nth-child(1) {
    margin-right: auto;
}

.el-menu-demo {
    height: 100%;
    display: flex;
    align-items: center;
}

#home_title {
    font-size: xx-large;
}

.title {
    display: flex;
    flex-direction: column;
    justify-content: end;
    align-items: end;
    margin-right: auto;
}

.el-aside {
    width: auto;
}

.el-menu-vertical-demo {
    height: 92vh;

    /* display: flex;
    flex-direction: column;
    justify-content: space-between; */
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
    width: auto;
    min-width: 180px;
    height: 92vh;
}

/* .fun {
    margin-top: auto;
} */


.userLogo {
    height: 3rem;


    display: flex;
    justify-content: space-between;
    align-items: center;

    border-radius: 6vh;
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2),
        -5px -5px 10px rgba(255, 255, 255, 1);
    transition: all .2s ease-out;
}

.el-menu--horizontal>.el-menu-item:nth-child(1).is-active {
    outline: 0 !important;
    color: var(-el-menu-tet-color) !important;
}

.el-menu--horizontal>.el-menu-item:nth-child(2):hover {
    outline: 0 !important;
    background-color: white !important;
    box-shadow: 0 0 0 rgba(0, 0, 0, 0.2),
        0 0 0 rgba(214, 216, 217, 0.954),
        inset 5px 5px 5px rgba(0, 0, 0, 0.1),
        inset -5px -5px 5px rgba(244, 255, 255, 0.92) !important;
}

.avatar {
    width: 2.5rem;
    height: 2.5rem;
    margin-left: 0.1rem;
    margin-right: 0.4rem;

    display: flex;
    justify-content: center;
    align-items: center;

    border-radius: 50%;
    object-fit: cover;
    background-color: rgb(214, 249, 249);
}

.avatar>img {
    width: 100%;
    height: 100%;
}

/* .username {
    margin-right: 1rem;
} */
</style>