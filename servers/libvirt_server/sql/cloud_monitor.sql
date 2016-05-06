/*
 Navicat Premium Data Transfer

 Source Server         : 125.211.198.185
 Source Server Type    : MySQL
 Source Server Version : 50540
 Source Host           : 125.211.198.185
 Source Database       : cloud_monitor

 Target Server Type    : MySQL
 Target Server Version : 50540
 File Encoding         : utf-8

 Date: 01/26/2016 15:32:30 PM
*/

SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `cloud_config`
-- ----------------------------
DROP TABLE IF EXISTS `cloud_config`;
CREATE TABLE `cloud_config` (
  `id` int(64) NOT NULL AUTO_INCREMENT,
  `key` varchar(64) NOT NULL,
  `value` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `cloud_config`
-- ----------------------------
BEGIN;
INSERT INTO `cloud_config` VALUES ('1', 'interval_check', '5'), ('2', 'interval_travelsal', '20'), ('3', 'host', '125.211.198.186');
COMMIT;

-- ----------------------------
--  Table structure for `cloud_result`
-- ----------------------------
DROP TABLE IF EXISTS `cloud_result`;
CREATE TABLE `cloud_result` (
  `batch_id` int(11) NOT NULL,
  `uuid` varchar(128) NOT NULL,
  `attr_name` varchar(20) NOT NULL,
  `value` varchar(100) DEFAULT NULL,
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`batch_id`,`uuid`,`attr_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `cloud_result_in_row`
-- ----------------------------
DROP TABLE IF EXISTS `cloud_result_in_row`;
CREATE TABLE `cloud_result_in_row` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `time` varchar(50) NOT NULL,
  `host` varchar(255) DEFAULT NULL,
  `uuid` varchar(128) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `state` int(11) DEFAULT NULL,
  `max_memory` int(11) DEFAULT NULL,
  `memory_usage` int(11) DEFAULT NULL,
  `number_cpus` int(11) DEFAULT NULL,
  `cpu_usage` float DEFAULT NULL,
  `block_capacity` bigint(11) DEFAULT NULL,
  `block_allocation` bigint(11) DEFAULT NULL,
  `block_physical` bigint(11) DEFAULT NULL,
  `block_rd_reqs` float DEFAULT NULL,
  `block_rd_bytes` float DEFAULT NULL,
  `block_wr_reqs` float DEFAULT NULL,
  `block_wr_bytes` float DEFAULT NULL,
  `block_fl_reqs` float DEFAULT NULL,
  `net_rx_bytes` float DEFAULT NULL,
  `net_rx_packets` float DEFAULT NULL,
  `net_rx_errs` float DEFAULT NULL,
  `net_rx_drop` float DEFAULT NULL,
  `net_tx_bytes` float DEFAULT NULL,
  `net_tx_packets` float DEFAULT NULL,
  `net_tx_errs` float DEFAULT NULL,
  `net_tx_drop` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `cloud_vhost`
-- ----------------------------
DROP TABLE IF EXISTS `cloud_vhost`;
CREATE TABLE `cloud_vhost` (
  `id` int(64) NOT NULL AUTO_INCREMENT,
  `host` varchar(64) NOT NULL,
  `uuid` varchar(256) NOT NULL,
  `enable` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `cloud_vhost`
-- ----------------------------
BEGIN;
INSERT INTO `cloud_vhost` VALUES ('1', '125.211.198.186', '1027147f-9593-4054-94f1-839edac435a3', '1'), ('2', '125.211.198.186', '0d030283-2e85-4637-b2c0-009296628e34', '1');
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
