<template>
    <div>
        <el-scrollbar class="main">
            <el-row style="height: 6vh;">
                <el-col :span="4">
                    <div id="mytitle">
                        <el-text class="mx-1" style="font-size: 26px">模型比较</el-text>
                    </div>
                </el-col>
            </el-row>
            <el-row>
                <el-col :span="8" :offset="7">
                    <el-text style="display: flex; justify-content: center; font-size: 20px; font-weight: 600;">
                        室内数据集 (ScanNet) 位姿估计
                    </el-text>
                </el-col>
            </el-row>
            <el-row>
                <el-col>
                    <el-table :data="ScanNet_data" style="width: 100%" :span-method="ScanNetSpanMethod"
                        :cell-class-name="ScanNetCellClassName" :cell-style="{ 'text-align': 'center' }"
                        :header-cell-style="{ 'text-align': 'center' }">
                        <el-table-column prop="type" label="" width="120" />
                        <el-table-column label="模型名称">
                            <el-table-column prop="name" width="127" />
                            <el-table-column prop="name2" width="128" />
                        </el-table-column>
                        <el-table-column label="640, 480">
                            <el-table-column prop="mid.AUC5" label="AUC@5 ⬆" width="110" />
                            <el-table-column prop="mid.AUC10" label="AUC@10 ⬆" width="110" />
                            <el-table-column prop="mid.AUC20" label="AUC@20 ⬆" width="110" />
                            <el-table-column prop="mid.Precision" label="Precision ⬆" width="110" />
                        </el-table-column>

                        <el-table-column label="640, 640">
                            <el-table-column prop="big.AUC5" label="AUC@5 ⬆" width="110" />
                            <el-table-column prop="big.AUC10" label="AUC@10 ⬆" width="110" />
                            <el-table-column prop="big.AUC20" label="AUC@20 ⬆" width="110" />
                            <el-table-column prop="big.Precision" label="Precision ⬆" width="110" />
                        </el-table-column>
                        <el-table-column label="480, 480">
                            <el-table-column prop="small.AUC5" label="AUC@5 ⬆" width="110" />
                            <el-table-column prop="small.AUC10" label="AUC@10 ⬆" width="110" />
                            <el-table-column prop="small.AUC20" label="AUC@20 ⬆" width="110" />
                            <el-table-column prop="small.Precision" label="Precision ⬆" width="110" />
                        </el-table-column>
                    </el-table>
                </el-col>
            </el-row>

            <br>

            <el-row>
                <el-col :span="8" :offset="7">
                    <el-text style="display: flex; justify-content: center; font-size: 20px; font-weight: 600;">
                        室外数据集 (MegaDepth) 位姿估计
                    </el-text>
                </el-col>
            </el-row>
            <el-row>
                <el-col>
                    <el-table :data="MegaDepth_data" style="width: 100%" :span-method="MegaDepthSpanMethod"
                        :cell-class-name="MegaDepthCellClassName" :header-cell-style="{ 'text-align': 'center' }"
                        :cell-style="{ 'text-align': 'center' }">
                        <el-table-column prop="type" label="" width="120" />
                        <el-table-column label="模型名称">
                            <el-table-column prop="name" width="127" />
                            <el-table-column prop="name2" width="128" />
                        </el-table-column>
                        <el-table-column label="640, 480">
                            <el-table-column prop="mid.AUC5" label="AUC@5 ⬆" width="110" />
                            <el-table-column prop="mid.AUC10" label="AUC@10 ⬆" width="110" />
                            <el-table-column prop="mid.AUC20" label="AUC@20 ⬆" width="110" />
                            <el-table-column prop="mid.Precision" label="Precision ⬆" width="110" />
                        </el-table-column>

                        <el-table-column label="832, 832">
                            <el-table-column prop="big.AUC5" label="AUC@5 ⬆" width="110" />
                            <el-table-column prop="big.AUC10" label="AUC@10 ⬆" width="110" />
                            <el-table-column prop="big.AUC20" label="AUC@20 ⬆" width="110" />
                            <el-table-column prop="big.Precision" label="Precision ⬆" width="110" />
                        </el-table-column>
                        <el-table-column label="480, 480">
                            <el-table-column prop="small.AUC5" label="AUC@5 ⬆" width="110" />
                            <el-table-column prop="small.AUC10" label="AUC@10 ⬆" width="110" />
                            <el-table-column prop="small.AUC20" label="AUC@20 ⬆" width="110" />
                            <el-table-column prop="small.Precision" label="Precision ⬆" width="110" />
                        </el-table-column>
                    </el-table>
                </el-col>
            </el-row>
        </el-scrollbar>
    </div>
