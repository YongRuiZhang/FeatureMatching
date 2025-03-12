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
                <el-col :span="24" style="
                    height: 38vh;
                    border-radius: 5px;
                    border-color: var(--el-border-color);
                    border-width: 1px;
                    border-style: solid;">
                    <UploadImagePair ref="pair" :setStepsActive1="setStepsActive1" :setStepsActive0="setStepsActive0"
                        :api="'http://127.0.0.1:5000/mosaic/upload_image'" style="margin-top: 10px;" />
                </el-col>
            </el-row>

            <el-row>
                <el-col :span="2" :offset="2" style="display: flex; justify-content: center;">
                    <div style="
                    margin: 10px 10px;
                    width: auto;
                    height: 3vh;
                    display: flex;">
                        <SvgIcon icon-name="icon-Down" />
                    </div>
                </el-col>
            </el-row>

            <el-row style="height: 33vh;">
                <el-col :span="6">
                    <div class="form-cantainer">
                        <div class="form-title">
                            <el-text style="font-size: 20px; color: #409EFF;">
                                选择方法
                            </el-text>
                        </div>
                        <div class="form">
                            <el-form :model="form" label-position="right" label-width="auto" size="small">
                                <el-form-item label="算法分类:">
                                    <el-radio-group v-model="form.class" label-position="right">
                                        <el-radio-button label="稀疏" value="稀疏" />
                                        <el-radio-button label="半稀疏" value="半稀疏" />
                                        <el-radio-button label="稠密" value="稠密" />
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="匹配算法:">
                                    <el-radio-group v-model="form.matchmethod">
                                        <el-radio-button label="LoFTR" value="LoFTR" v-if="form.class === '半稀疏'" />
                                        <el-radio-button label="Efficient LoFTR" value="Efficient LoFTR"
                                            v-if="form.class === '半稀疏'" />
                                        <el-radio-button label="DKM" value="DKM" v-if="form.class === '稠密'" />
                                        <el-radio-button label="SuperGlue" value="SuperGlue"
                                            v-if="form.class === '稀疏'" />
                                        <el-radio-button label="BF" value="BF" v-if="form.class === '稀疏'" />
                                        <el-radio-button label="FLANN" value="FLANN" v-if="form.class === '稀疏'" />
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="检测器算法:" v-if="form.class === '稀疏'">
                                    <el-radio-group v-model="form.kptmethod">
                                        <el-radio-button label="SuperPoint" value="SuperPoint" />
                                        <el-radio-button label="SIFT" value="SIFT"
                                            :disabled="form.matchmethod === 'SuperGlue'" />
                                        <el-radio-button label="ORB" value="ORB"
                                            :disabled="form.matchmethod === 'SuperGlue'" />
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="算法场景:" v-if="showScene()">
                                    <el-radio-group v-model="form.scene">
                                        <el-radio-button label="室内" value="室内" />
                                        <el-radio-button label="室外" value="室外" />
                                    </el-radio-group>
                                </el-form-item>
                                <el-form-item label="保留原尺寸:"
                                    v-if="form.kptmethod === 'SIFT' || form.kptmethod === 'ORB'">
                                    <div class="custom-style">
                                        <el-segmented v-model="form.scale" :options="['不保留', '保留']" />
                                        <el-tooltip class="box-item" effect="dark"
                                            content="因为深度学习模型执行矩阵操作，必须resize为固定尺寸，方便对比，建议不保留原尺寸" placement="bottom">
                                            <el-icon>
                                                <SvgIcon icon-name="icon-tishi" />
                                            </el-icon>
                                        </el-tooltip>
                                    </div>
                                </el-form-item>
                            </el-form>
                        </div>
                        <div class="submit">
                            <el-button type="primary" style="width: 50%;" @click="mosaic">
                                开始拼接
                            </el-button>
                        </div>
                    </div>
                </el-col>

                <el-col :span="1" style="display: flex; align-items: center; justify-content: center;">
                    <div style="width: 2.5vw;
                        height: auto;
                        display: flex;">
                        <SvgIcon iconName="icon-Right"></SvgIcon>
                    </div>
                </el-col>

                <el-col :span="17">
                    <div class="result" v-loading="resLoading && { text: '正在拼接中: ' + formatTime(elapsedTime) }"
                        :element-loading-spinner="true" :element-loading-background="true">
                        <el-empty description="结果将展示在这里" v-if="result_path_url === ''" />

                        <div v-if="result_path_url !== ''" id="resImg" style="height: 100%; width: 100%;">

                            <el-row
                                style="height: 100%; width: 100%;display: flex; justify-content: center; align-items: center;">
                                <el-col :span="18" :offset="1" style="height: 100%; width: 100%;">
                                    <el-tooltip placement="top" content="点击放大">
                                        <el-image style="height: 100%; width: 100%;" fit="contain"
                                            :src="result_path_url" :preview-src-list="[result_path_url]"
                                            alt="Preview Image" hide-on-click-modal preview-teleported />
                                    </el-tooltip>
                                </el-col>

                                <el-col :span="4" :offset="1">
                                    <div class="result-text">
                                        <el-text>
                                            总耗时: {{ formatTime(elapsedTime) }}
                                        </el-text>
                                    </div>
                                </el-col>
                            </el-row>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </el-scrollbar>
    </div>
</template>

