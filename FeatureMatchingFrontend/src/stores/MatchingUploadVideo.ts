import { defineStore } from 'pinia'

export const useMatchingUploadVideoStore = defineStore('matchingUploadVideo', {
  state: () => ({
    path: '',
    dir_name: '',
    filepath: '',
    filepath_url: '',
  }),
  actions: {
    setPath(path: string) {
      this.path = path
    },
    setDirName(dir_name: string) {
      this.dir_name = dir_name
    },
    setFilePath(filepath: string) {
      this.filepath = filepath
    },
    setFilePathUrl(filepath_url: string) {
      this.filepath_url = filepath_url
    },

    removePath() {
      this.path = ''
    },
    removeDirName() {
      this.dir_name = ''
    },
    removeFilePath() {
      this.filepath = ''
    },
    removeFilePathUrl() {
      this.filepath_url = ''
    },
    init() {
      this.removePath()
      this.removeDirName()
      this.removeFilePath()
      this.removeFilePathUrl()
    },
  },
  persist: true,
})