</template>

<script lang='ts' setup name='Comparison'>
import type { compaireResultType } from "@/types"
import type { TableColumnCtx } from "element-plus"
import { } from "vue"

interface SpanMethodProps {
    row: compaireResultType
    column: TableColumnCtx<compaireResultType>
    rowIndex: number
    columnIndex: number
}
const ScanNet_data = [
    {
        type: '稀疏',
        name: 'SuperPoint',
        name2: 'SuperGlue',
        mid: {
            AUC5: 26.14,
            AUC10: 44.52,
            AUC20: 55.59,
            Precision: 73.41,
        },
        big: {
            AUC5: 10.67,
            AUC10: 26.08,
            AUC20: 46.16,
            Precision: 80.86,
        },
        small: {
            AUC5: 21.94,
            AUC10: 36.99,
            AUC20: 48.49,
            Precision: 72.89,
        }
    },
    {
        type: '稀疏',
        name: 'SuperPoint',
        name2: 'BF',
        mid: {
            AUC5: 2.54,
            AUC10: 3.93,
            AUC20: 5.30,
            Precision: 14.26,
        },
        big: {
            AUC5: 1.36,
            AUC10: 2.88,
            AUC20: 4.91,
            Precision: 12.44,
        },
        small: {
            AUC5: 3.68,
            AUC10: 5.17,
            AUC20: 5.92,
            Precision: 14.39,
        }
    },
    {
        type: '稀疏',
        name: 'SuperPoint',
        name2: 'FLANN',
        mid: {
            AUC5: 0.10,
            AUC10: 0.78,
            AUC20: 2.01,
            Precision: 4.49,
        },
        big: {
            AUC5: 0.47,
            AUC10: 1.00,
            AUC20: 2.22,
            Precision: 4.60,
        },
        small: {
            AUC5: 0.12,
            AUC10: 0.79,
            AUC20: 1.88,
            Precision: 4.20,
        }
    },
    {
        type: '稀疏',
        name: 'SIFT',
        name2: 'BF',
        mid: {
            AUC5: 0.89,
            AUC10: 1.01,
            AUC20: 4.69,
            Precision: 9.45,
        },
        big: {
            AUC5: 0.93,
            AUC10: 1.22,
            AUC20: 4.16,
            Precision: 8.38,
        },
        small: {
            AUC5: 0.99,
            AUC10: 1.12,
            AUC20: 3.58,
            Precision: 9.35,
        }
    },
    {
        type: '稀疏',
        name: 'SIFT',
        name2: 'FLANN',
        mid: {
            AUC5: 0.87,
            AUC10: 1.44,
            AUC20: 3.26,
            Precision: 6.23,
        },
        big: {
            AUC5: 0.65,
            AUC10: 0.92,
            AUC20: 2.98,
            Precision: 5.84,
        },
        small: {
            AUC5: 0.97,
            AUC10: 1.42,
            AUC20: 3.48,
            Precision: 6.39,
        }
    },
    {
        type: '稀疏',
        name: 'ORB',
        name2: 'BF',
        mid: {
            AUC5: 1.19,
            AUC10: 2.34,
            AUC20: 4.52,
            Precision: 11.61,
        },
        big: {
            AUC5: 1.38,
            AUC10: 2.74,
            AUC20: 5.10,
            Precision: 13.43,
        },
        small: {
            AUC5: 1.22,
            AUC10: 2.12,
            AUC20: 4.89,
            Precision: 12.01,
        }
    },
    {
        type: '稀疏',
        name: 'ORB',
        name2: 'FLANN',
        mid: {
            AUC5: 0.33,
            AUC10: 0.84,
            AUC20: 3.04,
            Precision: 9.99,
        },
        big: {
            AUC5: 0.22,
            AUC10: 0.97,
            AUC20: 3.21,
            Precision: 10.34,
        },
        small: {
            AUC5: 0.54,
            AUC10: 1.02,
            AUC20: 3.15,
            Precision: 10.14,
        }
    },
    {
        type: '半稀疏',
        name: 'LoFTR',
        mid: {
            AUC5: 23.82,
            AUC10: 43.48,
            AUC20: 55.07,
            Precision: 70.12,
        },
        big: {
            AUC5: 10.69,
            AUC10: 21.27,
            AUC20: 41.75,
            Precision: 68.41,
        },
        small: {
            AUC5: 18.77,
            AUC10: 38.13,
            AUC20: 52.40,
            Precision: 75.33,
        }
    },
    {
        type: '半稀疏',
        name: 'ASpanFormer',
        mid: {
            AUC5: 26.93,
            AUC10: 49.62,
            AUC20: 61.48,
            Precision: 73.17,
        },
        big: {
            AUC5: 10.04,
            AUC10: 38.27,
            AUC20: 52.29,
            Precision: 71.35,
        },
        small: {
            AUC5: 20.30,
            AUC10: 40.89,
            AUC20: 57.11,
            Precision: 65.69,
        }
    },
    {
        type: '稠密',
        name: 'DKM',
        mid: {
            AUC5: 27.76,
            AUC10: 49.65,
            AUC20: 69.39,
            Precision: 71.22,
        },
        big: {
            AUC5: 27.20,
            AUC10: 48.96,
            AUC20: 67.55,
            Precision: 68.91,
        },
        small: {
            AUC5: 26.55,
            AUC10: 47.97,
            AUC20: 65.82,
            Precision: 67.79,
        }
    },
]
const ScanNetSpanMethod = ({
    rowIndex,
    columnIndex,
}: SpanMethodProps) => {
    if (columnIndex === 0) {
        if (rowIndex < 7 && rowIndex === 0) {
            return [7, 1]
        } else if (rowIndex < 7 && rowIndex !== 0) {
            return [0, 0]
        }
        if (rowIndex < 9 && rowIndex === 7) {
            return [2, 1]
        } else if (rowIndex < 9 && rowIndex !== 7) {
            return [0, 0]
        }
    }

    if (columnIndex === 1) {
        if (rowIndex < 3 && rowIndex === 0) {
            return [3, 1]
        } else if (rowIndex < 3 && rowIndex !== 0) {
            return [0, 0]
        }

        if (rowIndex < 5 && rowIndex === 3) {
            return [2, 1]
        } else if (rowIndex < 5 && rowIndex !== 3) {
            return [0, 0]
        }

        if (rowIndex < 7 && rowIndex === 5) {
            return [2, 1]
        } else if (rowIndex < 7 && rowIndex !== 5) {
            return [0, 0]
        }
    }

    if (rowIndex >= 7) {
        if (columnIndex === 1) {
            return [1, 2]
        } else if (columnIndex === 2) {
            return [0, 0]
        }
    }
}

