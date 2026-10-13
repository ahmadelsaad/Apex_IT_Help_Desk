CREATE DATABASE  IF NOT EXISTS `it_help_desk` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `it_help_desk`;
-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: it_help_desk
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `employee`
--

DROP TABLE IF EXISTS `employee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employee` (
  `employee_id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `department` varchar(45) NOT NULL,
  `work_email` varchar(100) NOT NULL,
  PRIMARY KEY (`employee_id`),
  UNIQUE KEY `Work_Email_UNIQUE` (`work_email`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `issue_category`
--

DROP TABLE IF EXISTS `issue_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `issue_category` (
  `category_id` int NOT NULL AUTO_INCREMENT,
  `category_name` varchar(45) NOT NULL,
  `sector_id` int NOT NULL,
  PRIMARY KEY (`category_id`),
  KEY `fk_issue_category_sector_idx` (`sector_id`),
  CONSTRAINT `fk_issue_category_sector` FOREIGN KEY (`sector_id`) REFERENCES `it_sector` (`sector_id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `it_sector`
--

DROP TABLE IF EXISTS `it_sector`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `it_sector` (
  `sector_id` int NOT NULL AUTO_INCREMENT,
  `sector_name` varchar(45) NOT NULL,
  PRIMARY KEY (`sector_id`),
  UNIQUE KEY `Sector_Name_UNIQUE` (`sector_name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `technician`
--

DROP TABLE IF EXISTS `technician`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `technician` (
  `tech_id` int NOT NULL AUTO_INCREMENT,
  `tech_name` varchar(60) NOT NULL,
  `tech_email` varchar(100) NOT NULL,
  `availability` tinyint NOT NULL DEFAULT '1',
  `sector_id` int NOT NULL,
  PRIMARY KEY (`tech_id`),
  UNIQUE KEY `tech_email_UNIQUE` (`tech_email`),
  KEY `fk_tech_sector_idx` (`sector_id`),
  CONSTRAINT `fk_tech_sector` FOREIGN KEY (`sector_id`) REFERENCES `it_sector` (`sector_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticket`
--

DROP TABLE IF EXISTS `ticket`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket` (
  `ticket_id` int NOT NULL AUTO_INCREMENT,
  `employee_id` int NOT NULL,
  `category_id` int NOT NULL,
  `issue_desc` varchar(500) NOT NULL,
  `ppl_affected` int NOT NULL,
  `work_impact` varchar(20) NOT NULL,
  `workaround` tinyint NOT NULL DEFAULT '1',
  `priority` varchar(20) NOT NULL,
  `status` varchar(45) NOT NULL DEFAULT 'New',
  `ticket_date_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `emp_update` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`ticket_id`),
  KEY `fk_ticket_employee_id_idx` (`employee_id`),
  KEY `fk_ticket_category_id_idx` (`category_id`),
  CONSTRAINT `fk_ticket_category_id` FOREIGN KEY (`category_id`) REFERENCES `issue_category` (`category_id`),
  CONSTRAINT `fk_ticket_employee_id` FOREIGN KEY (`employee_id`) REFERENCES `employee` (`employee_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ticket_assignment`
--

DROP TABLE IF EXISTS `ticket_assignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ticket_assignment` (
  `assign_id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int NOT NULL,
  `tech_id` int NOT NULL,
  `assign_date_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `active_assignment` tinyint NOT NULL DEFAULT '1',
  PRIMARY KEY (`assign_id`),
  KEY `fk_assign_ticket_id_idx` (`ticket_id`),
  KEY `fk_assign_tech_id_idx` (`tech_id`),
  CONSTRAINT `fk_assign_tech_id` FOREIGN KEY (`tech_id`) REFERENCES `technician` (`tech_id`),
  CONSTRAINT `fk_assign_ticket_id` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`)
) ENGINE=InnoDB AUTO_INCREMENT=952 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-12 23:54:41
