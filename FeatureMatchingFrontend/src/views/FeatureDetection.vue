<template>
    <el-row style="height: 8vh;">
        <el-col :span="4">
            <div id="mytitle">
                <el-text class="mx-1" style="font-size: 26px;">特征点检测</el-text>
            </div>
        </el-col>
        <el-col :span="18" :offset="1">
            <el-steps class="mb-4" style="max-width: 600px" :space="200" :active="stepsActive" simple
                finish-status="success" process-status="process">
                <el-step title="上传图片" :icon="UploadFilled" />
                <el-step title="特征检测" :icon="Picture" />
                <el-step title="结果下载" :icon="Download" />
            </el-steps>
        </el-col>
    </el-row>
    <div class="mid">
        <div class="left">
            <el-upload class="upload-demo" drag action="http://127.0.0.1:5000/detection/upload" method="post"
                name="file" multiple="flase" auto-upload="false" :on-success="uploadSuccess" :on-remove="removeFile">
                <div id="uploadBox" v-if="!havePic">
                    <div>
                        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                        <br />
                        <div class="el-upload__text">
                            将文件拖拽到这里 或者 <em>点击上传</em>
                        </div>
                    </div>
                </div>

                <div v-if="havePic" id="myimage">
                    <img :src="imagepath_url" alt="图片上传失败">
                </div>

                <template #tip>
                    <div class="el-upload__tip" style="margin-left: 1%;">
                        仅支持上传 jpg/jpeg/png , 大小 <= 500 kb </div>
                </template>
            </el-upload>


        </div>

        <div id="icon_right">
            <SvgIcon iconName="icon-Right"></SvgIcon>
        </div>

        <div id="right">
            <div id="rightTop">
                <div v-if="!haveResPic" id="noRes">
                    <div v-loading="resLoading" element-loading-text="检测中...">
                        <el-icon id="icon_picture">
                            <Picture />
                        </el-icon>
                        <br />
                        <el-text class="mx-1" style="font-size: large;">检测结果将会展示在这里</el-text>
                    </div>
                </div>

                <div v-if="haveResPic" id="resImg" v-loading="resLoading" element-loading-text="检测中...">
                    <img :src="resImagePath_url" alt="展示结果失败">
                </div>
            </div>
        </div>
    </div>
    <div class="bottom">
        <el-row>
            <el-col :span="12">
                <el-form :inline="true" :model="form" class="demo-form-inline">
                    <el-form-item label="检测器算法:">
                        <el-radio-group v-model="form.method">
                            <el-radio-button label="Harris" value="Harris" />
                            <el-radio-button label="Shi-Tomasi" value="Shi_Tomasi" />
                            <el-radio-button label="ORB" value="ORB" />
                            <el-radio-button label="SIFT" value="SIFT" />
                            <el-radio-button label="SuperPoint" value="SuperPoint" />
                        </el-radio-group>
                    </el-form-item>
                    <br v-if="form.method == 'Harris' || form.method == 'Shi_Tomasi'" />
                    <el-form-item>
                        <div v-if="form.method == 'Harris'">
                            <el-text style="margin-right: 5px;">blockSize: </el-text>
                            <el-input v-model="blocksize" placeholder="2" style="width: 40px; margin-right: 5px;" />
                            <el-tooltip class="box-item" effect="dark" content="检测窗口大小" placement="bottom-end">
                                <el-icon>
                                    <SvgIcon icon-name="icon-tishi" />
                                </el-icon>
                            </el-tooltip>

                            <el-text style="margin-left: 20px;margin-right: 5px;">ksize: </el-text>
                            <el-input v-model="ksize" placeholder="3" style="width: 40px; margin-right: 5px;" />
                            <el-tooltip class="box-item" effect="dark" content="Sobel的卷积核大小" placement="bottom">
                                <el-icon>
                                    <SvgIcon icon-name="icon-tishi" />
                                </el-icon>
                            </el-tooltip>

                            <el-text style="margin-left: 20px;margin-right: 5px;">k: </el-text>
                            <el-input v-model="k" placeholder="0.02" style="width: 58px; margin-right: 5px;" />
                            <el-tooltip class="box-item" effect="dark" content="权重系数, 经验值( 0.02 ~ 0.04 )"
                                placement="bottom-end">
                                <el-icon>
                                    <SvgIcon icon-name="icon-tishi" />
                                </el-icon>
                            </el-tooltip>
                        </div>

                        <div v-if="form.method == 'Shi_Tomasi'">
                            <el-text style="margin-right: 5px;">maxCorners: </el-text>
                            <el-input v-model="maxCorners" placeholder="1000" style="width: 60px; margin-right: 5px;" />
                            <el-tooltip class="box-item" effect="dark" content="角点的最大数，值为 0 表示无限制"
                                placement="bottom-end">
                                <el-icon>
                                    <SvgIcon icon-name="icon-tishi" />
                                </el-icon>
                            </el-tooltip>

                            <el-text style="margin-left: 20px;margin-right: 5px;">qualityLevel: </el-text>
                            <el-input v-model="qualityLevel" placeholder="0.01"
                                style="width: 50px; margin-right: 5px;" />
                            <el-tooltip class="box-item" effect="dark" content="角点的品质因子, 0 ~ 1 中的数字" placement="bottom">
                                <el-icon>
                                    <SvgIcon icon-name="icon-tishi" />
                                </el-icon>
                            </el-tooltip>

                            <el-text style="margin-left: 20px;margin-right: 5px;">minDistance: </el-text>
                            <el-input v-model="minDistance" placeholder="10" style="width: 40px; margin-right: 5px;" />
                            <el-tooltip class="box-item" effect="dark" content="两个角点的最近距离( 距离内选择品质最好的角点 )
