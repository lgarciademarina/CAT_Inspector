
import concurrent.futures
import os
from pathlib import Path

from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QGridLayout
from PyQt5.QtGui import QIcon
from qgis.core import QgsProject, Qgis
from qgis.gui import QgsMapToolPan
from qgis.utils import iface

from .explorer import Explorer
from .info import Info
from ..src.file import File
from ..src.infoTool import GetPixelInfo
from ..src.utils import create_wms_layer


URL_CATASTRO = 'https://ovc.catastro.meh.es/Cartografia/WMS/ServidorWMS.aspx'

class RightDock(QDockWidget):
    def __init__(self): 
        super().__init__()
        self.file = None
        self.tool = None

        widget = QWidget()
        layout = QVBoxLayout()
        load_layout = QHBoxLayout()
        self.path = QLineEdit()
        self.path.setPlaceholderText('Introduzca ruta del fichero CAT (*.zip) ...')
        load_layout.addWidget(self.path)
        icon_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'img/folder.png')
        explore_path = self.createButton( icon_path, 'Explorador de ficheros', self.select_file)
        load_layout.addWidget(explore_path)
        icon_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'img/upload.png')
        upload_file = self.createButton( icon_path, 'Cargar fichero', self.set_file)
        load_layout.addWidget(upload_file)
        layout.addLayout(load_layout)

        info_entity = QGroupBox('Información de la entidad generadora')
        self.entry_grid_layout = QGridLayout()
        self.entry_grid_layout.addWidget(QLabel('Tipo de entidad generadora:'), 0, 0)
        self.entry_grid_layout.addWidget(QLabel('Código de la Delegación MEH:'), 1, 0)
        self.entry_grid_layout.addWidget(QLabel('Nombre de la entidad generadora:'), 2, 0)
        info_entity.setLayout(self.entry_grid_layout)
        layout.addWidget(info_entity)

        info_file = QGroupBox('Información del fichero')
        self.file_grid_layout = QGridLayout()
        self.file_grid_layout.addWidget(QLabel('Fecha de generación del fichero:'), 0, 0)
        self.file_grid_layout.addWidget(QLabel('Tipo de fichero:'), 1, 0)
        info_file.setLayout(self.file_grid_layout)
        layout.addWidget(info_file)

        tools = QGroupBox('Herramientas')
        tool_layout = QHBoxLayout()
        self.RC = QLineEdit()
        self.RC.setPlaceholderText('Referencia Catastral')
        self.RC.setMinimumWidth(150)
        tool_layout.addWidget(self.RC)
        icon_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'img/explore.png')
        search = self.createButton( icon_path, 'Buscar Referencia Catastral', self.get_info)
        tool_layout.addWidget(search)
        tool_layout.addStretch()
        icon_path = os.path.join(Path(os.path.dirname(__file__)).parent, 'img/target.png')
        self.button = self.createButton( icon_path, 'Activar selección de punto', self.change_tool)
        tool_layout.addWidget(self.button)
        tools.setLayout(tool_layout)
        layout.addWidget(tools)

        layout.addStretch()
        widget.setLayout(layout)

        self.setWidget(widget)

    def createButton(self, image, tooltip, method):
        # https://www.flaticon.com/free-icons/
        button = QPushButton()
        button.setIcon(QIcon(image))
        button.setToolTip(tooltip)
        button.clicked.connect(method)
        return button
    
    def select_file(self):
        Explorer(self)

    def set_file(self):
        if self.path.text() != '':
            self.file = File(self.path.text()) if os.path.exists(self.path.text()) else None
            info = self.file.get_file_info()
            # Add info to the dock
            self.entry_grid_layout.addWidget(QLabel(info.get('tipo_de_entidad_generadora')), 0, 1)
            self.entry_grid_layout.addWidget(QLabel(str(info.get('codigo_delegacion_MEH'))), 1, 1)
            self.entry_grid_layout.addWidget(QLabel(info.get('nombre_de_entidad_generadora')), 2, 1)

            self.file_grid_layout.addWidget(QLabel(info.get('fecha_de_generacion')), 0, 1)
            self.file_grid_layout.addWidget(QLabel(info.get('tipo_de_fichero')), 1, 1)

    def change_tool(self):
        if iface.mapCanvas().mapTool():
            if iface.mapCanvas().mapTool().toolName() == 'GetFeatureInfo':
                self.disable_tool()
                return
        self.activate_tool()

    def activate_tool(self):
        print('Activando GetFeatureInfo')
        self.tool = GetPixelInfo(file=self.file, url=URL_CATASTRO.replace('https','http'))
        self.tool.setToolName('GetFeatureInfo')
        iface.mapCanvas().setMapTool(self.tool)

    def disable_tool(self):
        print('Desactivando GetFeatureInfo')
        iface.mapCanvas().unsetMapTool(self.tool)
        self.tool = None

    def get_info(self):
        if self.file:
            rc = self.RC.text()
            if rc and len(rc) == 14:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self.get_info_from_file, rc)
                registros = future.result()
                if registros:
                    print('Abriendo Info Dialog...')
                    dialog = Info(rc, registros)
                    dialog.exec_()
        else:
           iface.messageBar().pushMessage('CAT Inspector', f'Aún no se ha cargado ningún fichero CAT.', level=Qgis.Critical) 
        self.disable_tool()

    def get_info_from_file(self, rc):
        if self.file:
            registros = self.file.find_refcat(rc)
            if registros:
                print(f'Información encontrada en el fichero CAT: {len(registros)} registros.')
                return registros
            elif self.file.valid:
                    iface.messageBar().pushMessage('Mensaje de Catastro', f'No se ha encontrado información para la RC seleccionada.', level=Qgis.Warning)
        else:
            iface.messageBar().pushMessage('GetPixelInfo', f'No se ha cargado ningún fichero.', level=Qgis.Critical)


    def add_layer(self, name):
        uri = ''
        layers = QgsProject.instance().mapLayersByName('PNOA M.A.')
        if not layers:
            uri = f'format=image/png&layers=OI.OrthoimageCoverage&styles=OI.OrthoimageCoverage.Default&crs={self.crs}&url=https://www.ign.es/wms-inspire/pnoa-ma'
            create_wms_layer(uri, 'PNOA M.A.')

        layers = QgsProject.instance().mapLayersByName('Catastro')
        if not layers:
            uri = f'format=image/png&layers=Catastro&styles&crs={self.crs}&url={URL_CATASTRO}'
            create_wms_layer(uri, 'Catastro')