from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.core import Qgis

import os.path

from .src.dependencies import install_package
install_package('xmltodict')
from .gui.dock import RightDock

class CAT_Inspector:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.actions = []
        self.menu = self.tr('&Procesador_CAT')
        self.toolbar = self.iface.addToolBar('Procesador_CAT')
        self.toolbar.setObjectName('Procesador_CAT')
        self.items = []
        self.crs = 'EPSG:4326'

    def tr(self, message):
        return QCoreApplication.translate('Procesador_CAT', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=True, status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)
        if add_to_toolbar:
            self.toolbar.addAction(action)
        self.actions.append(action)
        return action

    def initGui(self):
        #Add tool
        icon_path = os.path.join(self.plugin_dir, 'img/icono.png')
        self.add_action(icon_path, text=self.tr('Procesador_CAT'), callback=self.run, parent=self.iface.mainWindow())


    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr('&Procesador_CAT'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def run(self):
        self.iface.messageBar().pushMessage("Plugin Traductor_CAT", "Bienvenido al plugin de procesamiento de ficheros CAT", level=Qgis.Info)
        # Crear y mostrar la ventana flotante
        self.dock = RightDock()
        self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.dock.show()