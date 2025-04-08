<template>
    <div class="">
        <el-row style="display: flex;align-items: center; margin-bottom: 20px;">
            <el-col :span="5">
                <el-text class="title">用户图像匹配记录</el-text>
            </el-col>
            <el-col :span="17" style="display: flex; align-items: center;">
                <el-input v-model="searchName" placeholder="通过 算法 查找"
                    style="width: 10vw; min-width: 180px; margin-right: 10px;" />
                <el-input v-model="searchMatchingDate" placeholder="通过 匹配日期 查找"
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

                <el-table-column fixed prop="origin_type" label="数据源类型" width="160" align="center" :filters="[
                    { text: '图片对', value: '两张图片' },
                    { text: '多张图片', value: '多张图片' },
                    { text: '视频', value: '视频' },
                ]" :filter-method="filterOriginType" filter-placement="bottom-end">
                    <template #default="scope">
                        <el-tag style="width: 80%;" :type="originType(scope.row.origin_type)" disable-transitions>
                            {{ scope.row.origin_type }}
                        </el-tag>
                    </template>
                </el-table-column>

                <el-table-column label="数据源" width="160" align="center">
                    <template #default="scope">
                        <el-image :src="scope.row.viz_path[0]" :preview-src-list="scope.row.viz_path"
                            hide-on-click-modal preview-teleported v-if="scope.row.origin_type != '视频'"
                            style="aspect-ratio: 16 / 10;" />
                        <video autoplay loop controls v-if="scope.row.origin_type === '视频'"
                            style="height: 100%; width: 100%;">
                            <source :src="scope.row.viz_path" type="video/mp4">
                            结果为视频，您的浏览器不支持 video 标签。
                        </video>
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

                <el-table-column prop="config" label="配置参数" width="200" align="left">
                    <template #default="scope">
                        <p v-for="c in scope.row.config">{{ c }}</p>
                    </template>
                </el-table-column>
                <el-table-column label="可视化结果" width="200" align="center">
                    <template #default="scope">
                        <el-image :src="scope.row.save_path_url" :preview-src-list="[scope.row.save_path_url]"
                            hide-on-click-modal preview-teleported v-if="scope.row.origin_type == '两张图片'" />
                        <video autoplay loop controls
                            v-if="scope.row.origin_type === '多张图片' || scope.row.origin_type === '视频'"
                            style="height: 100%; width: 100%;">
                            <source :src="scope.row.save_path_url" type="video/mp4">
                            结果为视频，您的浏览器不支持 video 标签。
                        </video>
                    </template>
                </el-table-column>
                <el-table-column prop="elapsed_time" label="耗时(ms)" width="160" align="center" />
                <el-table-column prop="matching_date" label="匹配日期" width="180" align="center" />

                <el-table-column fixed="right" label="操作" width="140">
                    <template #default="scope">
                        <el-button link type="primary" size="small" @click="deleteSomeOne(scope.row)">
                            删除
                        </el-button>

                        <br />

                        <el-button link type="primary" size="small" @click="downloadViz(scope.row)">
                            下载可视化结果
                        </el-button>

                        <br v-if="scope.row.save_matches_path != null && scope.row.save_matches_path != ''" />

                        <el-button link type="primary" size="small" @click="downloadMatches(scope.row)"
                            v-if="scope.row.save_matches_path != null && scope.row.save_matches_path != ''">
                            下载 Matches
                        </el-button>

                        <br v-if="scope.row.save_poses_path != null && scope.row.save_poses_path != ''" />

                        <el-button link type="primary" size="small" @click="downloadPose(scope.row)"
                            v-if="scope.row.save_poses_path != null && scope.row.save_poses_path != ''">
                            下载 Poses
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

