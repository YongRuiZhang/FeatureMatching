<template>
    <div class="">
        <el-row style="display: flex;align-items: center; margin-bottom: 20px;">
            <el-col :span="5">
                <el-text class="title">用户特征检测记录</el-text>
            </el-col>
            <el-col :span="17" style="display: flex; align-items: center;">
                <el-input v-model="searchName" placeholder="通过 Image Name 查找"
                    style="width: 10vw; min-width: 180px; margin-right: 10px;" />
                <el-input v-model="searchDetectionDate" placeholder="通过 Detection Date 查找"
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
                height="820" :table-layout="'auto'">
                <el-table-column type="selection" width="55" />
                <el-table-column fixed prop="id" label="Record ID" width="90" show-overflow-tooltip />

                <el-table-column fixed prop="origin_image_name" label="Image" width="100" />
                <el-table-column label="Origin Image" width="120">
                    <template #default="scope">
                        <el-image :src="scope.row.origin_image_url" :preview-src-list="[scope.row.origin_image_url]"
                            hide-on-click-modal preview-teleported></el-image>
                    </template>
                </el-table-column>
                <el-table-column prop="image_width" label="Width" width="80" />
                <el-table-column prop="image_height" label="Height" width="80" />
                <el-table-column prop="algorithm" label="Algorithm" width="140" :filters="[
                    { text: 'Harris', value: 'Harris' },
                    { text: 'Shi-Tomasi', value: 'Shi-Tomasi' },
                    { text: 'ORB', value: 'ORB' },
                    { text: 'SIFT', value: 'SIFT' },
                    { text: 'SuperPoint', value: 'SuperPoint' },
                ]" :filter-method="filterAlgorithm" filter-placement="bottom-end">
                    <template #default="scope">
                        <el-tag style="width: 80%;" :type="algorithmType(scope.row.algorithm)" disable-transitions>{{
                            scope.row.algorithm }}</el-tag>
                    </template>
                </el-table-column>
                <el-table-column prop="config" label="Config" width="240" />
                <el-table-column label="Result Image" width="120">
                    <template #default="scope">
                        <el-image :src="scope.row.res_image_url" :preview-src-list="[scope.row.res_image_url]"
                            hide-on-click-modal preview-teleported></el-image>
                    </template>
                </el-table-column>
                <el-table-column prop="res_kpts_num" label="Kpts Num" width="100" />
                <el-table-column prop="elapsed_time" label="Elapsed Time(ms)" width="160" />
                <el-table-column prop="detection_date" label="Detection Date" width="180" />

                <el-table-column fixed="right" label="Operations" width="140">
                    <template #default="scope">
                        <el-button link type="primary" size="small" @click="deleteSomeOne(scope.row)">
                            Delete
                        </el-button>
                        <br />
                        <el-button link type="primary" size="small" @click="downLoadKpts(scope.row)">
                            DownLoad Kpts
                        </el-button>
                        <br v-if="scope.row.res_scores_path != null && scope.row.res_scores_path != ''" />
                        <el-button link type="primary" size="small" @click="downLoadScores(scope.row)"
                            v-if="scope.row.res_scores_path != null && scope.row.res_scores_path != ''">
                            DownLoad Scores
                        </el-button>
                        <br v-if="scope.row.res_descriptors_path != null && scope.row.res_descriptors_path != ''" />
                        <el-button link type="primary" size="small" @click="downLoadDescriptors(scope.row)"
                            v-if="scope.row.res_descriptors_path != null && scope.row.res_descriptors_path != ''">
                            DownLoad Descriptors
                        </el-button>
                        <br />
                        <el-button link type="primary" size="small" @click="downLoadResImage(scope.row)">
                            DownLoad ResImg
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

<script lang='ts' setup name='UserDetection'>
import { computed, onMounted, reactive, ref } from "vue"
import { useUserStore } from "@/stores/UserStore"
import type { detectionRecordType, responseType } from "@/types"
import { ElMessage, ElMessageBox, ElNotification } from "element-plus"
import { jwt_refresh } from "@/utils/JWT"
import { useRouter } from 'vue-router'
import { storeToRefs } from "pinia"
import axios from "axios"
import { de } from "element-plus/es/locales.mjs"

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
const filterAlgorithm = (value: string, row: detectionRecordType) => {
    return row.algorithm === value
}
const algorithmType = (algorithm: string) => {
    switch (algorithm) {
        case 'Harris':
            return 'success'
        case 'Shi-Tomasi':
            return 'info'
        case 'ORB':
            return 'danger'
        case 'SIFT':
            return 'primary'
        case 'SuperPoint':
            return 'warning'
    }
}

