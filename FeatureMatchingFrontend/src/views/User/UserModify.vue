<template>
    <div class="wrap">
        <div class="contianer">
            <div class="myform">
                <el-form :model="form" label-width="auto" style="max-width: 40vw" label-position="left">
                    <div class="userLogo">
                        <div class="avatar">
                            <SvgIcon v-if="gender == 'male'" icon-name="icon-01" />
                            <SvgIcon v-if="gender == 'female'" icon-name="icon-34" />
                        </div>
                        <el-text style="font-size: 30px;"> {{ username }} </el-text>
                    </div>

                    <el-form-item label="邮箱：">
                        <el-input v-model="form.email" placeholder="邮箱">
                            <template #append>
                                <el-select v-model="form.select" style="width: 140px">
                                    <el-option label="@qq.com" value="@qq.com" />
                                    <el-option label="@gmail.com" value="@gmail.com" />
                                    <el-option label="@163.com" value="@163.com" />
                                    <el-option label="@edu.com" value="@edu.com" />
                                </el-select>
                            </template>
                        </el-input>
                    </el-form-item>
                    <el-form-item size="large" label="生日：">
                        <span class="demonstration" format="yyyy-MM-dd" value-format="yyyy-MM-dd"></span>
                        <el-date-picker v-model="form.birthday" type="dates" style="width: 100%;" placeholder="请选择生日" />
                    </el-form-item>
                    <el-form-item size="large" label="性别：">
                        <el-radio-group v-model="form.gender">
                            <el-radio value="male" size="large" border>男</el-radio>
                            <el-radio value="female" size="large" border>女</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-row>
                        <el-col :offset="4">
                            <el-text v-if="warning" type="danger" size="large">
                                您目前使用的是默认密码，不安全！！ 请重新设置密码！！
                            </el-text>
                        </el-col>
                    </el-row>
                    <el-form-item size="large" label="密码：">
                        <el-input v-model="form.password" type="password" placeholder="输入修改后的密码" show-password />
                    </el-form-item>
                    <el-form-item size="large" label="确认密码：">
                        <el-input v-model="form.confirmPassword" type="password" placeholder="重复修改后的密码" show-password />
                    </el-form-item>
                    <el-form-item style="display: flex; justify-self: center; align-items: center;">
                        <el-button type="primary" style="width: 30vw;" @click="onSubmit">修改</el-button>
                    </el-form-item>
                </el-form>
            </div>
        </div>
    </div>
</template>

<script lang='ts' setup name='UserModify'>
import type { responseType } from '@/types';
import { jwt_refresh } from '@/utils/JWT';
import axios from 'axios';
import { ElMessage, ElNotification } from 'element-plus';
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/UserStore';
import { storeToRefs } from 'pinia';

const router = useRouter()
const userStore = useUserStore()
let { username, gender } = storeToRefs(userStore)
let { access_token } = userStore
userStore.$subscribe((mutation, state) => {
    console.log('State changed:', mutation, state)
    username.value = state.username
    gender.value = state.gender
})

let form = reactive({
    email: '',
    select: '@qq.com',
    birthday: '',
    gender: '',
    password: '',
    confirmPassword: ''
})

let warning = ref(false)

let { role } = userStore
onMounted(async () => {
    if (username.value == '登陆' || gender.value == '' || role == '') {
        ElNotification.error({
            title: '未登陆！',
            message: '请先登陆'
        })
        router.push('/login')
    } else {
        try {
            getInfo()
        } catch (error) {
            ElMessage.error('请求失败' + error)
        }
    }
})

const getInfo = async () => {
    const headers = {
        Authorization: 'Bearer ' + access_token,
    }
    await axios.get('http://127.0.0.1:5000/user/' + username.value, { headers }).then((res) => {
        let response: responseType = res.data

        let originEmail = ''
        let originSelect = ''

        if (response.data.email != '') {
            originEmail = (response.data.email as string).split('@')[0]
            originSelect = '@' + (response.data.email as string).split('@')[1]
        }
        let resBirthday = response.data.birthday
        let originBirthday = ['']
        if (resBirthday != null) {
            originBirthday = [new Date(resBirthday).toISOString().split('T')[0]]
        }
        warning.value = response.data.warning

        let originGender = response.data.gender
        Object.assign(form, {
            'birthday': originBirthday,
            'gender': originGender,
            'email': originEmail,
            'select': originSelect
        })
    }).catch((error) => {
        if (error.response.status == 401 && error.response.data.msg == "Token has expired") {
            ElNotification.error({
                title: '更新用户token中...',
                message: '太久未登陆, token 已过期, 稍后重试'
            })
            jwt_refresh(router)
        }
    })
}



const onSubmit = async () => {
    if (form.password != form.confirmPassword) {
        ElMessage.error('两次密码不同')
    } else {
        const modifyForm = {
            'username': username.value,
            'email': form.email + form.select,
            'birthday': form.birthday,
            'gender': form.gender,
            'password': form.password,
            'confirmPassword': form.confirmPassword
        }
        const access_token = localStorage.getItem('access_token')
        const headers = {
            Authorization: 'Bearer ' + access_token,
        }

        await axios.put('http://127.0.0.1:5000/user/', modifyForm, {
            headers
        }).then((res) => {
            let response: responseType = res.data
            if (response.code === 500) {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
            } else {
                let content = response.data.content
                let modifySuccess = ""
                if (content != null || content.length > 0) {
                    content.forEach((c: string) => {

                        if (c === '性别') {
                            userStore.setGender(modifyForm.gender)
                        }

                        modifySuccess += c + " "
                    });
                    ElNotification.success({
                        title: response.msg,
                        message: '成功修改：' + modifySuccess
                    })
                } else {
                    ElNotification.info({
                        title: '未修改任何信息'
                    })
                }
            }
        }).catch((error) => {
            console.log(error)
            if (error.response.status == 401 && error.response.data.msg == "Token has expired") {
                ElNotification.error({
                    title: '更新用户token中...',
                    message: '太久未登陆, token 已过期, 稍后重试'
                })
                jwt_refresh(router)
            }
        })
    }
    getInfo()
}

</script>

<style scoped>
.wrap {
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.contianer {
    height: 75%;
    width: 70%;
    /* background-color: rgb(255, 239, 219); */
    box-shadow: 10px 10px 10px rgb(245, 247, 224, 0.95), -5px -5px 5px rgba(179, 255, 87, 0.4);

    display: flex;
    justify-content: center;
    align-items: center;
}

.userLogo {
    height: 10rem;
    transform: translateY(-30%);

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.avatar {
    width: 10rem;
    height: 10rem;
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

.el-radio {
    background-color: rgb(238, 255, 255) !important;
}
</style>