"""PySide2 port of the charts/audio example from Qt v5.x"""

import os
import sys
from PySide2.QtCharts import QtCharts
from PySide2.QtCore import QPointF, QRect, QSize
from PySide2.QtMultimedia import (QAudio, QAudioDeviceInfo, QAudioFormat,
        QAudioInput)
from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox

sampleCount = 2000
resolution = 4

class MainWindow(QMainWindow):
    def __init__(self, device):
        super(MainWindow, self).__init__()

        self.series = QtCharts.QLineSeries()
        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.series)
        self.axisX = QtCharts.QValueAxis()
        self.axisX.setRange(0, sampleCount)
        self.axisX.setLabelFormat("%g")
        self.axisX.setTitleText("Samples")
        self.axisY = QtCharts.QValueAxis()
        self.axisY.setRange(-1, 1)
        self.axisY.setTitleText("Audio level")
        self.chart.setAxisX(self.axisX, self.series)
        self.chart.setAxisY(self.axisY, self.series)
        self.chart.legend().hide()
        self.chart.setTitle("Data from the microphone ({})".format(device.deviceName()))

        formatAudio = QAudioFormat()
        formatAudio.setSampleRate(8000)
        formatAudio.setChannelCount(1)
        formatAudio.setSampleSize(8)
        formatAudio.setCodec("audio/pcm")
        formatAudio.setByteOrder(QAudioFormat.LittleEndian)
        formatAudio.setSampleType(QAudioFormat.UnSignedInt)

        self.audioInput = QAudioInput(device, formatAudio, self)
        self.ioDevice = self.audioInput.start()
        self.ioDevice.readyRead.connect(self._readyRead)

        self.chartView = QtCharts.QChartView(self.chart)
        self.setCentralWidget(self.chartView)

        self.buffer = [QPointF(x, 0) for x in range(sampleCount)]
        self.series.append(self.buffer)

    def closeEvent(self, event):
        if self.audioInput is not None:
            self.audioInput.stop()
        event.accept()

    def _readyRead(self):
        data = self.ioDevice.readAll()
        availableSamples = data.size() // resolution
        start = 0
        if (availableSamples < sampleCount):
            start = sampleCount - availableSamples
            for s in range(start):
                self.buffer[s].setY(self.buffer[s + availableSamples].y())

        dataIndex = 0
        for s in range(start, sampleCount):
            value = (ord(data[dataIndex]) - 128) / 128
            self.buffer[s].setY(value)
            dataIndex = dataIndex + resolution
        self.series.replace(self.buffer)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    inputDevice = QAudioDeviceInfo.defaultInputDevice()
    if (inputDevice.isNull()):
        QMessageBox.warning(None, "audio", "There is no audio input device available.")
        sys.exit(-1)

    mainWin = MainWindow(inputDevice)
    mainWin.setWindowTitle("audio")
    availableGeometry = app.desktop().availableGeometry(mainWin)
    size = availableGeometry.height() * 3 / 4
    mainWin.resize(size, size)
    mainWin.show()
    sys.exit(app.exec_())
