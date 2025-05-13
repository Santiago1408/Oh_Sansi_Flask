-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 11-05-2025 a las 06:05:01
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12
SET
    SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";

START TRANSACTION;

SET
    time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;

/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;

/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;

/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `olimpiada`
--
-- Eliminar tablas si existen, en orden inverso de dependencias
DROP TABLE IF EXISTS compite;

DROP TABLE IF EXISTS puede_tener;

DROP TABLE IF EXISTS inscripcion;

DROP TABLE IF EXISTS competencia;

DROP TABLE IF EXISTS competidor;

DROP TABLE IF EXISTS tutor;

DROP TABLE IF EXISTS administrador;

DROP TABLE IF EXISTS cajero;

DROP TABLE IF EXISTS usuario;

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `administrador`
--
CREATE TABLE
    `administrador` (
        `id_administrador` int (11) NOT NULL,
        `id_usuario` int (11) DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `administrador`
--
INSERT INTO
    `administrador` (`id_administrador`, `id_usuario`)
VALUES
    (1, 5);

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `cajero`
--
CREATE TABLE
    `cajero` (
        `id_cajero` int (11) NOT NULL,
        `id_usuario` int (11) DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `cajero`
--
INSERT INTO
    `cajero` (`id_cajero`, `id_usuario`)
VALUES
    (1, 4);

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `competencia`
--
CREATE TABLE
    `competencia` (
        `id_competencia` int (11) NOT NULL,
        `area` varchar(50) DEFAULT NULL,
        `categoria` varchar(50) DEFAULT NULL,
        `grado` varchar(50) DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `competencia`
--
INSERT INTO
    `competencia` (`id_competencia`, `area`, `categoria`, `grado`)
VALUES
    (8, 'Matematicas', 'Guacamayo', '3ro Secundaria'),
    (13, 'Robotica', 'Bufeo', '2do Secundaria'),
    (15, 'Quimica', '6S', '6to Secundaria'),
    (18, 'Robotica', 'Lego S', '6to Secundaria'),
    (19, 'Robotica', 'Lego S', '4to Secundaria'),
    (
        20,
        'Astronomia-Astrofisica',
        '3P',
        '3ro Primaria'
    ),
    (21, 'Robotica', 'Builders S', '6to Secundaria'),
    (
        22,
        'Astronomia-Astrofisica',
        '6S',
        '6to Secundaria'
    ),
    (23, 'Quimica', '6S', '6to Secundaria'),
    (24, 'Informatica', 'Jucumari', '6to Secundaria'),
    (25, 'Informatica', 'Puma', '6to Secundaria'),
    (
        27,
        'Astronomia-Astrofisica',
        '3P',
        '3ro Primaria'
    ),
    (28, 'Biologia', '3S', '3ro Secundaria'),
    (
        29,
        'Astronomia-Astrofisica',
        '4P',
        '4to Primaria'
    ),
    (
        32,
        'Matematicas',
        'Cuarto Nivel',
        '4to Secundaria'
    ),
    (33, 'Informatica', 'Jucumari', '6to Secundaria');

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `competidor`
--
CREATE TABLE
    `competidor` (
        `id_competidor` int (11) NOT NULL,
        `ci` varchar(10) DEFAULT NULL,
        `fecha_nacimiento` date DEFAULT NULL,
        `colegio` varchar(50) DEFAULT NULL,
        `curso` varchar(50) DEFAULT NULL,
        `departamento` varchar(50) DEFAULT NULL,
        `provincia` varchar(50) DEFAULT NULL,
        `nombre` varchar(50) DEFAULT NULL,
        `apellido` varchar(50) DEFAULT NULL,
        `email` varchar(50) DEFAULT NULL,
        `telefono` varchar(8) DEFAULT NULL,
        `estado` varchar(50) DEFAULT NULL,
        `id_tutor` int (11) DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `competidor`
--
INSERT INTO
    `competidor` (
        `id_competidor`,
        `ci`,
        `fecha_nacimiento`,
        `colegio`,
        `curso`,
        `departamento`,
        `provincia`,
        `nombre`,
        `apellido`,
        `email`,
        `telefono`,
        `estado`,
        `id_tutor`
    )
VALUES
    (
        1,
        '54162595',
        '2003-12-12',
        'Instituto Americano',
        '6to Secundaria',
        'Cochabamba',
        'Cercado',
        'Lucas',
        'Vargas',
        'lucasvargas@gmail.com',
        '74445896',
        'registrado',
        2
    ),
    (
        2,
        '17445297',
        '2004-06-02',
        'Instituto Americano',
        '5to Secundaria',
        'Cochabamba',
        'Cercado',
        'Gabriel',
        'Moscozo',
        'gabisex@gmail.com',
        '74445862',
        'pendiente',
        2
    ),
    (
        3,
        '41255574',
        '2004-11-08',
        'Laredo',
        '4to Secundaria',
        'Cochabamba',
        'Quillacollo',
        'Alvaro',
        'Tapia',
        'alvin@gmail.com',
        '74455216',
        'registrado',
        2
    ),
    (
        18,
        '1665522',
        '2006-08-05',
        'Calvert',
        '4to Secundaria',
        'La Paz',
        'Murillo',
        'Carlos',
        'Camacho',
        'camachocarlos@gmail.com',
        '75884167',
        'validado',
        2
    ),
    (
        19,
        '52211468',
        '2004-09-17',
        'Loyola',
        '4to Secundaria',
        'Santa Cruz',
        'Warnes',
        'Johan',
        'Daher',
        'camba@gmail.com',
        '78495844',
        'validado',
        2
    );

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `compite`
--
CREATE TABLE
    `compite` (
        `id_competencia` int (11) NOT NULL,
        `id_competidor` int (11) NOT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `inscripcion`
--
CREATE TABLE
    `inscripcion` (
        `id_inscripcion` int (11) NOT NULL,
        `id_competidor` int (11) DEFAULT NULL,
        `id_tutor` int (11) DEFAULT NULL,
        `fecha_inscripcion` date DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `puede_tener`
--
CREATE TABLE
    `puede_tener` (
        `id_tutor` int (11) NOT NULL,
        `id_competidor` int (11) NOT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `tutor`
--
CREATE TABLE
    `tutor` (
        `id_tutor` int (11) NOT NULL,
        `id_usuario` int (11) DEFAULT NULL,
        `tipo_tutor` varchar(50) DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

-- Agregar el campo `area` a la tabla `tutor`
ALTER TABLE `tutor` ADD `area` VARCHAR(255) DEFAULT NULL;

-- Volcado de datos para la tabla `tutor`
--
INSERT INTO
    `tutor` (`id_tutor`, `id_usuario`, `tipo_tutor`, `area`)
VALUES
    (1, 3, 'padre', 'matemática'),
    (2, 6, 'profesor', 'robótica'),
    (3, 7, 'profesor', 'física'),
    (4, 8, 'profesor', 'informática');

-- --------------------------------------------------------
--
-- Estructura de tabla para la tabla `usuario`
--
CREATE TABLE
    `usuario` (
        `id_usuario` int (11) NOT NULL,
        `nombre` varchar(50) DEFAULT NULL,
        `apellido` varchar(50) DEFAULT NULL,
        `email` varchar(50) DEFAULT NULL,
        `telefono` varchar(10) DEFAULT NULL,
        `contrasenia` varchar(50) DEFAULT NULL,
        `rol` varchar(20) DEFAULT NULL
    ) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuario`
--
INSERT INTO
    `usuario` (
        `id_usuario`,
        `nombre`,
        `apellido`,
        `email`,
        `telefono`,
        `contrasenia`,
        `rol`
    )
VALUES
    (
        1,
        'Josue ',
        'Garcia',
        'josueg4rcia@gmail.com',
        '69435058',
        'Jo$ue1408',
        'administrador'
    ),
    (
        2,
        'Santiago',
        'Gamez',
        'santiago@gmail.com',
        '70782381',
        'santiago0814',
        'cajero'
    ),
    (
        3,
        'Carlos',
        'Ayala',
        'carlitos@gmail.com',
        '75147596',
        'aeiou',
        'tutor'
    ),
    (
        4,
        'Luis Sebastian',
        'Villarroel Saavedra',
        'luisvill@gmail.com',
        '74154426',
        'Lui$1010',
        'cajero'
    ),
    (
        5,
        'Cristopher Marcelo',
        'Ajata Flores',
        'cheto@gmail.com',
        '75442556',
        'Cri$topher1',
        'administrador'
    ),
    (
        6,
        'Jose Manuel',
        'Tardio Fernandez',
        'tardiojose@gmail.com',
        '75193478',
        'Tardio06%',
        'tutor'
    ),
    (
        7,
        'Juaquin Daniel',
        'Pickman Arce',
        'pedrito@gmail.com',
        '75544114',
        'Pedro01@',
        'tutor'
    ),
    (
        8,
        'Fernanda',
        'Larrea Jimenez',
        'ferlarrea@gmail.com',
        '78445714',
        'Fernanda1#',
        'tutor'
    );

--
-- Índices para tablas volcadas
--
--
-- Indices de la tabla `administrador`
--
ALTER TABLE `administrador` ADD PRIMARY KEY (`id_administrador`),
ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `cajero`
--
ALTER TABLE `cajero` ADD PRIMARY KEY (`id_cajero`),
ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `competencia`
--
ALTER TABLE `competencia` ADD PRIMARY KEY (`id_competencia`);

--
-- Indices de la tabla `competidor`
--
ALTER TABLE `competidor` ADD PRIMARY KEY (`id_competidor`),
ADD KEY `id_tutor` (`id_tutor`);

--
-- Indices de la tabla `compite`
--
ALTER TABLE `compite` ADD PRIMARY KEY (`id_competencia`, `id_competidor`),
ADD KEY `id_competidor` (`id_competidor`);

--
-- Indices de la tabla `inscripcion`
--
ALTER TABLE `inscripcion` ADD PRIMARY KEY (`id_inscripcion`),
ADD KEY `id_competidor` (`id_competidor`),
ADD KEY `id_tutor` (`id_tutor`);

--
-- Indices de la tabla `puede_tener`
--
ALTER TABLE `puede_tener` ADD PRIMARY KEY (`id_tutor`, `id_competidor`),
ADD KEY `id_competidor` (`id_competidor`);

--
-- Indices de la tabla `tutor`
--
ALTER TABLE `tutor` ADD PRIMARY KEY (`id_tutor`),
ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario` ADD PRIMARY KEY (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--
--
-- AUTO_INCREMENT de la tabla `competencia`
--
ALTER TABLE `competencia` MODIFY `id_competencia` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 34;

--
-- AUTO_INCREMENT de la tabla `competidor`
--
ALTER TABLE `competidor` MODIFY `id_competidor` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 22;

--
-- AUTO_INCREMENT de la tabla `compite`
--
ALTER TABLE `compite` MODIFY `id_competencia` int (11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `inscripcion`
--
ALTER TABLE `inscripcion` MODIFY `id_inscripcion` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 12;

--
-- AUTO_INCREMENT de la tabla `tutor`
--
ALTER TABLE `tutor` MODIFY `id_tutor` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 5;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario` MODIFY `id_usuario` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 9;

-- AUTO_INCREMENT de la tabla `cajero`
ALTER TABLE `cajero` MODIFY `id_cajero` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 2;

-- AUTO_INCREMENT de la tabla `administrador`
ALTER TABLE `administrador` MODIFY `id_administrador` int (11) NOT NULL AUTO_INCREMENT,
AUTO_INCREMENT = 2;

--
-- Restricciones para tablas volcadas
--
--
-- Filtros para la tabla `administrador`
--
ALTER TABLE `administrador` ADD CONSTRAINT `administrador_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

--
-- Filtros para la tabla `cajero`
--
ALTER TABLE `cajero` ADD CONSTRAINT `cajero_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

--
-- Filtros para la tabla `competidor`
--
ALTER TABLE `competidor` ADD CONSTRAINT `competidor_ibfk_1` FOREIGN KEY (`id_tutor`) REFERENCES `tutor` (`id_tutor`);

--
-- Filtros para la tabla `compite`
--
ALTER TABLE `compite` ADD CONSTRAINT `compite_ibfk_1` FOREIGN KEY (`id_competencia`) REFERENCES `competencia` (`id_competencia`),
ADD CONSTRAINT `compite_ibfk_2` FOREIGN KEY (`id_competidor`) REFERENCES `competidor` (`id_competidor`);

--
-- Filtros para la tabla `inscripcion`
--
ALTER TABLE `inscripcion` ADD CONSTRAINT `inscripcion_ibfk_1` FOREIGN KEY (`id_competidor`) REFERENCES `competidor` (`id_competidor`),
ADD CONSTRAINT `inscripcion_ibfk_2` FOREIGN KEY (`id_tutor`) REFERENCES `tutor` (`id_tutor`);

--
-- Filtros para la tabla `puede_tener`
--
ALTER TABLE `puede_tener` ADD CONSTRAINT `puede_tener_ibfk_1` FOREIGN KEY (`id_tutor`) REFERENCES `tutor` (`id_tutor`),
ADD CONSTRAINT `puede_tener_ibfk_2` FOREIGN KEY (`id_competidor`) REFERENCES `competidor` (`id_competidor`);

--
-- Filtros para la tabla `tutor`
--
ALTER TABLE `tutor` ADD CONSTRAINT `tutor_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuario` (`id_usuario`);

COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;

/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;

/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;