<script lang='ts' setup name='Mosaic'>
import { reactive, ref, watchEffect } from "vue"
import axios from "axios"

import { UploadFilled, Picture, Download } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from "element-plus"

import UploadImagePair from '@/components/UploadImagePair.vue'
import { useUploadImagePairStore } from "@/stores/UploadImagePairStore"
import type { responseType } from "@/types"


// 步骤条
let stepsActive = ref(0)
const setStepsActive1 = () => {
    stepsActive.value = 1
}
const setStepsActive0 = () => {
    stepsActive.value = 0
}
// 选择方法的表单
let form = reactive({
    class: '稀疏',
    kptmethod: 'SuperPoint',
    matchmethod: 'SuperGlue',
    scene: '室内',
    scale: '不保留'
})
const showScene = () =>
    (form.class === '稀疏' && (form.matchmethod === 'LoFTR' || form.matchmethod === 'SuperGlue')) ||
    (form.class === '半稀疏' && form.matchmethod === 'LoFTR' || form.matchmethod === 'Efficient LoFTR');

watchEffect(() => {
    if (form.class === '稀疏' && form.matchmethod !== 'SuperGlue' && form.matchmethod !== 'BF' && form.matchmethod !== 'FLANN') {
        form.matchmethod = 'SuperGlue'
    }
    if (form.class === '半稀疏' && form.matchmethod !== 'LoFTR' && form.matchmethod !== 'Efficient LoFTR') {
        form.matchmethod = 'LoFTR'
    }
    if (form.class === '稠密' && form.matchmethod !== 'DKM') {
        form.matchmethod = 'DKM'
    }

    if (form.matchmethod === 'SuperGlue' && form.kptmethod !== 'SuperPoint') {
        form.kptmethod = 'SuperPoint'
    }
    if (form.kptmethod !== 'SIFT' && form.kptmethod !== 'ORB') {
        form.scale = '不保留'
    }
})

// 结果展示
let resLoading = ref(false) // 是否显示加载动画
let result_path = ref('') // 结果文件路径
let result_path_url = ref('') // 结果文件路径 url

const isRunning = ref(false); // 是否正在计时
const elapsedTime = ref(0); // 已耗时（以毫秒为单位）
let intervalId: any = null; // setInterval的ID

const formatTime = (milliseconds: any) => {
    const seconds = milliseconds / 1000;
    return `${String(seconds)} s`;
};

// 启动计时器
const startTimer = () => {
    if (isRunning.value) return; // 如果已经在计时，直接返回
    isRunning.value = true; // 更新状态为“正在计时”
    intervalId = setInterval(() => {
        elapsedTime.value += 10;
    }, 10);
};

// 暂停计时器
const pauseTimer = () => {
    isRunning.value = false; // 更新状态为“暂停”
    clearInterval(intervalId); // 清除计时器
};

// 重置计时器
const resetTimer = () => {
    isRunning.value = false; // 更新状态为“已重置”
    clearInterval(intervalId); // 清除计时器
    elapsedTime.value = 0; // 将已耗时设置为0
}

const mosaic = async () => {
    resLoading.value = true
    result_path_url.value = ''

    const imagePairStore = useUploadImagePairStore()
    let { path, dir_name, leftpath, rightpath } = imagePairStore

    if (path === undefined || path === '') {
        ElMessage.error('请先上传图片')
        return
    }
    if (leftpath === undefined || leftpath === '') {
        ElMessage.error('请先上传 左 图片')
    }
    if (rightpath === undefined || rightpath === '') {
        ElMessage.error('请先上传 右 图片')
    }
    const postForm = {
        'path': path,
        'dir_name': dir_name,
        'leftpath': leftpath,
        'rightpath': rightpath,
        'form': form
    }
    resetTimer()
    startTimer()

    await axios.post('http://127.0.0.1:5000/mosaic/', postForm)
        .then(res => {
            let response: responseType = res.data
            if (response.code === 200) {
                result_path.value = response.data.save_path
                result_path_url.value = response.data.save_path_url

                stepsActive.value = 2

                ElNotification.success({
                    title: '操作成功',
                    message: form.matchmethod + ' 方法' + response.msg,
                })
            } else {
                ElNotification.error({
                    title: response.msg,
                    message: response.data,
                })
            }
        })
    pauseTimer()
    resLoading.value = false
}
</script>

<style scoped>
.main {
    height: 86vh;
}

#mytitle {
    margin-left: 0.8vw;
}

.myIcon {
    width: 3vw;
    height: 3vh;
    display: flex;
}

.form-cantainer {
    width: 100%;
    height: 35vh;

    border-radius: 5px;
    border-color: var(--el-border-color);
    border-width: 1px;
    border-style: dashed;
}

.form-title {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 10%;
    margin-top: 10px;
}

.form {
    display: flex;
    margin-left: 10px;
    align-items: center;
    height: 75%;
}

.custom-style .el-segmented {
    --el-segmented-item-selected-color: var(--el-text-color-primary);
    --el-segmented-item-selected-bg-color: #1ea5ff;
    --el-border-radius-base: 16px;
}

.submit {
    height: 5%;
    display: flex;
    justify-content: center;
}

.result {
    height: 35vh;
    width: 99%;
    border-radius: 5px;
    border-color: var(--el-border-color);
    border-width: 1px;
    border-style: dashed;
}
</style>