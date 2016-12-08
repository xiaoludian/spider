/*
Navicat MySQL Data Transfer

Source Server         : localhost_3306
Source Server Version : 50713
Source Host           : localhost:3306
Source Database       : huajiao

Target Server Type    : MYSQL
Target Server Version : 50713
File Encoding         : 65001

Date: 2016-12-08 01:24:09
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `user`
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `FUserId` int(11) NOT NULL COMMENT '花椒ID',
  `FUserName` char(255) NOT NULL DEFAULT '' COMMENT '昵称',
  `FLevel` int(11) NOT NULL DEFAULT '0' COMMENT '等级',
  `FFollow` int(11) NOT NULL DEFAULT '0' COMMENT '关注数',
  `FFollowed` int(11) NOT NULL DEFAULT '0' COMMENT '粉丝数',
  `FSupported` int(11) NOT NULL DEFAULT '0' COMMENT '赞数',
  `FExperience` int(11) NOT NULL DEFAULT '0' COMMENT '经验值',
  `FAvatar` char(255) NOT NULL DEFAULT '' COMMENT '头像地址',
  `FScrapedTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '爬虫时间',
  PRIMARY KEY (`FUserId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of user
-- ----------------------------
