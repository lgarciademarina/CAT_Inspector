
from qgis.core import Qgis, QgsApplication, QgsTask, QgsMessageLog
from qgis.gui import QgsMapToolEmitPoint
from qgis.utils import iface

import concurrent.futures
import requests
import xmltodict
import re

from ..gui.info import Info
from .utils import get_layer_crs

LAYER_NAME = 'Catastro'
REGEX_CATASTRO = r'https://www1\.sedecatastro\.gob\.es/CYCBienInmueble/OVCListaBienes\.aspx\?del=[0-9]+&muni=[0-9]+&rc1=[A-Za-z0-9]+&rc2=[A-Za-z0-9]+'

# Clase para manejar el clic en el mapa
class GetPixelInfo(QgsMapToolEmitPoint):
    def __init__(self, file, url):
        super().__init__(iface.mapCanvas())
        self.file = file
        self.url = url

    def canvasReleaseEvent(self, event):
        if self.file:
            crs = get_layer_crs()
            if crs != None:
                # Obtener las coordenadas del clic
                point = self.toMapCoordinates(event.pos())
                x = point.x()
                y = point.y()
                print(f'Punto: ({x}, {y})')
                layer_crs = crs.authid()

                # Crear el parámetro de consulta GetFeatureInfo
                params = {
                    'SERVICE': 'WMS',
                    'VERSION': '1.1.1',
                    'REQUEST': 'GetFeatureInfo',
                    'LAYERS': LAYER_NAME,
                    'QUERY_LAYERS': LAYER_NAME,
                    'STYLES': '',
                    'BBOX': ','.join(map(str, iface.mapCanvas().extent().toRectF().getCoords())),
                    'FEATURE_COUNT': '1',
                    'HEIGHT': str(iface.mapCanvas().height()),
                    'WIDTH': str(iface.mapCanvas().width()),
                    'INFO_FORMAT': 'text/plain',
                    'SRS': layer_crs,
                    'X': str(event.pos().x()),
                    'Y': str(event.pos().y())
                }

                # Hacer la consulta GetFeatureInfo
                response = requests.get(self.url, params=params)
                if response.status_code == 200:
                    if 'APLICACION EN MANTENIMIENTO' in response.text:
                        iface.messageBar().pushMessage('Mensaje de Catastro', f'APLICACION EN MANTENIMIENTO', level=Qgis.Critical)
                    else:
                        url_pattern = re.compile(REGEX_CATASTRO)
                        xml = url_pattern.sub('', response.text)
                        print(f'Respuesta GetFeatureInfo: {xml}')

                        response = xmltodict.parse(xml, encoding='ISO-8859-1')
                        rc = None
                        try:
                            rc = response.get('html').get('body').get('p')[1].get('a').get('#text')
                            if rc:
                                print(f'RC: {rc}')
                                with concurrent.futures.ThreadPoolExecutor() as executor:
                                    future = executor.submit(self.get_info_from_file, rc)
                                registros = future.result()
                                if registros:
                                    print('Abriendo Info Dialog...')
                                    dialog = Info(rc, registros)
                                    dialog.exec_()
                                """task = QgsTask.fromFunction(description='GetPixelInfo', function=self.get_info_from_file, on_finish=self.finished)
                                QgsApplication.taskManager().addTask(task)"""
                        except:
                            iface.messageBar().pushMessage('GetPixelInfo', f'No se ha encontrado ninguna Referencia Catastral para el punto seleccionado', level=Qgis.Warning)
                else:
                    iface.messageBar().pushMessage('GetPixelInfo', f'Error en la consulta GetFeatureInfo: {response.status_code}', level=Qgis.Critical)
            else:
                iface.messageBar().pushMessage('GetPixelInfo', f'No existe ninguna capa activa.', level=Qgis.Critical)
        else:
            iface.messageBar().pushMessage('GetPixelInfo', f'No se ha cargado ningún fichero.', level=Qgis.Critical)
    
    def get_info_from_file(self, rc):
        print('Buscando en el fichero...')
        registros = self.file.find_refcat(rc)
        if registros:
            print(f'Información encontrada en el fichero CAT: {len(registros)} registros.')
            return registros
        elif self.file.valid:
                iface.messageBar().pushMessage('Mensaje de Catastro', f'No se ha encontrado información para el punto seleccionado.', level=Qgis.Warning)