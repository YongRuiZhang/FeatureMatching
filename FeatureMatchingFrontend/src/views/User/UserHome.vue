<template>
    <div class="">
        <el-descriptions title="个人信息" border style="width: 80%; margin-top: 20px; margin-left: 10%;">
            <el-descriptions-item label="id" :rowspan="1" :span="3" label-align="center">
                {{ id }}
            </el-descriptions-item>
            <el-descriptions-item :rowspan="2" :width="120" label="头像" align="center">
                <SvgIcon icon-name="icon-01" v-if="gender == 'male'" />
                <SvgIcon icon-name="icon-34" v-if="gender == 'female'" />
            </el-descriptions-item>
            <el-descriptions-item label="用户名" :width="180" label-align="center">{{ username }}</el-descriptions-item>
            <el-descriptions-item label="性别" :width="180" label-align="center"><el-tag>{{ gender
            }}</el-tag></el-descriptions-item>
            <el-descriptions-item label="邮箱" :width="180" label-align="center">{{ email }}</el-descriptions-item>
            <el-descriptions-item label="生日" :width="180" label-align="center">
                {{ birthday }}
            </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 50px;"></div>

        <el-row>
            <el-col :offset="2" :span="9">
                <h3>特征检测算法使用次数</h3>
                <Chart :option="barDetectionOption" height="400px" v-if="barData_detection.length !== 0" />
            </el-col>
            <el-col :offset="2" :span="9">
                <h3>特征匹配算法使用次数</h3>
                <Chart :option="barMatchingOption" height="440px" v-if="barData_matching.length !== 0" />
            </el-col>
        </el-row>
        <el-row>
            <el-col :offset="2" :span="9">
                <h3>图像拼接算法使用次数</h3>
                <Chart :option="barMosaicOption" height="400px" v-if="barData_mosaic.length !== 0" />
            </el-col>
            <el-col :offset="2" :span="9">
                <h3>各功能使用次数</h3>
                <Chart :option="pieOption" height="400px" v-if="pieData.length !== 0" />
            </el-col>
        </el-row>

    </div>
</template>

<script lang='ts' setup name='UserHome'>
import { onMounted, ref, reactive, watch } from "vue"
import { useUserStore } from "@/stores/UserStore";
import { useRouter } from "vue-router";
import { ElNotification } from "element-plus";
import axios from "axios";
import type { responseType } from "@/types";
import { jwt_refresh } from "@/utils/JWT";

import Chart from '@/components/Chart.vue';
import { log } from "echarts/types/src/util/log.js";

const router = useRouter()
const userStore = useUserStore()
let { username, gender, role, access_token, user_id } = userStore

onMounted(() => {
    if (username == '登陆' || gender == '' || role == '') {
        ElNotification.error({
            title: '未登陆！',
            message: '请先登陆'
        })
        router.push('/login')
    } else {
        getUserInfo()
        getChartData()
    }
})

let birthday = ref('')
let email = ref('')
let id = ref('')
let register_date = ref('')

const getUserInfo = async () => {
    const headers = {
        Authorization: 'Bearer ' + access_token,
    }
    await axios.get('http://127.0.0.1:5000/user/' + username, { headers }).then((res) => {
        let response: responseType = res.data

        birthday.value = response.data.birthday
        email.value = response.data.email
        id.value = response.data.id
        register_date.value = response.data.register_date


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

interface BarChartData {
    name: string;
    value: number;
}

interface PieChartData {
    name: string;
    value: number;
}

const barData_detection = ref<BarChartData[]>([]);
const barData_matching = ref<BarChartData[]>([]);
const barData_mosaic = ref<BarChartData[]>([]);
const pieData = ref<PieChartData[]>([]);

const getChartData = async () => {

    const headers = {
        Authorization: 'Bearer ' + access_token,
    }
    await axios.get('http://127.0.0.1:5000/user/charts/' + user_id, { headers }).then((res) => {
        let response: responseType = res.data

        barData_detection.value = response.data.data_detection
        barData_matching.value = response.data.data_matching
        barData_mosaic.value = response.data.data_mosaic
        pieData.value = response.data.data_pie

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


const barDetectionOption = reactive({
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow',
        },
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
    },
    xAxis: {
        type: 'category',
        data: barData_detection.value.map(item => item.name),
        axisLabel: {
            rotate: -45,
            margin: 10,
            textStyle: {
                fontSize: 12,
            }
        },
    },
    yAxis: {
        type: 'value',
    },
    series: [
        {
            name: '特征检测算法使用次数',
            type: 'bar',
            data: barData_detection.value.map(item => item.value),
        },
    ],
});

const barMatchingOption = reactive({
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow',
        },
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
    },
    xAxis: {
        type: 'category',
        data: barData_matching.value.map(item => item.name),
        axisLabel: {
            rotate: -45,
            margin: 10,
            textStyle: {
                fontSize: 12,
            }
        },
    },
    yAxis: {
        type: 'value',
    },
    series: [
        {
            name: '特征匹配算法使用次数',
            type: 'bar',
            data: barData_matching.value.map(item => item.value),
        },
    ],
});

const barMosaicOption = reactive({
    tooltip: {
        trigger: 'axis',
        axisPointer: {
            type: 'shadow',
        },
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
    },
    xAxis: {
        type: 'category',
        data: barData_mosaic.value.map(item => item.name),
        axisLabel: {
            rotate: -45,
            margin: 10,
            textStyle: {
                fontSize: 12,
            }
        },
    },
    yAxis: {
        type: 'value',
    },
    series: [
        {
            name: '图像拼接算法使用次数',
            type: 'bar',
            data: barData_mosaic.value.map(item => item.value),
        },
    ],
});

const pieOption = reactive({
    tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)',
    },
    legend: {
        orient: 'vertical',
        left: 'left',
    },
    series: [
        {
            name: '算法分布',
            type: 'pie',
            radius: '50%',
            data: pieData.value,
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: 'rgba(0, 0, 0, 0.5)',
                },
            },
        },
    ],
});
const updateBarDetection = () => {
    barDetectionOption.xAxis.data = barData_detection.value.map(item => item.name);
    barDetectionOption.series[0].data = barData_detection.value.map(item => item.value);
};
watch(barData_detection, updateBarDetection, { deep: true });

const updateBarMatching = () => {
    barMatchingOption.xAxis.data = barData_matching.value.map(item => item.name);
    barMatchingOption.series[0].data = barData_matching.value.map(item => item.value);
};
watch(barData_matching, updateBarMatching, { deep: true });

const updateBarMosaic = () => {
    barMosaicOption.xAxis.data = barData_mosaic.value.map(item => item.name);
    barMosaicOption.series[0].data = barData_mosaic.value.map(item => item.value);
};
watch(barData_mosaic, updateBarMosaic, { deep: true });

const updatePie = () => {
    pieOption.series[0].data = pieData.value;
};
watch(pieData, updatePie, { deep: true });
</script>

<style scoped></style>