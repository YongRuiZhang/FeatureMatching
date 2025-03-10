import { defineStore } from 'pinia'

export const useMatchingUploadImagePairStore = defineStore('matchingUploadImagePair', {
  state: () => ({
    path: '',
    dir_name: '',
    leftpath: '',
    rightpath: '',
  }),
  actions: {
    setPath(path: string) {
      this.path = path
    },
    setDirName(dir_name: string) {
      this.dir_name = dir_name
    },
    setLeftPath(leftpath: string) {
      this.leftpath = leftpath
    },
    setRightPath(rightpath: string) {
      this.rightpath = rightpath
    },

    removePath() {
      this.path = ''
    },
    removeDirName() {
      this.dir_name = ''
    },
    removeLeftPath() {
      this.leftpath = ''
    },
    removeRightPath() {
      this.rightpath = ''
    },
    init() {
      this.removePath()
      this.removeDirName()
      this.removeLeftPath()
      this.removeRightPath()
    },
  },
  persist: true,
})
