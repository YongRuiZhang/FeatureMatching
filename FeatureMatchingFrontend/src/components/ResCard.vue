<template>
    <div class="bd">
        <h1>{{ prop.name }}</h1>
        <h3>{{ prop.res }}</h3>
    </div>
</template>

<script lang='ts' setup name='ResCard'>
const prop = defineProps(['name', 'res']);
</script>

<style scoped>
.bd {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    /* border: 1px solid black; */
    border-radius: 6px;
    box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.2),
        -5px -5px 10px rgba(255, 255, 255, 1);
}

h1 {
    font-size: 20px;
    color: rgb(255, 110, 97)
}

h3 {
    font-size: 15px;
    color: rgb(61, 90, 127)
}
</style>