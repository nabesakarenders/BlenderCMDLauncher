import re
import sys
import time
from datetime import timedelta

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
        self.process = None

        # Setup time tracking for time remaining estimation
        self._render_start_time = None
        self._frame_times = []
        self._total_frames_in_job = 0
        self._completed_frames = 0
        self._is_animation_job = False

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
        container.addLayout(self.createEstimationDisplay())

        # Setup Central Widget
        widget = QWidget()
        widget.setLayout(container)
        self.setCentralWidget(widget)
        self.setWindowTitle("Blender CMD Launcher")
        self.setFixedSize(750, 750)

        self._widgets_to_disable_during_render = [
            self.blender_path, self.blender_path_button,
            self.blend_path, self.blend_path_button,
            self.is_animation,
            self.solo_frame_label, self.solo_frame,
            self.start_frame_label, self.start_frame,
            self.end_frame_label, self.end_frame,
            self.renderer, self.render_api, self.use_cpu,
            self.output_folder, self.output_folder_button,
            self.output_filename
            # Add extra UI elements to disable while rendering here
        ]

        # Load any saved settings
        self.loadSettings()

        self._set_ui_rendering_state(False)

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
    
    def createEstimationDisplay(self):
        container = QHBoxLayout()
        container.setContentsMargins(5, 5, 5, 20)
        self.estimation_label = QLabel()
        self.estimation_label.setText('Estimated Time Remaining: [Waiting for first frame]')
        self.estimation_label.setStyleSheet("font-weight: bold; font-size: 13pt;")
        container.addWidget(self.estimation_label)
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

        # Probably not needed anymore but kept for posterity
        # If Blender is already running don't try to run it again
        # if self.process is not None:
        #     QMessageBox.warning(self, "Blender Running!", "Blender is already running. Check the log box and wait for it to finish!")
        #     return False

        # Reset estimation variables
        self._render_start_time = time.time()
        self._frame_times = []
        self._total_frames_in_job = 0
        self._completed_frames = 0
        self._is_animation_job = self.is_animation.isChecked()
        self.estimation_label.setText('Estimated Time Remaining: [Waiting for first frame...]')
        self.remaining_time.setText('Time Remaining: [Calculating...]')

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
            self._total_frames_in_job = end_frame - start_frame + 1
        else:
            # Must be since frame render
            solo_frame = self.solo_frame.value()
            if solo_frame is None:
                QMessageBox.warning(self, "Error", "Please enter a frame to render")
                return False
            self._total_frames_in_job = 1
        
        # Renderer
        renderer = self.renderer.currentText().upper()
        renderer_api = ""
        use_cpu = False
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
        
        print("Starting Blender with command:", command)

        self.addToLog(f"Starting Blender render... Total frames: {self._total_frames_in_job}")

        # Set UI to rendering state
        self._set_ui_rendering_state(True)

        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handleStdout)
        self.process.readyReadStandardError.connect(self.handleStderr)
        self.process.stateChanged.connect(self.handleState)
        self.process.finished.connect(lambda exitCode, exitStatus: self.runRenderCommandFinished(exitCode, exitStatus))
        self.process.start(blender_path, command)

        if not self.process.waitForStarted(5000):
            self.addToLog("!!! Blender process failed to start! Check Blender path and permissions")
            QMessageBox.critical(self, "Process Error", "Failed to start the Blender process. Check the log!")
            self._set_ui_rendering_state(False)
            self.process = None
            return
        
    def cancelRenderCommand(self):
        """Attempts to terminate the currently running Blender process"""
        if self.process and self.process.state() != QProcess.ProcessState.NotRunning:
            self.addToLog("--- Attempting to cancel render... ---")
            reply = QMessageBox.question(self, 'Cancel Render', "Are you sure you want to cancel the current render? Blender will not close nicely while rendering, this will force close Blender.", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                self.addToLog("--- User confirmed cancellation. Terminating Blender process... ---")
                self.process.kill()
            else:
                self.addToLog("--- User aborted cancellation... ---")
        else:
            self.addToLog("--- Cancel requested, but no Blender process running ---")
            if not self.process:
                self._set_ui_rendering_state(False)
    
    def handleStdout(self):
        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8", errors='ignore')
        remainingTime = self.extractRemainingTime(stdout)
        # Process line by line for better parsing
        for line in stdout.splitlines():
            self.addToLog(line) # Log the raw line
            self._process_output_line(line) # Process for estimates

    def handleStderr(self):
        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8", errors='ignore')
         # Process line by line for better parsing
        for line in stderr.splitlines():
            self.addToLog(line) # Log the raw line
            self._process_output_line(line) # Process for estimates

    def _process_output_line(self, line):
        """Processes a line of output for Blender info and updates estimates."""
        # --- Try to match the final frame time line FIRST ---
        frame_time_match = re.search(r"^Time:\s*([\d:.]+)\s*\(Saving:\s*[\d:.]+\)$", line)
        if frame_time_match and self._is_animation_job and self._total_frames_in_job > 1:
            frame_time_str = frame_time_match.group(1) # Get the captured total time
            frame_time_sec = self._parse_blender_time_to_seconds(frame_time_str)

            if frame_time_sec is not None and frame_time_sec > 0:
                self._frame_times.append(frame_time_sec)
                self._completed_frames = len(self._frame_times)

                # Calculate Average Time
                avg_time_per_frame = sum(self._frame_times) / self._completed_frames

                # Calculate estimated remaining time
                remaining_frames = self._total_frames_in_job - self._completed_frames
                estimated_remaining_sec = avg_time_per_frame * remaining_frames

                # Format the time for humans
                if estimated_remaining_sec >= 0:
                    eta_str = str(timedelta(seconds=int(estimated_remaining_sec)))
                    avg_str = f"{avg_time_per_frame:.2f}"
                    self.estimation_label.setText(f'Estimated Time Remaining: {eta_str} ({self._completed_frames}/{self._total_frames_in_job} frames @ {avg_str}s avg)')
                else:
                    # Handle case where calculation might be slightly off at the very end
                    self.estimation_label.setText('Estimated Time Remaining: [Finishing...]')

                self.addToLog(f"--- Detected Frame Time: {frame_time_sec:.2f}s ---")
            return # We've processed this line, no need to check for "Remaining:"

        # --- If it wasn't the frame time line, check for "Remaining:" ---
        remaining_time_blender = self.extractRemainingTime(line)
        if remaining_time_blender: # Check if not None or empty
            try:
                # Keep your existing logic for displaying Blender's remaining time
                display_time = remaining_time_blender
                if ':' in remaining_time_blender and '.' in remaining_time_blender:
                     # Attempt to remove milliseconds for cleaner display if present
                     parts = remaining_time_blender.split('.')
                     if len(parts) > 1 and len(parts[-1]) > 0: # Check if there's something after '.'
                         display_time = parts[0]

                self.updateRemainingTime(f"{display_time} (Reported by Blender)")
            except Exception as e:
                 self.addToLog(f"Error processing Blender remaining time: {e}")
                 self.updateRemainingTime(f"{remaining_time_blender} (Reported by Blender)") # Fallback
        elif "Fra:" in line and "Remaining:" not in line and not frame_time_match:
             # If we see frame progress but no remaining time AND it wasn't the final frame time line,
             # clear the Blender time estimate.
             self.updateRemainingTime("[Calculating...]")          

    def handleState(self, state):
        states = {
            QProcess.ProcessState.NotRunning: 'Not Running',
            QProcess.ProcessState.Starting: 'Starting',
            QProcess.ProcessState.Running: 'Running'
        }
        stateReadableName = states[state]
        self.addToLog(f"State Changed: {stateReadableName}")
    
    def runRenderCommandFinished(self, exitCode, exitStatus):
        self.addToLog("Blender Process Exited.")
        end_time = time.time()
        total_duration_sec = end_time - self._render_start_time if self._render_start_time else 0
        total_duration_str = str(timedelta(seconds=int(total_duration_sec)))

        final_log_message = f"Render finished. Total time: {total_duration_str}."

        was_cancelled = exitStatus == QProcess.ExitStatus.NormalExit and exitCode != 0

        if exitStatus == QProcess.ExitStatus.NormalExit and exitCode == 0:
            final_log_message += " (Completed Successfully)"
            self.estimation_label.setText(f'Finished! Total time: {total_duration_str}')
            self.remaining_time.setText("Time Remaining: [Render Complete]")
        elif was_cancelled or "Terminating process" in self.log_text.toPlainText().splitlines()[-5:]:
            final_log_message += f" (Cancelled by user. Exit code: {exitCode})"
            self.estimation_label.setText(f'Render Canclled! Total time: {total_duration_str}')
            self.remaining_time.setText("Time Remaining: [Render Cancelled]")
            QMessageBox.information(self, "Render Cancelled", f"Render process was cancelled by the user.")
        else:
            final_log_message += f" (Exited with status: {exitStatus}, code: {exitCode})"
            self.estimation_label.setText(f'Finished (Possible Errors). Total time: {total_duration_str}')
            self.remaining_time.setText("Time Remaining: [Render Finished/Error]")
            QMessageBox.warning(self, "Render Finished", f"Blender process finished, but maybe with errors (Exit Code: {exitCode}). Check the log.")

        self.addToLog(final_log_message)

        self.process = None
        self._set_ui_rendering_state(False)

        self._render_start_time = None
        self._is_animation_job = False

    def addToLog(self, s):
        self.log_text.appendPlainText(s)

    def updateRemainingTime(self, t):
        if t is not None:
            self.remaining_time.setText(f"Time Remaining: {t}")

    def extractRemainingTime(self, output):
        patterns = [
            r"Remaining:([\d:.]+)",            # Common pattern
            r"Remaining: ([\d.:]+)\s*\|",      # Alternative with space and pipe
            r"Rendered \d+/\d+, Remaining: ([\d.:]+)" # Another variation
        ]
        for pattern in patterns:
            m = re.search(pattern, output)
            if m:
                return m.group(1).strip()
        return None
        
    def _parse_blender_time_to_seconds(self, time_str):
        """Converts Blender time string (HH:MM:SS.ms or MM:SS.ms) to seconds"""
        parts = time_str.split(':')
        try:
            if len(parts) == 3: # HH:MM:SS.ms
                h, m, s = map(float, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2: # MM:SS.ms
                m, s = map(float, parts)
                return m * 60 + s
            elif len(parts) == 1: # SS.ms
                s = float(parts[0])
                return s
            else:
                raise None
        except ValueError:
            print(f"Warning: Could not parse time string: {time_str}")
            return None
    
    def _set_ui_rendering_state(self, is_rendering):
        """Enabled/Disables UI elements based on rendering status"""
        try:
            self.render_button.clicked.disconnect()
        except TypeError:
            pass

        if is_rendering:
            self.render_button.setText("Cancel Render")
            self.render_button.clicked.connect(self.cancelRenderCommand)
            for widget in self._widgets_to_disable_during_render:
                widget.setEnabled(False)
        else:
            self.render_button.setText("Render Now")
            self.render_button.clicked.connect(self.runRenderCommand)
            for widget in self._widgets_to_disable_during_render:
                widget.setEnabled(True)
            self.showAnimationOptions(self.is_animation.checkState())
            self.canDisplayRenderApi(self.renderer.currentIndex())
            self.canDisplayCpuOption(self.render_api.currentIndex())

    

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