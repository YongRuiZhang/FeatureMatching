<template>
    <el-row>
        <el-col :span="10" :offset="7">
            <el-upload class="upload-demo" drag action="http://127.0.0.1:5000/matching/upload_video" method="post"
                name="file" multiple="flase" auto-upload="false" :on-success="uploadSuccess" :on-remove="removeFile">
                <div id="uploadBox">
                    <div>
                        <el-icon class="el-icon--upload">
                            <upload-filled />
                        </el-icon>
                        <br />
                        <div class="el-upload__text">
                            将文件拖拽到这里 或者 <em>点击上传</em>
                        </div>
                    </div>
                </div>

                <template #tip>
                    <div class="el-upload__tip" style="margin-left: 1%;">
                        仅支持上传 jpg/jpeg/png , 大小 <= 15000 kb </div>
                </template>
            </el-upload>
        </el-col>
    </el-row>
</template>

<script lang='ts' setup name='UploadVideo'>
import { ElNotification } from "element-plus"
import { ref } from "vue"
import { useMatchingUploadVideoStore } from "@/stores/MatchingUploadVideo"

const props = defineProps(['setStepsActive1', 'setStepsActive0'])

const store = useMatchingUploadVideoStore()

let filepath = ref("")
let filepath_url = ref("")
let uid = ref("")
let dir_path = ref("")

const uploadSuccess = (response: any) => {
    if (response.code != 200) {
        if (response.data === null) response.data = ""
        ElNotification.error({
            title: response.msg,
            message: '失败原因: ' + response.data,
        })
    } else {
        filepath.value = response.data.file_path
        filepath_url.value = response.data.file_path_url
        uid.value = response.data.uid
        dir_path.value = response.data.dir_path

        store.setPath(dir_path.value)
        store.setDirName(uid.value)
        store.setFilePath(filepath.value)
        store.setFilePathUrl(filepath_url.value)

        ElNotification.success({
            title: response.msg,
        })
    }
}

const removeFile = () => {
    filepath.value = ""
    filepath_url.value = ""
    uid.value = ""
    dir_path.value = ""
    store.init()
}
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
</style>