<template>
    <el-scrollbar class="">
        <el-row>
            <el-col :span="10" :offset="1">
                <el-text>
                    上传左图片
                </el-text>
                <el-upload class="upload-demo" drag :action="api" method="post" name="file"
                    :data="{ 'uid': uid, 'dir_path': dir_path }" multiple="flase" :limit="1" auto-upload="false"
                    :on-success="leftUploadSuccess" :on-remove="leftRemoveFile">
                    <div id="uploadBox" v-if="!left.havePic">
                        <div>
                            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                            <br />
                            <div class="el-upload__text">
                                将文件拖拽到这里 或者 <em>点击上传</em>
                            </div>
                        </div>
                    </div>

                    <div v-if="left.havePic" id="myimage">
                        <img :src="left.imagePath_url" alt="图片上传失败">
                    </div>

                    <template #tip>
                        <div class="el-upload__tip" style="margin-left: 1%;">
                            仅支持上传 jpg/jpeg/png , 大小 <= 500 kb </div>
                    </template>
                </el-upload>
            </el-col>

            <el-col :span="10" :offset="1">
                <el-text>
                    上传右图片
                </el-text>
                <el-upload class="upload-demo" drag :action="api" method="post" name="file"
                    :data="{ 'uid': uid, 'dir_path': dir_path }" multiple="flase" :limit="1" auto-upload="false"
                    :on-success="rightUploadSuccess" :on-remove="rightRemoveFile">
                    <div id="uploadBox" v-if="!right.havePic">
                        <div>
                            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                            <br />
                            <div class="el-upload__text">
                                将文件拖拽到这里 或者 <em>点击上传</em>
                            </div>
                        </div>
                    </div>

                    <div v-if="right.havePic" id="myimage">
                        <img :src="right.imagePath_url" alt="图片上传失败">
                    </div>

                    <template #tip>
                        <div class="el-upload__tip" style="margin-left: 1%;">
                            仅支持上传 jpg/jpeg/png , 大小 <= 500 kb </div>
                    </template>
                </el-upload>
            </el-col>
        </el-row>
    </el-scrollbar>
</template>

<script lang='ts' setup name='UploadImagePair'>
import type { responseType, uploadImageType } from "@/types"
import { ElMessage, ElNotification } from "element-plus"
import { reactive, ref } from "vue"
import { useUploadImagePairStore } from "@/stores/UploadImagePairStore";
import axios from "axios";

const store = useUploadImagePairStore()

const props = defineProps(['setStepsActive1', 'setStepsActive0', 'api'])

let api = ref<string>(props.api)

let uid = ref<string>('') // uuid 的文件名
let dir_path = ref<string>('') // 目录路径
let left = reactive<uploadImageType>({
    havePic: false,
    imagePath: '',
    imagePath_url: '',
})
let right = reactive<uploadImageType>({
    havePic: false,
    imagePath: '',
    imagePath_url: '',
})


function leftUploadSuccess(response: any) {
    if (response.code != 200) {
        if (response.data === null) response.data = ""
        ElNotification.error({
            title: response.msg,
            message: '失败原因: ' + response.data,
        })
    } else {
        Object.assign(left, {
            imagePath: response.data.filepath,
            imagePath_url: response.data.filepath_url,
            havePic: true,
        })

        uid.value = response.data.uid
        dir_path.value = response.data.dir_path

        store.setPath(dir_path.value)
        store.setDirName(uid.value)
        store.setLeftPath(left.imagePath)

        ElNotification.success({
            title: '成功上传 左 图片',
        })

        if (right.havePic) {
            props.setStepsActive1()
        }
    }
}

function rightUploadSuccess(response: any) {
    if (response.code != 200) {
        if (response.data === null) response.data = ""
        ElNotification.error({
            title: response.msg,
            message: '失败原因: ' + response.data,
        })
    } else {
        Object.assign(right, {
            imagePath: response.data.filepath,
            imagePath_url: response.data.filepath_url,
            havePic: true,
        })

        uid.value = response.data.uid
        dir_path.value = response.data.dir_path

        store.setPath(dir_path.value)
        store.setDirName(uid.value)
        store.setRightPath(right.imagePath)

        ElNotification.success({
            title: '成功上传 右 图片',
        })

        if (left.havePic) {
            props.setStepsActive1()
        }
    }
}

const leftRemoveFile = async (uploadFile: any) => {
    await axios.delete(api.value, {
        data: {
            'path': dir_path.value,
            'name': uploadFile.name
        }
    }).then(res => {
        let response: responseType = res.data

        if (response.code === 200) {
            Object.assign(left, {
                havePic: false,
                imagePath: '',
                imagePath_url: '',
            })

            store.removeLeftPath()

            if (!right.havePic) {
                dir_path.value = ''
                uid.value = ''
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

async function rightRemoveFile(uploadFile: any) {
    await axios.delete(api.value, {
        data: {
            'path': dir_path.value,
            'name': uploadFile.name
        }
    }).then(res => {
        let response: responseType = res.data

        if (response.code === 200) {
            Object.assign(right, {
                havePic: false,
                imagePath: '',
                imagePath_url: '',
            })

            store.removeRightPath()

            if (!left.havePic) {
                dir_path.value = ''
                uid.value = ''
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

function init() {

    Object.assign(left, {
        havePic: false,
        imagePath: '',
        imagePath_url: '',
    })

    Object.assign(right, {
        havePic: false,
        imagePath: '',
        imagePath_url: '',
    })

    uid.value = ''
    dir_path.value = ''

    store.init()
}

defineExpose({
    init
})
</script>

<style scoped>
.upload-demo {
    height: 32vh;
}

#uploadBox {
    width: 100%;
    /* 固定长宽比为 16:9 */
    aspect-ratio: 16 / 5;

    display: flex;
    justify-content: center;
    align-items: center;
}

#myimage {
    width: 90%;
    aspect-ratio: 16 / 5;

    display: flex;
    align-items: center;
    justify-content: center;
}

#myimage img {
    max-width: 100%;
    max-height: 100%;
}
</style>