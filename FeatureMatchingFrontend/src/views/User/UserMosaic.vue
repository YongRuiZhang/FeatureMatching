<template>
    <div class="">
        <el-row style="display: flex;align-items: center; margin-bottom: 20px;">
            <el-col :span="5">
                <el-text class="title">用户图像拼接记录</el-text>
            </el-col>
            <el-col :span="17" style="display: flex; align-items: center;">
                <el-input v-model="searchName" placeholder="通过 算法 查找"
                    style="width: 10vw; min-width: 180px; margin-right: 10px;" />
                <el-input v-model="searchMosaicDate" placeholder="通过 拼接日期 查找"
                    style="width: 11vw;  min-width: 180px;margin-right: 10px;" />
                <el-tooltip class="box-item" effect="dark" content="注意：查找功能只能查找当前页的记录。您要找的记录可能存在于其他页"
                    placement="bottom">
                    <el-icon>
                        <SvgIcon icon-name="icon-tishi" />
                    </el-icon>
                </el-tooltip>
            </el-col>
            <el-col :span="2" style="display: flex; justify-content: end;">
                <el-button type="danger" v-if="deleteIds.length > 0" @click="deleteSome">
                    <el-icon>
                        <SvgIcon icon-name="icon-shanchu" />
                    </el-icon>
                    &nbsp;批量删除
                </el-button>
            </el-col>
        </el-row>


        <div class="table-container">
            <el-table :data="filterTableData" style="width: 100%"
                :default-sort="{ prop: 'register_date', order: 'descending' }" @selection-change="handleSelectionChange"
                height="820" :table-layout="'auto'" :header-cell-style="{ 'text-align': 'center' }">
                <el-table-column type="selection" width="55" align="center" />
                <el-table-column fixed prop="id" label="记录 ID" width="120" show-overflow-tooltip />

                <el-table-column label="左图像" width="160" align="center">
                    <template #default="scope">
                        <el-image :src="scope.row.left_url" :preview-src-list="[scope.row.left_url]" hide-on-click-modal
                            preview-teleported style="aspect-ratio: 16 / 10;" />
                    </template>
                </el-table-column>
                <el-table-column label="右图像" width="160" align="center">
                    <template #default="scope">
                        <el-image :src="scope.row.right_url" :preview-src-list="[scope.row.right_url]"
                            hide-on-click-modal preview-teleported style="aspect-ratio: 16 / 10;" />
                    </template>
                </el-table-column>
                <el-table-column prop="algorithm_type" label="算法类型" width="160" align="center" :filters="[
                    { text: '稀疏', value: '稀疏' },
                    { text: '半稀疏', value: '半稀疏' },
                    { text: '稠密', value: '稠密' },
                ]" :filter-method="filterAlgorithm" filter-placement="bottom-end">
                    <template #default="scope">
                        <el-tag style="width: 80%;" :type="algorithmType(scope.row.algorithm_type)" disable-transitions>
                            {{ scope.row.algorithm_type }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="algorithm" label="算法" width="110" align="center" />

                <el-table-column prop="scene" label="场景" width="120" align="center" />
                <el-table-column label="可视化结果" width="200" align="center">
                    <template #default="scope">
                        <el-image :src="scope.row.save_path_url" :preview-src-list="[scope.row.save_path_url]"
                            hide-on-click-modal preview-teleported />
                    </template>
                </el-table-column>
                <el-table-column prop="elapsed_time" label="耗时(ms)" width="160" align="center" />
                <el-table-column prop="mosaic_date" label="拼接日期" width="180" align="center" />

                <el-table-column fixed="right" label="操作" width="140">
                    <template #default="scope">
                        <el-button link type="primary" size="small" @click="deleteSomeOne(scope.row)">
                            删除
                        </el-button>

                        <br />

                        <el-button link type="primary" size="small" @click="downloadViz(scope.row)">
                            下载可视化结果
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>
        </div>

        <el-pagination v-model:current-page="currentPage" v-model:page-size="pageSize" :page-sizes="[10, 15, 20, 25]"
            size="large" :disabled="false" :background="false" layout="total, sizes, prev, pager, next, jumper"
            :total="total" :hide-on-single-page="total == 0" @size-change="handleSizeChange"
            @current-change="handleCurrentChange" />
    </div>
</template>

<script lang='ts' setup name='UserMosaic'>
import { computed, onMounted, reactive, ref } from "vue"
import { useUserStore } from "@/stores/UserStore"
import type { mosaicRecordType, responseType } from "@/types"
import { ElMessage, ElMessageBox, ElNotification } from "element-plus"
import { jwt_refresh } from "@/utils/JWT"
import { useRouter } from 'vue-router'
import { storeToRefs } from "pinia"
import axios from "axios"

const router = useRouter()
const userStore = useUserStore()
let { user_id, access_token } = storeToRefs(userStore)
userStore.$subscribe((mutate, state) => {
    access_token.value = state.access_token
})
const headers = {
    Authorization: 'Bearer ' + access_token.value,
}

let currentPage = ref(1)
let pageSize = ref(10)
let total = ref(100)
let tableData = reactive([])
const filterAlgorithm = (value: string, row: mosaicRecordType) => {
    return row.algorithm === value
}
const algorithmType = (algorithm_type: string) => {
    switch (algorithm_type) {
        case '稀疏':
            return 'success'
        case '半稀疏':
            return 'primary'
        case '稠密':
            return 'danger'
    }
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
    await axios.get('http://127.0.0.1:5000/mosaic/total/' + user_id.value, { headers })
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
    await axios.get('http://127.0.0.1:5000/mosaic/' + user_id.value + '/' + pageSize.value + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: mosaicRecordType[] = []
                response.data.forEach((record: mosaicRecordType) => {
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,

                        'left_url': record.left_url,
                        'right_url': record.right_url,

                        'algorithm_type': record.algorithm_type,
                        'algorithm': record.algorithm,
                        'scene': record.scene,

                        'elapsed_time': record.elapsed_time,
                        'save_path': record.save_path,
                        'save_path_url': record.save_path_url,

                        'mosaic_date': new Date(record.mosaic_date as string).toISOString().replace('T', ' ').substring(0, 19),
                    })
                });

                tableData.splice(0, tableData.length);
                Object.assign(tableData, records)

                console.log(tableData);

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
    await axios.get('http://127.0.0.1:5000/mosaic/' + user_id.value + '/' + newPageSize + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: mosaicRecordType[] = []
                response.data.forEach((record: mosaicRecordType) => {
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,

                        'left_url': record.left_url,
                        'right_url': record.right_url,

                        'algorithm_type': record.algorithm_type,
                        'algorithm': record.algorithm,
                        'scene': record.scene,

                        'elapsed_time': record.elapsed_time,
                        'save_path': record.save_path,
                        'save_path_url': record.save_path_url,

                        'mosaic_date': new Date(record.mosaic_date as string).toISOString().replace('T', ' ').substring(0, 19),
                    })
                });

                tableData.splice(0, tableData.length);
                Object.assign(tableData, records)
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
    await axios.get('http://127.0.0.1:5000/mosaic/' + user_id.value + '/' + pageSize.value + '/' + newPage, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: mosaicRecordType[] = []
                response.data.forEach((record: mosaicRecordType) => {
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,

                        'left_url': record.left_url,
                        'right_url': record.right_url,

                        'algorithm_type': record.algorithm_type,
                        'algorithm': record.algorithm,
                        'scene': record.scene,

                        'elapsed_time': record.elapsed_time,
                        'save_path': record.save_path,
                        'save_path_url': record.save_path_url,

                        'mosaic_date': new Date(record.mosaic_date as string).toISOString().replace('T', ' ').substring(0, 19),
                    })
                });

                tableData.splice(0, tableData.length);
                Object.assign(tableData, records)
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
        }).catch((error: any) => {
            if (error.response.status == 401 && error.response.data.msg == "Token has expired") {
                ElNotification.error({
                    title: '更新用户token中...',
                    message: '太久未登陆, token 已过期, 稍后重试'
                })
                jwt_refresh(router)
            }
        })
}
let searchName = ref('')
let searchMosaicDate = ref('')
const filterTableData = computed(() =>
    tableData.filter(
        (data: mosaicRecordType) =>
            (!searchName.value ||
                data.algorithm.toLowerCase().includes(searchName.value.toLowerCase())) &&
            (!searchMosaicDate.value ||
                (data.mosaic_date as string).toLowerCase().includes(searchMosaicDate.value.toLowerCase()))
    )
)

