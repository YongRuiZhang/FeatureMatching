<template>
    <div class="">
        <el-row
            style="height: 10vh; margin-top: 10%; display: flex; align-items: center; justify-content: center; flex-direction: column;">
            <div>
                <el-text style="font-size: 50px; font-weight: 600; color: #000;">
                    欢迎使用
                </el-text>
            </div>
            <div>
                <el-text>
                    本网站介绍特征匹配算法模型，并提供模型快捷方便使用的功能
                </el-text>
            </div>
        </el-row>

        <br>

        <el-carousel :interval="4000" type="card" height="350px">
            <el-carousel-item v-for="item in info" :key="item" @click="goto(item)">
                <div class="frosted_glass">
                    <h3 style="color: #475669;">{{ item }}</h3>
                </div>
            </el-carousel-item>
        </el-carousel>
    </div>
</template>

<script lang='ts' setup name='Home'>

import { ref } from "vue"
import { useRouter } from "vue-router"
const router = useRouter()

let info = ref(['模型简介', '特征检测', '特征匹配', '图像拼接', '模型比较'])

function goto(item: string) {
    router.push({ name: item })
}
</script>

<style scoped>
.el-carousel__item {
    display: flex;
    justify-content: center;
    align-items: center;
    /* border: 1px solid black; */
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2),
        -5px -5px 10px rgba(228, 242, 242, 0.949);
}

.el-carousel__item div {
    width: 80%;
    height: 40%;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 5px;

    letter-spacing: 0.5em;
    backdrop-filter: blur(20px);
    opacity: 0.98;
    color: #fff;
    box-shadow: 0 0 30px 10px rgba(0, 0, 0, .3);
}

.el-carousel__item:nth-child(1) {
    /* background-color: #99a9bf; */
    background-image: url(/src/assets/img/introduction.png);
    background-size: 100%;
    background-position: center;
}

.el-carousel__item:nth-child(2) {
    /* background-color: #d3dce6; */
    background-image: url(/src/assets/img/detection.png);
    background-size: 100%;
    background-position: center;
}

.el-carousel__item:nth-child(3) {
    background-image: url(/src/assets/img/matching.png);
    background-size: 100%;
    background-position: center;
}

.el-carousel__item:nth-child(4) {
    background-image: url(/src/assets/img/stitch.png);
    background-size: 100%;
    background-position: center;
}

.el-carousel__item:nth-child(5) {
    background-image: url(/src/assets/img/comparison.png);
    background-size: 100%;
    background-position: center;
}
</style>