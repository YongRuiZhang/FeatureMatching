<template>
    <div class="">
        <el-scrollbar class="main">
            <el-row style="height: 6vh;">
                <el-col :span="4">
                    <div id="mytitle">
                        <el-text class="mx-1" style="font-size: 26px;">图像拼接</el-text>
                    </div>
                </el-col>
                <el-col :span="18" :offset="1">
                    <el-steps class="mb-4" style="max-width: 600px" :space="200" :active="stepsActive"
                        finish-status="success" process-status="process" simple>
                        <el-step title="上传数据" :icon="UploadFilled" />
                        <el-step title="图像拼接" :icon="Picture" />
                        <el-step title="结果下载" :icon="Download" />
                    </el-steps>
                </el-col>
            </el-row>

            <el-row>
                <el-col :span="24">
                    <UploadImagePair ref="pair" :setStepsActive1="setStepsActive1" :setStepsActive0="setStepsActive0"
                        :api="'http://127.0.0.1:5000/mosaic/upload_image'" />
                </el-col>
            </el-row>


        </el-scrollbar>
    </div>
</template>

<script lang='ts' setup name='Mosaic'>
import { ref } from "vue"
import { UploadFilled, Picture, Download } from '@element-plus/icons-vue'
import UploadImagePair from '@/components/UploadImagePair.vue'

// 步骤条
let stepsActive = ref(0)
const setStepsActive1 = () => {
    stepsActive.value = 1
}
const setStepsActive0 = () => {
    stepsActive.value = 0
}
</script>

<style scoped></style>