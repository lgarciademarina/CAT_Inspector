from zipfile import ZipFile
from gzip import GzipFile
from io import BytesIO

from qgis.core import Qgis
from qgis.utils import iface


class File:
    def __init__(self, path) -> None:
        self.path = path
        self.valid = True
        print(f'Fichero CAT: {self.path}')
    
    def get_file_info(self):
        try:
            with ZipFile(self.path) as compressed:
                for file in compressed.namelist():
                    data = BytesIO(compressed.read(file))
                    with ZipFile(data) as compressedCAT:
                        gz = compressedCAT.filelist[1] # El primer elemento es la carpeta contenedora
                        print(f'Primer fichero gz: {gz.filename}')
                        if gz.filename.endswith('.gz'):
                            with GzipFile(fileobj=compressedCAT.open(gz)) as CAT:
                                row = CAT.readline()
                                info = row.decode('iso-8859-1')
                                # Important! We do not use switch to mantain compatibility for versions prior to 3.11
                                tipo_de_registro = info[0:2]
                                if tipo_de_registro == '01':
                                    # REGISTRO DE CABECERA
                                    return self.get_cabecera(info)
        except:
            iface.messageBar().pushMessage('File', f'El fichero no es válido', level=Qgis.Critical)
            self.valid = False
            return {}

    def find_refcat(self, refcat):
        if self.valid:
            print(f'Buscando Referencia Catastral: {refcat}')
            with ZipFile(self.path) as compressed:
                for file in compressed.namelist():
                    data = BytesIO(compressed.read(file))
                    with ZipFile(data) as compressedCAT:
                        for gz in compressedCAT.filelist:
                            if gz.filename.endswith('.gz'):
                                with GzipFile(fileobj=compressedCAT.open(gz)) as CAT:
                                    self.valid = True
                                    registros = []
                                    for row in CAT.readlines():
                                        info = row.decode('iso-8859-1')
                                        # Important! We do not use switch to mantain compatibility for versions prior to 3.11
                                        tipo_de_registro = info[0:2]
                                        if info[30:44] == refcat:
                                            if tipo_de_registro == '01':
                                                # REGISTRO DE CABECERA
                                                #registros.append(self.get_cabecera(info))
                                                pass
                                            elif tipo_de_registro == '11':
                                                # REGISTRO DE FINCA
                                                registros.append(self.get_finca(info))
                                            elif tipo_de_registro == '13':
                                                # UNIDAD CONSTRUCTIVA
                                                registros.append(self.get_UC(info))
                                            elif tipo_de_registro == '14':
                                                # CONSTRUCCION
                                                registros.append(self.get_constru(info))
                                            elif tipo_de_registro == '15':
                                                # BIEN INMUEBLE
                                                registros.append(self.get_BI(info))
                                            elif tipo_de_registro == '16':
                                                # REPARTO DE ELEMENTOS COMUNES
                                                registros.append(self.get_EC(info))
                                            elif tipo_de_registro == '17':
                                                # CULTIVOS AGRARIOS
                                                registros.append(self.get_cultivos(info))
                                            elif tipo_de_registro == '90':
                                                # REGISTRO DE COLA
                                                # registros.append(self.get_cola(info))
                                                pass
                                    del CAT
                                    if len(registros) > 0:
                                        return registros
        else:
            iface.messageBar().pushMessage('File', f'El fichero no es válido', level=Qgis.Critical)
    
    def get_cabecera(self, info):
        registro = {'tipo_de_registro': '01', 'referencia': 'Registro de cabecera'}
        # 1. Identificación de la entidad generadora
        registro['tipo_de_entidad_generadora'] = info[2:3]
        registro['codigo_delegacion_MEH'] = info[3:5]
        blanco = info[5:6]
        registro['nombre_de_entidad_generadora'] = info[12:39].strip()
        # 2. Datos del fichero
        registro['fecha_de_generacion'] = info[45:47] + '-' + info[43:45] + '-' + info[39:43]
        registro['hora_de_generacion'] = info[47:49] + ':' + info[49:51] + ':' + info[51:53]
        registro['tipo_de_fichero'] = info[53:57]
        registro['descripcion_del_contenido'] = info[57:96].strip()
        return registro
    
    def get_finca(self, info):
        registro = {'tipo_de_registro': '11', 'referencia': 'Registro de Finca'}
        # 1. Identificación de la parcela catastral
        registro['codigo_delegacion_MEH'] = info[23:25]
        registro['codigo_municipio_DGC'] = info[25:28]
        registro['caracteristicas_especiales'] = info[28:30]
        registro['parcela_catastral'] = info[30:44]
        # 2. Domicilio tributario / Localización de la parcela
        registro['codigo_provincia_INE'] = info[50:52]
        registro['nombre_provincia'] = info[52:77].strip()
        registro['codigo_municipio_DGC'] = info[77:80]
        registro['codigo_municipio_INE'] = info[80:83]
        registro['nombre_municipio'] = info[83:123].strip()
        registro['nombre_entidad_menor'] = info[123:153].strip()
        registro['codigo_de_via_publica_DGC'] = info[153:158]
        registro['tipo_de_via_o_sigla_publica'] = info[158:163]
        registro['nombre_de_via_publica'] = info[163:188].strip()
        registro['primer_numero_de_policia'] = info[188:192]
        registro['primera_letra'] = info[192:193]
        registro['segundo_numero_de_policia'] = info[193:197]
        registro['segunda_letra'] = info[197:198]
        registro['kilometro'] = info[198:203]
        registro['bloque'] = info[203:207]
        registro['texto_de_direccion_no_estructurada'] = info[215:240].strip()
        registro['codigo_postal'] = info[240:245]
        registro['codigo_municipio_origen_DGC'] = info[247:250]
        registro['codigo_zona_de_concentracion'] = info[250:252]
        registro['codigo_poligono_rustico'] = info[252:255]
        registro['codigo_parcela'] = info[255:260]
        registro['codigo_paraje_DGC'] = info[260:265]
        registro['nombre_paraje'] = info[265:295].strip()
        # 3. Datos fiscales
        registro['superficie_finca_o_parcela_m2'] = info[295:305]
        registro['superficie_construida_total_m2'] = info[305:312]
        registro['superficie_construida_sobre_rasante_m2'] = info[312:319]
        registro['superficie_construida_bajo_rasante_m2'] = info[319:326]
        registro['superficie_cubierta'] = info[326:333]
        registro['coordenada_X'] = float(info[333:340] + '.' + info[340:342])
        registro['coordenada_Y'] = float(info[342:350] + '.' + info[350:352])
        registro['SRS'] = info[666:676]
        return registro
    
    def get_UC(self, info):
        registro = {'tipo_de_registro': '13', 'referencia': 'Registro de  Constructiva'}
        # 1. Identificación del elemento
        registro['codigo_delegacion_MEH'] = info[23:25]
        registro['codigo_municipio_DGC'] = info[25:28]
        registro['clase_de_unidad_constructiva'] = info[28:30]
        registro['parcela_catastral'] = info[30:44]
        registro['codigo_unidad_constructiva'] = info[44:48]
        # 2. Domicilio tributario / Localización de la unidad constructiva
        registro['codigo_provincia_INE'] = info[50:52]
        registro['nombre_provincia'] = info[52:77].strip()
        registro['codigo_municipio_DGC'] = info[77:80]
        registro['codigo_municipio_INE'] = info[80:83]
        registro['nombre_municipio'] = info[83:123].strip()
        registro['nombre_entidad_menor'] = info[123:153].strip()
        registro['codigo_de_via_publica_DGC'] = info[153:158]
        registro['tipo_de_via_o_sigla_publica'] = info[158:163].strip()
        registro['nombre_de_via_publica'] = info[163:188].strip()
        registro['primer_numero_de_policia'] = info[188:192]
        registro['primera_letra'] = info[192:193]
        registro['segundo_numero_de_policia'] = info[193:197]
        registro['segunda_letra'] = info[197:198]
        registro['kilometro'] = info[198:203]
        registro['texto_de_direccion_no_estructurada'] = info[215:240].strip()
        # 3. Datos fisicos
        registro['año_de_construccion'] = info[295:299]
        registro['exactitud_año_de_construccion'] = info[299:300]
        registro['superficie_ocupada_por_la_UC_m2'] = info[300:307]
        registro['longitud_de_fachada_cm'] = info[307:312]
        return registro

    def get_constru(self, info):
        registro = {'tipo_de_registro': '14', 'referencia': 'Registro de Construcción'}
        # 1. Identificación del elemento
        registro['codigo_delegacion_MEH'] = info[23:25]
        registro['codigo_municipio_DGC'] = info[25:28]
        registro['parcela_catastral'] = info[30:44]
        registro['codigo_unidad_constructiva'] = info[44:48]
        # 2. Información adicional
        registro['cargo'] = info[50:54]
        registro['codigo_de_la_UC'] = info[54:58]
        # 3. Domicilio tributario del elemento
        registro['bloque'] = info[58:62]
        registro['escalera'] = info[62:64]
        registro['planta'] = info[64:67]
        registro['puerta'] = info[67:70]
        # 4. Datos físicos
        registro['codigo_de_destino_DGC'] = info[70:73]
        registro['tipo_de_reforma_o_rehabilitacion'] = info[73:74]
        registro['año_de_reforma'] = info[74:78]
        registro['año_de_antiguedad_efectiva_DGC'] = info[78:82]
        registro['indicador_de_local_interior'] = info[82:83]
        registro['superficie_total_del_local_m2'] = info[83:90]
        registro['superficie_porches_y_terrazas_m2'] = info[90:97]
        registro['superficie_imputada_al_local_en_otras_plantas_m2'] = info[97:104]
        # 5. Datos económicos
        registro['tipologia_constructiva'] = info[104:109]
        registro['codigo_modalidad_de_reparto'] = info[111:114]
        return registro

    def get_BI(self, info):
        registro = {'tipo_de_registro': '15', 'referencia': 'Registro de Bien Inmueble'}
        # 1. Identificación del bien inmueble
        registro['codigo_delegacion_MEH'] = info[23:25]
        registro['codigo_municipio_DGC'] = info[25:28]
        registro['clase_de_bien_inmueble'] = info[28:30]
        registro['parcela_catastral'] = info[30:44]
        registro['cargo'] = info[44:48]
        registro['primer_caracter_control'] = info[48:49]
        registro['segundo_caracter_control'] = info[49:50]
        # 2. Identificadores adicionales
        registro['numero_fijo_de_bien_inmueble_Gerencia'] = info[50:58]
        registro['id_bien_inmueble_Ayto'] = info[58:73]
        registro['numero_de_finca_registral'] = info[73:92]
        # 3. Domicilio tributario / Localización del bien inmueble
        registro['codigo_provincia_INE'] = info[92:94]
        registro['nombre_provincia'] = info[94:119].strip()
        registro['codigo_municipio_DGC'] = info[119:122]
        registro['codigo_municipio_INE'] = info[122:125]
        registro['nombre_municipio'] = info[125:165].strip()
        registro['nombre_entidad_menor'] = info[165:195].strip()
        registro['codigo_de_via_publica_DGC'] = info[195:200]
        registro['tipo_de_via_o_sigla_publica'] = info[200:205]
        registro['nombre_de_via_publica'] = info[205:230].strip()
        registro['primer_numero_de_policia'] = info[230:234]
        registro['primera_letra'] = info[234:235]
        registro['segundo_numero_de_policia'] = info[235:239]
        registro['segunda_letra'] = info[239:240]
        registro['kilometro'] = info[240:245]
        registro['bloque'] = info[245:249]
        registro['escalera'] = info[249:251]
        registro['planta'] = info[251:254]
        registro['puerta'] = info[254:257]
        registro['texto_de_direccion_no_estructurada'] = info[257:282]
        registro['codigo_postal'] = info[282:287]
        registro['distrito_municipal'] = info[287:289]
        registro['codigo_municipio_origen_DGC'] = info[289:292]
        registro['codigo_zona_de_concentracion'] = info[292:294]
        registro['codigo_poligono_rustico'] = info[294:297]
        registro['codigo_parcela'] = info[297:302]
        registro['codigo_paraje_DGC'] = info[302:307]
        registro['nombre_paraje'] = info[307:337].strip()
        # 4. Información adicional
        registro['orden_en_la_escritura'] = info[367:371]
        registro['año_de_antiguedad'] = info[371:375]
        # 5. Datos económicos
        registro['clave_de_grupo_de_bienes_inmuebles_con_caracteristicas_especiales'] = info[427:428]
        registro['superficie_de_elementos_constructivos_asociados_m2'] = info[441:451]
        registro['superficie_de_elementos_de_suelo_asociados_m2'] = info[451:461]
        registro['coeficiente_de_propiedad_respecto_a_la_finca'] = info[461:470]
        return registro

    def get_EC(self, info):
        registro = {'tipo_de_registro': '16', 'referencia': 'Reparto de Elementos Comunes'}
        # 1. Identificación del elemento a repartir
        registro['codigo_delegacion_MEH'] = info[23:25]
        registro['codigo_municipio_DGC'] = info[25:28]
        registro['parcela_catastral'] = info[30:44]
        registro['numero_de_orden_del_elemento'] = info[44:48]
        registro['calificacion_catastral_de_la_subparcela_a_repartir'] = info[48:50]
        registro['numero_de_orden_del_registro_o_segmento_de_repartos'] = info[50:54]
        # 2. Reparto
        start = 54
        reparto = []
        for iter in range(15):
            cargo = info[start:start+4]
            start += 4
            porcentaje_de_reparto = info[start:start+6]
            start+=6
            no_info = info[start:start+49]
            start+=49
            reparto.append({'cargo':cargo, 'porcentaje_de_reparto':porcentaje_de_reparto})
        registro['reparto'] = reparto
        return registro

    def get_cultivos(self, info):
        registro = {'tipo_de_registro': '17', 'referencia': 'Registro de Cultivos Agrarios'}
        # 1. Identificación de la subparcela
        registro['codigo_delegacion_MEH'] = info[23:25]
        registro['codigo_municipio_DGC'] = info[25:28]
        registro['naturaleza_del_suelo'] = info[28:30]
        registro['parcela_catastral'] = info[30:44]
        registro['codigo_subparcela'] = info[44:48]
        # 2. Información adicional
        registro['cargo'] = info[50:54]
        # 3. Datos físicos y económicos
        registro['tipo_se_subparcela'] = info[54:55]
        registro['superficie_subparcela_m2'] = info[55:65]
        registro['calificacion_catastral_o_clase_de_cultivo'] = info[65:67]
        registro['denominacion_clase_de_cultivo'] = info[67:107]
        registro['intensidad_productiva'] = info[107:109]
        registro['codigo_modalidad_de_reparto'] = info[126:129]
        return registro
    
    def get_cola(self, info):
        registro = {'tipo_de_registro': '90', 'referencia': 'Registro de cola'}
        # 1. Datos de cola
        registro['registros_tipo_41'] = info[2:9]
        registro['registros_tipo_11'] = info[9:16]
        registro['registros_tipo_12'] = info[16:23]
        registro['registros_tipo_13'] = info[23:30]
        registro['registros_tipo_14'] = info[30:37]
        registro['registros_tipo_15'] = info[37:44]
        registro['registros_tipo_16'] = info[44:51]
        registro['registros_tipo_17'] = info[51:58]
        registro['registros_tipo_46'] = info[58:65]
        registro['registros_tipo_47'] = info[65:72]
        registro['registros_tipo_48'] = info[72:79]
        registro['registros_tipo_49'] = info[79:86]
        registro['registros_tipo_62'] = info[86:93]
        return registro