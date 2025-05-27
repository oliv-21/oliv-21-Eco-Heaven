-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 10, 2025 at 06:50 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.1.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `ecoheaven_db`
--
CREATE DATABASE IF NOT EXISTS `ecoheaven_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `ecoheaven_db`;

-- --------------------------------------------------------

--
-- Table structure for table `addresses_buyer`
--

CREATE TABLE `addresses_buyer` (
  `address_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `houseNo` varchar(50) NOT NULL,
  `street` varchar(50) NOT NULL,
  `barangay` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `Province` varchar(50) NOT NULL,
  `postal_code` varchar(10) NOT NULL,
  `address_type` enum('Home','Work','Other') DEFAULT 'Home'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `addresses_buyer`
--

INSERT INTO `addresses_buyer` (`address_id`, `buyer_id`, `houseNo`, `street`, `barangay`, `city`, `Province`, `postal_code`, `address_type`) VALUES
(22, 4, 'wewew', 'ew', 'Diaat', 'Maria Aurora', 'Aurora', 'wewe', 'Home'),
(24, 1001, 'wewew', 'ew', 'Tamak', 'Padre Garcia', 'Batangas', 'wewe', 'Home');

-- --------------------------------------------------------

--
-- Table structure for table `addresses_rider`
--

CREATE TABLE `addresses_rider` (
  `address_id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `houseNo` varchar(50) NOT NULL,
  `street` varchar(50) NOT NULL,
  `barangay` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `Province` varchar(50) NOT NULL,
  `postal_code` varchar(10) NOT NULL,
  `address_type` enum('Home','Work','Other') DEFAULT 'Home'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `addresses_rider`
--

INSERT INTO `addresses_rider` (`address_id`, `rider_id`, `houseNo`, `street`, `barangay`, `city`, `Province`, `postal_code`, `address_type`) VALUES
(1, 3006, '12', 'magsaysay', 'Poblacion', 'Cavinti', 'Laguna', '4013', 'Home'),
(2, 3007, '', 'MAGSAYSAY', 'Poblacion', 'Cavinti', 'Laguna', '4013', 'Home');

-- --------------------------------------------------------

--
-- Table structure for table `addresses_seller`
--

CREATE TABLE `addresses_seller` (
  `address_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `houseNo` varchar(50) NOT NULL,
  `street` varchar(50) NOT NULL,
  `barangay` varchar(50) NOT NULL,
  `city` varchar(50) NOT NULL,
  `Province` varchar(50) NOT NULL,
  `postal_code` varchar(10) NOT NULL,
  `address_type` enum('Home','Work','Other') DEFAULT 'Home'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `addresses_seller`
--

INSERT INTO `addresses_seller` (`address_id`, `seller_id`, `houseNo`, `street`, `barangay`, `city`, `Province`, `postal_code`, `address_type`) VALUES
(16, 2, '123', 'Bukana Raymer Village', 'Gatid', 'Sta Cruz', 'Laguna', '4009', 'Home'),
(17, 3, '226', 'Bukana', 'Gatid', 'Sta Cruz', 'Laguna', '4009', 'Home');

-- --------------------------------------------------------

--
-- Table structure for table `assignrider`
--

CREATE TABLE `assignrider` (
  `assign_id` int(11) NOT NULL,
  `rider_id` int(11) NOT NULL,
  `order_id` int(11) NOT NULL,
  `delivery_status` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `assignrider`
--

INSERT INTO `assignrider` (`assign_id`, `rider_id`, `order_id`, `delivery_status`) VALUES
(11, 3007, 28, 'Completed');

-- --------------------------------------------------------

--
-- Table structure for table `baner`
--

CREATE TABLE `baner` (
  `banner_id` int(11) NOT NULL,
  `banner_filename` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `baner`
--

INSERT INTO `baner` (`banner_id`, `banner_filename`) VALUES
(1, 'banner_1_2_3.png'),
(2, 'logo.png.png'),
(3, 'banner_1_2_3_4.png'),
(4, '462559739_882680960712551_6017515949967456951_n.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `buyers`
--

CREATE TABLE `buyers` (
  `buyer_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `Fname` varchar(20) NOT NULL,
  `Mname` varchar(20) NOT NULL,
  `Lname` varchar(20) NOT NULL,
  `mobile_number` varchar(15) DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `birthdate` date DEFAULT NULL,
  `profile_pic` varchar(250) NOT NULL,
  `valid_id` varchar(250) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buyers`
--

INSERT INTO `buyers` (`buyer_id`, `user_id`, `email`, `Fname`, `Mname`, `Lname`, `mobile_number`, `gender`, `birthdate`, `profile_pic`, `valid_id`, `active`) VALUES
(4, 65, 'Roldanoliveros21@gmail.com', 'qwe', 'qwe', 'we', 'q', 'Male', '0000-00-00', 'profile-icon-design-free-vector.jpg', 'WIN_20241113_11_01_16_Pro.jpg', 0),
(1001, 70, 'roldan@ymail.com', 'qwe', 'qwe', 'we', '123654897', 'Female', '2010-12-15', 'profile-icon-design-free-vector.jpg', 'WIN_20241113_11_01_41_Pro.jpg', 0);

-- --------------------------------------------------------

--
-- Table structure for table `buyers_reported`
--

CREATE TABLE `buyers_reported` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `report_type` varchar(50) NOT NULL,
  `description` varchar(100) NOT NULL,
  `reported_image` varchar(250) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `buyers_reported`
--

INSERT INTO `buyers_reported` (`id`, `buyer_id`, `seller_id`, `report_type`, `description`, `reported_image`) VALUES
(7, 4, 2, 'payment-issue', 'asdasd', 'id.jpg');

-- --------------------------------------------------------

--
-- Table structure for table `cart_items`
--

CREATE TABLE `cart_items` (
  `id` int(11) NOT NULL,
  `buyer_id` int(11) DEFAULT NULL,
  `product_id` int(11) DEFAULT NULL,
  `product_name` varchar(50) NOT NULL,
  `price` double NOT NULL,
  `quantity` int(11) DEFAULT 1,
  `Description` varchar(30) NOT NULL,
  `shop_name` varchar(50) NOT NULL,
  `product_image` varchar(250) NOT NULL,
  `variation_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `messages`
--

CREATE TABLE `messages` (
  `id` int(11) NOT NULL,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `message` text NOT NULL,
  `timestamp` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `messages`
--

INSERT INTO `messages` (`id`, `sender_id`, `receiver_id`, `message`, `timestamp`) VALUES
(53, 4, 2, '-buyer', '2024-12-08 21:45:26'),
(54, 4, 2, '-buyer', '2024-12-08 21:45:39'),
(55, 2, 4, '-seller', '2024-12-08 21:45:48'),
(56, 4, 2, '-buyer', '2024-12-08 21:45:52'),
(57, 2, 4, '-seller', '2024-12-08 21:45:58'),
(58, 2, 4, 'seller', '2024-12-08 21:46:19'),
(59, 4, 2, 'seller', '2024-12-08 21:46:25'),
(60, 4, 2, '-buyer', '2024-12-08 21:46:42');

-- --------------------------------------------------------

--
-- Table structure for table `notification_buyer`
--

CREATE TABLE `notification_buyer` (
  `notification_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `cancel_reason` varchar(100) NOT NULL,
  `order_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification_buyer`
--

INSERT INTO `notification_buyer` (`notification_id`, `seller_id`, `cancel_reason`, `order_id`) VALUES
(1, 2, 'Out of Stock', 26);

-- --------------------------------------------------------

--
-- Table structure for table `notification_seller`
--

CREATE TABLE `notification_seller` (
  `notification_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `cancel_reason` varchar(100) NOT NULL,
  `order_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notification_seller`
--

INSERT INTO `notification_seller` (`notification_id`, `buyer_id`, `cancel_reason`, `order_id`) VALUES
(3, 4, 'Changed mind', 25);

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `order_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `buyer_id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `order_status` enum('Pending','Approved','Completed','Shipped','Cancelled','Out For Delivery') DEFAULT 'Pending',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `quantity` int(11) DEFAULT 1,
  `total_price` decimal(10,2) DEFAULT NULL,
  `variation_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`order_id`, `product_id`, `buyer_id`, `seller_id`, `order_status`, `created_at`, `updated_at`, `quantity`, `total_price`, `variation_id`) VALUES
(22, 1, 1000, 2, 'Completed', '2024-11-28 06:38:04', '2024-11-28 12:55:22', 1, 1999.00, 0),
(23, 135, 4, 3, 'Completed', '2024-11-28 15:55:39', '2024-11-28 15:55:55', 1, 99.00, 0),
(24, 3, 4, 2, 'Completed', '2024-11-28 15:59:50', '2024-11-28 15:59:59', 1, 1000.00, 0),
(25, 30, 4, 2, 'Cancelled', '2024-11-30 12:53:16', '2024-12-06 12:37:47', 1, 1000.00, 0),
(26, 2, 4, 2, 'Cancelled', '2024-11-30 12:53:16', '2024-12-06 12:58:44', 1, 1000.00, 31),
(27, 103, 1001, 3, 'Pending', '2025-01-28 13:51:38', '2025-01-28 13:51:38', 1, 130.00, 0),
(28, 118, 4, 3, 'Completed', '2025-03-01 12:42:15', '2025-03-10 05:43:20', 1, 750.00, 0);

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `Id` int(11) NOT NULL,
  `Product_Name` varchar(255) NOT NULL,
  `Description` text DEFAULT NULL,
  `Price` decimal(10,2) NOT NULL,
  `Stock_Quantity` int(11) NOT NULL DEFAULT 10,
  `Status` enum('active','inactive') DEFAULT 'active',
  `Seller_Id` int(11) DEFAULT NULL,
  `Image` varchar(250) DEFAULT NULL,
  `category` enum('Gardening Tools','Outdoor Living','Home Tools','Kitchen Appliances','Furniture','Decor','Bedding','Bath','Others') NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`Id`, `Product_Name`, `Description`, `Price`, `Stock_Quantity`, `Status`, `Seller_Id`, `Image`, `category`) VALUES
(1, ' Slow Cooker', 'Cooks food slowly at a low temperature over several hours. Ideal for stews, soups, and tender meat dishes.', 1999.00, 62, 'active', 2, 'j.png', 'Kitchen Appliances'),
(2, 'Microwave', 'Heats and cooks food quickly using microwaves. Useful for reheating leftovers, defrosting frozen food, and making quick meals.', 1000.00, 10, 'active', 2, 'o.png', 'Kitchen Appliances'),
(3, 'Stand Mixer', 'Mixes, whips, and kneads ingredients for baking. Can be used for making dough, cake batter, and whipping cream. Attachments can add functions like pasta making or meat grinding.', 1000.00, 9, 'active', 2, 'p.png', 'Kitchen Appliances'),
(4, 'Coffee Maker', 'Brews fresh coffee quickly and easily. Some models offer programmable settings, built-in grinders, or the ability to make specialty drinks like espresso.', 1000.00, 6, 'active', 2, 'r.png', 'Kitchen Appliances'),
(5, 'Toaster', 'Browns and toasts bread, bagels, and pastries. Higher-end models may have wider slots or special settings for bagels and defrosting.', 1000.00, 10, 'active', 2, 'u.png', 'Kitchen Appliances'),
(6, 'Air Fryer', 'Uses hot air to fry food with minimal oil, creating crispy results similar to deep-frying. Great for making fries, chicken wings, and roasted vegetables.', 1000.00, 10, 'active', 2, 'v.png', 'Kitchen Appliances'),
(7, 'Refrigerator', 'Stores and keeps food fresh, preserving it for days or weeks. Some models have advanced features like temperature control and ice makers.', 1000.00, 10, 'active', 2, 'w.png', 'Kitchen Appliances'),
(8, 'Sofa', 'Available in various styles such as sectional, loveseat, and sleeper sofas. Offers seating for 2 to 6 people and comes in materials like leather, fabric, or velvet.', 1000.00, 10, 'active', 2, 'sofa.png', 'Furniture'),
(9, 'Dining Table', 'Comes in different shapes (rectangular, round, square) and materials (wood, glass, metal). Seats 4 to 10 people, depending on size.', 1000.00, 10, 'active', 2, 'table.png', 'Furniture'),
(10, 'Nightstand', 'Small table placed beside the bed, usually with one or more drawers or open shelves for convenience.', 1000.00, 10, 'active', 2, 'table1.png', 'Furniture'),
(11, 'TV Stand/Entertainment Center', 'Holds the TV and media equipment, with shelves or drawers for DVDs, consoles, and décor items.', 1000.00, 10, 'active', 2, 'tv.png', 'Furniture'),
(12, 'Mattress', 'Options include memory foam, spring, hybrid, and latex mattresses. Different levels of firmness cater to personal comfort preferences.', 1000.00, 10, 'active', 2, 'mattress.png', 'Furniture'),
(13, 'Coffee Table', 'in the living room, available in wood, glass, or metal. Can include storage shelves or drawers.', 1000.00, 10, 'active', 2, 'coffee.png', 'Furniture'),
(14, 'Chairs', 'Dining chairs, accent chairs, and armchairs available in different materials such as wood, upholstered, or metal.', 1000.00, 10, 'active', 2, 'chairs.png', 'Furniture'),
(15, 'Bed Frame', 'Ranges from basic wooden frames to ornate, upholstered, or metal designs. Sizes include single, double, queen, and king.', 1000.00, 10, 'active', 2, 'bed_frame.png', 'Furniture'),
(16, 'Microfiber Duvet Cover', 'Lightweight, hypoallergenic, and easy-to-wash duvet cover with button closure.', 1000.00, 10, 'active', 2, '1.png', 'Bedding'),
(17, 'Down Alternative Comforter', 'Fluffy, warm, and ideal for all seasons; perfect for those with allergies', 1000.00, 10, 'active', 2, '2.png', 'Bedding'),
(18, 'Silk Pillowcases', 'Smooth, hypoallergenic silk pillowcases that reduce frizz and promote healthy hair.', 1000.00, 10, 'active', 2, '3.png', 'Bedding'),
(19, 'Weighted Blanket', '7-kg blanket designed to relieve anxiety and improve sleep quality', 1000.00, 10, 'active', 2, '4.png', 'Bedding'),
(20, 'Cooling Gel Mattress Topper', 'Keeps you cool and adds an extra layer of plush comfort to your mattress.', 1000.00, 10, 'active', 2, '5.png', 'Bedding'),
(21, 'Quilted Bedspread Set', 'Stylish and lightweight bedspread with matching pillow shams.', 1000.00, 10, 'active', 2, '6.png', 'Bedding'),
(22, 'Bamboo Fiber Sheet Set', 'Eco-friendly, moisture-wicking, and extremely soft sheets', 1000.00, 10, 'active', 2, '7.png', 'Bedding'),
(23, 'Velvet Throw Blanket', 'Luxurious velvet throw perfect for adding warmth and style to your bedroom', 1000.00, 10, 'active', 2, '8.png', 'Bedding'),
(24, 'Electric Blanket', 'Adjustable heating levels for personalized warmth during colder nights.', 1000.00, 10, 'active', 2, '9.png', 'Bedding'),
(25, 'Organic Cotton Bed Skirt', 'Adds elegance to your bed while hiding the space underneath.', 1000.00, 10, 'active', 2, '10.png', 'Bedding'),
(26, 'Anti-Allergy Pillow', 'Specially treated to resist dust mites and allergens.', 1000.00, 10, 'active', 2, '11.png', 'Bedding'),
(27, 'Waterproof Mattress Protector', ' Shields your mattress from spills and stains while remaining breathable', 1000.00, 10, 'active', 2, '112.png', 'Bedding'),
(28, 'Sherpa Fleece Blanket', 'Double-sided fleece and sherpa blanket for extra warmth and comfort', 1000.00, 10, 'active', 2, '14.png', 'Bedding'),
(29, 'Hotel-Quality Goose Down Comforter', 'Premium goose down filling for a five-star hotel sleep experience', 1000.00, 10, 'active', 2, '15.png', 'Bedding'),
(30, 'Bed Canopy Net', 'Elegant canopy to protect against mosquitoes and create a cozy atmosphere.', 1000.00, 9, 'active', 2, '16.png', 'Bedding'),
(31, 'Heated Mattress Pad', 'Provides gentle heat under your bedding for the ultimate comfort.', 1000.00, 10, 'active', 2, '17.png', 'Bedding'),
(32, 'Flannel Bed Sheets', 'Soft and warm, perfect for cold weather', 1000.00, 10, 'active', 2, '18.png', 'Bedding'),
(33, 'Body Pillow', 'Long, supportive pillow ideal for side sleepers or expectant mothers.', 1000.00, 10, 'active', 2, '19.png', 'Bedding'),
(34, 'Portable Air Bed', 'Inflatable air mattress that’s easy to store and perfect for guests.', 1000.00, 10, 'active', 2, '20.png', 'Bedding'),
(35, 'Luxury Cotton Bath Towels', 'Ultra-absorbent, 100% cotton towels with a soft, plush fee.', 1000.00, 10, 'active', 2, '1.png', 'Bath'),
(36, 'Bathrobe', 'Comfortable and cozy bathrobe made from premium cotton or microfiber.', 1000.00, 10, 'active', 2, '2.png', 'Bath'),
(37, 'Exfoliating Bath Mitt', 'Textured mitt designed for exfoliating and removing dead skin cells.', 1000.00, 10, 'active', 2, '3.png', 'Bath'),
(38, 'Aromatherapy Bath Bombs', 'Scented bath bombs infused with essential oils for a relaxing soak.', 1000.00, 10, 'active', 2, '4.png', 'Bath'),
(39, 'Shower Gel Set', 'Set of moisturizing and fragrant shower gels in different scents.', 1000.00, 10, 'active', 2, '5.png', 'Bath'),
(40, 'Loofah Sponge', 'Natural loofah for gentle exfoliation and cleansing.', 1000.00, 10, 'active', 2, '6.png', 'Bath'),
(41, 'Antibacterial Hand Soap', 'Liquid hand soap with antibacterial properties for clean, germ-free hands.', 1000.00, 10, 'active', 2, '7.png', 'Bath'),
(42, 'Bath Mat Set', 'Soft and absorbent bath mat set to keep your bathroom floor dry and safe', 1000.00, 10, 'active', 2, '8.png', 'Bath'),
(43, 'Shower Cap', 'Waterproof cap to keep hair dry during showers.', 148.00, 10, 'active', 2, '9.png', 'Bath'),
(44, 'Body Wash with Natural Oils', 'Nourishing body wash infused with natural oils for hydrated skin.', 1000.00, 10, 'active', 2, '10.png', 'Bath'),
(45, 'Bath Salts', 'Mineral-rich bath salts for muscle relaxation and rejuvenation.', 1000.00, 10, 'active', 2, '11.png', 'Bath'),
(46, 'Bath Pillow', 'Waterproof, cushioned pillow for neck and head support during baths.', 1000.00, 10, 'active', 2, '12.png', 'Bath'),
(47, 'Bath Pillow Essential Oil Diffuser', 'Portable diffuser that releases calming scents into the bathroom.', 1000.00, 10, 'active', 2, '13.png', 'Bath'),
(48, 'Microfiber Hair Wrap', 'Super absorbent hair wrap that dries hair quickly and reduces frizz', 1000.00, 10, 'active', 2, '14.png', 'Bath'),
(49, 'Bath Towel Warmer', 'Compact electric warmer that keeps your towels toasty for post-bath comfort.', 1000.00, 10, 'active', 2, '15.png', 'Bath'),
(50, 'Foot Scrub', 'Exfoliating scrub designed to remove calluses and soften feet', 1000.00, 10, 'active', 2, '16.png', 'Bath'),
(51, 'Natural Sea Sponge', 'Eco-friendly sea sponge for gentle body cleansing.', 148.00, 10, 'active', 2, '17.png', 'Bath'),
(52, 'Shower Caddy', 'Organizer rack for holding shampoo, conditioner, and bath essentials.', 1000.00, 10, 'active', 2, '18.png', 'Bath'),
(53, 'Bubble Bath', 'Foaming bubble bath liquid with soothing properties.', 1000.00, 10, 'active', 2, '19.png', 'Bath'),
(54, 'Epsom Salt', 'Magnesium sulfate crystals for relaxing muscle relief in baths.', 1000.00, 10, 'active', 2, '20.png', 'Bath'),
(56, 'Shovel', 'Shovel. To plant a seed, you need to dig! That\'s why shovels are a must-have. They are used for loosening, digging, lifting, and smoothing the soil.', 700.00, 4, 'active', 3, 'Screenshot_2024-11-12_160224.png', 'Gardening Tools'),
(57, 'Gardening Hose', 'Garden Hose. A garden hose is a great way to water your fruits, veggies and flowers. Similar to the watering can, the garden hose is used for watering plants in the garden.', 269.00, 10, 'active', 3, 'Screenshot_2024-11-12_160237.png', 'Gardening Tools'),
(58, 'Loppers', 'Loppers are a must-have gardening tool for any gardener with trees around their yard. Coming in many shapes and sizes, some loppers have a ratchet function to make branch removal a breeze.\r\n', 578.00, 10, 'active', 3, 'Screenshot_2024-11-12_160245.png', 'Gardening Tools'),
(59, 'Cultivator', 'A hand cultivator is one of the basic gardening equipment that is very versatile. Another hand tool is called the “fork” or “cultivator.”', 148.00, 10, 'active', 3, 'Screenshot_2024-11-12_160253.png', 'Gardening Tools'),
(60, ' Aerator', 'Aerator. Aerator An aerator is a tool that is used to get air and water down deeper in the ground. It is a professional gardening tool that can help you to transform tired-looking and patchy lawns.', 4999.00, 10, 'active', 3, 'Screenshot_2024-11-12_160302.png', 'Gardening Tools'),
(61, 'Dibber', 'Trowel. A garden trowel is a must for every gardener\'s toolkit and will help keep your hands a lot cleaner when planting out in the garden.', 130.00, 10, 'active', 3, 'Screenshot_2024-11-12_160310.png', 'Gardening Tools'),
(62, ' Garden Fork', 'Digging Fork. One of the essential gardening tools, known for its versatility, Digging Fork, needs to be on top of your list.', 1190.00, 10, 'active', 3, 'Screenshot_2024-11-12_160318.png', 'Gardening Tools'),
(63, ' Wheelbarrow', 'Wheelbarrow. Wheelbarrows are a versatile piece of gardening equipment which can be used for many jobs. Wheelbarrows are great at hauling large, heavy loads.', 1299.00, 10, 'active', 3, 'Screenshot_2024-11-12_160329.png', 'Gardening Tools'),
(64, 'Sprayer', 'Sprayers are used for applying pesticides, herbicides, or fertilizers.', 315.00, 10, 'active', 3, 'Screenshot_2024-11-12_160336.png', 'Gardening Tools'),
(65, ' Tiller', 'Tillers are used to prepare large areas of soil for planting.', 7049.00, 10, 'active', 3, 'Screenshot_2024-11-12_160344.png', 'Gardening Tools'),
(66, ' Auger', 'A machine used for making holes in the ground for planting.', 3599.00, 10, 'active', 3, 'Screenshot_2024-11-12_160351.png', 'Gardening Tools'),
(67, 'Bulb Planter', 'This tool is specifically designed to make the correct-sized hole for planting bulbs and other plants.', 130.00, 10, 'active', 3, 'Screenshot_2024-11-12_160357.png', 'Gardening Tools'),
(68, 'Spade', 'spade is a flat metal digging equipment with a sharp edge that can be used for digging as well as moving dirt, debris, and similar things. Most of the spades have rectangular blades, while others are sharply pointed to improve the blade\'s penetrating capabilities.', 750.00, 10, 'active', 3, 'Screenshot_2024-11-12_160404.png', 'Gardening Tools'),
(69, '  Outdoor Chair', 'Brand:Heim \r\nSeries:Mekore \r\nDesc:Outdoor Brown Folding Chair Model:Yc-048 \r\n', 1249.00, 10, 'active', 3, 'Screenshot_2024-11-12_160417.png', 'Outdoor Living'),
(70, ' Outdoor Table ', 'rand:Heim \r\nSeries:Fir \r\nDesc:Outdoor Bar Table And Chair Se Model:Sak-70h+yc-055 \r\n', 12009.00, 10, 'active', 3, 'Screenshot_2024-11-12_160426.png', 'Outdoor Living'),
(71, ' 4 Seater Folding Table', 'Brand:Heim \r\nSeries:Stygian\r\nDesc:4 Seater Folding Table \r\nModel:Nzk-120 Size:120x60x54\r\n', 2000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160436.png', 'Outdoor Living'),
(72, ' Metal Bench', 'Brand:Leigh Country \r\nDesc:Metal Bench \r\nModel:Tx 94101 \r\n', 6009.00, 10, 'active', 3, 'Screenshot_2024-11-12_160443.png', 'Outdoor Living'),
(73, ' Steel Banana Umbrella', 'Brand:Heim \r\nSeries:Polyester/Steel Banana Umbrella Series \r\nDesc:Cantilever Patio Umbrella \r\nModel:Syc019\r\n', 4099.00, 10, 'active', 3, 'Screenshot_2024-11-12_160450.png', 'Outdoor Living'),
(74, ' Metal Umbrella Base', 'Brand:Heim\r\nDesc:Metal Umbrella Base Model:Sj-071-19\r\n', 1200.00, 10, 'active', 3, 'Screenshot_2024-11-12_160458.png', 'Outdoor Living'),
(75, ' Camping Tent', 'Camping Tent good for 2-4 Kids or 2-3 adults', 2110.00, 10, 'active', 3, 'Screenshot_2024-11-12_160507.png', 'Outdoor Living'),
(76, ' Camping Lantern', 'EverBrite LED Camping Lantern, USB C Rechargeable Lantern with Stepless Dimming, Vintage Portable Camping Lights & Lanterns, Lanterns for Power Outages, Hurricane, Emergency, Fishing, Home and More', 1000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160519.png', 'Outdoor Living'),
(77, ' Camping Water Jug', '5 Gallon Water Jug, Camping Water Container BPA Free Water Storage with Spigot No Leakage Portable Emergency Water Tank for Outdoor Hiking Camping Picnic Supplies Green', 1200.00, 10, 'active', 3, 'Screenshot_2024-11-12_160541.png', 'Outdoor Living'),
(78, 'Outdoor Mat Blanket', 'Picnic Blanket/ Outdoor Blanket\r\n•	Top Fabric: Polyester\r\n•	Filling: Polyester\r\n•	Bottom Fabric: Aluminum\r\n\r\n', 879.00, 10, 'active', 3, 'Screenshot_2024-11-12_160551.png', 'Outdoor Living'),
(79, ' Outdoor Gas Grill', 'Stainless steel lid, handle, and control panel · Cooking area and warming rack', 5000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160600.png', 'Outdoor Living'),
(80, ' Cooler Box', '•	Top Fabric: Polyester\r\n•	Filling: Polyester\r\n•	Bottom Fabric: Aluminum\r\n\r\n', 1000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160608.png', 'Outdoor Living'),
(81, 'Outdoor Post Lamp', 'Outdoor post lamp, water proof ', 420.00, 10, 'active', 3, 'Screenshot_2024-11-12_160620.png', 'Outdoor Living'),
(82, 'Outdoor Flower Pot', '•	Pure ceramic flower pot. Used to put plant decoration outdoor', 499.00, 10, 'active', 3, 'Screenshot_2024-11-12_160628.png', 'Outdoor Living'),
(83, ' Metal Flower Stand', '5 Tier Metal Flower stand', 1000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160635.png', 'Outdoor Living'),
(84, ' Foldable Recliner Chair', 'Picnic Blanket/ Outdoor Blanket\r\n•	Top Fabric: Polyester\r\n•	Filling: Polyester\r\n•	Bottom Fabric: Aluminum\r\n\r\n', 2000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160644.png', 'Outdoor Living'),
(85, ' Extension Ladder', 'Our extension ladders are our longest ladders. They allow you to reach anything higher than 20 feet while collapsing for easy storage.', 900.00, 10, 'active', 3, 'Screenshot_2024-11-12_160714.png', 'Outdoor Living'),
(86, ' Drill Machine', 'Drill Machine can perform operations other than drilling, such as countersinking, counterboring, reaming, and tapping large or small holes.', 3999.00, 10, 'active', 3, 'Screenshot_2024-11-12_160721.png', 'Home Tools'),
(87, ' Grinder Machine', 'A grinding machine is a machine for material removal with geometrically non-defined, bonded cutting edges, where the relative movement between tool and workpiece is rotational or linear. The machine further must provide relative feed and positioning movements between tool and workpiece.', 2090.00, 10, 'active', 3, 'Screenshot_2024-11-12_160729.png', 'Home Tools'),
(88, ' Jack Hammer Machine', 'The automatic portable hammering machine can be considered as the basis of any hammering operation in mass production. Its main purpose is to perform hammering work safely and efficiently, including punching, filleting, riveting, and smithy operations, such as upset forging, under all intended operating conditions.', 21.00, 10, 'active', 3, 'Screenshot_2024-11-12_160735.png', 'Home Tools'),
(89, ' Vacuum Blower', 'Vacuum blowers are widely used in various industrial applications such as material handling, pneumatic conveying, and wastewater treatment. They can also be utilized for residential purposes, such as yard cleaning or removing water from flooded areas.', 1700.00, 10, 'active', 3, 'Screenshot_2024-11-12_160741.png', 'Home Tools'),
(90, ' Nail gun', 'A nail gun, nailgun or nailer is a form of hammer used to drive nails into wood or other materials. It is usually driven by compressed air (pneumatic), electromagnetism, highly flammable gases such as butane or propane, or, for powder-actuated tools, a small explosive charge.', 2000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160749.png', 'Home Tools'),
(91, ' Steel Claw Hammer', 'A hammer is a tool that consists of a heavy piece of metal at the end of a handle. It is used, for example, to hit nails into a piece of wood or a wall, or to break things into pieces.', 700.00, 10, 'active', 3, 'Screenshot_2024-11-12_160755.png', 'Home Tools'),
(92, 'Hand Saw', '• 65Mn blade, heat treated\r\n• With teeth protector\r\n• Packing: color sleeve\r\n', 265.00, 10, 'active', 3, 'Screenshot_2024-11-12_160801.png', 'Home Tools'),
(93, 'Crow Bar', 'The crowbar is the oldest type of pry bar and was first used in France in 1748. This straight piece of iron with a wedge-shaped end was developed to open wooden crates, doors, and boxes.', 430.00, 10, 'active', 3, 'Screenshot_2024-11-12_160807.png', 'Home Tools'),
(94, ' Platform Trolley', 'This good maneuvering equipment is designed for easy transportation of heavy and bulky items. They come in great use for where carrying heavy items manually over longer distances would be unsafe or strenuous on your body.', 1899.00, 10, 'active', 3, 'Screenshot_2024-11-12_160814.png', 'Home Tools'),
(95, 'Measuring Tape', 'A tape measure is a flexible ruler used to size up spaces and objects with precision. Whether it\'s a compact 12-foot (3.66-meter) tape for smaller scale interior projects or a robust 100-foot cloth tape for outdoor use, these handy tools come in various lengths and styles to suit your measuring needs.', 250.00, 10, 'active', 3, 'Screenshot_2024-11-12_160825.png', 'Home Tools'),
(96, 'Masonry Trowel', 'The Masonry trowel is a hand trowel used in brickwork or stonework for levelling, spreading and shaping mortar or concrete. They come in several shapes and sizes depending on the task.', 245.00, 10, 'active', 3, 'Screenshot_2024-11-12_160831.png', 'Home Tools'),
(97, 'Putty Knife', 'A putty knife is a versatile and useful hand tool that can be used to help with applying several filler materials such as wood filler, drywall compound and others. It can also be used as a scraping tool to remove residue as well as having several other uses.', 335.00, 10, 'active', 3, 'Screenshot_2024-11-12_160838.png', 'Home Tools'),
(98, 'PVC Float', 'Expanded Poly Vinyl Chloride (PVC) is one of the most commonly used materials for floats and buoys worldwide. Characteristics of PVC Floats and Buoys are: Fitec PVC Floats and Buoys are made from the finest additives and resins available.', 170.00, 10, 'active', 3, 'Screenshot_2024-11-12_160844.png', 'Home Tools'),
(99, ' Bull Float', 'a machine for giving the final surfacing to an area of concrete, as on a road.', 2000.00, 10, 'active', 3, 'Screenshot_2024-11-12_160851.png', 'Home Tools'),
(100, 'Concrete Broom', 'Broom finish concrete is a technique used to create slip-resistant surfaces on freshly poured concrete. This method involves dragging a broom or similar tool with coarse bristles across the wet concrete, creating small ridges that improve traction and prevent slipping.', 1.00, 10, 'active', 3, 'Screenshot_2024-11-12_160859.png', 'Home Tools'),
(101, 'Stainless Steel Wire Brush', 'Steel wire brushes are a common and essential tool in any metal fabrication shop. These brushes can be used for a variety of applications, including weld cleaning, deburring, rust and oxide removal, surface preparation, and surface finishing.', 136.00, 10, 'active', 3, 'Screenshot_2024-11-12_160906.png', 'Home Tools'),
(102, 'Masking Tape', 'Masking tape, also known as painter\'s tape, is a type of pressure-sensitive tape made of a thin and easy-to-tear paper, and an easily released pressure-sensitive adhesive. It is available in a variety of widths. It is used mainly in painting, to mask off areas that should not be painted.', 70.00, 10, 'active', 3, 'Screenshot_2024-11-12_160912.png', 'Home Tools'),
(103, 'Abrasive Paper', 'Dry abrasive paper is widely used in industries such as woodworking, stone processing, precision mold polishing, and synthetic material processing, and is widely used in industries such as furniture and decoration.', 130.00, 10, 'active', 3, 'Screenshot_2024-11-12_160917.png', 'Home Tools'),
(104, 'Paint Brush', 'A paintbrush is a brush used to apply paint or ink. A paintbrush is usually made by clamping bristles to a handle with a ferrule. They are available in various sizes, shapes, and materials. Thicker ones are used for filling in, and thinner ones are used for details.', 30.00, 10, 'active', 3, 'Screenshot_2024-11-12_160924.png', 'Home Tools'),
(105, 'Paint Roller Brush', 'Paint rollers are designed to efficiently paint large flat surfaces, such as walls and ceilings. A paint roller can hold more paint than a paint brush and will distribute an even layer of paint quicker. Similarly to paint brushes, paint rollers also differ in sizes, styles and material.', 145.00, 10, 'active', 3, 'Screenshot_2024-11-12_160930.png', 'Home Tools'),
(106, 'Paint Tray', 'Paint trays are used to hold paint for decorating with a paint roller, typically having a well and a ridged slope with which to spread paint evenly over the roller. They\'re an essential tool for repainting walls.', 100.00, 10, 'active', 3, 'Screenshot_2024-11-12_160936.png', 'Home Tools'),
(107, ' Knipex Cutter', ' High Leverage Angled Diagonal Cutters', 100.00, 10, 'active', 3, 'Screenshot_2024-11-12_160941.png', 'Home Tools'),
(108, 'Screw Driver', 'A screwdriver is a simple and common tool used to install or remove screws. Screwdrivers usually have a plastic or rubber handle and a head made of alloy steel.', 85.00, 10, 'active', 3, 'Screenshot_2024-11-12_160956.png', 'Home Tools'),
(109, 'Adjustable Wrench', 'a wrench similar to an open end wrench but having one fixed jaw and one adjustable jaw.', 175.00, 10, 'active', 3, 'Screenshot_2024-11-12_161005.png', 'Home Tools'),
(110, 'Combination Spanner Set', 'Combination spanners are double-ended tools. It has an open-ended profile on one end and a closed loop on the other end. The two heads are usually at a 15 degree angle to the shaft for better access to the nuts or bolts. This single tool serves the functions of two spanners at once.', 750.00, 10, 'active', 3, 'Screenshot_2024-11-12_161011.png', 'Home Tools'),
(111, 'Plier', 'pliers, hand-operated tool for holding and gripping small articles or for bending and cutting wire.', 550.00, 10, 'active', 3, 'Screenshot_2024-11-12_161019.png', 'Home Tools'),
(112, ' Wire Nails', 'Common wire nails are used by manufacturers worldwide as wood joiner, however, the most common use of this product is in building structures (joining wooden boards) , and also in the construction industry.', 100.00, 10, 'active', 3, 'Screenshot_2024-11-12_161029.png', 'Home Tools'),
(113, 'Screw', 'A screw is a small metal rod with a notch in the top that\'s used as a fastener. You can attach one piece of wood to another by rotating a screw through the two surfaces. A screw is similar to a nail, but instead of hammering it in, you turn it repeatedly with a screwdriver.', 20.00, 10, 'active', 3, 'Screenshot_2024-11-12_161038.png', 'Home Tools'),
(114, 'Hammer', 'A hammer is a tool, most often a hand tool, consisting of a weighted \"head\" fixed to a long handle that is swung to deliver an impact to a small area of an object.', 196.00, 10, 'active', 3, 'Screenshot_2024-11-12_161106.png', 'Home Tools'),
(115, 'Binding Wire', 'Binding Wire is used for the purpose of tying applications in the field of construction. It is used extensively in the construction sector for tying the rebars at the junctions/joints so as to keep the structure intact. Binding wire is made of mild steel.', 70.00, 10, 'active', 3, 'Screenshot_2024-11-12_161052.png', 'Home Tools'),
(116, 'Candle Holder', 'Gold, 3 branch candle holder', 450.00, 10, 'active', 3, 'Screenshot_2024-11-13_103137.png', 'Decor'),
(117, 'Artificial Plant', 'Aesthetic artificial plant. Great for decoration.', 350.00, 10, 'active', 3, 'Screenshot_2024-11-13_103205.png', 'Decor'),
(118, 'Photo Frame', 'Gold Photo Frame, thick and sturdy border.', 750.00, 9, 'active', 3, 'Screenshot_2024-11-13_103218.png', 'Decor'),
(119, 'Clock', 'Round Wall Clock', 250.00, 10, 'active', 3, 'Screenshot_2024-11-13_103226.png', 'Decor'),
(120, 'Home Fragrance Holder', 'Fragrance holder , aesthetically pleasing with gold design', 199.00, 10, 'active', 3, 'Screenshot_2024-11-13_103235.png', 'Decor'),
(121, ' Figurine', 'Popular figurine for house décor', 1499.00, 10, 'active', 3, 'Screenshot_2024-11-13_103245.png', 'Decor'),
(122, 'Vase', 'Flower vase that can be used in the living room or even in the dining table', 499.00, 10, 'active', 3, 'Screenshot_2024-11-13_103251.png', 'Decor'),
(123, 'Candle ', '6 pcs white candle', 100.00, 10, 'active', 3, 'Screenshot_2024-11-13_103256.png', 'Decor'),
(124, 'Accent Table', 'Foldable and easy to use', 599.00, 10, 'active', 3, 'Screenshot_2024-11-13_103304.png', 'Decor'),
(125, 'Lamp', 'Aesthetic lamp for better decoration in your house', 654.00, 10, 'active', 3, 'Screenshot_2024-11-13_103311.png', 'Decor'),
(126, 'Storage Basket', 'Aesthetic storage basket for a much more organize house', 249.00, 10, 'active', 3, 'Screenshot_2024-11-13_103318.png', 'Decor'),
(127, 'Throw Pillow', 'White Pillow with floral pattern', 289.00, 10, 'active', 3, 'Screenshot_2024-11-13_103324.png', 'Decor'),
(128, 'Metal Flower', 'Wall décor made of metal, can be used in the living room to make it more aesthetically pleasing in the eyes', 899.00, 10, 'active', 3, 'Screenshot_2024-11-13_103335.png', 'Decor'),
(129, 'Mirror', 'Aesthetically pleasing mirror', 550.00, 10, 'active', 3, 'Screenshot_2024-11-13_103343.png', 'Decor'),
(130, ' Wall Decor', '3 in 1 wall décor, moon design', 1900.00, 10, 'active', 3, 'Screenshot_2024-11-13_103348.png', 'Decor'),
(131, ' White Curtain ', 'Used in decorating the house when there are occasions. 2pcs', 1200.00, 10, 'active', 3, 'Screenshot_2024-11-13_103355.png', 'Decor'),
(132, 'Bowl', 'Gold decorative bowl. Can be a snack bowl', 249.00, 10, 'active', 3, 'Screenshot_2024-11-13_103400.png', 'Decor'),
(133, 'Cute Duck Lamp ', 'Used in either small table in the study room or anywhere that needs a small and not bright light', 469.00, 10, 'active', 3, 'Screenshot_2024-11-13_103407.png', 'Decor'),
(134, 'Wall Art', 'Aesthetic wall art, flower design good for wall décor', 999.00, 10, 'active', 3, 'Screenshot_2024-11-13_103415.png', 'Decor'),
(135, 'Wall Paper', 'Sticker Wall Paper with aesthetic design. 1meter long', 99.00, 9, 'active', 3, 'Screenshot_2024-11-13_103422.png', 'Decor'),
(137, 'eyyyyy', 'HAHHAHAHHAHHA', 200.00, 10, 'active', 3, 'WIN_20241113_11_01_41_Pro.jpg', 'Gardening Tools'),
(138, 'test for size', 'test size ', 200.00, 10, 'active', 3, 'e.png', 'Kitchen Appliances');

-- --------------------------------------------------------

--
-- Table structure for table `productvariations`
--

CREATE TABLE `productvariations` (
  `id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `color` varchar(100) DEFAULT NULL,
  `size` varchar(100) DEFAULT NULL,
  `stock` int(11) DEFAULT 0,
  `price` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `productvariations`
--

INSERT INTO `productvariations` (`id`, `product_id`, `color`, `size`, `stock`, `price`) VALUES
(0, NULL, NULL, NULL, 0, NULL),
(31, 2, 'BLUE', NULL, 10, 200.00),
(32, 137, 'blue', 'Large', 11, 200.00),
(33, 137, 'blue', 'Small', 6, 200.00),
(34, 137, 'blue', 'Medium', 100, 200.00),
(35, 138, NULL, 'large', 10, 200.00),
(36, 138, NULL, 'small', 10, 200.00);

-- --------------------------------------------------------

--
-- Table structure for table `rating`
--

CREATE TABLE `rating` (
  `rating_id` int(250) NOT NULL,
  `product_id` int(11) NOT NULL,
  `rate` int(11) NOT NULL,
  `description` varchar(250) NOT NULL,
  `product_pic` varchar(250) NOT NULL,
  `buyer_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `rating`
--

INSERT INTO `rating` (`rating_id`, `product_id`, `rate`, `description`, `product_pic`, `buyer_id`) VALUES
(3, 3, 3, 'test with niña pic', 'WIN_20241113_11_01_19_Pro.jpg', 4);

-- --------------------------------------------------------

--
-- Table structure for table `report_sellerproduct`
--

CREATE TABLE `report_sellerproduct` (
  `id` int(11) NOT NULL,
  `seller_id` int(11) NOT NULL,
  `violation_type` varchar(100) NOT NULL,
  `description` varchar(100) NOT NULL,
  `report_image` varchar(250) NOT NULL,
  `buyer_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `report_sellerproduct`
--

INSERT INTO `report_sellerproduct` (`id`, `seller_id`, `violation_type`, `description`, `report_image`, `buyer_id`) VALUES
(8, 2, 'product-issue', 'asd', 'roldan_pic.jpg', 4);

-- --------------------------------------------------------

--
-- Table structure for table `riders`
--

CREATE TABLE `riders` (
  `rider_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `email` varchar(100) NOT NULL,
  `Fname` varchar(20) NOT NULL,
  `Mname` varchar(20) NOT NULL,
  `Lname` varchar(20) NOT NULL,
  `mobile_number` varchar(15) DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `birthdate` date DEFAULT NULL,
  `profile_pic` varchar(250) NOT NULL,
  `valid_id` varchar(250) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `riders`
--

INSERT INTO `riders` (`rider_id`, `user_id`, `email`, `Fname`, `Mname`, `Lname`, `mobile_number`, `gender`, `birthdate`, `profile_pic`, `valid_id`, `active`) VALUES
(3006, 78, 'roldanolivero0921@gmail.com', 'roldan', 'Araneta', 'Oliveros', '09205804090', 'Male', '2003-06-21', 'profile-icon-design-free-vector.jpg', 'WIN_20241113_11_01_22_Pro.jpg', 0),
(3007, 79, 'roldanolivero0621@gmail.com', 'roldan', 'the', 'rider', '09500925977', 'Male', '2003-06-21', 'profile-icon-design-free-vector.jpg', 'roldan_pic.jpg', 0);

-- --------------------------------------------------------

--
-- Table structure for table `sellers`
--

CREATE TABLE `sellers` (
  `seller_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `email` varchar(50) NOT NULL,
  `Fname` varchar(20) NOT NULL,
  `Mname` varchar(20) NOT NULL,
  `Lname` varchar(20) NOT NULL,
  `shop_name` varchar(255) DEFAULT NULL,
  `mobile_number` varchar(15) DEFAULT NULL,
  `gender` varchar(20) NOT NULL,
  `profile_pic` varchar(250) NOT NULL,
  `shop_description` varchar(100) DEFAULT NULL,
  `valid_id` varchar(250) NOT NULL,
  `shop_logo` varchar(250) NOT NULL,
  `business_permit` varchar(250) NOT NULL,
  `approval` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sellers`
--

INSERT INTO `sellers` (`seller_id`, `user_id`, `email`, `Fname`, `Mname`, `Lname`, `shop_name`, `mobile_number`, `gender`, `profile_pic`, `shop_description`, `valid_id`, `shop_logo`, `business_permit`, `approval`) VALUES
(2, 61, 'ninavillodo@gmail.com', 'Nina Clarisse', 'Ragudo', 'Villodo', 'anya_shop', '09078106644', 'FeMale', 'profile-icon-design-free-vector.jpg', 'The category is all about Home', 'WIN_20240521_09_35_44_Pro.jpg', 'the-nun-movie-0p-1920x1080.jpg', 'Screenshot_2024-09-24_211040.png', 0),
(3, 62, 'jona@gmail.com', 'Jona', 'Conception', 'Javier', 'jona_online_shop', '09161044535', 'FeMale', 'profile-icon-design-free-vector.jpg', 'this shop sells product with this categories:\r\ngardening tools\r\nhome tools\r\ndecor\r\noutdoor living', 'WIN_20240521_09_35_42_Pro.jpg', 'Shop_Logo_Sample.png', 'business_permit.png', 0);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `email` varchar(100) NOT NULL,
  `role_id` int(11) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `approval` tinyint(1) DEFAULT 0,
  `active` enum('ACTIVE','DEACTIVE') NOT NULL DEFAULT 'ACTIVE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `email`, `role_id`, `password`, `created_at`, `approval`, `active`) VALUES
(59, 'admin@gmail.com', 3, 'scrypt:32768:8:1$0Q5uIBjW7ccg3fJA$18f0ef5c7e49cc2eb07dfc822e58d94cffce5b77b82d3ed84233b9021464dbf30737d216731943ec50df6cf8c2175cfe56c6db53f52619e26f9b3059a1fde44e', '2024-11-13 00:43:50', 1, 'ACTIVE'),
(61, 'ninavillodo@gmail.com', 2, 'scrypt:32768:8:1$ZTJ0VsWduuFCd4Az$0a1663469cf2710dc490f7cddbf4943a531d908756199da9478e41959966fa91465ac55b23d7ccec540056c40559b8325bbd82a8a40a67f962cae38f132f7db7', '2024-11-13 00:55:20', 1, 'ACTIVE'),
(62, 'jona@gmail.com', 2, 'scrypt:32768:8:1$xyBuYzeniNupXOBt$51728d9bb1504cfb1149511bd101c608846397b4582c9b688b09ecea05105f22c7dd84638da5b1521d348f5d787cb104381ed348ff9f135b7e085a01ea6e8819', '2024-11-13 01:47:34', 1, 'ACTIVE'),
(65, 'Roldanoliveros21@gmail.com', 1, 'scrypt:32768:8:1$XzseKzhQeJvvyeMd$521d02a387751a71cf0fa8e23225eb023d533c71d6f084d54afc2eac711b020ecb016b50e77c4aa1af54fb3cad5a13389a06a40f831d5634d1e6e111ab733891', '2024-11-20 12:05:34', 1, 'ACTIVE'),
(70, 'roldan@ymail.com', 1, 'scrypt:32768:8:1$PUJTnaBd4fvHmKOR$33040e3ac9913efcb49a33807cfd8685d8b775c5c29a1a831802fa420c66a975461521767e4754b2eae0633c6f071e7fd442abf7237c8e260351fe00a6f8633e', '2024-11-28 15:09:03', 1, 'ACTIVE'),
(78, 'roldanolivero0921@gmail.com', 4, 'scrypt:32768:8:1$NIrEymjzbPAarwYk$2fb599bc18d52be0adfc00b3f333f5717ed0e06998ffeea655af80807c075174f53d1c2a5f59722c8505edeb382c022e71fd1efb91187956acd50119e8a07a7f', '2025-02-03 15:11:34', 1, 'ACTIVE'),
(79, 'roldanolivero0621@gmail.com', 4, 'scrypt:32768:8:1$kTeRWBCafQaq8UoD$6eb7b1e315377f0366bf4d12465c1029d15cedbffcf41582e42674f84d93237e5d568df00a6564a4b62eb3383542ee27e88c29ea75a705e8f1752afc12edbd56', '2025-03-01 10:23:18', 1, 'ACTIVE');

-- --------------------------------------------------------

--
-- Table structure for table `user_roles`
--

CREATE TABLE `user_roles` (
  `id` int(11) NOT NULL,
  `role_name` varchar(50) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user_roles`
--

INSERT INTO `user_roles` (`id`, `role_name`, `created_at`) VALUES
(1, 'buyer', '2024-10-04 03:39:09'),
(2, 'seller', '2024-10-04 03:39:09'),
(3, 'admin', '2024-10-04 03:39:09'),
(4, 'Rider', '2025-02-03 15:10:04');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `addresses_buyer`
--
ALTER TABLE `addresses_buyer`
  ADD PRIMARY KEY (`address_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `addresses_rider`
--
ALTER TABLE `addresses_rider`
  ADD PRIMARY KEY (`address_id`),
  ADD KEY `rider_id` (`rider_id`);

--
-- Indexes for table `addresses_seller`
--
ALTER TABLE `addresses_seller`
  ADD PRIMARY KEY (`address_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `assignrider`
--
ALTER TABLE `assignrider`
  ADD PRIMARY KEY (`assign_id`),
  ADD KEY `rider_id` (`rider_id`),
  ADD KEY `order_id` (`order_id`);

--
-- Indexes for table `baner`
--
ALTER TABLE `baner`
  ADD PRIMARY KEY (`banner_id`);

--
-- Indexes for table `buyers`
--
ALTER TABLE `buyers`
  ADD PRIMARY KEY (`buyer_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `buyers_reported`
--
ALTER TABLE `buyers_reported`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `buyer_id` (`buyer_id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `messages`
--
ALTER TABLE `messages`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notification_buyer`
--
ALTER TABLE `notification_buyer`
  ADD PRIMARY KEY (`notification_id`);

--
-- Indexes for table `notification_seller`
--
ALTER TABLE `notification_seller`
  ADD PRIMARY KEY (`notification_id`),
  ADD KEY `buyer_id` (`buyer_id`);

--
-- Indexes for table `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`order_id`),
  ADD KEY `product_id` (`product_id`),
  ADD KEY `buyer_id` (`buyer_id`),
  ADD KEY `seller_id` (`seller_id`);

--
-- Indexes for table `products`
--
ALTER TABLE `products`
  ADD PRIMARY KEY (`Id`),
  ADD KEY `Seller_Id` (`Seller_Id`);

--
-- Indexes for table `productvariations`
--
ALTER TABLE `productvariations`
  ADD PRIMARY KEY (`id`),
  ADD KEY `product_id` (`product_id`);

--
-- Indexes for table `rating`
--
ALTER TABLE `rating`
  ADD PRIMARY KEY (`rating_id`);

--
-- Indexes for table `report_sellerproduct`
--
ALTER TABLE `report_sellerproduct`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `riders`
--
ALTER TABLE `riders`
  ADD PRIMARY KEY (`rider_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `sellers`
--
ALTER TABLE `sellers`
  ADD PRIMARY KEY (`seller_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `role_id` (`role_id`);

--
-- Indexes for table `user_roles`
--
ALTER TABLE `user_roles`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `addresses_buyer`
--
ALTER TABLE `addresses_buyer`
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `addresses_rider`
--
ALTER TABLE `addresses_rider`
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `addresses_seller`
--
ALTER TABLE `addresses_seller`
  MODIFY `address_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT for table `assignrider`
--
ALTER TABLE `assignrider`
  MODIFY `assign_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `baner`
--
ALTER TABLE `baner`
  MODIFY `banner_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `buyers`
--
ALTER TABLE `buyers`
  MODIFY `buyer_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1006;

--
-- AUTO_INCREMENT for table `buyers_reported`
--
ALTER TABLE `buyers_reported`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `cart_items`
--
ALTER TABLE `cart_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `messages`
--
ALTER TABLE `messages`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=61;

--
-- AUTO_INCREMENT for table `notification_buyer`
--
ALTER TABLE `notification_buyer`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `notification_seller`
--
ALTER TABLE `notification_seller`
  MODIFY `notification_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `orders`
--
ALTER TABLE `orders`
  MODIFY `order_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `products`
--
ALTER TABLE `products`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=139;

--
-- AUTO_INCREMENT for table `productvariations`
--
ALTER TABLE `productvariations`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT for table `rating`
--
ALTER TABLE `rating`
  MODIFY `rating_id` int(250) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `report_sellerproduct`
--
ALTER TABLE `report_sellerproduct`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `riders`
--
ALTER TABLE `riders`
  MODIFY `rider_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3008;

--
-- AUTO_INCREMENT for table `sellers`
--
ALTER TABLE `sellers`
  MODIFY `seller_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=80;

--
-- AUTO_INCREMENT for table `user_roles`
--
ALTER TABLE `user_roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `addresses_buyer`
--
ALTER TABLE `addresses_buyer`
  ADD CONSTRAINT `addresses_buyer_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`) ON DELETE CASCADE;

--
-- Constraints for table `addresses_rider`
--
ALTER TABLE `addresses_rider`
  ADD CONSTRAINT `addresses_rider_ibfk_1` FOREIGN KEY (`rider_id`) REFERENCES `riders` (`rider_id`) ON DELETE CASCADE;

--
-- Constraints for table `addresses_seller`
--
ALTER TABLE `addresses_seller`
  ADD CONSTRAINT `addresses_seller_ibfk_1` FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`seller_id`) ON DELETE CASCADE;

--
-- Constraints for table `assignrider`
--
ALTER TABLE `assignrider`
  ADD CONSTRAINT `assignrider_ibfk_1` FOREIGN KEY (`rider_id`) REFERENCES `riders` (`rider_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `assignrider_ibfk_2` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`) ON DELETE CASCADE;

--
-- Constraints for table `buyers`
--
ALTER TABLE `buyers`
  ADD CONSTRAINT `buyers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `cart_items`
--
ALTER TABLE `cart_items`
  ADD CONSTRAINT `cart_items_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`),
  ADD CONSTRAINT `cart_items_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `products` (`Id`);

--
-- Constraints for table `notification_seller`
--
ALTER TABLE `notification_seller`
  ADD CONSTRAINT `notification_seller_ibfk_1` FOREIGN KEY (`buyer_id`) REFERENCES `buyers` (`buyer_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `products`
--
ALTER TABLE `products`
  ADD CONSTRAINT `products_ibfk_1` FOREIGN KEY (`Seller_Id`) REFERENCES `sellers` (`seller_id`) ON DELETE CASCADE;

--
-- Constraints for table `riders`
--
ALTER TABLE `riders`
  ADD CONSTRAINT `riders_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `sellers`
--
ALTER TABLE `sellers`
  ADD CONSTRAINT `sellers_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `users`
--
ALTER TABLE `users`
  ADD CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `user_roles` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
