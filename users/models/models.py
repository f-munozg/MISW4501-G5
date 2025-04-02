# users
numIdentificacion: int
nombre: string
password: string
email: string
rol: Rol
# roles
nombreRol: string
privilegios: list[privilegios]

# privilegio
nombrePrivilegio: string
modulo: string
atributoModulo: string
tipoAcceso: enum
# enum tipoAcceso
permitir
solo_lectura
denegar