let deleteIds = ref([])
const handleSelectionChange = (records: mosaicRecordType[]) => {
    deleteIds.value = []
    records.forEach(record => {
        deleteIds.value.push(record.id as never)
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
        axios.delete('http://127.0.0.1:5000/mosaic/', { data: { 'deleteIds': deleteIds.value, 'user_id': user_id.value }, headers })
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
const deleteSomeOne = async (record: mosaicRecordType) => {
    ElMessageBox.confirm(
        '将要删除 ' + record.id + ' 的记录，是否继续?',
        '警告',
        {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        axios.delete('http://127.0.0.1:5000/mosaic/' + record.id + '/' + user_id.value, { headers })
            .then((res) => {
                let response: responseType = res.data

                if (response.code == 200) {
                    getTotal()
                    getInfo()
                    ElNotification.success({
                        title: '删除成功！',
                        message: '成功删除 ' + record.id + ' 的记录',
                    });
                } else {
                    ElNotification.error({
                        title: response.msg,
                        message: response.data,
                    });
                }
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

// 下载
const downloadViz = async (record: mosaicRecordType) => {
    let post_info = {
        'dfilepath': record.save_path,
        'type': 'image'
    }
    await axios.post('http://127.0.0.1:5000/mosaic/download', post_info, {
        responseType: 'blob'
    }).then((response) => {
        if (response.status != 200) {
            ElNotification.error(
                '下载失败状态码错误'
            )
        } else {
            // 检查 Content-Disposition
            const contentDisposition = response.headers['content-disposition'];
            const filename = contentDisposition ? contentDisposition.split('filename=')[1].replace(/['"]/g, '') : 'None.npy';

            // 创建一个隐藏的 a 标签用于下载
            const url = window.URL.createObjectURL(new Blob([response.data]))

            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    }).catch((error) => {
        ElNotification.error('下载失败:', error);
    });
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
</style>