" placement="bottom-end">
                                <el-icon>
                                    <SvgIcon icon-name="icon-tishi" />
                                </el-icon>
                            </el-tooltip>
                        </div>
                    </el-form-item>
                    <br />
                    <el-form-item>
                        <el-button type="primary" class="detectionBtn" @click="detection" size="large">检测</el-button>
                    </el-form-item>
                </el-form>
            </el-col>
            <el-col :span="12" v-if="haveResPic">
                <br />
                <el-row>
                    <el-col :span="6">
                        <ResCard style="height: 50px; width: 200px;" :name="'图像宽度'" :res="width"></ResCard>
                    </el-col>
                    <el-col :span="6">
                        <ResCard style="height: 50px; width: 200px;" :name="'图像高度'" :res="height"></ResCard>
                    </el-col>
                    <el-col :span="6">
                        <ResCard style="height: 50px; width: 200px;" :name="'特征点个数'" :res="num_kpts"></ResCard>
                    </el-col>
                    <el-col :span="6">
                        <ResCard style="height: 50px; width: 200px;" :name="'耗时'" :res="detectionTimes / 1000">
                        </ResCard>
                    </el-col>
                </el-row>
                <br />
                <el-row :gutter="2">
                    <el-col :span="6">
                        <el-button type="success" round @click="downloadImage" style="width: 100%;">结果图片下载</el-button>
                    </el-col>
                    <el-col :span="6">
                        <el-button type="warning" round @click="downloadKpts" style="width: 100%;">kpts下载</el-button>
                    </el-col>
                    <el-col :span="6">
                        <el-button type="warning" round @click="downloadDes"
                            style="width: 100%;">Descriptors下载</el-button>
                    </el-col>
                    <el-col :span="6">
                        <el-button type="warning" round @click="downloadScores" style="width: 100%;"
                            v-if="form.method === 'SuperPoint'">Scores下载</el-button>
                    </el-col>
                </el-row>
            </el-col>
        </el-row>
    </div>
</template>

<script lang='ts' setup name='FeatureDetection'>
import { reactive, ref } from "vue"
import { UploadFilled, Picture, Download } from '@element-plus/icons-vue'
import axios from "axios"
import { ElMessage, ElNotification, type UploadFile } from "element-plus"
import ResCard from '@/components/ResCard.vue'
import { type responseType } from '@/types/index'
import { useUserStore } from "@/stores/UserStore"
import { useRouter } from 'vue-router'
import { jwt_refresh } from "@/utils/JWT"

const router = useRouter()
const userStore = useUserStore()
let { username, access_token } = userStore

