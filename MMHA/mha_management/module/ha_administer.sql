-- MySQL dump 10.13  Distrib 5.6.36, for Linux (x86_64)
--
-- Host: localhost    Database: mha_list
-- ------------------------------------------------------
-- Server version	5.6.37-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `mysql_cluster_info`
--

DROP TABLE IF EXISTS `mysql_cluster_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mysql_cluster_info` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cluster_name` varchar(32) DEFAULT NULL COMMENT 'mysql 集群的名字',
  `mvip` varchar(16) NOT NULL COMMENT '主库的虚拟写ip',
  PRIMARY KEY (`id`),
  UNIQUE KEY `mvip_idx` (`mvip`),
  UNIQUE KEY `cluster_name_idx` (`cluster_name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COMMENT='mysql集群信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mysql_table_list`
--

DROP TABLE IF EXISTS `mysql_table_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mysql_table_list` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `cluster_name` varchar(32) DEFAULT NULL COMMENT '集群名',
  `ip` varchar(16) NOT NULL COMMENT '机器ip',
  `domain` varchar(20) NOT NULL COMMENT '机器域名',
  `port` int(10) NOT NULL COMMENT '实例端口',
  `role` varchar(10) NOT NULL COMMENT '实例角色',
  `no_master` int(2) NOT NULL COMMENT '是否有资格提升master 0:有 1:没有',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COMMENT='mysql集群细表';
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-12-01 14:22:25
