<template>
    <div>
        <el-scrollbar class="main">
            <el-row style="height: 6vh;">
                <el-col :span="4">
                    <div id="mytitle">
                        <el-text class="mx-1" style="font-size: 26px;">特征匹配</el-text>
                    </div>
                </el-col>
                <el-col :span="18" :offset="1">
                    <el-steps class="mb-4" style="max-width: 600px" :space="200" :active="stepsActive"
                        finish-status="success" process-status="process" simple>
                        <el-step title="上传数据" :icon="UploadFilled" />
                        <el-step title="特征匹配" :icon="Picture" />
                        <el-step title="结果下载" :icon="Download" />
                    </el-steps>
                </el-col>
            </el-row>

            <el-row>
                <el-col :span="24">
                    <el-tabs tab-position="top" type="border-card" @tab-click="tabClick">
                        <el-tab-pane label="两张图片">
                            <UploadImagePair ref="pair" :setStepsActive1="setStepsActive1"
                                :setStepsActive0="setStepsActive0"
                                :api="'http://127.0.0.1:5000/matching/upload_image'" />
                        </el-tab-pane>
                        <el-tab-pane label="多张图片">
                            <UploadImages ref="images" :setStepsActive1="setStepsActive1"
                                :setStepsActive0="setStepsActive0" />
                        </el-tab-pane>
                        <el-tab-pane label="视频">
                            <UploadVideo ref="video" :setStepsActive1="setStepsActive1"
                                :setStepsActive0="setStepsActive0" />
                        </el-tab-pane>
                        <el-tab-pane label="实时">
                            <el-row>
                                <el-col :span="9" :offset="4">
                                    <div style="height: 33vh; display: flex; justify-content: center; align-items: center; 
                                    border-radius: 5px;
                                    border-color: var(--el-border-color);
                                    border-width: 1px;
                                    border-style: dashed;
                                ">
                                        <el-button v-if="!showPcCamera" @click="showPcCamera = true" type="primary">
                                            打开电脑摄像头
                                        </el-button>

                                        <el-tooltip placement="top" content="点击画面关闭摄像头" v-if="showPcCamera">
                                            <img src="http://127.0.0.1:5000/matching/video_feed"
                                                style="max-height: 33vh;" @click="closePcCamera">
                                        </el-tooltip>
                                    </div>

                                </el-col>

                                <el-col :span="1" style="display: flex; align-items: center; justify-content: center;">
                                    <div style="width: 2.5vw;
                        height: auto;
                        display: flex;">
                                        <SvgIcon iconName="icon-Right"></SvgIcon>
                                    </div>
                                </el-col>

                                <el-col :span="6">
                                    <div class="form-cantainer" style="margin-left: 20px;">
                                        <div class="form-title">
                                            <el-text style="font-size: 20px; color: #409EFF;">
                                                选择方法
                                            </el-text>
                                        </div>
                                        <div class="form">
                                            <el-form :model="form" label-position="right" label-width="auto"
                                                size="small">
                                                <el-form-item label="算法分类:">
                                                    <el-radio-group v-model="form.class" label-position="right">
                                                        <el-radio-button label="稀疏" value="稀疏" />
                                                        <el-radio-button label="半稀疏" value="半稀疏" />
                                                        <el-radio-button label="稠密" value="稠密" />
                                                    </el-radio-group>
                                                </el-form-item>
                                                <el-form-item label="匹配算法:">
                                                    <el-radio-group v-model="form.matchmethod">
                                                        <el-radio-button label="LoFTR" value="LoFTR" />
                                                        <el-radio-button label="SuperGlue" value="SuperGlue"
                                                            v-if="form.class === '稀疏'" />
                                                        <el-radio-button label="BF" value="BF"
                                                            v-if="form.class === '稀疏'" />
                                                        <el-radio-button label="FLANN" value="FLANN"
                                                            v-if="form.class === '稀疏'" />
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

                                                <el-row style="height: 14px;">
                                                    <el-col :offset="10">
                                                        <el-text
                                                            style="font-size: 12px; color: var(--el-text-color-secondary); line-height: 14px;">
                                                            当前数据源为: {{ tabName }}
                                                        </el-text>
                                                    </el-col>
                                                </el-row>
                                                <br />

                                                <el-form-item label="基准配置:" v-if="tabName === '多张图片'">
                                                    <div class="custom-style">
                                                        <el-segmented v-model="form.fix"
                                                            :options="['首张作为基准', '前张作为基准']" />
                                                    </div>
                                                </el-form-item>
                                                <el-form :inline="true" :model="form" class="demo-form-inline"
                                                    size="small">
                                                    <el-text style="margin-right: 5px;">skip: </el-text>
                                                    <el-input v-model="form.skip" placeholder="1"
                                                        style="width: 40px; margin-right: 5px;" />
                                                    <el-tooltip class="box-item" effect="dark"
                                                        content="匹配时跳过图片(帧)数, 视频建议30" placement="bottom">
                                                        <el-icon>
                                                            <SvgIcon icon-name="icon-tishi" />
                                                        </el-icon>
                                                    </el-tooltip>
                                                </el-form>
                                            </el-form>
                                        </div>
                                        <div class="submit">
                                            <el-button type="primary" style="width: 50%;" @click="matching">
                                                开始匹配
                                            </el-button>
                                        </div>
                                    </div>
                                </el-col>
                            </el-row>

                        </el-tab-pane>
                    </el-tabs>
                </el-col>
            </el-row>

            <el-row v-if="tabName !== '实时'">
                <el-col :span="2" :offset="3" style="display: flex; justify-content: center;">
                    <div style="
                    margin: 10px 10px;
                    width: auto;
                    height: 3vh;
                    display: flex;">
                        <SvgIcon icon-name="icon-Down" />
                    </div>
                </el-col>
            </el-row>

            <el-row v-if="tabName === '实时'">
                <el-col :span="2" :offset="10" style="display: flex; justify-content: center;">
                    <div style="
                    margin: 10px 10px;
                    width: auto;
                    height: 3vh;
                    display: flex;">
                        <SvgIcon icon-name="icon-Down" />
                    </div>
                </el-col>
            </el-row>

            <el-row style="height: 33vh;" v-if="tabName !== '实时'">
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

                                <el-row style="height: 14px;">
                                    <el-col :offset="10">
                                        <el-text
                                            style="font-size: 12px; color: var(--el-text-color-secondary); line-height: 14px;">
                                            当前数据源为: {{ tabName }}
                                        </el-text>
                                    </el-col>
                                </el-row>
                                <br />

                                <el-form-item label="基准配置:" v-if="tabName === '多张图片' || tabName === '视频'">
                                    <div class="custom-style">
                                        <el-segmented v-model="form.fix" :options="['首张作为基准', '前张作为基准']" />
                                    </div>
                                </el-form-item>
                                <el-form :inline="true" :model="form" class="demo-form-inline" size="small">
                                    <el-text style="margin-right: 5px;">skip: </el-text>
                                    <el-input v-model="form.skip" placeholder="1"
                                        style="width: 40px; margin-right: 5px;" />
                                    <el-tooltip class="box-item" effect="dark" content="匹配时跳过图片数，视频建议30，即（2 fps）"
                                        placement="bottom">
                                        <el-icon>
                                            <SvgIcon icon-name="icon-tishi" />
                                        </el-icon>
                                    </el-tooltip>
                                </el-form>
                            </el-form>
                        </div>
                        <div class="submit">
                            <el-button type="primary" style="width: 50%;" @click="matching">
                                开始匹配
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
                    <div class="result" v-loading="resLoading && { text: '正在匹配中: ' + formatTime(elapsedTime) }"
                        :element-loading-spinner="true" :element-loading-background="true">

                        <el-empty description="结果将展示在这里" v-if="result_path_url === ''"
                            style="height: 100%; width: 100%;" />

                        <div v-if="result_path_url !== ''" id="resImg" style="height: 100%; width: 100%;">
                            <el-row style="height: 100%; width: 100%;">
                                <el-col :span="18" :offset="1" style="height: 100%; width: 100%;">
                                    <img :src="result_path_url" alt="展示结果失败" v-if="tabName === '两张图片'"
                                        style="max-height: 98%; max-width: 98%;" />

                                    <video autoplay loop controls :key="result_path_url"
                                        v-if="tabName === '多张图片' || tabName === '视频'"
                                        style="height: 100%; width: 100%;">
                                        <source :src="result_path_url" type="video/mp4">
                                        结果为视频，您的浏览器不支持 video 标签。
                                    </video>
                                </el-col>


                                <el-col :span="5">
                                    <div class="result-text">
                                        <el-text>
                                            总耗时: {{ formatTime(elapsedTime) }}
                                        </el-text>
                                    </div>
                                    <br />
                                    <div class="result-button">
                                        <el-button type="success" round @click="downloadImage">
                                            <el-tooltip placement="top" class="box-item" effect="dark"
                                                content="下载左侧展示内容">
                                                可视化结果下载
                                            </el-tooltip>
                                        </el-button>
                                        <el-button type="success" round @click="downloadMatches">
                                            <el-tooltip placement="top" class="box-item" effect="dark"
                                                content="包含匹配对与置信度">
                                                Matches 下载
                                            </el-tooltip>
                                        </el-button>
                                        <el-button type="success" round @click="downloadPose">
                                            <el-tooltip placement="top" class="box-item" effect="dark"
                                                content="包含本质矩阵、R、T及合法匹配对">
                                                Poses 下载
                                            </el-tooltip>
                                        </el-button>
                                    </div>
                                </el-col>
                            </el-row>
                        </div>
                    </div>
                </el-col>
            </el-row>

            <el-row v-if="tabName === '实时'">
                <el-col :span="24" style="display: flex; justify-content: center;">
                    <div class="result" style="height: 34vh;">
                        <el-empty description="结果将展示在这里" v-if="result_path_url === ''" />
                    </div>
                </el-col>
            </el-row>
        </el-scrollbar>
    </div>
