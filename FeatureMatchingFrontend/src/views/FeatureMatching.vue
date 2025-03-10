<template>
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
                        <UploadImagePair :changeStepsActive="changeStepsActive" />
                    </el-tab-pane>
                    <el-tab-pane label="多张图片">
                        <UploadImages :changeStepsActive="changeStepsActive" />
                    </el-tab-pane>
                    <el-tab-pane label="视频">视频</el-tab-pane>
                    <el-tab-pane label="实时">实时</el-tab-pane>
                </el-tabs>
            </el-col>
        </el-row>

        <el-row>
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
                                    <el-radio-button label="LoFTR" value="LoFTR" />
                                    <el-radio-button label="SuperGlue" value="SuperGlue" v-if="form.class === '稀疏'" />
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

                            <el-form-item label="基准配置:" v-if="tabName === '多张图片'">
                                <div class="custom-style">
                                    <el-segmented v-model="form.fix" :options="['首张作为基准', '前张作为基准']" />
                                </div>
                            </el-form-item>
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
                <div class="result" v-loading="resLoading" element-loading-text="特征匹配中...">
                    <el-empty description="结果将展示在这里" v-if="result_path_url === ''" />
                    <div v-if="result_path_url !== ''" id="resImg"
                        style="display: flex; align-items: center; justify-content: center;">

                        <img :src="result_path_url" alt="展示结果失败" v-if="tabName === '两张图片'"
                            style="height: 98%; width: 98%;" />

                        <video autoplay loop controls :key="result_path_url"
                            v-if="tabName === '多张图片' || tabName === '视频'" style="height: 100%; width: 100%;">
                            <source :src="result_path_url" type="video/mp4">
                            结果为视频，您的浏览器不支持 video 标签。
                        </video>

                    </div>
                </div>
            </el-col>
        </el-row>
    </el-scrollbar>
</template>

<script lang='ts' setup name='FeatureMatching'>
import UploadImages from "@/components/matching/UploadImages.vue";
import { UploadFilled, Picture, Download } from '@element-plus/icons-vue'
import { ref, reactive, watchEffect } from "vue"
import { useMatchingUploadImagesStore } from "@/stores/MatchingUploadImagesStore";
import { useMatchingUploadImagePairStore } from "@/stores/MatchingUploadImagePairStore";
import axios from "axios";
import { ElMessage, ElNotification } from "element-plus";
import type { responseType } from "@/types";
import UploadImagePair from "@/components/matching/UploadImagePair.vue";

// 获取选择的 TabName
let tabName = ref('两张图片')
const tabClick = (tab: any) => {
    tabName.value = tab.props.label
}
// 步骤条
let stepsActive = ref(0)
const changeStepsActive = () => {
    stepsActive.value = 1
}
// 选择方法的表单
let form = reactive({
    class: '稀疏',
    kptmethod: 'SuperPoint',
    matchmethod: 'SuperGlue',
    scene: '室内',
    fix: '首张作为基准',
})
const showScene = () =>
    (form.class === '稀疏' && (form.matchmethod === 'LoFTR' || form.matchmethod === 'SuperGlue')) ||
    (form.class === '半稀疏' && form.matchmethod === 'LoFTR');

watchEffect(() => {
    if (form.class === '半稀疏' && (form.matchmethod !== 'LoFTR')) {
        form.matchmethod = 'LoFTR'
    }

    if (form.matchmethod === 'SuperGlue' && form.kptmethod !== 'SuperPoint') {
        form.kptmethod = 'SuperPoint'
    }
})

// 结果展示
let resLoading = ref(false) // 是否显示加载动画
let result_path = ref('') // 结果文件路径
let result_path_url = ref('') // 结果文件路径 url

// 匹配两张图片
const matchingPairs = async () => {
    const matchingImagePairStore = useMatchingUploadImagePairStore()
    let { path, dir_name, leftpath, rightpath } = matchingImagePairStore

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
    await axios.post('http://127.0.0.1:5000/matching/image', postForm)
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
    resLoading.value = false
}

// 匹配多张图片
const matchingIamges = async () => {
    // 获取 多张图片 的返回值
    const matchingUploadImagesStore = useMatchingUploadImagesStore()
    let { path, dir_name, filesInfo } = matchingUploadImagesStore
    if (path === undefined || path === '') {
        ElMessage.error('请先上传图片')
        return
    }
    if (filesInfo.length <= 2) {
        ElMessage.error('请上传两张以上图片')
        return
    }
    const postForm = {
        'path': path,
        'dir_name': dir_name,
        'form': form,
    }
    ElMessage.success('正在匹配，请稍等')
    await axios.post('http://127.0.0.1:5000/matching/images', postForm)
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
    resLoading.value = false
}

// 匹配视频
const matchingVideo = async () => {
    await axios.post('http://127.0.0.1:5000/matching', form)
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
    } else if (tabName.value === '多张图片') {
        matchingIamges()
    } else if (tabName.value === '视频') {
        matchingVideo()
    } else if (tabName.value === '实时') {
        matchingRealTime()
    }

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
    height: 100%;

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
    height: 100%;
    width: 99%;
    border-radius: 5px;
    border-color: var(--el-border-color);
    border-width: 1px;
    border-style: dashed;
}
</style>