<script lang='ts' setup name='UserMatching'>
import { computed, onMounted, reactive, ref } from "vue"
import { useUserStore } from "@/stores/UserStore"
import type { matchingRecordType, responseType } from "@/types"
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
const filterOriginType = (value: string, row: matchingRecordType) => {
    return row.origin_type === value
}
const originType = (origin_type: string) => {
    switch (origin_type) {
        case '两张图片':
            return 'success'
        case '多张图片':
            return 'primary'
        case '视频':
            return 'danger'
    }
}
const filterAlgorithm = (value: string, row: matchingRecordType) => {
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
    await axios.get('http://127.0.0.1:5000/matching/total/' + user_id.value, { headers })
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
    await axios.get('http://127.0.0.1:5000/matching/' + user_id.value + '/' + pageSize.value + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: matchingRecordType[] = []
                response.data.forEach((record: matchingRecordType) => {
                    let config = []
                    if (record.config == '{}') {
                        config.push('无参数')
                    } else {
                        let c = JSON.parse(record.config as string)
                        Object.keys(c).forEach(key => {
                            config.push(`${key}: ${c[key]}`)
                        });
                    }
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,

                        'viz_path': JSON.parse(record.viz_path),
                        'origin_type': record.origin_type,

                        'algorithm_type': record.algorithm_type,
                        'algorithm': record.algorithm,
                        'config': config,

                        'elapsed_time': record.elapsed_time,
                        'save_path': record.save_path,
                        'save_path_url': record.save_path_url,
                        'save_matches_path': record.save_matches_path,
                        'save_poses_path': record.save_poses_path,

                        'matching_date': new Date(record.matching_date as string).toISOString().replace('T', ' ').substring(0, 19),
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
    await axios.get('http://127.0.0.1:5000/matching/' + user_id.value + '/' + newPageSize + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: matchingRecordType[] = []
                response.data.forEach((record: matchingRecordType) => {
                    let config = []
                    if (record.config == '{}') {
                        config.push('无参数')
                    } else {
                        let c = JSON.parse(record.config as string)
                        Object.keys(c).forEach(key => {
                            config.push(`${key}: ${c[key]}`)
                        });
                    }
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,

                        'viz_path': JSON.parse(record.viz_path),
                        'origin_type': record.origin_type,

                        'algorithm_type': record.algorithm_type,
                        'algorithm': record.algorithm,
                        'config': config,

                        'elapsed_time': record.elapsed_time,
                        'save_path': record.save_path,
                        'save_path_url': record.save_path_url,
                        'save_matches_path': record.save_matches_path,
                        'save_poses_path': record.save_poses_path,

                        'matching_date': new Date(record.matching_date as string).toISOString().replace('T', ' ').substring(0, 19),

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
    await axios.get('http://127.0.0.1:5000/matching/' + user_id.value + '/' + pageSize.value + '/' + newPage, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: matchingRecordType[] = []
                response.data.forEach((record: matchingRecordType) => {
                    let config = []
                    if (record.config == '{}') {
                        config.push('无参数')
                    } else {
                        let c = JSON.parse(record.config as string)
                        Object.keys(c).forEach(key => {
                            config.push(`${key}: ${c[key]}`)
                        });
                    }
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,

                        'viz_path': JSON.parse(record.viz_path),
                        'origin_type': record.origin_type,

                        'algorithm_type': record.algorithm_type,
                        'algorithm': record.algorithm,
                        'config': config,

                        'elapsed_time': record.elapsed_time,
                        'save_path': record.save_path,
                        'save_path_url': record.save_path_url,
                        'save_matches_path': record.save_matches_path,
                        'save_poses_path': record.save_poses_path,

                        'matching_date': new Date(record.matching_date as string).toISOString().replace('T', ' ').substring(0, 19),

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
let searchMatchingDate = ref('')
const filterTableData = computed(() =>
    tableData.filter(
        (data: matchingRecordType) =>
            (!searchName.value ||
                data.algorithm.toLowerCase().includes(searchName.value.toLowerCase())) &&
            (!searchMatchingDate.value ||
                (data.matching_date as string).toLowerCase().includes(searchMatchingDate.value.toLowerCase()))
    )
)

let deleteIds = ref([])
const handleSelectionChange = (records: matchingRecordType[]) => {
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
        axios.delete('http://127.0.0.1:5000/matching/', { data: { 'deleteIds': deleteIds.value, 'user_id': user_id.value }, headers })
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
const deleteSomeOne = async (record: matchingRecordType) => {
    ElMessageBox.confirm(
        '将要删除 ' + record.id + ' 的记录，是否继续?',
        '警告',
        {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        axios.delete('http://127.0.0.1:5000/matching/' + record.id + '/' + user_id.value, { headers })
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

async function downloadViz(record: matchingRecordType) {
    let post_info = {
        'dfilepath': record.save_path,
        'type': 'image'
    }
    download(post_info)
}
async function downloadMatches(record: matchingRecordType) {
    let post_info = {
        'dfilepath': record.save_matches_path,
        'type': 'numpy'
    }
    download(post_info)
}
async function downloadPose(record: matchingRecordType) {
    let post_info = {
        'dfilepath': record.save_poses_path,
        'type': 'numpy'
    }
    download(post_info)
}
const download = async (post_info: any) => {
    await axios.post('http://127.0.0.1:5000/matching/download', post_info, {
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