</template>

<script lang='ts' setup name='FeatureMatching'>
import { ref, reactive, watchEffect, onBeforeUnmount } from "vue"
import axios from "axios";

import { UploadFilled, Picture, Download } from '@element-plus/icons-vue'
import { ElMessage, ElNotification } from "element-plus";

import type { responseType } from "@/types";

import UploadImages from "@/components/UploadImages.vue";
import UploadImagePair from "@/components/UploadImagePair.vue";
import UploadVideo from "@/components/UploadVideo.vue";


import { useUploadImagesStore } from "@/stores/UploadImagesStore";
import { useUploadImagePairStore } from "@/stores/UploadImagePairStore";
import { useUploadVideoStore } from "@/stores/UploadVideo";

let pair = ref(null)
let images = ref(null)
let video = ref(null)

onBeforeUnmount(() => {
    result_path_url.value = ''
    result_path.value = ''
    if (pair.value !== null) {
        (pair.value as any).init()
    }
    if (images.value !== null) {
        (images.value as any).init()
    }
    if (video.value !== null) {
        (video.value as any).init()
    }
})

// 获取选择的 TabName
let tabName = ref('两张图片')
const tabClick = (tab: any) => {
    tabName.value = tab.props.label
    result_path_url.value = ''
    result_path.value = ''
    if (pair.value !== null) {
        (pair.value as any).init()
    }
    if (images.value !== null) {
        (images.value as any).init()
    }
    if (video.value !== null) {
        (video.value as any).init()
    }
}
// 实时
let showPcCamera = ref(false)
const closePcCamera = async () => {
    await axios.delete('http://127.0.0.1:5000/matching/video_feed').then(res => {
        if (res.data.code == 200)
            showPcCamera.value = false
    })
}
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
    fix: '首张作为基准',
    skip: 1,
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

    if (tabName.value === '实时' || tabName.value === '视频') {
        form.skip = 30
    } else {
        form.skip = 1
    }
})