const MegaDepth_data = [
    {
        type: '稀疏',
        name: 'SuperPoint',
        name2: 'SuperGlue',
        mid: {
            AUC5: 51.07,
            AUC10: 67.30,
            AUC20: 78.91,
            Precision: 74.14,
        },
        big: {
            AUC5: 49.17,
            AUC10: 65.29,
            AUC20: 77.65,
            Precision: 76.11,
        },
        small: {
            AUC5: 46.14,
            AUC10: 62.71,
            AUC20: 74.40,
            Precision: 73.88,
        }
    },
    {
        type: '稀疏',
        name: 'SuperPoint',
        name2: 'BF',
        mid: {
            AUC5: 3.64,
            AUC10: 4.73,
            AUC20: 5.99,
            Precision: 18.26,
        },
        big: {
            AUC5: 3.60,
            AUC10: 5.18,
            AUC20: 6.91,
            Precision: 17.34,
        },
        small: {
            AUC5: 3.90,
            AUC10: 5.61,
            AUC20: 6.73,
            Precision: 17.39,
        }
    },
    {
        type: '稀疏',
        name: 'SuperPoint',
        name2: 'FLANN',
        mid: {
            AUC5: 0.90,
            AUC10: 3.78,
            AUC20: 5.61,
            Precision: 9.49,
        },
        big: {
            AUC5: 1.47,
            AUC10: 3.05,
            AUC20: 4.52,
            Precision: 10.46,
        },
        small: {
            AUC5: 0.98,
            AUC10: 2.15,
            AUC20: 4.28,
            Precision: 9.10,
        }
    },
    {
        type: '稀疏',
        name: 'SIFT',
        name2: 'BF',
        mid: {
            AUC5: 1.69,
            AUC10: 2.41,
            AUC20: 4.94,
            Precision: 9.35,
        },
        big: {
            AUC5: 1.33,
            AUC10: 2.62,
            AUC20: 4.36,
            Precision: 8.77,
        },
        small: {
            AUC5: 1.99,
            AUC10: 2.72,
            AUC20: 4.58,
            Precision: 9.33,
        }
    },
    {
        type: '稀疏',
        name: 'SIFT',
        name2: 'FLANN',
        mid: {
            AUC5: 1.78,
            AUC10: 2.64,
            AUC20: 4.16,
            Precision: 8.23,
        },
        big: {
            AUC5: 1.15,
            AUC10: 1.92,
            AUC20: 3.98,
            Precision: 7.84,
        },
        small: {
            AUC5: 1.00,
            AUC10: 2.79,
            AUC20: 4.08,
            Precision: 8.39,
        }
    },
    {
        type: '稀疏',
        name: 'ORB',
        name2: 'BF',
        mid: {
            AUC5: 1.12,
            AUC10: 2.64,
            AUC20: 4.12,
            Precision: 10.61,
        },
        big: {
            AUC5: 2.38,
            AUC10: 3.79,
            AUC20: 5.12,
            Precision: 13.63,
        },
        small: {
            AUC5: 2.12,
            AUC10: 3.32,
            AUC20: 4.95,
            Precision: 13.08,
        }
    },
    {
        type: '稀疏',
        name: 'ORB',
        name2: 'FLANN',
        mid: {
            AUC5: 0.63,
            AUC10: 1.56,
            AUC20: 3.74,
            Precision: 10.99,
        },
        big: {
            AUC5: 0.72,
            AUC10: 1.67,
            AUC20: 4.35,
            Precision: 11.34,
        },
        small: {
            AUC5: 1.34,
            AUC10: 2.02,
            AUC20: 4.35,
            Precision: 9.90,
        }
    },
    {
        type: '半稀疏',
        name: 'LoFTR',
        mid: {
            AUC5: 59.02,
            AUC10: 73.18,
            AUC20: 91.37,
            Precision: 74.22,
        },
        big: {
            AUC5: 57.39,
            AUC10: 69.17,
            AUC20: 76.75,
            Precision: 69.91,
        },
        small: {
            AUC5: 47.51,
            AUC10: 63.24,
            AUC20: 74.61,
            Precision: 69.93,
        }
    },
    {
        type: '半稀疏',
        name: 'ASpanFormer',
        mid: {
            AUC5: 46.96,
            AUC10: 49.65,
            AUC20: 61.51,
            Precision: 72.27,
        },
        big: {
            AUC5: 60.14,
            AUC10: 72.57,
            AUC20: 83.19,
            Precision: 74.05,
        },
        small: {
            AUC5: 45.61,
            AUC10: 63.29,
            AUC20: 73.81,
            Precision: 73.59,
        }
    },
    {
        type: '稠密',
        name: 'DKM',
        mid: {
            AUC5: 62.77,
            AUC10: 74.98,
            AUC20: 82.41,
            Precision: 72.21,
        },
        big: {
            AUC5: 59.73,
            AUC10: 73.08,
            AUC20: 79.95,
            Precision: 76.19,
        },
        small: {
            AUC5: 59.07,
            AUC10: 72.27,
            AUC20: 80.41,
            Precision: 77.19,
        }
    },
]
const MegaDepthSpanMethod = ({
    rowIndex,
    columnIndex,
}: SpanMethodProps) => {
    if (columnIndex === 0) {
        if (rowIndex < 7 && rowIndex === 0) {
            return [7, 1]
        } else if (rowIndex < 7 && rowIndex !== 0) {
            return [0, 0]
        }
        if (rowIndex < 9 && rowIndex === 7) {
            return [2, 1]
        } else if (rowIndex < 9 && rowIndex !== 7) {
            return [0, 0]
        }
    }

    if (columnIndex === 1) {
        if (rowIndex < 3 && rowIndex === 0) {
            return [3, 1]
        } else if (rowIndex < 3 && rowIndex !== 0) {
            return [0, 0]
        }

        if (rowIndex < 5 && rowIndex === 3) {
            return [2, 1]
        } else if (rowIndex < 5 && rowIndex !== 3) {
            return [0, 0]
        }

        if (rowIndex < 7 && rowIndex === 5) {
            return [2, 1]
        } else if (rowIndex < 7 && rowIndex !== 5) {
            return [0, 0]
        }
    }

    if (rowIndex >= 7) {
        if (columnIndex === 1) {
            return [1, 2]
        } else if (columnIndex === 2) {
            return [0, 0]
        }
    }
}


