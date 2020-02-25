SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for proxy
-- ----------------------------
DROP TABLE IF EXISTS `proxy`;
CREATE TABLE `proxy`  (
  `ip` varchar(15) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,
  `port` varchar(5) CHARACTER SET utf8 COLLATE utf8_turkish_ci NOT NULL,
  `country` varchar(50) CHARACTER SET utf8 COLLATE utf8_turkish_ci NULL DEFAULT NULL,
  `create_time` datetime(0) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0),
  `status` tinyint(1) NULL DEFAULT NULL,
  PRIMARY KEY (`ip`, `port`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_turkish_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Triggers structure for table proxy
-- ----------------------------
DROP TRIGGER IF EXISTS `tg_proxy_create_time`;
delimiter ;;
CREATE TRIGGER `tg_proxy_create_time` BEFORE INSERT ON `proxy` FOR EACH ROW SET NEW.create_time = sysdate()
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