// 样式配置
let stepsActive = ref(0) // 步骤
let resLoading = ref(false) // 展示结果时是否出现加载动画加载

// 提交图片相关变量
let havePic = ref(false)  // 是否上传图片
let haveResPic = ref(false)  // 是否有结果图片
let originName = ref('')  // 上传图片初始名
let filename = ref('')  // 上传图片返回名（uuid+初始名）
let imagepath = ref('')  // 上传图片返回文件路径
let imagepath_url = ref('')  // 上传图片返回url路径
let resImagePath = ref('')  // 结果图片返回文件路径
let resImagePath_url = ref('') // 结果图片返回url路径
let width = ref(0)  // 图片宽度
let height = ref(0) // 图片高度
let detectionTimes = ref(0) // 检测时间
let num_kpts = ref(0) // 检测点数量
let kpts_path = ref('')
let scores_path = ref('')
let descriptors_path = ref('')

// 检测相关变量
const form = reactive({
    'method': 'Harris'
})
let config = reactive<Record<string, any>>({}) // 提交参数
let blocksize = ref(2) // Harris 参数 检测窗口大小
let ksize = ref(3) // Harris 参数 Sobel的卷积核大小
let k = ref(0.02) // Harris 参数
let maxCorners = ref(1000) // Shi-Tomasi 参数 角点的最大数
let qualityLevel = ref(0.01) // Shi-Tomasi 参数
let minDistance = ref(10) // Shi-Tomasi 参数 角点之间最小欧式距离，忽略小于此距离的点


function uploadSuccess(response: any, uploadFile: UploadFile) {
    if (response.code != 200) {
        if (response.data === null) response.data = ""
        ElNotification.error({
            title: response.msg,
            message: '失败原因: ' + response.data,
        })
    } else {
        originName.value = response.data.originName
        filename.value = response.data.filename
        imagepath.value = response.data.filepath
        if (response.data.filepath_url !== "") {
            imagepath_url.value = response.data.filepath_url
        } else {
            imagepath_url.value = uploadFile.url!
        }
        if (imagepath.value !== "" && imagepath_url.value !== "") {
            havePic.value = true
        }
        stepsActive.value = 1
        ElNotification.success({
            title: response.msg,
        })
    }
}

function removeFile() {
    // 上传图片重置
    originName.value = ""
    filename.value = ""
    imagepath.value = ""
    imagepath_url.value = ""
    havePic.value = false

    // 结果图片重置
    resImagePath.value = ""
    resImagePath_url.value = ""
    width.value = 0
    height.value = 0
    detectionTimes.value = 0
    haveResPic.value = false
    num_kpts.value = 0
    kpts_path.value = ""
    scores_path.value = ""
    descriptors_path.value = ""

    // 步骤重置
    stepsActive.value = 0
}

async function detection() {
    resLoading.value = true
    detectionTimes.value = 0
    if (form.method === 'Harris') {
        Object.assign(config, {
            'blocksize': blocksize.value,
            'ksize': ksize.value,
            'k': k.value
        })
    } else if (form.method === 'Shi_Tomasi') {
        Object.assign(config, {
            'maxCorners': maxCorners.value,
            'qualityLevel': qualityLevel.value,
            'minDistance': minDistance.value
        })
    }
    let detectionForm = reactive({
        'method': form.method,
        'filename': filename.value,
        'filepath': imagepath.value,
        'config': config
    })

    await axios({
        method: 'POST',
        url: 'http://127.0.0.1:5000/detection/detect',
        data: detectionForm,
        headers: {
            "Content-Type": "multipart/form-data"
        }
    }).then(res => {
        let response: responseType = res.data

        if (response.code != 200) {
            resLoading.value = false
            if (response.data === null) response.data = ""

            ElNotification.error({
                title: response.msg,
                message: '失败原因: ' + response.data,
            })
        } else {
            resLoading.value = false

            resImagePath.value = response.data.resImagePath
            resImagePath_url.value = response.data.resImagePath_url
            width.value = Number(response.data.width)
            height.value = Number(response.data.height)
            detectionTimes.value = Number(response.data.detectionTimes)
            num_kpts.value = Number(response.data.num_kpts)
            kpts_path.value = response.data.kpts_path
            scores_path.value = response.data.scores_path === '' ? '' : response.data.scores_path
            descriptors_path.value = response.data.descriptors_path === '' ? '' : response.data.descriptors_path

            if (resImagePath.value !== "" && resImagePath_url.value !== "") {
                haveResPic.value = true
            }
            stepsActive.value = 2

            if (username != null && username != '' && username != '登陆') {
                addDetectionRecord()
            }

            ElNotification.success({
                title: '操作成功',
                message: form.method + ' ' + response.msg,
            })
        }
    }).catch((error) => {
        ElMessage.error(error);
    })
    Object.keys(config).forEach(key => {
        delete config[key];
    });
}

