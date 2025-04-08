export interface responseType {
  code: number
  msg: string
  data?: any
}

export interface userType {
  id: string
  username: string
  email: string
  gender: string
  birthday: Date | string
  role?: string
  password?: string
  register_date?: string | Date
}

export interface detectionRecordType {
  id: string
  user_id: string
  origin_image_name: string
  origin_image_url: string
  algorithm: string
  config: string | string[]
  image_width: string
  image_height: string
  elapsed_time: number
  res_image_url: string
  res_image_path: string
  res_kpts_num: string
  res_kpts_path: string
  res_scores_path: string
  res_descriptors_path: string
  detection_date: Date | string
}

export interface uploadImageType {
  havePic: boolean // 是否上传图片
  imagePath: string // 上传图片返回文件路径
  imagePath_url: string // 上传图片返回url路径
}

export interface compaireType {
  AUC5: number
  AUC10: number
  AUC20: number
  Precision?: number
}

export interface compaireResultType {
  type: string
  name: string
  name2?: string
  mid: compaireType
  big: compaireType
  small: compaireType
}

export interface matchingRecordType {
  id: string
  user_id: string

  viz_path: string // 可视化路径
  origin_type: string // 数据源类型

  algorithm_type: string
  algorithm: string
  config: string[] | string

  elapsed_time: number
  save_path: string
  save_path_url: string
  save_matches_path: string
  save_poses_path: string

  matching_date: Date | string
}

export interface mosaicRecordType {
  id: string
  user_id: string

  left_url: string
  right_url: string

  algorithm_type: string
  algorithm: string
  scene: string

  elapsed_time: number
  save_path: string
  save_path_url: string

  mosaic_date: Date | string
}
