-- psql -U postgres
-- \c maindb


-- USERS DB
insert into roles (id, name) values 
('8646926d-7ea6-40f4-ab02-c57c2842e076', 'Administrador'), 
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', 'Logistica'), 
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'Compras'),  
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', 'Ventas'), 
('9ab54a6d-d42c-4b28-ba4d-99fb1624f3d9', 'Cliente'), 
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', 'Vendedor');


insert into privileges (id, name, module, module_attribute, access_type) values
('04eae931-59ff-496e-8cae-1ec0ddf4aa9e', 'Consulta Producto Bodega', 'Inventario', 'read', 'ALLOW'),  -- 001
('72f58609-1f6d-4cb3-bf8c-7940d1019012', 'Registro Fabricante', 'Proveedores', 'create', 'ALLOW'), -- 002
('0e9de9e1-55c1-46bd-94f9-3f7372ac3004', 'Gestion Portafolio', 'Proveedores', 'create', 'ALLOW'), -- 003 
('c87ad87b-8379-488c-80f7-daedcd76fd3a', 'Registro Productos', 'Inventario', 'create', 'ALLOW'), -- 004 
('f7c72544-fe6b-4448-8831-5fc0d72f95a1', 'Registro Masivo Productos', 'Inventario', 'create', 'ALLOW'), -- 005
('551d81eb-9e47-48ca-8707-7b3234b91278', 'Definicion Reglas Legales', 'Reglas', 'create', 'ALLOW'), -- 006
('2fb48d72-6697-489a-83d9-5f0ac5a45fdc', 'Definicion Reglas Tributarias', 'Reglas', 'create', 'ALLOW'), -- 007
('166bd87e-ea75-4e4c-a633-1579d429d74c', 'Definicion Reglas Comerciales', 'Reglas', 'create', 'ALLOW'), -- 008
('ad92dc41-f5a4-4428-ae4a-76d8e9d518cc', 'Reportes Ventas', 'Reportes', 'create', 'ALLOW'), -- 009
('01d0429a-57dd-459c-8c90-669a89b38acc', 'Reportes Vendedor', 'Reportes', 'create', 'ALLOW'), -- 010
('d6de107a-093f-4c9d-83c0-8a8dbe1bb8f6', 'Reportes Rotacion Inventario', 'Reportes', 'create', 'ALLOW'), -- 011
('d344a27f-20ab-460a-936f-187c9674d009', 'Listado Productos', 'Inventario', 'read', 'ALLOW'), -- 012
('d8bb42c1-3273-4e17-8d6c-18854a6f5943', 'Consulta Inventario', 'Inventario', 'read', 'ALLOW'), -- 013
('9e160843-3eb0-4abd-b2c0-6f019271a62a', 'Consulta Ventas', 'Ventas', 'read', 'ALLOW'), -- 014
('68b7bf2d-7f21-4a6f-9f91-a3fca86ab51e', 'Optimizacion Compras', 'Inventario', 'create', 'ALLOW'), -- 015
('f29cbac7-1f91-4b54-b796-02168078ac95', 'Alertas Inventario', 'Inventario', 'create', 'ALLOW'), -- 016
('0d977e25-9dbc-4bbe-95a2-682b61283a0f', 'Generacion Ruta Entrega', 'Rutas', 'create', 'ALLOW'), -- 017
('ab2b45b3-95e7-40c3-bf6b-f6123e12e9d5', 'Ubicación Camión', 'Rutas', 'read', 'ALLOW'), -- 018
('8a174554-816a-44fd-ba42-d35b5126247a', 'Optimizar Ruta Entrega', 'Rutas', 'create', 'ALLOW'), -- 019
('6524060c-16a1-4a6d-a1c3-54fcdbbe1619', 'Trazabilidad Logistica', 'Inventario', 'read', 'ALLOW'), -- 020
('9ec00f4f-8d5b-4cf6-aa7a-2c95dd3a9ef0', 'Vista Perfil Vendedor', 'Ventas', 'create', 'ALLOW'), -- 021
('58d03750-7746-425a-b6a7-2b5ffa0d5e0f', 'Seguimiento Plan Ventas Vendedor', 'Ventas', 'read', 'ALLOW'), -- 022
('344dddfb-ed3d-41bb-9d12-1ef7d8f04d3a', 'Definir Plan Ventas', 'Ventas', 'create', 'ALLOW'), -- 023
('9dcd5eac-2ac2-4784-b304-a8897fab2ad1', 'Listado Usuarios', 'Usuarios', 'read', 'ALLOW'), -- 024
('eaf70b0f-9c06-46f0-a931-011a8d65cb83', 'Detalle Usuario', 'Usuarios', 'read', 'ALLOW'), -- 025
('24d10646-8f9a-461f-b071-e86fb323eccf', 'Agregar Usuario', 'Usuarios', 'create', 'ALLOW'), -- 026
('ff1ac836-697b-441c-8841-ceb28fe1bb64', 'Eliminar Usuario', 'Usuarios', 'delete', 'ALLOW'), -- 027
('0a830cbb-d6cc-4ce8-b488-91abcf4fb5f0', 'Movimientos Inventario', 'Inventario', 'read', 'ALLOW'), -- 028
('27c7afed-55a5-4425-bb45-3ac561873995', 'Gestion Bodegas', 'Inventario', 'create', 'ALLOW'), -- 029
('92c04450-dbcc-4ee7-bda9-165b65b671c4', 'Detalle Bodegas', 'Inventario', 'read', 'ALLOW'), -- 030
('1e5053a2-4df6-4763-9ee8-b2b43fff2517', 'Pedidos', 'Cliente', 'create', 'ALLOW'), -- 031
('89aa371b-b8ea-432a-8083-ae37cc2fa924', 'Configuracion', 'Cliente', 'create', 'ALLOW'), -- 032
('6ccc2140-309b-464a-be73-d1f286c41d68', 'Inventario', 'Cliente', 'read', 'ALLOW'), -- 033
('738ec2a8-3ad2-4dac-95dd-fcd82361944e', 'Perfil', 'Cliente', 'read', 'ALLOW'), -- 034
('b4635684-e8f2-4bdd-8975-5dc8455dfdf8', 'Clientes', 'Vendedor', 'read', 'ALLOW'), -- 035
('c5488df4-6980-49b5-9a30-42c59f87ff53', 'Visitas', 'Vendedor', 'create', 'ALLOW'), -- 036
('d91f4e87-8b58-4b52-a105-6ed6dc41780e', 'PQRS', 'Vendedor', 'read', 'ALLOW'), -- 037
('be11745e-5802-49a1-bfbe-44e7e838ce84', 'Tiendas', 'Vendedor', 'read', 'ALLOW'); -- 038


