<template>
    <div class="">
        <el-text size="large">查</el-text>
        <br />
        <el-button type="primary" @click="getname2">
            get restful all
        </el-button>
        <br />
        <el-text v-show="getname2have">{{ getname2Data }}</el-text>

        <br />
        <br />

        <el-input v-model="getname1input" style="width: 200px;" placeholder="输入名字"></el-input>
        <el-input v-model="getage1input" style="width: 200px;" placeholder="输入年龄"></el-input>
        <el-button type="primary" @click="getname1">
            get restful someone
        </el-button>
        <br />
        <el-text v-show="getname1have">{{ getname1Data }}</el-text>

        <br />
        <br />

        <hr />
        <el-text size="large">增</el-text>
        <br />

        <el-input v-model="postname1input" style="width: 200px;" placeholder="输入名字"></el-input>
        <el-button type="primary" @click="postname1">
            post restful
        </el-button>
        <br />
        <el-text v-show="postname1have">{{ postname1Data }}</el-text>

        <br />
        <br />

        <el-input v-model="postname2input" style="width: 200px;" placeholder="输入名字"></el-input>
        <el-input v-model="postage2input" style="width: 200px;" placeholder="输入年龄"></el-input>
        <el-button type="primary" @click="postname2">
            post restful 2
        </el-button>
        <br />
        <el-text v-show="postname2have">{{ postname2Data }}</el-text>

        <br />
        <br />

        <hr />
        <el-text size="large">改</el-text>
        <br />

        <el-input v-model="putname1input" style="width: 200px;" placeholder="输入名字"></el-input>
        <el-input v-model="putage1input" style="width: 200px;" placeholder="输入年龄"></el-input>
        <el-button type="primary" @click="putname1">
            put restful
        </el-button>
        <br />
        <el-text v-show="putname1have">{{ putname1Data }}</el-text>
        <br />
        <br />

        <hr />
        <el-text size="large">删</el-text>
        <br />

        <el-input v-model="deletename1input" style="width: 200px;" placeholder="输入名字"></el-input>
        <el-input v-model="deleteage1input" style="width: 200px;" placeholder="输入年龄"></el-input>
        <el-button type="primary" @click="deletename1">
            delete restful
        </el-button>
        <br />
        <el-text v-show="deletename1have">{{ deletename1Data }}</el-text>
    </div>
</template>

<script lang='ts' setup name='testAxios'>
import { reactive, ref } from "vue"
import axios from "axios";
import { type responseType } from "@/types/index";

let getname1have = ref(false)
let getname1input = ref('')
let getage1input = ref('')
let getname1Data = reactive({})
async function getname1() {
    await axios.get('http://127.0.0.1:5000/test/name/' + getname1input.value + "/" + getage1input.value
    ).then(response => {
        const { code, msg, data }: responseType = response.data

        if (code === 200) {
            getname1have.value = true
            Object.assign(getname1Data, data)
        }
    })
}

let getname2have = ref(false)
let getname2Data = reactive({})
async function getname2() {
    await axios.get('http://127.0.0.1:5000/test/name'
    ).then(response => {
        const { code, msg, data }: responseType = response.data

        if (code === 200) {
            getname2have.value = true
            Object.assign(getname2Data, data)
        }
    })
}


let postname1have = ref(false)
let postname1input = ref('')
let postname1Data = reactive({})
async function postname1() {
    await axios.post('http://127.0.0.1:5000/test/name', postname1input.value, {
        headers: {
            // 默认是 application/x-www-form-urlencoded
            "Content-Type": "application/json"
        }
    })
        .then(response => {
            const { code, msg, data }: responseType = response.data

            if (code === 200) {
                postname1have.value = true
                Object.assign(postname1Data, data)
            }
        })
}

let postname2have = ref(false)
let postname2input = ref('')
let postage2input = ref('')
let postname2Data = reactive({})
async function postname2() {
    await axios.post('http://127.0.0.1:5000/test/name', { 'name': postname2input.value, 'age': postage2input.value })
        .then(response => {
            const { code, msg, data }: responseType = response.data

            if (code === 200) {
                postname2have.value = true
                Object.assign(postname2Data, data)
            }
        })
}

let putname1have = ref(false)
let putname1input = ref('')
let putage1input = ref('')
let putname1Data = reactive({})
async function putname1() {
    await axios.put('http://127.0.0.1:5000/test/name', { 'name': putname1input.value, 'age': putage1input.value })
        .then(response => {
            const { code, msg, data }: responseType = response.data

            if (code === 200) {
                putname1have.value = true
                Object.assign(putname1Data, data)
            }
        })
}

let deletename1have = ref(false)
let deletename1input = ref('')
let deleteage1input = ref('')
let deletename1Data = reactive({})
async function deletename1() {
    await axios.put('http://127.0.0.1:5000/test/name', { 'name': deletename1input.value, 'age': deleteage1input.value })
        .then(response => {
            const { code, msg, data }: responseType = response.data

            if (code === 200) {
                deletename1have.value = true
                Object.assign(deletename1Data, data)
            }
        })
}
</script>

<style scoped></style>