// 查
const getTotal = async () => {
    await axios.get('http://127.0.0.1:5000/detection/total/' + user_id.value, { headers })
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
    await axios.get('http://127.0.0.1:5000/detection/' + user_id.value + '/' + pageSize.value + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data

            if (response.code === 200) {
                let records: detectionRecordType[] = []
                response.data.forEach((record: detectionRecordType) => {
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,
                        'origin_image_name': record.origin_image_name,
                        'origin_image_url': record.origin_image_url,
                        'algorithm': record.algorithm,
                        'config': record.config == '{}' ? '无参数' : record.config,
                        'image_width': record.image_width,
                        'image_height': record.image_height,
                        'elapsed_time': Number(record.elapsed_time) / 1000,
                        'res_image_url': record.res_image_url,
                        'res_image_path': record.res_image_path,
                        'res_kpts_num': record.res_kpts_num,
                        'res_kpts_path': record.res_kpts_path,
                        'res_scores_path': record.res_scores_path,
                        'res_descriptors_path': record.res_descriptors_path,
                        'detection_date': new Date(record.detection_date as string).toISOString().replace('T', ' ').substring(0, 19),
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
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data
                })
            }
        })
}
onMounted(async () => {
    try {
        getTotal()
        getInfo()
    } catch (error) {
        console.error('请求失败:', error)
    }
})
const handleSizeChange = async (newPageSize: number) => {
    await axios.get('http://127.0.0.1:5000/detection/' + user_id.value + '/' + newPageSize + '/' + currentPage.value, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: detectionRecordType[] = []
                response.data.forEach((record: detectionRecordType) => {
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,
                        'origin_image_name': record.origin_image_name,
                        'origin_image_url': record.origin_image_url,
                        'algorithm': record.algorithm,
                        'config': record.config == '{}' ? '无参数' : record.config,
                        'image_width': record.image_width,
                        'image_height': record.image_height,
                        'elapsed_time': Number(record.elapsed_time) / 1000,
                        'res_image_url': record.res_image_url,
                        'res_image_path': record.res_image_path,
                        'res_kpts_num': record.res_kpts_num,
                        'res_kpts_path': record.res_kpts_path,
                        'res_scores_path': record.res_scores_path,
                        'res_descriptors_path': record.res_descriptors_path,
                        'detection_date': new Date(record.detection_date as string).toISOString().replace('T', ' ').substring(0, 19),

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
    await axios.get('http://127.0.0.1:5000/detection/' + user_id.value + '/' + pageSize.value + '/' + newPage, { headers })
        .then((res) => {
            let response: responseType = res.data
            if (response.code === 200) {
                let records: detectionRecordType[] = []
                response.data.forEach((record: detectionRecordType) => {
                    records.push({
                        'id': record.id,
                        'user_id': record.user_id,
                        'origin_image_name': record.origin_image_name,
                        'origin_image_url': record.origin_image_url,
                        'algorithm': record.algorithm,
                        'config': record.config == '{}' ? '无参数' : record.config,
                        'image_width': record.image_width,
                        'image_height': record.image_height,
                        'elapsed_time': Number(record.elapsed_time) / 1000,
                        'res_image_url': record.res_image_url,
                        'res_image_path': record.res_image_path,
                        'res_kpts_num': record.res_kpts_num,
                        'res_kpts_path': record.res_kpts_path,
                        'res_scores_path': record.res_scores_path,
                        'res_descriptors_path': record.res_descriptors_path,
                        'detection_date': new Date(record.detection_date as string).toISOString().replace('T', ' ').substring(0, 19),

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
let searchDetectionDate = ref('')
const filterTableData = computed(() =>
    tableData.filter(
        (data: detectionRecordType) =>
            (!searchName.value ||
                data.origin_image_name.toLowerCase().includes(searchName.value.toLowerCase())) &&
            (!searchDetectionDate.value ||
                (data.detection_date as string).toLowerCase().includes(searchDetectionDate.value.toLowerCase()))
    )
)

let deleteIds = ref([])
const handleSelectionChange = (records: detectionRecordType[]) => {
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
        axios.delete('http://127.0.0.1:5000/detection/', { data: { 'deleteIds': deleteIds.value, 'user_id': user_id.value }, headers })
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
const deleteSomeOne = async (detectionRecord: detectionRecordType) => {
    ElMessageBox.confirm(
        '将要删除 ' + detectionRecord.origin_image_name + ' 的记录，是否继续?',
        '警告',
        {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        axios.delete('http://127.0.0.1:5000/detection/' + detectionRecord.id + '/' + user_id.value, { headers })
            .then((res) => {
                let response: responseType = res.data

                if (response.code == 200) {
                    getTotal()
                    getInfo()
                    ElNotification.success({
                        title: '删除成功！',
                        message: '成功删除 ' + detectionRecord.origin_image_name + ' 的记录',
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

const downLoadKpts = async (detectionRecord: detectionRecordType) => {
    download(detectionRecord, 'kpts')
}
const downLoadScores = async (detectionRecord: detectionRecordType) => {
    download(detectionRecord, 'scores')
}
const downLoadDescriptors = async (detectionRecord: detectionRecordType) => {
    download(detectionRecord, 'descriptors')
}
const downLoadResImage = async (detectionRecord: detectionRecordType) => {
    download(detectionRecord, 'image')
}
const download = async (detectionRecord: detectionRecordType, type: string) => {
    await axios.get('http://127.0.0.1:5000/detection/download/' + detectionRecord.id + '/' + type, { headers, responseType: 'blob' }).then((response) => {

        if (response.status != 200) {
            ElNotification.error(
                '下载失败状态码错误'
            )
        } else {
            // 检查 Content-Disposition
            const contentDisposition = response.headers['content-disposition'];
            const filename = contentDisposition ? contentDisposition.split('filename=')[1].replace(/['"]/g, '') : 'kpts.npy';

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