-- Asignar todos los permisos al rol admin
insert into role_privilege (privilege_id, role_id) select id, '8646926d-7ea6-40f4-ab02-c57c2842e076' from privileges;

-- Asignar permisos correspondientes a otros usuarios
insert into role_privilege ( role_id, privilege_id) values
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', '04eae931-59ff-496e-8cae-1ec0ddf4aa9e'),
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', '68b7bf2d-7f21-4a6f-9f91-a3fca86ab51e'),
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', '0d977e25-9dbc-4bbe-95a2-682b61283a0f'),
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', 'ab2b45b3-95e7-40c3-bf6b-f6123e12e9d5'),
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', '8a174554-816a-44fd-ba42-d35b5126247a'),
('07534e4c-4b67-49e7-bb67-3e8ad1d08c92', '6524060c-16a1-4a6d-a1c3-54fcdbbe1619'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '04eae931-59ff-496e-8cae-1ec0ddf4aa9e'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '72f58609-1f6d-4cb3-bf8c-7940d1019012'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '0e9de9e1-55c1-46bd-94f9-3f7372ac3004'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'c87ad87b-8379-488c-80f7-daedcd76fd3a'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'f7c72544-fe6b-4448-8831-5fc0d72f95a1'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '551d81eb-9e47-48ca-8707-7b3234b91278'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '2fb48d72-6697-489a-83d9-5f0ac5a45fdc'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '166bd87e-ea75-4e4c-a633-1579d429d74c'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'd6de107a-093f-4c9d-83c0-8a8dbe1bb8f6'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'd344a27f-20ab-460a-936f-187c9674d009'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'd8bb42c1-3273-4e17-8d6c-18854a6f5943'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '9e160843-3eb0-4abd-b2c0-6f019271a62a'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', '68b7bf2d-7f21-4a6f-9f91-a3fca86ab51e'),
('2f48a66d-6ee9-41f3-950f-10350c9935da', 'f29cbac7-1f91-4b54-b796-02168078ac95'),
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', 'ad92dc41-f5a4-4428-ae4a-76d8e9d518cc'),
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', '01d0429a-57dd-459c-8c90-669a89b38acc'),
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', 'd6de107a-093f-4c9d-83c0-8a8dbe1bb8f6'),
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', 'd344a27f-20ab-460a-936f-187c9674d009'),
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', '9ec00f4f-8d5b-4cf6-aa7a-2c95dd3a9ef0'),
('b30aca0e-b68d-4b4c-977e-7b47f6a79482', '58d03750-7746-425a-b6a7-2b5ffa0d5e0f'),
('9ab54a6d-d42c-4b28-ba4d-99fb1624f3d9', '1e5053a2-4df6-4763-9ee8-b2b43fff2517'),
('9ab54a6d-d42c-4b28-ba4d-99fb1624f3d9', '89aa371b-b8ea-432a-8083-ae37cc2fa924'),
('9ab54a6d-d42c-4b28-ba4d-99fb1624f3d9', '6ccc2140-309b-464a-be73-d1f286c41d68'),
('9ab54a6d-d42c-4b28-ba4d-99fb1624f3d9', '738ec2a8-3ad2-4dac-95dd-fcd82361944e'),
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', '1e5053a2-4df6-4763-9ee8-b2b43fff2517'),
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', '89aa371b-b8ea-432a-8083-ae37cc2fa924'),
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', 'b4635684-e8f2-4bdd-8975-5dc8455dfdf8'),
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', 'c5488df4-6980-49b5-9a30-42c59f87ff53'),
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', 'd91f4e87-8b58-4b52-a105-6ed6dc41780e'),
('af31c4c0-7fb5-4f61-8162-2ee33e193fde', 'be11745e-5802-49a1-bfbe-44e7e838ce84');

-- ORDERS DB

insert into warehouse (id,name,address,country,city,location,storage_volume,available_volume,truck_capacity) values 
(gen_random_uuid(), 'Bodega principal', 'Calle 80', 'Colombia', 'Bogota', '4.735142, -74.132452', 500, 500, 5),
(gen_random_uuid(), 'Bodega Secundaria', 'Calle 170', 'Colombia', 'Bogota', '4.754507, -74.045692', 200, 500, 5),
(gen_random_uuid(), 'Bodega Terciaria', 'Zona industrial', 'Colombia', 'Bogota', '4.629951, -74.114383', 1500, 500, 5);

-- ROUTES DB

-- PROVIDERS DB