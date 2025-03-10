<template>
    <div class="">
        <el-row>
            <el-col :span="23">
                <el-upload ref="uploadRef" class="upload-demo" v-model:file-list="fileList" list-type="picture-card"
                    action="#" :limit="19" :on-preview="preview" multiple="true" accept="image/*" :auto-upload="false"
                    :on-remove="removeFile" :on-exceed="exceed">
                    <el-icon>
                        <Plus />
                    </el-icon>
                    <template #tip>
                        <div class="el-upload__tip" style="margin-left: 1%;">
                            仅支持上传 jpg/jpeg/png , 大小 <= 500 kb </div>
                    </template>
                </el-upload>

            </el-col>
            <el-col :span="1" style="display: flex; align-items: center;">
                <el-button type="success" @click="submitUpload" style="writing-mode: vertical-lr; height: 200px;">
                    上传到服务器
                </el-button>
            </el-col>
        </el-row>

        <el-dialog v-model="dialogVisible" style="display:flex; max-height: 75vh; max-width: 70vw;">
            <el-image style="height: 100%; width: 100%;" fit="contain" :src="dialogImageUrl" alt="Preview Image" />
        </el-dialog>
    </div>
</template>

<script lang='ts' setup name='UploadImages'>
import axios from "axios";
import { ElMessage, ElNotification, type UploadFile } from "element-plus";
import { onMounted, ref } from "vue"
import type { UploadUserFile } from 'element-plus'
import type { responseType } from "@/types";
import { useMatchingUploadImagesStore } from "@/stores/MatchingUploadImagesStore";

const props = defineProps(['setStepsActive1', 'setStepsActive0'])

const store = useMatchingUploadImagesStore()

let uploadRef = ref(null) // 上传组件的引用
let fileList = ref<UploadUserFile[]>([]) // 上传的文件列表
let path = ref('') // 返回的文件夹路径
let dir_name = ref('') // 返回的文件夹名称
let filesInfo = ref([]) // 上传的文件信息

// 预览图片
const dialogImageUrl = ref('')
const dialogVisible = ref(false)
const preview = (uploadFile: UploadFile) => {
    dialogImageUrl.value = uploadFile.url!
    dialogVisible.value = true
}

onMounted(() => {
    store.init();

    const inputElement = (uploadRef.value as any).$el.querySelector('.el-upload__input');
    (inputElement as HTMLInputElement).webkitdirectory = true
})

const exceed = () => {
    ElMessage({
        message: '超出文件数量限制',
        type: 'error'
    })
}

const submitUpload = async () => {
    const postInfo = new FormData()
    fileList.value.forEach(file => {
        postInfo.append('file', file.raw as File)
    });

    await axios.post('http://127.0.0.1:5000/matching/upload_images', postInfo
    ).then((res) => {
        let response: responseType = res.data

        if (response.code === 200) {
            path.value = response.data.path
            dir_name.value = response.data.dir_name
            filesInfo.value = response.data.files

            store.setPath(path.value)
            store.setDirName(dir_name.value)
            store.setFilesInfo(filesInfo.value)

            ElMessage({
                message: response.msg,
                type: 'success'
            })

            props.setStepsActive1()
        } else if (response.code === 300 || response.code === 500) {
            ElNotification({
                title: response.msg,
                message: response.data,
                type: 'error'
            })
        }
    })
}

const removeFile = async (uploadFile: any) => {
    filesInfo.value.forEach(async (item, index) => {
        if ((item as any).filename === uploadFile.name) {
            await axios.delete('http://127.0.0.1:5000/matching/upload_images', {
                data: {
                    'path': path.value,
                    'name': uploadFile.name
                }
            }).then((res) => {
                let response: responseType = res.data

                if (response.code === 200) {
                    filesInfo.value.splice(index, 1);

                    store.setFilesInfo(filesInfo.value)

                    if (filesInfo.value.length === 0) {
                        store.init()
                        props.setStepsActive0()
                    }

                    ElMessage({
                        message: response.msg,
                        type: 'success'
                    })
                } else if (response.code === 300 || response.code === 500) {
                    ElNotification({
                        title: response.msg,
                        message: response.data,
                        type: 'error'
                    })
                }
            })
        }
    })
}
</script>

<style scoped></style>