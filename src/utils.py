from typing import Optional

from qgis.core import QgsProject, QgsCoordinateReferenceSystem, QgsRasterLayer, Qgis
from qgis.utils import iface


def get_layer_crs() -> Optional[QgsCoordinateReferenceSystem]:
    current = iface.activeLayer()

    # Verificar si se encontró una capa activa
    if not current:
        print(f"No se encontró ninguna capa activa.")
    else: # Obtener la primera capa que coincide con el nombre
        print(f"Capa encontrada: {current.name()}")
        # Obtener el CRS de la capa
        print("CRS de la capa:", current.crs().authid())
        return current.crs()

def create_wms_layer(uri:str, layer_name:str) -> None:
    print(f'Creando capa {layer_name} ...')
    rlayer = QgsRasterLayer(uri, layer_name, 'wms') # EDIT THIS LINE

    if rlayer.isValid():
        QgsProject.instance().addMapLayer(rlayer)
        print(f'¡Capa {layer_name} creada!')
    else:
        print('La capa WMS no es válida')
        iface.messageBar().pushMessage('Utils:create_wms_layer()', rlayer.error().message(), level=Qgis.Critical)

def get_layer_source(layer_name:str) -> Optional[str]:
    # Obtener la capa por nombre
    layers = QgsProject.instance().mapLayersByName(layer_name)

    # Verificar si se encontró la capa
    if not layers:
        iface.messageBar().pushMessage('Utils:get_layer_source()', f'No se encontró ninguna capa con el nombre: {layer_name}', level=Qgis.Critical)
    else:
        layer = layers[0]  # Obtener la primera capa que coincide con el nombre
        print(f"Capa encontrada: {layer.name()}")
        # Verificar si la capa es WMS
        if layer.providerType() == 'wms':
            print("La capa es una capa WMS")
            # Obtener la URL de la capa
            wms_url = layer.source()
            print("URL de la capa WMS:", wms_url)
            return get_source(wms_url)
        else:
            iface.messageBar().pushMessage('Utils:get_layer_source()', 'La capa no es una capa WMS', level=Qgis.Critical)

def get_source(url:str) -> str:
    # Parsear la URL para obtener la URL base del WMS
    query_params = [{param.split('=')[0]: param.split('=')[1]} for param in url.split('&') if len(param.split('=')) == 2]
    print(f'Parámetros: {query_params}')
    # Reconstruir la URL base del WMS sin los parámetros adicionales
    wms_base_url = [d for d in query_params if d.get('url')][0].get('url')
    print("URL base:", wms_base_url)
    return wms_base_url