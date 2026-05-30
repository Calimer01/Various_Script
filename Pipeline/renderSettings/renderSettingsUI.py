from PySide6 import QtWidgets, QtCore
import maya.cmds as cmds
import json
import renderSettings.renderSettingsFunction as rsf

class RenderSetupUI(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle("Render Setup Tool")
        self.setMinimumWidth(300)

        self.build_ui()
        self.create_connections()

    def build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # -----------------------------
        # Path Section
        # -----------------------------
        self.path_label = QtWidgets.QLabel("Output Path")
        self.path_combo = QtWidgets.QComboBox()
        self.path_combo.addItems(["Lighting", "Local", "Network", "Custom"])

        # Line edit for custom path
        self.path_edit = QtWidgets.QLineEdit()
        self.togglePath(self.path_combo.currentText())

        # Horizontal layout for combo + edit
        path_layout = QtWidgets.QHBoxLayout()
        path_layout.addWidget(self.path_combo)
        path_layout.addWidget(self.path_edit)

        layout.addWidget(self.path_label)
        layout.addLayout(path_layout)

        #path button to only set the path without applying other settings
        self.path_btn = QtWidgets.QPushButton("Set Path Only")
        layout.addWidget(self.path_btn)

        # Resolution
        self.res_label = QtWidgets.QLabel("Resolution: 100%")
        self.res_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.res_slider.setRange(25, 100)
        self.res_slider.setValue(100)

        self.res_btn = QtWidgets.QPushButton("Set Resolution Only")

        # Sampling Precision
        self.sample_label = QtWidgets.QLabel("Sampling Precision:")
        self.sample_comboBox = QtWidgets.QComboBox()
        self.sample_comboBox.addItems(["Low", "Medium", "High"])

        ## Cryptomatte
        #self.crypto_checkbox = QtWidgets.QCheckBox("Enable Cryptomatte")
        #self.crypto_checkbox.setChecked(True)

        # Character selection
        self.char_label = QtWidgets.QLabel("Character:")
        self.charaddsItems()
    
        # LPE
        self.lpe_checkbox = QtWidgets.QCheckBox("Enable LPE")
        self.lpe_checkbox.setChecked(True)

        # Reset button
        self.reset_btn = QtWidgets.QPushButton("Reset Current Settings")

        # LPE button
        self.lpe_btn = QtWidgets.QPushButton("Set Ligth Groups")

        # Button
        self.apply_btn = QtWidgets.QPushButton("Apply Settings")

        self.spacer = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        layout.addWidget(self.res_label)
        layout.addWidget(self.res_slider)
        layout.addWidget(self.res_btn)
        layout.addWidget(self.sample_label)
        layout.addWidget(self.sample_comboBox)
        #layout.addWidget(self.crypto_checkbox)
        layout.addWidget(self.char_label)
        layout.addLayout(self.char_layout)
        layout.addWidget(self.lpe_checkbox)
        layout.addItem(self.spacer)
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.lpe_btn)
        layout.addWidget(self.apply_btn)

    def create_connections(self):
        data = self.load_json()
        self.res_slider.valueChanged.connect(self.update_label)
        self.reset_btn.clicked.connect(self.reset_settings)
        self.lpe_btn.clicked.connect(lambda : self.create_lpe(data.get("lpe", "")))
        self.apply_btn.clicked.connect(self.apply_settings)
        self.path_combo.currentIndexChanged.connect(lambda : self.togglePath(self.path_combo.currentText()))
        self.path_btn.clicked.connect(lambda : self.setup_path(self.path_edit.text()))
        self.res_btn.clicked.connect(lambda : self.set_resolution(data.get("resolution", {}), self.res_slider.value()/100.0))

    def update_label(self, value):
        self.res_label.setText(f"Resolution: {value}%")
    
    def togglePath(self, path):
        self.path_edit.setText(rsf.computePath(path))
        if path == "Custom":
            self.path_edit.setReadOnly(False)
        else:
            self.path_edit.setReadOnly(True)

    def charaddsItems(self):
        #create one checkbox per char in json and add to layout
        data = self.load_json()
        chars = data.get("Char", [])
        self.char_layout = QtWidgets.QHBoxLayout()
        for char in chars:
            checkbox = QtWidgets.QCheckBox(char)
            checkbox.setChecked(True)
            self.char_layout.addWidget(checkbox)

    # 🔧 CORE LOGIC
    def apply_settings(self):
        percent = self.res_slider.value() / 100.0
        #crypto = self.crypto_checkbox.isChecked()
        precision = self.sample_comboBox.currentText() if hasattr(self, 'sample_comboBox') else None
        lpeBool = self.lpe_checkbox.isChecked()
        path = self.path_edit.text()
        chars = self.getCheckedChars(self.char_layout)

        data = self.load_json()
        rsf.setup_render_settings()
        self.set_sampling(data.get("sampling", {}), precision=precision)
        self.set_resolution(data.get("resolution", {}), percent)
        self.setup_aovs(data.get("aovs", []), data.get("lpe", []), lpeBool, data.get("pxrTeeDisplay", []))
        self.setup_Layer(data.get("layers", []), chars)
        self.setup_path(path)

        #if crypto:
        #    self.setup_cryptomatte(data.get("cryptomatte", []))

        print("✅ Render setup applied")
        self.accept()  # Close the UI after applying settings

    # -----------------------------
    # LOGIC FUNCTIONS
    # -----------------------------

    def getCheckedChars(self, layout):
        unchecked_chars = []
        for i in range(layout.count()):
            checkbox = layout.itemAt(i).widget()
            if isinstance(checkbox, QtWidgets.QCheckBox) and not checkbox.isChecked():
                unchecked_chars.append(checkbox.text())
        return unchecked_chars
    
    def reset_settings(self):
        rsf.reset_all()

    def create_lpe(self, data):
        rsf.create_lpe(data)
    
    def setup_path(self, path):
        rsf.setOutputPath(path)

    def load_json(self):
        path = "//Gandalf/3d5_2526/02_TOP_HIT/00_Pipeline/renderSettings.json"
        with open(path, "r") as f:
            return json.load(f)

    def set_resolution(self, data, percent):
        rsf.set_resolution(data, percent)

    def set_sampling(self, data, precision=None):
        rsf.set_sampling(data, precision=precision)

    def setup_integrator(self, data):
        rsf.setup_integrator(data)

    def setup_aovs(self, aovs, lpe, lpeBool, pxrtee):
        rsf.setup_aovs(aovs, lpe, lpeBool, pxrtee)

    def setup_cryptomatte(self, data):
        rsf.setup_cryptomatte(data)
    
    def setup_Layer(self, data, char):
        rsf.setup_Layer(data, char)

# Run UI
def show_ui():
    global render_setup_ui

    try:
        render_setup_ui.close()
        render_setup_ui.deleteLater()
    except:
        pass

    render_setup_ui = RenderSetupUI()
    render_setup_ui.show()
