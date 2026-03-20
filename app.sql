

-- Drop table if exists `restaurants`
DROP TABLE IF EXISTS `restaurants`;

-- Table structure for `restaurants`
CREATE TABLE `restaurants` (`id` INT NOT NULL, `name` VARCHAR(120) NOT NULL, `is_active` BOOLEAN NOT NULL, `created_at` DATETIME NOT NULL, `address` VARCHAR(14), `phone` VARCHAR(20) DEFAULT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `restaurants` VALUES (1, 'Warung Soto Megang', 1, '2026-03-16 06:16:47.849585', 'Jl. Soto No. 1', '112');
INSERT INTO `restaurants` VALUES (2, 'Resto B', 1, '2026-03-16 06:16:47.850962', NULL, NULL);

-- Drop table if exists `users`
DROP TABLE IF EXISTS `users`;

-- Table structure for `users`
CREATE TABLE `users` (`id` INT NOT NULL, `restaurant_id` INT, `username` VARCHAR(80) NOT NULL, `password_hash` VARCHAR(255) NOT NULL, `role` VARCHAR(20) NOT NULL, `full_name` VARCHAR(120) DEFAULT NULL, `created_at` DATETIME NOT NULL, `is_active` BOOLEAN NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `users` VALUES (1, NULL, 'superadmin', '$pbkdf2-sha256$29000$FkLoHUNIKeXc./.fk1LqvQ$SwgELnuUCN9Eq.L2IDh.AjGoaIKHkid1OgKT5LLxx1o', 'superadmin', NULL, '2026-03-16 06:16:47.865866', 'true');
INSERT INTO `users` VALUES (2, 1, 'admin_a', '$pbkdf2-sha256$29000$u5eSMqZUao3RuhcCgDAG4A$szerM2GZ5yb/WM8hpP6HCtfdK05gSTyAI.RI.gm0uHI', 'admin', NULL, '2026-03-16 06:16:47.880140', 'true');
INSERT INTO `users` VALUES (3, 1, 'kasir_a', '$pbkdf2-sha256$29000$YAxhDAEAIGQMAaDUujfmHA$jK4wV0A2ttrX1Xp7SW5jprpDKP49gckGx7HbtFV/cAI', 'kasir', 'Bambang', '2026-03-16 06:16:47.892953', 'true');
INSERT INTO `users` VALUES (4, 1, 'koki_a', '$pbkdf2-sha256$29000$YEwppZSSEkJIKQVA6N3bOw$ucrhHOjAu27PmXO/W6TU9bIHRY.8aHWcPHoQIgDJWlc', 'koki', NULL, '2026-03-16 06:16:47.906201', 'true');
INSERT INTO `users` VALUES (5, 1, 'waiter_a', '$pbkdf2-sha256$29000$KmWs9b7XmpMSAuAcwxjjXA$MrMtWkEw0IqU2vwB7SqkC22QbX9ztWYEeX2bWLJxygo', 'waiter', NULL, '2026-03-16 06:16:47.919428', 'true');
INSERT INTO `users` VALUES (6, 2, 'admin_b', '$pbkdf2-sha256$29000$/19LqXWulfK.l/I.h9C6Vw$q6FnLAT0cqcJe1Yr9nlQ.rz4Ofor31RE82DBEBkaKGk', 'admin', NULL, '2026-03-16 06:16:47.934548', 'true');
INSERT INTO `users` VALUES (7, 2, 'kasir_b', '$pbkdf2-sha256$29000$JESo9Z6zttaa07q3lvJ.Tw$BMLxjWNwJE78pKtcqPC2z5q3iIHqaQnh/UGE2YkYCdI', 'kasir', NULL, '2026-03-16 06:16:47.947914', 'true');
INSERT INTO `users` VALUES (8, 2, 'koki_b', '$pbkdf2-sha256$29000$4txbK4VwjpGyVgohJGRMaQ$miZvnx6ZY0V.Jy97L3rnXrF14Ckki0hvNvQfsDsYC2E', 'koki', NULL, '2026-03-16 06:16:47.961497', 'true');
INSERT INTO `users` VALUES (9, 2, 'waiter_b', '$pbkdf2-sha256$29000$/v/fm1PqHcMY45xTynnv3Q$Juoqwx599iV45WQWmiP1ufR.ppQlHNIL9TaKoXDSW6s', 'waiter', NULL, '2026-03-16 06:16:47.974500', 'true');

-- Drop table if exists `orders`
DROP TABLE IF EXISTS `orders`;

-- Table structure for `orders`
CREATE TABLE `orders` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `table_no` VARCHAR(20) NOT NULL, `table_location` VARCHAR(120) NOT NULL, `status` VARCHAR(20) NOT NULL, `created_by` INT NOT NULL, `created_at` DATETIME NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `orders` VALUES (1, 1, '1', 'dekat pohon', 'paid', 2, '2026-03-18 08:14:38.500916');
INSERT INTO `orders` VALUES (2, 1, '2', 'dekat pohon', 'paid', 2, '2026-03-18 08:18:08.451006');
INSERT INTO `orders` VALUES (3, 1, '3', 'dekat pohon', 'paid', 2, '2026-03-18 08:19:15.944034');
INSERT INTO `orders` VALUES (4, 1, '1', '1', 'paid', 2, '2026-03-18 08:22:24.481129');
INSERT INTO `orders` VALUES (5, 1, '23', 'pohon', 'paid', 2, '2026-03-18 08:24:46.841549');
INSERT INTO `orders` VALUES (6, 1, '44', 'pohon', 'paid', 2, '2026-03-18 08:29:09.028969');
INSERT INTO `orders` VALUES (7, 1, '12', '12', 'paid', 2, '2026-03-18 08:30:57.130436');
INSERT INTO `orders` VALUES (8, 1, '21', '21', 'paid', 2, '2026-03-18 08:33:08.782223');
INSERT INTO `orders` VALUES (9, 1, '33', '33', 'paid', 2, '2026-03-18 08:40:06.738248');

-- Drop table if exists `order_items`
DROP TABLE IF EXISTS `order_items`;

-- Table structure for `order_items`
CREATE TABLE `order_items` (`id` INT NOT NULL, `order_id` INT NOT NULL, `menu_item_id` INT NOT NULL, `qty` INT NOT NULL, `price_each` INT NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `order_items` VALUES (1, 1, 1, 1, 12000);
INSERT INTO `order_items` VALUES (2, 2, 1, 2, 12000);
INSERT INTO `order_items` VALUES (3, 3, 1, 1, 12000);
INSERT INTO `order_items` VALUES (4, 3, 2, 1, 15000);
INSERT INTO `order_items` VALUES (5, 4, 1, 1, 12000);
INSERT INTO `order_items` VALUES (6, 4, 2, 1, 15000);
INSERT INTO `order_items` VALUES (7, 5, 1, 1, 12000);
INSERT INTO `order_items` VALUES (8, 6, 1, 2, 2500);
INSERT INTO `order_items` VALUES (9, 7, 1, 1, 3000);
INSERT INTO `order_items` VALUES (10, 1, 1, 1, 9544);
INSERT INTO `order_items` VALUES (11, 1, 2, 1, 6000);
INSERT INTO `order_items` VALUES (12, 2, 1, 1, 9544);
INSERT INTO `order_items` VALUES (13, 2, 2, 1, 6000);
INSERT INTO `order_items` VALUES (14, 3, 1, 1, 9544);
INSERT INTO `order_items` VALUES (15, 3, 2, 1, 6000);
INSERT INTO `order_items` VALUES (16, 4, 1, 1, 9544);
INSERT INTO `order_items` VALUES (17, 5, 1, 1, 9544);
INSERT INTO `order_items` VALUES (18, 6, 1, 1, 9544);
INSERT INTO `order_items` VALUES (19, 6, 2, 1, 6000);
INSERT INTO `order_items` VALUES (20, 7, 1, 1, 9544);
INSERT INTO `order_items` VALUES (21, 8, 1, 1, 9544);
INSERT INTO `order_items` VALUES (22, 9, 1, 1, 9544);
INSERT INTO `order_items` VALUES (23, 9, 2, 1, 6000);

-- Drop table if exists `payments`
DROP TABLE IF EXISTS `payments`;

-- Table structure for `payments`
CREATE TABLE `payments` (`id` INT NOT NULL, `order_id` INT NOT NULL, `paid_by` INT NOT NULL, `method` VARCHAR(30) NOT NULL, `total` INT NOT NULL, `amount_paid` INT NOT NULL, `change` INT NOT NULL, `paid_at` DATETIME NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `payments` VALUES (1, 1, 2, 'cash', 27544, 27544, 0, '2026-03-18 08:17:31.104909');
INSERT INTO `payments` VALUES (2, 5, 2, 'cash', 21544, 21544, 0, '2026-03-18 08:24:56.089054');
INSERT INTO `payments` VALUES (3, 6, 2, 'cash', 20544, 20544, 0, '2026-03-18 08:29:19.046882');
INSERT INTO `payments` VALUES (4, 8, 2, 'cash', 9544, 9544, 0, '2026-03-18 08:33:11.526907');
INSERT INTO `payments` VALUES (5, 9, 2, 'cash', 15544, 30000, 14456, '2026-03-18 08:40:13.986684');
INSERT INTO `payments` VALUES (6, 7, 2, 'cash', 12544, 12544, 0, '2026-03-18 16:23:48.154458');
INSERT INTO `payments` VALUES (7, 8, 2, 'cash', 9544, 9544, 0, '2026-03-18 16:23:54.731924');
INSERT INTO `payments` VALUES (8, 5, 2, 'cash', 21544, 21544, 0, '2026-03-18 16:24:03.572571');
INSERT INTO `payments` VALUES (9, 4, 2, 'cash', 36544, 36544, 0, '2026-03-18 16:24:13.250917');
INSERT INTO `payments` VALUES (10, 3, 2, 'cash', 42544, 42544, 0, '2026-03-18 16:24:20.477927');
INSERT INTO `payments` VALUES (11, 1, 2, 'cash', 27544, 27544, 0, '2026-03-18 16:24:28.941826');
INSERT INTO `payments` VALUES (12, 2, 2, 'cash', 39544, 39544, 0, '2026-03-18 16:24:34.739053');

-- Drop table if exists `alembic_version`
DROP TABLE IF EXISTS `alembic_version`;

-- Table structure for `alembic_version`
CREATE TABLE `alembic_version` (`version_num` VARCHAR(32) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `alembic_version` VALUES ('add_is_active_to_users');

-- Drop table if exists `menu_categories`
DROP TABLE IF EXISTS `menu_categories`;

-- Table structure for `menu_categories`
CREATE TABLE `menu_categories` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `name` VARCHAR(80) NOT NULL, `created_at` DATETIME NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `menu_categories` VALUES (1, 1, 'Makanan', '2026-03-16 08:38:24.559410');
INSERT INTO `menu_categories` VALUES (2, 1, 'Minuman', '2026-03-17 03:07:14.957412');

-- Drop table if exists `kitchen_inventory`
DROP TABLE IF EXISTS `kitchen_inventory`;

-- Table structure for `kitchen_inventory`
CREATE TABLE `kitchen_inventory` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `name` VARCHAR(120) NOT NULL, `unit` VARCHAR(20) NOT NULL, `current_quantity` FLOAT NOT NULL, `created_at` DATETIME NOT NULL, `updated_at` DATETIME NOT NULL, `unit_cost` FLOAT NOT NULL, `price` FLOAT NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `kitchen_inventory` VALUES (1, 1, 'Ayam Potong', 'kg', 3.0, '2026-03-18 05:11:25.378127', '2026-03-18 05:14:53.417150', 37777.777777777774, 37777.777777777774);
INSERT INTO `kitchen_inventory` VALUES (2, 1, 'Beras', 'kg', 4.0, '2026-03-18 05:29:55.082620', '2026-03-18 07:58:58.415582', 18250.0, 18250.0);
INSERT INTO `kitchen_inventory` VALUES (3, 1, 'Susu Indomilk', 'pcs', 1.0, '2026-03-18 06:11:37.024124', '2026-03-18 06:12:34.163639', 10000.0, 10000.0);
INSERT INTO `kitchen_inventory` VALUES (4, 1, 'Air Soda', 'pcs', 5.0, '2026-03-18 06:11:53.472572', '2026-03-18 06:12:13.699282', 3000.0, 3000.0);

-- Drop table if exists `kitchen_transactions`
DROP TABLE IF EXISTS `kitchen_transactions`;

-- Table structure for `kitchen_transactions`
CREATE TABLE `kitchen_transactions` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `inventory_item_id` INT NOT NULL, `type` VARCHAR(10) NOT NULL, `quantity` FLOAT NOT NULL, `cost` FLOAT NOT NULL, `notes` VARCHAR(255) DEFAULT NULL, `created_at` DATETIME NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `kitchen_transactions` VALUES (1, 1, 1, 'IN', 2.0, 70000.0, NULL, '2026-03-18 05:11:54.200148');
INSERT INTO `kitchen_transactions` VALUES (2, 1, 1, 'IN', 1.0, 40000.0, NULL, '2026-03-18 05:12:16.668639');
INSERT INTO `kitchen_transactions` VALUES (3, 1, 1, 'OUT', 1.0, 36666.666666666664, NULL, '2026-03-18 05:14:16.412015');
INSERT INTO `kitchen_transactions` VALUES (4, 1, 1, 'IN', 1.0, 40000.0, NULL, '2026-03-18 05:14:53.472769');
INSERT INTO `kitchen_transactions` VALUES (5, 1, 2, 'IN', 1.0, 15000.0, NULL, '2026-03-18 05:30:12.807069');
INSERT INTO `kitchen_transactions` VALUES (6, 1, 2, 'IN', 1.0, 18000.0, NULL, '2026-03-18 05:49:52.272915');
INSERT INTO `kitchen_transactions` VALUES (7, 1, 4, 'IN', 5.0, 15000.0, NULL, '2026-03-18 06:12:13.706629');
INSERT INTO `kitchen_transactions` VALUES (8, 1, 3, 'IN', 1.0, 10000.0, NULL, '2026-03-18 06:12:34.170864');
INSERT INTO `kitchen_transactions` VALUES (9, 1, 2, 'IN', 1.0, 20000.0, NULL, '2026-03-18 07:10:59.370569');
INSERT INTO `kitchen_transactions` VALUES (10, 1, 2, 'IN', 1.0, 20000.0, NULL, '2026-03-18 07:58:58.422293');

-- Drop table if exists `menu_items`
DROP TABLE IF EXISTS `menu_items`;

-- Table structure for `menu_items`
CREATE TABLE `menu_items` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `name` VARCHAR(120) NOT NULL, `price` INT NOT NULL, `is_active` BOOLEAN NOT NULL, `created_at` DATETIME NOT NULL, `profit` INT NOT NULL, `category_id` INT NOT NULL, `image_url` VARCHAR(255) NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `menu_items` VALUES (1, 1, 'Ayam Goreng', 9544, 1, '2026-03-18 07:09:55.783421', 4000, 1, '/uploads/f3d6c76de589448b9566a7263ea00e96.jpg');
INSERT INTO `menu_items` VALUES (2, 1, 'Susu Soda', 6000, 1, '2026-03-18 08:05:43.237285', 2000, 2, '/uploads/0a3da75135c94ec6baf28f6d53ca00d3.jpg');

-- Drop table if exists `recipes`
DROP TABLE IF EXISTS `recipes`;

-- Table structure for `recipes`
CREATE TABLE `recipes` (`id` INT NOT NULL, `menu_item_id` INT NOT NULL, `inventory_item_id` INT NOT NULL, `quantity` FLOAT NOT NULL, `created_at` DATETIME NOT NULL, `restaurant_id` INT NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `recipes` VALUES (1, 1, 2, 0.1, '2026-03-18 07:09:55.859247', 1);
INSERT INTO `recipes` VALUES (2, 1, 1, 0.1, '2026-03-18 07:09:55.871807', 1);
INSERT INTO `recipes` VALUES (3, 2, 3, 0.1, '2026-03-18 08:05:43.260469', 1);
INSERT INTO `recipes` VALUES (4, 2, 4, 1.0, '2026-03-18 08:05:43.271796', 1);

-- Drop table if exists `recipes_new`
DROP TABLE IF EXISTS `recipes_new`;

-- Table structure for `recipes_new`
CREATE TABLE `recipes_new` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `menu_item_id` INT NOT NULL, `inventory_item_id` INT NOT NULL, `quantity` DOUBLE NOT NULL, `created_at` TIMESTAMP NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Drop table if exists `finance_entries`
DROP TABLE IF EXISTS `finance_entries`;

-- Table structure for `finance_entries`
CREATE TABLE `finance_entries` (`id` INT NOT NULL, `restaurant_id` INT NOT NULL, `created_by` INT NOT NULL, `title` VARCHAR(120) NOT NULL, `entry_type` VARCHAR(20) NOT NULL, `amount` FLOAT NOT NULL, `notes` VARCHAR(255) DEFAULT NULL, `entry_date` DATETIME NOT NULL, `created_at` DATETIME NOT NULL, `updated_at` DATETIME NOT NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
INSERT INTO `finance_entries` VALUES (1, 1, 2, 'transpot belanja', 'expense', 50000.0, NULL, '2026-03-18 00:00:00.000000', '2026-03-18 16:21:31.070945', '2026-03-18 16:21:31.070973');