<template>
    <div class="">
        <el-row style="display: flex;align-items: center;">
            <el-col :span="4">
                <el-text class="title">用户信息管理</el-text>
            </el-col>
            <el-col :span="17" style="display: flex; align-items: center;">
                <el-input v-model="searchName" placeholder="通过 User Name 查找"
                    style="width: 10vw; min-width: 180px; margin-right: 10px;" />
                <el-input v-model="searchEmail" placeholder="通过 Email 查找"
                    style="width: 9vw; min-width: 160px; margin-right: 10px;" />
                <el-input v-model="searchRegisterDate" placeholder="通过 Register Date 查找"
                    style="width: 11vw;  min-width: 180px;margin-right: 10px;" />
                <el-input v-model="searchBirthday" placeholder="通过 Birthday 查找"
                    style="width: 10vw; min-width: 160px; margin-right: 10px;" />
                <el-tooltip class="box-item" effect="dark" content="注意：查找功能只能查找当前页的记录。您要找的记录可能存在于其他页"
                    placement="bottom">
                    <el-icon>
                        <SvgIcon icon-name="icon-tishi" />
                    </el-icon>
                </el-tooltip>
            </el-col>
            <el-col :span="3" style="display: flex; justify-content: end;">
                <el-button type="danger" v-if="deleteIds.length > 0" @click="deleteSome">
                    <el-icon>
                        <SvgIcon icon-name="icon-shanchu" />
                    </el-icon>
                    &nbsp;批量删除
                </el-button>
                <el-button type="primary" @click="addDialogVisible = true">
                    <el-icon>
                        <SvgIcon icon-name="icon-zengjia" />
                    </el-icon>
                    &nbsp;新增
                </el-button>
            </el-col>
        </el-row>

        <el-dialog v-model="addDialogVisible" title="添加用户..." width="450" align-center center>
            <div class="addForm">
                <el-form :model="addForm" label-width="auto" style="max-width: 30vw" label-position="right">
                    <el-text></el-text>
                    <el-form-item label="用户名：" prop="username" :rules="[
                        { required: true, message: '用户名 是必须的', trigger: 'blur' },
                    ]">
                        <el-input v-model="addForm.username" placeholder="用户名" />
                    </el-form-item>
                    <el-form-item label="密码：">
                        <el-input disabled v-model="addForm.password" style="width: 90%" placeholder="123456" />
                        <el-tooltip class="box-item" effect="dark" content="密码默认为123456,无需修改" placement="left">
                            <el-icon>
                                <SvgIcon icon-name="icon-tishi" />
                            </el-icon>
                        </el-tooltip>
                    </el-form-item>

                    <el-form-item label="邮箱：">
                        <el-input v-model="addForm.email" placeholder="邮箱">
                            <template #append>
                                <el-select v-model="addForm.select" style="width: 120px">
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
                        <el-date-picker v-model="addForm.birthday" type="dates" style="width: 100%;"
                            placeholder="请选择生日" />
                    </el-form-item>
                    <el-form-item size="large" label="性别：">
                        <el-radio-group v-model="addForm.gender">
                            <el-radio value="male" size="large">男</el-radio>
                            <el-radio value="female" size="large">女</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item size="large" label="管理员：">
                        <el-switch v-model="addForm.role" class="mb-2" active-text="是" inactive-text="否" />
                    </el-form-item>
                </el-form>
            </div>

            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="addDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="onSubmitAdd">
                        添加
                    </el-button>
                </div>
            </template>
        </el-dialog>


        <div class="table-container">
            <el-table :data="filterTableData" style="width: 100%"
                :default-sort="{ prop: 'register_date', order: 'descending' }" @selection-change="handleSelectionChange"
                height="800" :table-layout="'auto'">
                <el-table-column type="selection" width="55" />
                <el-table-column fixed prop="id" label="User ID" width="160" show-overflow-tooltip />
                <el-table-column fixed prop="username" label="User Name" width="160" />
                <el-table-column prop="gender" label="Gender" width="140" :filters="[
                    { text: 'Male', value: 'male' },
                    { text: 'Female', value: 'female' },
                ]" :filter-method="filterGender" filter-placement="bottom-end">
                    <template #default="scope">
                        <el-tag style="width: 80%;" :type="scope.row.gender === 'male' ? 'primary' : 'success'"
                            disable-transitions>{{
                                scope.row.gender }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="role" label="Role" width="140" :filters="[
                    { text: 'Admin', value: 'admin' },
                    { text: 'Guest', value: 'guest' },
                ]" :filter-method="filterRole" filter-placement="bottom-end">
                    <template #default="scope">
                        <el-tag style="width: 80%;" :type="scope.row.role === 'admin' ? 'primary' : 'success'"
                            disable-transitions>{{
                                scope.row.role }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="register_date" label="Register Date" width="240" sortable />
                <el-table-column prop="email" label="Email" width="240" />
                <el-table-column prop="birthday" label="Birthday" width="200" />
                <el-table-column fixed="right" label="Operations" min-width="160">
                    <template #default="scope">
                        <el-button link type="primary" size="large" @click="editSomeOne(scope.row)">Edit</el-button>
                        <el-button link type="primary" size="large" @click="deleteSomeOne(scope.row)">Delete</el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[20, 25, 30, 35]"
            size="large" :disabled="false" :background="false" layout="total, sizes, prev, pager, next, jumper"
            :total="total" :hide-on-single-page="total < pageSize" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />

        <el-dialog v-model="centerDialogVisible" :title="'用户：' + editForm.username" width="300" align-center center>
            <div class="editForm">
                <el-form :model="editForm" label-width="auto" style="max-width: 40vw" label-position="left">
                    <el-text></el-text>
                    <el-form-item size="small" label="性别：">
                        <el-radio-group v-model="editForm.gender">
                            <el-radio value="male" size="small" border>男</el-radio>
                            <el-radio value="female" size="small" border>女</el-radio>
                        </el-radio-group>
                    </el-form-item>
                    <el-form-item size="small" label="管理员：">
                        <el-radio-group v-model="editForm.role">
                            <el-radio value="admin" size="small" border>是</el-radio>
                            <el-radio value="guest" size="small" border>否</el-radio>
                        </el-radio-group>
                    </el-form-item>
                </el-form>
            </div>

            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="centerDialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="onSubmitEdit">
                        修改
                    </el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script lang='ts' setup name=''>
import axios from "axios"
import { computed, onMounted, reactive, ref } from "vue"
import { useUserStore } from "@/stores/UserStore"
import type { responseType, userType } from "@/types"
import { ElMessage, ElMessageBox, ElNotification } from "element-plus"
import { jwt_refresh } from "@/utils/JWT"
import { useRouter } from 'vue-router'
import { storeToRefs } from "pinia"
import SvgIcon from "@/components/SvgIcon.vue"

const router = useRouter()
const userStore = useUserStore()
let { access_token } = storeToRefs(userStore)
userStore.$subscribe((mutate, state) => {
    access_token.value = state.access_token
})
const headers = {
    Authorization: 'Bearer ' + access_token.value,
}

let currentPage = ref(1)
let pageSize = ref(20)
let total = ref(100)
const tableData = reactive([])
const filterGender = (value: string, row: userType) => {
    return row.gender === value
}
const filterRole = (value: string, row: userType) => {
    return row.role === value
}

let { username, gender, role } = userStore
onMounted(async () => {
    if (username == '登陆' || gender == '' || role == '') {
        ElNotification.error({
            title: '未登陆！',
            message: '请先登陆'
        })
        router.push('/login')
    } else {
        try {
            getTotal()
            getInfo()
        } catch (error) {
            console.error('请求失败:', error)
        }
    }
})

// 查
const getTotal = async () => {
    await axios.get('http://127.0.0.1:5000/user/total', { headers })
        .then((res) => {
            let response: responseType = res.data

            if (response.code === 200) {
                total.value = response.data
            } else if (response.code === 300) {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
                router.push('/user')
            } else if (response.code === 301 || response.code === 302 || response.code === 303) {
                ElNotification.error({
                    title: response.msg
                })
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
            }
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
const getInfo = async () => {
    await axios.get('http://127.0.0.1:5000/user/' + pageSize.value + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let users: userType[] = []
                response.data.forEach((user: userType) => {
                    users.push({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email !== '' ? user.email : '用户未设置',
                        'gender': user.gender,
                        'birthday': user.birthday !== null ? new Date(user.birthday as string).toISOString().split('T')[0] : '用户未设置',
                        'role': user.role,
                        'register_date': new Date(user.register_date as string).toISOString().replace('T', ' ').substring(0, 19)
                    })
                });

                tableData.splice(0, tableData.length);
                Object.assign(tableData, users)
            } else if (response.code === 300) {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
                router.push('/user')
            } else if (response.code === 301 || response.code === 302 || response.code === 303) {
                ElNotification.error({
                    title: response.msg
                })
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
            }
        })
}

const handleSizeChange = async (newPageSize: number) => {
    await axios.get('http://127.0.0.1:5000/user/' + newPageSize + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let users: userType[] = []
                response.data.forEach((user: userType) => {
                    users.push({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email !== '' ? user.email : '用户未设置',
                        'gender': user.gender,
                        'birthday': user.birthday !== null ? new Date(user.birthday as string).toISOString().split('T')[0] : '用户未设置',
                        'role': user.role,
                        'register_date': new Date(user.register_date as string).toISOString().replace('T', ' ').substring(0, 19)
                    })
                });

                tableData.splice(0, tableData.length);
                Object.assign(tableData, users)
            } else if (response.code === 300) {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
                router.push('/user')
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
                router.push('/login')
            }
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
const handleCurrentChange = async (newPage: number) => {
    await axios.get('http://127.0.0.1:5000/user/' + pageSize.value + '/' + newPage, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let users: userType[] = []
                response.data.forEach((user: userType) => {
                    users.push({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email !== '' ? user.email : '用户未设置',
                        'gender': user.gender,
                        'birthday': user.birthday !== null ? new Date(user.birthday as string).toISOString().split('T')[0] : '用户未设置',
                        'role': user.role,
                        'register_date': new Date(user.register_date as string).toISOString().replace('T', ' ').substring(0, 19)
                    })
                });
                tableData.splice(0, tableData.length);
                Object.assign(tableData, users)
            } else if (response.code === 300) {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
                router.push('/user')
            } else if (response.code === 301 || response.code === 302 || response.code === 303) {
                ElNotification.error({
                    title: response.msg
                })
                router.push('/login')
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
            }
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
// 联合查找
let searchName = ref('')
let searchEmail = ref('')
let searchRegisterDate = ref('')
let searchBirthday = ref('')
const filterTableData = computed(() =>
    tableData.filter(
        (data: userType) =>
            (!searchName.value ||
                data.username.toLowerCase().includes(searchName.value.toLowerCase())) &&
            (!searchEmail.value ||
                data.email.toLowerCase().includes(searchEmail.value.toLowerCase())) &&
            (!searchRegisterDate.value ||
                (data.register_date as string).toLowerCase().includes(searchRegisterDate.value.toLowerCase())) &&
            (!searchBirthday.value ||
                (data.birthday as string).toLowerCase().includes(searchBirthday.value.toLowerCase()))
    )
)


// 增加
let addDialogVisible = ref(false)
let addForm = reactive({
    username: '',
    email: '',
    select: '@qq.com',
    gender: 'male',
    birthday: '',
    role: false,
    password: '123456',
})
const onSubmitAdd = async () => {
    if (addForm.username === '') {
        ElNotification.error({
            title: '添加失败！',
            message: '用户名不能为空！'
        })
        addDialogVisible.value = false
    } else {
        const addUserForm = {
            'username': addForm.username,
            'email': addForm.email + addForm.select,
            'birthday': addForm.birthday,
            'gender': addForm.gender,
            'password': addForm.password,
            'role': addForm.role === false ? 'guest' : 'admin'
        }
        axios.post('http://127.0.0.1:5000/user/', addUserForm, { headers })
            .then((res) => {
                let response: responseType = res.data

                if (response.code === 300) {
                    ElNotification.error({
                        title: response.msg,
                        message: response.data
                    })
                } else if (response.code === 200) {
                    ElNotification.success(response.msg)
                }
                addDialogVisible.value = false
                getTotal()
                getInfo()
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
    Object.assign(addForm, {
        username: '',
        email: '',
        select: '@qq.com',
        gender: 'male',
        birthday: '',
        role: false,
        password: '123456',
    })

}

// 改
let centerDialogVisible = ref(false)
let editForm = reactive<userType>({
    id: '',
    username: '',
    email: '',
    gender: 'male',
    birthday: '',
    role: 'guest',
})
const editSomeOne = async (user: userType) => {
    centerDialogVisible.value = true
    Object.assign(editForm, user)
}
const onSubmitEdit = async () => {
    await axios.put('http://127.0.0.1:5000/user/role', editForm, {
        headers
    }).then((res) => {
        let response: responseType = res.data

        let content = response.data.content
        let modifySuccess = ""
        content.forEach((c: string) => {

            if (c === '性别') {
                userStore.setGender(editForm.gender)
            } else if (c === '身份') {
                userStore.setRole(editForm.role as string)
            }

            modifySuccess += c + " "
        });
        if (content.length > 0) {
            getInfo()
            ElNotification.success({
                title: response.msg,
                message: '成功修改：' + editForm.username + ' 的 ' + modifySuccess
            })
        } else {
            ElNotification.info({
                title: '未修改任何信息'
            })
        }
    }).catch((error) => {
        if (error.response.status == 401 && error.response.data.msg == "Token has expired") {
            ElNotification.error({
                title: '更新用户token中...',
                message: '太久未登陆, token 已过期, 稍后重试'
            })
            jwt_refresh(router)
        }
    })
    centerDialogVisible.value = false
}

const deleteSomeOne = async (user: userType) => {
    await axios.delete('http://127.0.0.1:5000/user/', { data: { 'uid': user.id, 'username': user.username }, headers },
    )
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                ElNotification.success({
                    title: response.msg,
                    message: response.data
                })
                getTotal()
                getInfo()
            } else if (response.code === 300) {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
                router.push('/user')
            } else if (response.code === 301 || response.code === 302 || response.code === 303) {
                ElNotification.error({
                    title: response.msg
                })
                router.push('/login')
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
            }
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

// 删
let deleteIds = ref([])
const handleSelectionChange = (users: userType[]) => {
    deleteIds.value = []
    users.forEach(user => {
        deleteIds.value.push(user.id as never)
    });
}
const deleteSome = () => {
    ElMessageBox.confirm(
        '将要删除' + deleteIds.value.length + '条记录，是否继续?',
        '警告',
        {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        axios.delete('http://127.0.0.1:5000/user/some', { data: { 'deleteIds': deleteIds.value }, headers })
            .then((res) => {
                let response: responseType = res.data

                if (response.code == 200) {
                    getTotal()
                    getInfo()
                    ElNotification.success({
                        title: '删除成功！',
                        message: '成功删除 ' + deleteIds.value.length + ' 条记录',
                    });
                } else {
                    ElNotification.error({
                        title: response.msg,
                        message: response.data,
                    });
                }
            })
    }).catch((err) => {
        ElMessage({
            type: 'info',
            message: '取消操作',
        });
    })
}

</script>

<style scoped>
.title {
    font-size: 26px;
    font-weight: 600;
    color: rgb(2, 79, 79)
}

.table-container {
    height: 100%;
    display: flex;
    flex-direction: column;
}

.addForm {
    display: flex;
    justify-content: center;
}

.editForm {
    display: flex;
    justify-content: center;
}
</style>