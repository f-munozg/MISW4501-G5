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


insert into role_privilege (role_id, privilege_id) values
('cc4a4702-3d00-4a1f-9474-d8ff331485a7', )

perfil ventas
productos, vendedor, reportes
-> 009
-> 010
-> 011
-> 012
-> 021
-> 022

perfil Compras
productos, fabricantes, reportes, inventario, ventas, compras, reglas
-> 001
-> 002
-> 003
-> 004
-> 005
-> 006
-> 007
-> 008
-> 011
-> 012
-> 013
-> 014
-> 015
-> 016

perfil logistica
inventario, generacion ruta, optimizacion compras, rastreo, optimizacion entrega, trazabilidad pedidos
-> 001
-> 015
-> 017
-> 018
-> 019
-> 020

perfil administrador
gestion productos, gestion fabricantes, gestion vendedores, gestion reportes, gestion pedidos, gestion bodegas e inventarios, gestion ventas, gestion compras, gestion usuarios, gestion rutas, gestion reglas
-> 001
-> 002
-> 003
-> 004
-> 005
-> 006
-> 007
-> 008
-> 009
-> 010
-> 011
-> 012
-> 013
-> 014
-> 015
-> 016
-> 017
-> 018
-> 019
-> 020
-> 021
-> 022
-> 023
-> 024
-> 025
-> 026
-> 027
-> 028
-> 029
-> 030

perfil Cliente
-> 031
-> 032
-> 033
-> 034


perfil vendedor
-> 031
-> 032
-> 035
-> 036
-> 037
-> 038