<template>
    <div class="" style="height: 100%;display: flex; justify-content: center; align-items: center; font-size: 55px;">
        用户首页
    </div>
</template>

<script lang='ts' setup name='UserHome'>
import { onMounted } from "vue"
import { useUserStore } from "@/stores/UserStore";
import { useRouter } from "vue-router";
import { ElNotification } from "element-plus";

const router = useRouter()
const userStore = useUserStore()
let { username, gender, role } = userStore

console.log(username, gender, role);

onMounted(() => {
    if (username == '登陆' || gender == '' || role == '') {
        ElNotification.error({
            title: '未登陆！',
            message: '请先登陆'
        })
        router.push('/login')
    }
})


</script>

<style scoped></style>