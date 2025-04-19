-- psql -U postgres
-- \c maindb

insert into roles (id, name) values (gen_random_uuid(), 'Administrador'), (gen_random_uuid(), 'Logistica'), (gen_random_uuid(), 'Compras'),  (gen_random_uuid(), 'Ventas'), (gen_random_uuid(), 'Cliente'), (gen_random_uuid(), 'Vendedor');

insert into privileges (id, name, module, module_attribute, access_type) values
(gen_random_uuid(), 'Consulta Producto Bodega', 'Inventario', 'read', 'ALLOW'),  -- 001
(gen_random_uuid(), 'Registro Fabricante', 'Proveedores', 'create', 'ALLOW'), -- 002
(gen_random_uuid(), 'Gestion Portafolio', 'Proveedores', 'create', 'ALLOW'), -- 003 
(gen_random_uuid(), 'Registro Productos', 'Inventario', 'create', 'ALLOW'), -- 004 
(gen_random_uuid(), 'Registro Masivo Productos', 'Inventario', 'create', 'ALLOW'), -- 005
(gen_random_uuid(), 'Definicion Reglas Legales', 'Reglas', 'create', 'ALLOW'), -- 006
(gen_random_uuid(), 'Definicion Reglas Tributarias', 'Reglas', 'create', 'ALLOW'), -- 007
(gen_random_uuid(), 'Definicion Reglas Comerciales', 'Reglas', 'create', 'ALLOW'), -- 008
(gen_random_uuid(), 'Reportes Ventas', 'Reportes', 'create', 'ALLOW'), -- 009
(gen_random_uuid(), 'Reportes Vendedor', 'Reportes', 'create', 'ALLOW'), -- 010
(gen_random_uuid(), 'Reportes Rotacion Inventario', 'Reportes', 'create', 'ALLOW'), -- 011
(gen_random_uuid(), 'Listado Productos', 'Inventario', 'read', 'ALLOW'), -- 012
(gen_random_uuid(), 'Consulta Inventario', 'Inventario', 'read', 'ALLOW'), -- 013
(gen_random_uuid(), 'Consulta Ventas', 'Ventas', 'read', 'ALLOW'), -- 014
(gen_random_uuid(), 'Optimizacion Compras', 'Inventario', 'create', 'ALLOW'), -- 015
(gen_random_uuid(), 'Alertas Inventario', 'Inventario', 'create', 'ALLOW'), -- 016
(gen_random_uuid(), 'Generacion Ruta Entrega', 'Rutas', 'create', 'ALLOW'), -- 017
(gen_random_uuid(), 'Ubicación Camión', 'Rutas', 'read', 'ALLOW'), -- 018
(gen_random_uuid(), 'Optimizar Ruta Entrega', 'Rutas', 'create', 'ALLOW'), -- 019
(gen_random_uuid(), 'Trazabilidad Logistica', 'Inventario', 'read', 'ALLOW'), -- 020
(gen_random_uuid(), 'Vista Perfil Vendedor', 'Ventas', 'create', 'ALLOW'), -- 021
(gen_random_uuid(), 'Seguimiento Plan Ventas Vendedor', 'Ventas', 'read', 'ALLOW'), -- 022
(gen_random_uuid(), 'Definir Plan Ventas', 'Ventas', 'create', 'ALLOW'), -- 023
(gen_random_uuid(), 'Listado Usuarios', 'Usuarios', 'read', 'ALLOW'), -- 024
(gen_random_uuid(), 'Detalle Usuario', 'Usuarios', 'read', 'ALLOW'), -- 025
(gen_random_uuid(), 'Agregar Usuario', 'Usuarios', 'create', 'ALLOW'), -- 026
(gen_random_uuid(), 'Eliminar Usuario', 'Usuarios', 'delete', 'ALLOW'), -- 027
(gen_random_uuid(), 'Movimientos Inventario', 'Inventario', 'read', 'ALLOW'), -- 028
(gen_random_uuid(), 'Gestion Bodegas', 'Inventario', 'create', 'ALLOW'), -- 029
(gen_random_uuid(), 'Detalle Bodegas', 'Inventario', 'read', 'ALLOW'), -- 030
(gen_random_uuid(), 'Pedidos', 'Cliente', 'create', 'ALLOW'), -- 031
(gen_random_uuid(), 'Configuracion', 'Cliente', 'create', 'ALLOW'), -- 032
(gen_random_uuid(), 'Inventario', 'Cliente', 'read', 'ALLOW'), -- 033
(gen_random_uuid(), 'Perfil', 'Cliente', 'read', 'ALLOW'), -- 034
(gen_random_uuid(), 'Clientes', 'Vendedor', 'read', 'ALLOW'), -- 035
(gen_random_uuid(), 'Visitas', 'Vendedor', 'create', 'ALLOW'), -- 036
(gen_random_uuid(), 'PQRS', 'Vendedor', 'read', 'ALLOW'), -- 037
(gen_random_uuid(), 'Tiendas', 'Vendedor', 'read', 'ALLOW'); -- 038

insert into warehouse (id,name,address,country,city,location,storage_volume,available_volume,truck_capacity) values (gen_random_uuid(), 'Bodega principal', 'Calle 80', 'Colombia', 'Bogota', '-37.4885502, -72.3302756', 500, 500, 5);

-- Asignar todos los permisos al rol admin
insert into role_privilege (privilege_id, role_id) select id, {{id_rol_admin}} from privileges;