const addDetectionRecord = async () => {
    const headers = {
        Authorization: 'Bearer ' + access_token,
    };
    const postInfo = {
        'username': username,
        'origin_image_name': originName.value,
        'origin_image_url': imagepath_url.value,
        'origin_image_path': imagepath.value,
        'algorithm': form.method,
        'config': JSON.stringify(config),
        'image_width': width.value,
        'image_height': height.value,
        'elapsed_time': detectionTimes.value,
        'res_image_url': resImagePath_url.value,
        'res_image_path': resImagePath.value,
        'res_kpts_num': num_kpts.value,
        'res_kpts_path': kpts_path.value,
        'res_scores_path': scores_path.value,
        'res_descriptors_path': descriptors_path.value
    }

    await axios.post('http://127.0.0.1:5000/detection/record', postInfo, { headers })
        .then((res) => {
            let response: responseType = res.data

            if (response.code === 200) {

                ElNotification.success({
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

async function downloadKpts() {
    let post_info = {
        'dfilename': filename.value,
        'dfilepath': kpts_path.value,
        'type': 'numpy'
    }
    download(post_info)
}
async function downloadImage() {
    let post_info = {
        'dfilename': filename.value,
        'dfilepath': resImagePath.value,
        'type': 'image'
    }
    download(post_info)
}
async function downloadScores() {
    let post_info = {
        'dfilename': filename.value,
        'dfilepath': scores_path.value,
        'type': 'numpy'
    }
    download(post_info)
}
async function downloadDes() {
    let post_info = {
        'dfilename': filename.value,
        'dfilepath': descriptors_path.value,
        'type': 'numpy'
    }
    download(post_info)
}
const download = async (post_info: any) => {
    await axios.post('http://127.0.0.1:5000/detection/download', post_info, {
        responseType: 'blob'
    }).then((response) => {
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
            stepsActive.value = 3
        }
    }).catch((error) => {
        ElNotification.error('下载失败:', error);
    });
}


</script>

<style scoped>
#mytitle {
    margin-left: 0.8vw;
}

.mid {
    display: flex;
    justify-content: space-evenly;
}

/* 左边 */
.upload-demo {
    width: 45vw;
}

#uploadBox {
    width: 100%;
    /* 固定长宽比为 16:9 */
    aspect-ratio: 16 / 9;

    display: flex;
    justify-content: center;
    align-items: center;
}

.el-upload__text {
    font-size: large;
}

#myimage {
    width: 100%;
    aspect-ratio: 16 / 9;

    display: flex;
    align-items: center;
    justify-content: center;
}

#myimage img {
    max-width: 100%;
    max-height: 100%;
}

.detectionBtn {
    width: 40vw;
}

/* 中间图标 */
#icon_right {
    width: 3vw;
    height: auto;
    display: flex;
}

/* 右边 */
#right {
    width: 45vw;
    aspect-ratio: 16 / 9;
}

#rightTop {
    width: 100%;
    height: 100%;
}

#noRes {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    border: 1px dashed var(--el-border-color);
}

#icon_picture {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;


    font-size: 45px;
    color: var(--el-text-color-secondary);
}

#resImg {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;

    background-color: rgba(212, 221, 232, 0.957);
    box-shadow: 2px 2px rgb(237, 247, 249);
    border-radius: 10px;
}

#resImg img {
    max-width: 96%;
    max-height: 96%;
}
</style>