// 结果展示
let resLoading = ref(false) // 是否显示加载动画
let result_path = ref('') // 结果图片路径
let result_path_url = ref('') // 结果文件路径 url
let result_matches_path = ref('') // 匹配结果路径
let result_poses_path = ref('') // 位姿结果路径

const isRunning = ref(false); // 是否正在计时
const elapsedTime = ref(0); // 已耗时（以毫秒为单位）
let intervalId: any = null; // setInterval的ID

const formatTime = (milliseconds: any) => {
    const seconds = milliseconds / 1000;
    return `${String(seconds)} s`;
};

// 启动计时器
const startTimer = () => {
    console.log(1);

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

// 匹配两张图片
const matchingPairs = async () => {
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
    await axios.post('http://127.0.0.1:5000/matching/image', postForm)
        .then(res => {
            let response: responseType = res.data
            if (response.code === 200) {
                result_path.value = response.data.save_path
                result_path_url.value = response.data.save_path_url
                result_matches_path.value = response.data.save_matches_path
                result_poses_path.value = response.data.save_poses_path

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

// 匹配多张图片 及 视频
const matchingIamgesAndVideo = async () => {
    let path, dir_name;
    if (tabName.value === '多张图片') {
        const matchingUploadImagesStore = useUploadImagesStore()
        let { path: imagePath, dir_name: imageDirName, filesInfo } = matchingUploadImagesStore
        if (imagePath === undefined || imagePath === '') {
            ElMessage.error('请先上传图片')
            return
        }
        if (filesInfo.length <= 2) {
            ElMessage.error('请上传两张以上图片')
            return
        }
        path = imagePath
        dir_name = imageDirName
    } else if (tabName.value === '视频') {
        const matchingUploadVideoStore = useUploadVideoStore()
        let { path: videoPath, dir_name: videoDirName } = matchingUploadVideoStore
        if (videoPath === undefined || videoPath === '') {
            ElMessage.error('请先上传视频')
            return
        }
        path = videoPath
        dir_name = videoDirName
    }
    const postForm = {
        'path': path,
        'dir_name': dir_name,
        'type': tabName.value,
        'form': form,
    }
    resetTimer()
    startTimer()
    ElMessage.success('正在匹配，请稍等')
    await axios.post('http://127.0.0.1:5000/matching/images', postForm)
        .then(res => {
            let response: responseType = res.data
            if (response.code === 200) {
                result_path.value = response.data.save_path
                result_path_url.value = response.data.save_path_url
                result_matches_path.value = response.data.save_matches_path
                result_poses_path.value = response.data.save_poses_path

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

// 实时匹配
const matchingRealTime = async () => {
    await axios.post('http://127.0.0.1:5000/matching', form)
}

// 匹配按钮
const matching = async () => {
    resLoading.value = true
    if (tabName.value === '两张图片') {
        matchingPairs()
    } else if (tabName.value === '多张图片' || tabName.value === '视频') {
        matchingIamgesAndVideo()
    } else if (tabName.value === '实时') {
        matchingRealTime()
    }
}

// 下载
async function downloadImage() {
    let post_info = {
        'dfilepath': result_path.value,
        'type': 'image'
    }
    download(post_info)
}
async function downloadMatches() {
    let post_info = {
        'dfilepath': result_matches_path.value,
        'type': 'numpy'
    }
    download(post_info)
}
async function downloadPose() {
    let post_info = {
        'dfilepath': result_poses_path.value,
        'type': 'numpy'
    }
    download(post_info)
}
const download = async (post_info: any) => {
    console.log(post_info);

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
            stepsActive.value = 3
        }
    }).catch((error) => {
        ElNotification.error('下载失败:', error);
    });
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
    height: 33vh;

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
    height: 33vh;
    width: 99%;
    border-radius: 5px;
    border-color: var(--el-border-color);
    border-width: 1px;
    border-style: dashed;
}

.result-text {
    height: 10%;
    display: flex;
    justify-content: center;
    align-items: center;
}

.result-button {
    height: 90%;
    display: flex;
    flex-direction: column;
    justify-content: space-evenly;
    align-items: center;
}
</style>