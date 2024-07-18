from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, QTreeWidget, QTreeWidgetItem

class Info(QDialog):
    def __init__(self, rc, registros, parent=None):
        """Constructor."""
        super(Info, self).__init__(parent)
        self.setWindowTitle(f'Referencia Catastral {rc}')
        self.registros = registros
        print('Creando interfaz de usuario...')
        self.setLayout(QVBoxLayout())
        self.resize(600,600)

        # 1. Tipos de registro
        select_lbl = QLabel('Tipo de registro')
        self.layout().addWidget(select_lbl)
        select_layout = QHBoxLayout()
        self.select = QComboBox()
        registros_ordenados = sorted(registros, key=lambda d: d['tipo_de_registro'])
        items = [registro.get('referencia') for registro in registros_ordenados]
        items = sorted(set(items), key=items.index)
        self.select.addItems(items)
        select_layout.addWidget(self.select)
        select_layout.addStretch()
        self.layout().addLayout(select_layout)

        # 2. Opciones de filtrado
        filter_lbl = QLabel('Aplicar filtro: ')
        self.layout().addWidget(filter_lbl)
        filter_layout = QHBoxLayout()
        self.fields = QComboBox()
        filter_layout.addWidget(self.fields)
        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText('Inserte texto...')
        filter_layout.addWidget(self.filter_text)
        filter_layout.addStretch()
        self.layout().addLayout(filter_layout)
        
        # 3. Panel donde irá el formulario
        self.form_panel = QVBoxLayout()
        self.form = None
        self.layout().addLayout(self.form_panel)

        self.update_fields()
        self.update_form()
        self.filter_text.textChanged.connect(self.update_form)
        self.fields.currentTextChanged.connect(self.reset_text)
        self.select.currentIndexChanged.connect(self.update_fields)
        
    def update_fields(self):
        registros_filtrados = [{'registro': registro} for registro in self.registros if registro.get('referencia') == self.select.currentText()]
        self.fields.clear()
        self.fields.addItems(list(registros_filtrados[0].get('registro').keys()))
    
    def reset_text(self):
        self.filter_text.clear()
        self.filter_text.textChanged.emit('True')

    """ MÉTODOS PARA GENERAR EL FORMULARIO DE CONFIGURACIÓN"""
    def update_form(self):
        print('Actualizando el formulario...')
        if self.form:
            self.form_panel.removeWidget(self.form)
        self.form = Formulario()
        self.form_panel.addWidget(self.form)
        registros_filtrados = [{'registro': registro} for registro in self.registros if (registro.get('referencia') == self.select.currentText()) and (self.filter_text.text() in registro.get(self.fields.currentText()) if self.filter_text.text() != '' else True)]
        print(f'Registros filtrados: {len(registros_filtrados)}')
        [self.form.add_register(registro, self.form) for registro in registros_filtrados]
        self.form.expandAll()
        self.form.resizeColumnToContents(0)
        self.form.resizeColumnToContents(1)


class Formulario(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('Formulario')
        self.setColumnCount(2)
        self.setHeaderLabels(['Variable', 'Valor'])        
        
    def add_register(self, dictionary=None, parent=None):
        for key, value in dictionary.items():
            item = QTreeWidgetItem(parent)
            item.setText(0, key.replace('_', ' ').capitalize())
            if isinstance(value, dict):
                self.add_register(dictionary=value, parent=item)
            elif isinstance(value, list):
                [self.add_register(i, parent=item) for idx, i in enumerate(value)]
            else:
                item.setText(1, str(value))