const extractColumnValues = (data: any[], columnIndex: number, part: 'mid' | 'big' | 'small'): number[] => {
    return data.map((item) => {
        const keys = Object.keys(data[0][part]);
        const key = keys[columnIndex];

        return parseFloat(item[part][key]);
    });
};
const getRankClass = (rowIndex: number, columnIndex: number, data: any[]): string => {
    if (columnIndex > 2) {
        const partIndex = Math.floor((columnIndex - 3) / 4);
        const part = partIndex === 0 ? 'mid' : partIndex === 1 ? 'big' : 'small';
        const localColumnIndex = (columnIndex - 3) % 4;

        const columnValues = extractColumnValues(data, localColumnIndex, part);

        const sortedValues = [...columnValues].sort((a, b) => b - a).slice(0, 3);

        const keys = Object.keys(data[0][part]);
        const key = keys[localColumnIndex];
        const currentValue = parseFloat(data[rowIndex][part][key]);

        if (currentValue === sortedValues[0]) {
            return 'best-cell';
        } else if (currentValue === sortedValues[1]) {
            return 'second-cell';
        } else if (currentValue === sortedValues[2]) {
            return 'third-cell';
        }
    }

    return '';
};
const ScanNetCellClassName = ({
    row,
    column,
    rowIndex,
    columnIndex
}: SpanMethodProps) => {
    return getRankClass(rowIndex, columnIndex, ScanNet_data);
}

const MegaDepthCellClassName = ({
    row,
    column,
    rowIndex,
    columnIndex
}: SpanMethodProps) => {
    return getRankClass(rowIndex, columnIndex, MegaDepth_data);
}

</script>

<style scoped>
.main {
    height: 100%;
}

:deep(.best-cell) {
    background: #c5e5cf;
}

:deep(.second-cell) {
    background: #e7f5ec;
}

:deep(.third-cell) {
    background: #fef8ca;
}
</style>