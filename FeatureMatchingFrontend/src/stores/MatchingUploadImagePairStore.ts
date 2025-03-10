import { defineStore } from 'pinia'

export const useMatchingUploadImagePairStore = defineStore('matchingUploadImagePair', {
  state: () => ({
    path: '',
    dir_name: '',
    leftpath: '',
    rightpath: '',
    leftpath_url: '',
    rightpath_url: '',
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
    setLeftPathUrl(leftpath_url: string) {
      this.leftpath_url = leftpath_url
    },
    setRightPathUrl(rightpath_url: string) {
      this.rightpath_url = rightpath_url
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
    removeLeftPathUrl() {
      this.leftpath_url = ''
    },
    removeRightPathUrl() {
      this.rightpath_url = ''
    },
    init() {
      this.removePath()
      this.removeDirName()
      this.removeLeftPath()
      this.removeRightPath()
      this.removeLeftPathUrl()
      this.removeRightPathUrl()
    },
  },
  persist: true,
})
