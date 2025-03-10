<template>
    <div class="">
        <el-row>
            <el-col :span="10" :offset="1">
                <el-text>
                    上传左图片
                </el-text>
                <el-upload class="upload-demo" drag action="http://127.0.0.1:5000/matching/upload_image" method="post"
                    name="file" :data="{ 'uid': uid, 'dir_path': dir_path }" multiple="flase" auto-upload="false"
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
                <el-upload class="upload-demo" drag action="http://127.0.0.1:5000/matching/upload_image" method="post"
                    name="file" :data="{ 'uid': uid, 'dir_path': dir_path }" multiple="flase" auto-upload="false"
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

    </div>
</template>

<script lang='ts' setup name='UploadImagePair'>
import type { uploadImageType } from "@/types"
import { ElNotification } from "element-plus"
import { reactive, ref } from "vue"
import { useMatchingUploadImagePairStore } from "@/stores/MatchingUploadImagePairStore";

const store = useMatchingUploadImagePairStore()

const changeStepsActive = defineProps(['changeStepsActive'])


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
            changeStepsActive.changeStepsActive()
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
            changeStepsActive.changeStepsActive()
        }
    }
}

function leftRemoveFile() {
    Object.assign(left, {
        havePic: false,
        imagePath: '',
        imagePath_url: '',
    })

    store.removeLeftPath()

    if (!right.havePic) {
        dir_path.value = ''
        store.init()
    }
}

function rightRemoveFile() {
    Object.assign(right, {
        havePic: false,
        imagePath: '',
        imagePath_url: '',
    })

    store.removeRightPath()

    if (!left.havePic) {
        dir_path.value = ''
        store.init()
    }
}
</script>

<style scoped>
.upload-demo {
    height: 18vw;
}

#uploadBox {
    width: 90%;
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