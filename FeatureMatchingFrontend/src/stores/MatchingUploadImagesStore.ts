import { defineStore } from 'pinia'

export const useMatchingUploadImagesStore = defineStore('matchingUploadImages', {
  state: () => ({
    path: '',
    dir_name: '',
    filesInfo: [],
  }),
  actions: {
    setPath(path: string) {
      this.path = path
    },
    setDirName(dir_name: string) {
      this.dir_name = dir_name
    },
    setFilesInfo(filesInfo: any) {
      this.filesInfo = filesInfo
    },

    removePath() {
      this.path = ''
    },
    removeDirName() {
      this.dir_name = ''
    },
    removeFilesInfo() {
      this.filesInfo = []
    },
    init() {
      this.removePath()
      this.removeDirName()
      this.removeFilesInfo()
    },
  },
  persist: true,
})
