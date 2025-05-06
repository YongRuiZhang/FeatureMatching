<template>
    <div class="container">
        <el-row class="top">
            <el-col :span="4" :offset="2" class="top-left">
                <div class="name">
                    {{ paper.name }}
                </div>
            </el-col>
            <el-col :span="14" class="top-right">
                <el-row style="height: 100%; padding: 0; justify-content: start; margin: 0;">
                    <el-col :span="24" class="top-right-up">
                        <div class="tag">
                            {{ paper.tag }}
                        </div>
                    </el-col>
                    <el-col :span="24" class="top-right-down">
                        <div class="paperTitle">
                            {{ paper.paperTitle }}
                        </div>
                    </el-col>
                </el-row>
            </el-col>
            <el-col :span="2" style="display: flex; justify-content: end;">
                <el-switch v-model="localLanguage" inline-prompt active-text="中" inactive-text="en"
                    style="--el-switch-on-color: #13ce66; --el-switch-off-color: blue" @change="handleLanguageChange" />
            </el-col>
        </el-row>

        <el-row>
            <el-col :span="20" :offset="2">
                <div class="content" v-if="paper.language === true">
                    {{ paper.content }}
                </div>
                <div class="content" v-if="paper.language === false">
                    {{ paper.content_ch }}
                </div>
            </el-col>
        </el-row>
        <el-row>

        </el-row>
        <el-divider border-style="dotted" />
        <el-row>

        </el-row>
    </div>
</template>

<script lang='ts' setup name='IntroItem'>
import { ref } from 'vue';

const prop = defineProps(['paper']);
const emit = defineEmits(['update-language']);

const localLanguage = ref(prop.paper.language);

const handleLanguageChange = () => {
    emit('update-language', prop.paper.id, !prop.paper.language);
};

</script>

<style scoped>
.container {
    width: 100%;
}

.el-row {
    /* 行距 */
    margin-bottom: 10px;
    margin-top: 10px;
}

.top {
    /* 底部对齐 */
    align-items: flex-end;
}

.top-left,
.top-right {
    /* border: 1px solid black; */
    height: 50px;
}

.top-right-up,
.top-right-down {
    height: 50%;
}

.name {
    font-size: 34px;
    height: 100%;
    display: flex;
    align-items: center;

    font-family: 'Times New Roman', Times, serif;
}

.tag {
    font-family: 'Times New Roman', Times, serif;
    font-style: italic;
}

.paperTitle {
    font-family: 'Times New Roman', Times, serif;
    font-size: 20px;
}

.content {
    font-family: 'Times New Roman', Times, serif;
}
</style>