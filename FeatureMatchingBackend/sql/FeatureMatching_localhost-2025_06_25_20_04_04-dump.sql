-- MySQL dump 10.13  Distrib 8.0.32, for macos13 (arm64)
--
-- Host: 127.0.0.1    Database: FeatureMatching
-- ------------------------------------------------------
-- Server version	8.0.32

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('8f210eb69483');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_detection`
--

DROP TABLE IF EXISTS `t_detection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_detection` (
  `id` varchar(128) NOT NULL,
  `user_id` varchar(128) NOT NULL,
  `origin_image_name` varchar(128) NOT NULL COMMENT '原图片名（无uuid）',
  `origin_image_url` varchar(256) NOT NULL COMMENT '原图片url，用于显示',
  `algorithm` varchar(64) NOT NULL COMMENT '使用算法',
  `config` varchar(256) NOT NULL COMMENT '参数',
  `image_width` int NOT NULL,
  `image_height` int NOT NULL,
  `elapsed_time` float NOT NULL,
  `res_image_url` varchar(256) NOT NULL COMMENT '结果图片url',
  `res_kpts_num` int NOT NULL COMMENT 'kpts数量',
  `res_image_path` varchar(256) NOT NULL COMMENT '结果图片路径，用于下载',
  `res_kpts_path` varchar(256) NOT NULL COMMENT '结果kpts路径，用于下载',
  `record_date` datetime NOT NULL COMMENT '产生记录的时间',
  `origin_image_path` varchar(256) NOT NULL COMMENT '原图片Path',
  `res_scores_path` varchar(256) DEFAULT NULL COMMENT '结果分数路径，用于下载',
  `res_descriptors_path` varchar(256) DEFAULT NULL COMMENT '结果描述子路径，用于下载',
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `t_detection_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_detection`
--

LOCK TABLES `t_detection` WRITE;
/*!40000 ALTER TABLE `t_detection` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_detection` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_matching`
--

DROP TABLE IF EXISTS `t_matching`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_matching` (
  `id` varchar(128) NOT NULL,
  `user_id` varchar(128) NOT NULL,
  `record_date` datetime NOT NULL COMMENT '产生记录的时间',
  `data_id` varchar(128) NOT NULL,
  `origin_type` varchar(64) NOT NULL COMMENT '数据源类型',
  `algorithm_type` varchar(64) NOT NULL COMMENT '使用算法类型',
  `algorithm` varchar(64) NOT NULL COMMENT '使用算法',
  `config` varchar(256) NOT NULL COMMENT '参数',
  `elapsed_time` float NOT NULL COMMENT '耗时',
  `save_path` varchar(256) NOT NULL COMMENT '可视化结果路径，用于下载',
  `save_path_url` varchar(256) NOT NULL COMMENT '可视化结果url，用于预览',
  `save_matches_path` varchar(256) NOT NULL COMMENT '结果matches路径，用于下载',
  `save_poses_path` varchar(256) DEFAULT NULL COMMENT '结果poses路径，用于下载',
  PRIMARY KEY (`id`),
  KEY `data_id` (`data_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `t_matching_ibfk_1` FOREIGN KEY (`data_id`) REFERENCES `t_upload_data` (`id`),
  CONSTRAINT `t_matching_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_matching`
--

LOCK TABLES `t_matching` WRITE;
/*!40000 ALTER TABLE `t_matching` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_matching` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_mosaic`
--

DROP TABLE IF EXISTS `t_mosaic`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_mosaic` (
  `id` varchar(128) NOT NULL,
  `user_id` varchar(128) NOT NULL,
  `record_date` datetime NOT NULL COMMENT '产生记录的时间',
  `data_id` varchar(128) NOT NULL,
  `algorithm_type` varchar(64) NOT NULL COMMENT '使用算法类型',
  `algorithm` varchar(64) NOT NULL COMMENT '使用算法',
  `elapsed_time` float NOT NULL COMMENT '耗时',
  `save_path` varchar(256) NOT NULL COMMENT '可视化结果路径，用于下载',
  `save_path_url` varchar(256) NOT NULL COMMENT '可视化结果url，用于预览',
  `scene` varchar(256) NOT NULL COMMENT '场景',
  PRIMARY KEY (`id`),
  KEY `data_id` (`data_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `t_mosaic_ibfk_1` FOREIGN KEY (`data_id`) REFERENCES `t_upload_data` (`id`),
  CONSTRAINT `t_mosaic_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `t_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_mosaic`
--

LOCK TABLES `t_mosaic` WRITE;
/*!40000 ALTER TABLE `t_mosaic` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_mosaic` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_upload_data`
--

DROP TABLE IF EXISTS `t_upload_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_upload_data` (
  `id` varchar(128) NOT NULL,
  `left_url` varchar(256) DEFAULT NULL COMMENT '左图片url',
  `right_url` varchar(256) DEFAULT NULL COMMENT '右图片url',
  `video_url` varchar(256) DEFAULT NULL COMMENT '视频url',
  `path` varchar(256) NOT NULL COMMENT '路径',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_upload_data`
--

LOCK TABLES `t_upload_data` WRITE;
/*!40000 ALTER TABLE `t_upload_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `t_upload_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `t_user`
--

DROP TABLE IF EXISTS `t_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `t_user` (
  `id` varchar(128) NOT NULL,
  `username` varchar(64) NOT NULL,
  `password` varchar(128) NOT NULL COMMENT '密码',
  `role` varchar(64) NOT NULL COMMENT '角色',
  `register_date` datetime NOT NULL,
  `email` varchar(128) DEFAULT NULL COMMENT '邮箱地址',
  `birthday` date DEFAULT NULL,
  `gender` varchar(16) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_t_user_username` (`username`),
  KEY `ix_t_user_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `t_user`
--

LOCK TABLES `t_user` WRITE;
/*!40000 ALTER TABLE `t_user` DISABLE KEYS */;
INSERT INTO `t_user` VALUES ('087e7a8b-2948-4061-a6c1-1baf4fd6fa2b','小冯','123456','guest','2025-02-19 21:12:28','','2003-07-11','female'),('130f3887-029e-4fef-98f5-2e1ea457f49a','xiaobai','xiaobai','guest','2025-02-19 21:10:06','xiaobai@gmail.com','2025-02-05','female'),('19b8b4b7-c435-4088-8d5c-ce7e0f049252','秋白','123456','admin','2025-02-19 21:08:41','','2025-02-01','male'),('1ec44f70-8642-4a32-86e3-9d869dcfd108','小王','123456','guest','2025-02-19 21:12:33','',NULL,'male'),('26ce218f-8bc9-4c86-991a-4026aeb439e2','honey','123456','guest','2025-02-20 16:35:56','honey@qq.com','2020-02-04','female'),('2f071e63-6744-410f-9faf-e39d8be81a24','xiaohei','123456','guest','2025-02-19 21:10:12','xiaohei@gmail.com','2025-01-31','female'),('426a791e-4ae0-4a4b-ab50-9dad585cfa1b','王五','123456','guest','2025-02-19 21:06:29','',NULL,'male'),('4967d9d5-0605-4713-8e0a-e79bcbbd2377','zhangyr','123456','admin','2025-02-19 21:08:18','zhangyr@gmail.com','2026-06-26','male'),('4a2f267c-9c0c-4a14-885e-ebbe56c113da','Jack','123456','guest','2025-02-19 21:09:51','Jack@gmail.com',NULL,'male'),('4d1f8fc9-d544-4e96-9078-90cc935f77a4','小赵','123456','guest','2025-02-19 21:12:06','','2023-02-11','female'),('53423eda-9553-47d5-8a3b-78f6ceb93821','xxx','xxx123','guest','2025-05-20 16:41:10','',NULL,'male'),('560881cb-0f96-4caa-bcc9-b98c273e2c7f','zhanghao','123456','guest','2025-06-25 12:39:09','',NULL,'male'),('56524e7f-9f1a-40e7-b7b0-b63cee0e051b','John','123456','guest','2025-02-19 21:09:56','John@gmail.com','2025-02-13','male'),('5c14d5a2-08da-4b96-8e16-19e1e89d8ba2','zyr','123456','admin','2025-02-19 21:08:11','zyr@gmail.com','2003-07-13','male'),('6291075a-79ee-4b2a-9110-911844dca929','管理员','123456','admin','2025-02-19 21:11:47','',NULL,'male'),('661649a2-d6ef-4e4e-9b1c-88566b9168b6','小白','123456','guest','2025-02-19 21:10:17','','2025-02-06','female'),('678dca67-effe-4388-a7c6-00173b96a015','小李','123456','guest','2025-02-19 21:12:10','xiaoli@163.com',NULL,'male'),('708cc440-eddd-4b18-9124-3479c9718167','小黑','123456','guest','2025-02-19 21:10:21','',NULL,'male'),('78416080-a1fb-4ee6-8db9-fadcb9c0d2b2','张三','123456','guest','2025-02-19 21:06:59','','2020-11-21','male'),('7bae42ff-9550-4185-acc6-21f99c7cf2a3','我是人','123456','guest','2025-02-19 21:12:01','',NULL,'male'),('81df46cd-6080-47a3-9d85-50a286517456','zhaoliu','123456','guest','2025-02-19 21:08:01','zhaoliu@qq.com',NULL,'female'),('842ee299-9d91-4104-9099-75f190645bf1','fengyunyun','123456','admin','2025-02-19 21:10:37','fengyunyun@edu.com',NULL,'female'),('8bd60957-ed90-4cfc-be77-56a0bc0c752c','zhangsan','123456','guest','2025-02-19 21:03:51','zhangsan@qq.com','2012-12-31','male'),('8be0f994-06c1-4b5d-af6d-cc47051a5290','Mary','123456','guest','2025-02-19 21:10:01','',NULL,'female'),('8cdfb9e6-224a-42b8-9ca7-ec41775ebd09','李四','123456','guest','2025-02-19 21:06:54','Mary@gmail.com',NULL,'male'),('988adf5e-67aa-44e2-a98d-72fe54407e47','zhangqiubai','123456','guest','2025-02-19 21:08:33','',NULL,'male'),('9f1de039-3f48-466b-adb4-d656037fad7c','qiubai','123456','admin','2025-02-19 21:08:28','qiubai@qq.com','1999-05-15','female'),('a8ecf6d1-102a-46a3-9e6a-5797f3efbd4f','qiufengshuishui','123456','guest','2025-02-19 21:10:48','',NULL,'female'),('ae4f92e9-caaf-4c91-8371-f7232822c105','gule','123456','guest','2025-02-19 21:08:47','gule@163.com',NULL,'female'),('b0d30b42-e735-454b-a422-5178967efea1','小张','123456','guest','2025-02-19 21:12:20','',NULL,'male'),('bbcf5911-1f45-41c2-9246-129d35153f48','lisi','lisi1234','guest','2025-02-19 21:07:05','lisi@163.com','2001-10-10','male'),('c0982124-e649-415a-97f4-1d440a78d5e9','小黄','123456','guest','2025-02-19 21:10:26','',NULL,'male'),('cc0ff635-5500-451e-b991-496a98ec5382','hanhan','123456','guest','2025-02-20 16:34:56','',NULL,'male'),('ce699c6b-59a3-49d1-ac38-fa6fc452a825','Alice','123456','guest','2025-02-20 16:36:42','Alice@163.com','2018-03-01','female'),('d0a3baa0-9322-4f64-91a2-db3e4c52361f','admin','admin','admin','2025-02-19 21:03:41','admin@gmail','1970-01-01','female'),('d5556353-e081-4efa-b294-71f1f6cc079b','张永锐','zyr123','admin','2025-02-21 22:10:00','zhangyongrui@gmail.com','2003-07-13','male'),('d95f904d-6fd0-4428-b08d-31cd1b04b50d','赵六','123456','guest','2025-02-19 21:06:37','',NULL,'male'),('df84141c-fe67-4046-ab99-fbb2f32533ec','wangwu','123456','guest','2025-02-19 21:07:10','wangwu@gmail',NULL,'male'),('e5275b68-b203-40fa-8621-f1ffa62146dd','xiaohuang','123456','guest','2025-02-19 21:10:31','xiaohuang@gmail',NULL,'male'),('f1b65715-965d-4e0d-abd6-6c197d6ce5e0','小航','123456','guest','2025-02-19 21:12:15','',NULL,'female'),('f4617b50-f08a-4449-99e1-329d5e76442e','zhangyongrui','123456','admin','2025-02-19 21:08:23','zyr@163.com','2003-07-13','male');
/*!40000 ALTER TABLE `t_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-06-25 20:04:04
