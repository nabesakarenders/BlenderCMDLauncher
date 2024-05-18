import re
import sys

from PyQt6.QtCore import QSettings, Qt, pyqtSignal, QProcess
from PyQt6.QtGui import QFontDatabase, QFont, QPalette, QColor
from PyQt6.QtWidgets import *

# Color Palette
# Dark blue = #27374D
# Mid blue = #526D82
# Light Blue = #9DB2BF
# Lightest Blue = #9DB2BF

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Track Blender Process run status
        self.process = None;

        # Create main layout container
        container = QVBoxLayout()


        # Add Sub Layouts to Main Layout
        container.addLayout(self.createPathsHeader())
        container.addLayout(self.createPathOptions())
        container.addLayout(self.createFrameHeader())
        container.addLayout(self.createFrameOptions())
        container.addLayout(self.createRendererHeader())
        container.addLayout(self.createRendererOptions())
        container.addLayout(self.createOutputHeader())
        container.addLayout(self.createOutputOptions())
        container.addLayout(self.createRenderButton())
        container.addLayout(self.createConsoleHeader())
        container.addLayout(self.createConsoleLog())
        container.addLayout(self.createRemainingTime())

        # Setup Central Widget
        widget = QWidget()
        widget.setLayout(container)
        self.setCentralWidget(widget)
        self.setWindowTitle("Blender CMD Launcher")
        self.setFixedSize(750, 750)

        # Load any saved settings
        self.loadSettings()

    def createPathsHeader(self):
        container = QHBoxLayout()
        container.setSpacing(0)
        container.setContentsMargins(2, 2, 0, 2)

        header = QLabel("Blender Paths")
        header.setStyleSheet("font-weight: bold; font-size: 12pt;")
        container.addWidget(header)
        return container
    
    def createPathOptions(self):
        container = QHBoxLayout()


        # Add H Group for Blender Path
        left_container = QHBoxLayout()
        left_container.setSpacing(1)
        left_container.setContentsMargins(0, 0, 10, 10)


        # Add Blender Path display
        self.blender_path = ClickableLineEdit()
        self.blender_path.setPlaceholderText("Path To Blender.exe")
        self.blender_path.setReadOnly(True)
        self.blender_path.clicked.connect(self.selectBlenderExe)
        left_container.addWidget(self.blender_path)

        
        # Add Blender Path Select Button
        self.blender_path_button = QPushButton("Pick Blender.exe")
        self.blender_path_button.clicked.connect(self.selectBlenderExe)
        left_container.addWidget(self.blender_path_button)


        # Add H Group for Blend Path
        right_container = QHBoxLayout()
        right_container.setSpacing(1)
        right_container.setContentsMargins(0, 0, 10, 10)


        # Add Blend Path display
        self.blend_path = ClickableLineEdit()
        self.blend_path.setPlaceholderText("Path To yourscene.blend")
        self.blend_path.setReadOnly(True)
        self.blend_path.clicked.connect(self.selectBlendFile)
        right_container.addWidget(self.blend_path)


        # Add Blend Path Select Button
        self.blend_path_button = QPushButton("Select Blend File")
        self.blend_path_button.clicked.connect(self.selectBlendFile)
        right_container.addWidget(self.blend_path_button)


        container.addLayout(left_container)
        container.addLayout(right_container)

        return container
    
    def createFrameHeader(self):
        container = QHBoxLayout()
        container.setSpacing(0)
        container.setContentsMargins(2, 2, 0, 2)

        header = QLabel("Animation & Frame Rates")
        header.setStyleSheet("font-weight: bold; font-size: 12pt;")
        container.addWidget(header)

        return container
    
    def createFrameOptions(self):
        container = QHBoxLayout()


        # First container
        first_container = QHBoxLayout()
        
        
        # Add animation checkbox
        self.is_animation = QCheckBox("Is Animation")
        self.is_animation.stateChanged.connect(self.showAnimationOptions)
        first_container.addWidget(self.is_animation)


        # Second Container
        second_container = QHBoxLayout()
        second_container.setSpacing(2)
        second_container.setContentsMargins(0, 5, 10, 5)

        self.solo_frame_label = QLabel("Which Frame?")
        self.solo_frame_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        second_container.addWidget(self.solo_frame_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.solo_frame = QSpinBox()
        self.solo_frame.setMinimum(1)
        self.solo_frame.setMaximum(10000)
        self.solo_frame.setValue(1)
        second_container.addWidget(self.solo_frame)


        # Add Start Frame Label
        self.start_frame_label = QLabel("Start Frame")
        self.start_frame_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        second_container.addWidget(self.start_frame_label, alignment=Qt.AlignmentFlag.AlignVCenter)


        # Add Start Frame
        self.start_frame = QSpinBox()
        self.start_frame.setMinimum(1)
        self.start_frame.setMaximum(10000)
        self.start_frame.setValue(1)
        second_container.addWidget(self.start_frame)


        # Third Container
        third_container = QHBoxLayout()
        third_container.setSpacing(2)
        third_container.setContentsMargins(0, 5, 10, 5)

        # Add Start Frame Label
        self.end_frame_label = QLabel("End Frame")
        self.end_frame_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        third_container.addWidget(self.end_frame_label, alignment=Qt.AlignmentFlag.AlignVCenter)


         # Add End Frame
        self.end_frame = QSpinBox()
        self.end_frame.setMinimum(1)
        self.end_frame.setMaximum(10000)
        self.end_frame.setValue(10)
        third_container.addWidget(self.end_frame)

        # Create animaton options group for hiding/unhiding
        self.show_animation_options = [self.start_frame, self.start_frame_label, self.end_frame, self.end_frame_label]
        self.show_single_frame_options = [self.solo_frame_label, self.solo_frame]

        # Hide the animation options
        for option in self.show_animation_options:
            option.hide()

        
        container.addLayout(first_container)
        container.addLayout(second_container)
        container.addLayout(third_container)

        return container
    
    def createRendererHeader(self):
        container = QHBoxLayout()
        container.setSpacing(0)
        container.setContentsMargins(2, 2, 0, 2)

        header = QLabel("Renderer Options")
        header.setStyleSheet("font-weight: bold; font-size: 12pt;")
        container.addWidget(header)

        return container
    
    def createRendererOptions(self):
        container = QHBoxLayout()


        # Add Renderer Selection
        self.renderer = QComboBox()
        self.renderer.addItems(["Cycles", "Eevee", "Workbench"])
        container.addWidget(self.renderer)
        self.renderer.currentIndexChanged.connect(self.canDisplayRenderApi)
        
        
        # Add Render API Selection
        self.render_api = QComboBox()
        self.render_api.addItems(["CPU", "CUDA", "OPTIX", "HIP", "ONEAPI", "METAL"])
        self.render_api.setCurrentIndex(2) # Default to OPTIX
        container.addWidget(self.render_api)

        self.render_api.currentIndexChanged.connect(self.canDisplayCpuOption)


        # Add Render API with CPU option
        self.use_cpu = QCheckBox("+ CPU?")
        self.use_cpu.setToolTip("Render with CPU and GPU (Has no effect if CPU is chosen as render API)")
        container.addWidget(self.use_cpu)

        return container

    def createOutputHeader(self):
        container = QHBoxLayout()
        container.setSpacing(0)
        container.setContentsMargins(2, 2, 0, 2)

        header = QLabel("Output Options")
        header.setStyleSheet("font-weight: bold; font-size: 12pt;")
        container.addWidget(header)

        return container

    def createOutputOptions(self):
        container = QHBoxLayout()

        left_container = QHBoxLayout()
        left_container.setSpacing(1)
        left_container.setContentsMargins(0, 0, 10, 10)

        # Add Output Folder
        self.output_folder = QLineEdit()
        self.output_folder.setPlaceholderText("Output Folder")
        self.output_folder.setReadOnly(True)
        left_container.addWidget(self.output_folder)


        # Add Output Folder Button
        self.output_folder_button = QPushButton("Pick Output Folder")
        self.output_folder_button.clicked.connect(self.selectOutputFolder)
        self.output_folder_button.setToolTip("Select Output Folder")
        left_container.addWidget(self.output_folder_button)


        right_container = QHBoxLayout()
        right_container.setSpacing(1)
        right_container.setContentsMargins(0, 0, 10, 10)

        # Add Output Filename
        self.output_filename = QLineEdit()
        self.output_filename.setPlaceholderText("Output Filename")
        self.output_filename.setToolTip("Frame Number will be appended automatically")
        right_container.addWidget(self.output_filename)

        container.addLayout(left_container)
        container.addLayout(right_container)

        return container
    
    def createRenderButton(self):
        container = QHBoxLayout()

        self.render_button = QPushButton("Render Now")
        self.render_button.clicked.connect(self.runRenderCommand)
        self.render_button.setMaximumWidth(100)
        container.addWidget(self.render_button, alignment=Qt.AlignmentFlag.AlignCenter)

        return container
    
    def createRemainingTime(self):
        container = QHBoxLayout()
        container.setContentsMargins(5, 20, 5, 20)
        self.remaining_time = QLabel()
        self.remaining_time.setText('Time Remaining: [Waiting for Render Start]')
        self.remaining_time.setStyleSheet("font-weight: bold; font-size: 12pt;")
        container.addWidget(self.remaining_time)

        return container
    
    def createConsoleHeader(self):
        container = QHBoxLayout()
        container.setSpacing(0)
        container.setContentsMargins(2, 2, 0, 2)

        header = QLabel("Log Output")
        header.setStyleSheet("font-weight: bold; font-size: 12pt;")
        container.addWidget(header)

        return container

    def createConsoleLog(self):
        container = QHBoxLayout()

        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        container.addWidget(self.log_text)

        return container

    def showAnimationOptions(self, state):
        if state == Qt.CheckState.Checked.value:
            for option in self.show_animation_options:
                option.show()

            for option in self.show_single_frame_options:
                option.hide()
                
        else :
            for option in self.show_animation_options:
                option.hide()

            for option in self.show_single_frame_options:
                option.show()
            
    def canDisplayRenderApi(self, index):
        if index == 0:
            self.render_api.show()
            self.canDisplayCpuOption(self.render_api.currentIndex)
        else:
            self.render_api.hide()
            self.use_cpu.hide()

    def canDisplayCpuOption(self, index):
        if index != 0:
            self.use_cpu.show()
        else:
            self.use_cpu.hide()

    def loadSettings(self):
        self.settings = QSettings('./BlenderCMD.ini', QSettings.Format.IniFormat)
        try:
            print("loading settings")
            print("Blender Path %s", self.settings.value("blender_path", '', type=str))
            self.blender_path.setText( self.settings.value("blender_path", '') )
        except:
            pass

    def selectBlenderExe(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Blender Executable', '', "Blender Executable (Blender.exe)")
        if fileName:
            self.blender_path.setText(fileName)
            self.settings.setValue('blender_path', fileName)

    def selectBlendFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, 'Blend File', '', "Blend File (*.blend)")
        if fileName:
            self.blend_path.setText(fileName)

    def selectOutputFolder(self):
        folderName = QFileDialog.getExistingDirectory(self, 'Select Output Folder', '', QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)
        if folderName:
            self.output_folder.setText(folderName)

    def runRenderCommand(self):

        # If Blender is already running don't try to run it again
        if self.process is not None:
            QMessageBox.warning(self, "Blender Running!", "Blender is already running. Check the log box and wait for it to finish!")
            return False

        # Paths
        blender_path = self.blender_path.text()
        blend_path = self.blend_path.text()

        if not blender_path or not blend_path:
            QMessageBox.warning(self, "Missing Path", "Please select your Blender Executable and a Blend File to render")
            return False

        # Animation & Frames
        animation = self.is_animation.isChecked()

        # Is animation?
        if animation:
            start_frame = self.start_frame.value()
            end_frame = self.end_frame.value()
            if animation and (start_frame is None or end_frame is None):
                QMessageBox.warning(self, "Error", "Please enter a start and end frame")
                return False
        else:
            # Must be since frame render
            solo_frame = self.solo_frame.value()
            if solo_frame is None:
                QMessageBox.warning(self, "Error", "Please enter a frame to render")
                return False
        
        # Renderer
        renderer = self.renderer.currentText().upper()
        if renderer == "CYCLES":
            renderer_api = self.render_api.currentText().upper()
            if renderer_api != "CPU":
                use_cpu = self.use_cpu.isChecked()

        # Output
        output_folder = self.output_folder.text()
        output_file = self.output_filename.text()

        if not output_folder or not output_file:
            QMessageBox.warning(self, "Missing Output", "Please enter an output folder and filename")
            return False

        command = ['-b', blend_path]

        final_output_path = f"{output_folder}/{output_file}"
        command.extend(["-o", final_output_path])

        if animation:
            command.extend(["-s", str(start_frame), "-e", str(end_frame), "-a"])
        else:
            command.extend(["-f", str(solo_frame)])

        command.extend(["-E", renderer])

        if renderer == "CYCLES":
            if use_cpu:
                renderer_api += "+CPU"
            command.extend(["--", "--cycles-device", renderer_api])
        
        print(command)

        self.addToLog("Running Blender...")
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handleStdout)
        self.process.readyReadStandardError.connect(self.handleStderr)
        self.process.stateChanged.connect(self.handleState)
        self.process.finished.connect(self.runRenderCommandFinished)
        self.process.start(blender_path, command)

        # process = subprocess.run(command, stdout=subprocess.PIPE, text=True)

        # for line in process.stdout:
        #     print(line, end="")

        # if process.returncode == 0:
        #     QMessageBox.information(self, "Success", "Rendering complete!")
        # else:
        #     QMessageBox.critical(self, "Error", "Rendering failed! Check log for errors.")
    
    def handleStdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        remainingTime = self.extractRemainingTime(stdout)
        if remainingTime:
            self.updateRemainingTime(remainingTime)

        self.addToLog(stdout)

    def handleStderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        remainingTime = self.extractRemainingTime(stderr)
        if remainingTime:
            self.updateRemainingTime(remainingTime)

        self.addToLog(stderr)

    def handleState(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not Running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running'
        }
        stateReadableName = states[state]
        self.addToLog(f"State Changed: {stateReadableName}")
    
    def runRenderCommandFinished(self):
        self.addToLog("Blender Exited. Check above for more details.")
        self.process = None
        self.updateRemainingTime("Time Remaining: [Waiting for Render Start]")

    def addToLog(self, s):
        self.log_text.appendPlainText(s)

    def updateRemainingTime(self, t):
        self.remaining_time.setText(f"Time Remaining: {t}")

    def extractRemainingTime(self, output):
        remainingRe = r"Remaining:([\d:]+\.\d+)\s*\|"
        m = re.search(remainingRe, output)
        if m:
            remainingTime = m.group(1)
            return remainingTime
        else:
            return "Unknown"
    

class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal() # signal when the text entry is left clicked

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton: self.clicked.emit()
        else: super().mousePressEvent(event)

app = QApplication(sys.argv)

QFontDatabase.addApplicationFont("resources/fonts/OpenSans-SemiBold.ttf")
app.setFont(QFont("Open Sans SemiBold", 10))
app.setStyle("Fusion")

window = MainWindow()
window.show()

app.exec()