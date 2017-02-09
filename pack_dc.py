#!/usr/bin/python
# -*- coding: utf-8 -*-

# Packaging Double-Check Tool
#
# Author: Simon Lachaîne


import os
import sys
import time
from collections import OrderedDict

from PyQt4 import QtCore, QtGui

import pack_dc_ui as main_frame


operators = [
    u"Francis Nadeau-Lussier",
    u"Philippe Lesiège",
    u"Patrick Gauthier",
    u"Pierre Beaulieu-Desbiens",
]


workflows = [
    u"Validation Copie Zéro (eOne)",
    u"Validation Librairie",
    u"Validation VOD",
    u"Validation CC",
    u"Correction/Patch",
    u"Package iTunes",
    u"Package Bell",
    u"Package Google",
    u"Package Sasktel",
    u"Package Amazon",
    u"Package Microsoft",
]


class CreateReport(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        pass


class PackDcApp(QtGui.QMainWindow, main_frame.Ui_PackDCWindow):
    def __init__(self, parent=None):
        super(PackDcApp, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        self.create_report_thread = CreateReport()
        self.default_dir = ""
        self.op = u"Francis Nadeau-Lussier"

        self.setupUi(self)

        # lists of checkboxes
        self.frame1_checks = OrderedDict([
            (self.frame1_prores, ["ProRes 422 HQ", None]),
            (self.frame1_24, ["24 bit", None]),
            (self.frame1_23, ["23.98", None]),
            (self.frame1_mono, ["Pistes mono", None]),
            (self.frame1_jes, ["JES", None]),
            (self.frame1_ordre, ["Ordre Pistes", None]),
            (self.frame1_peak, ["Peaking", None]),
            (self.frame1_valeurs, ["Valeurs noirs/blancs", None]),
            (self.frame1_colo, ["Colo ftr vs textless", None]),
            (self.frame1_tc, ["TC Original", None]),
            (self.frame1_assignation, ["Assignation de pistes", None]),
            (self.frame1_titre, ["Titre", None]),
            (self.frame1_ratio, ["Ratio", None]),
            (self.frame1_framerate, ["Framerate", None]),
            (self.frame1_audio, ["Langue Audio", None]),
            (self.frame1_mixes, ["Mixes", None]),
            (self.frame1_subs, ["Langue Subs", None]),
            (self.frame1_version, ["Version", None]),
            (self.frame1_prequal, ["Prequal", None]),
        ])

        self.frame2_checks = [
            self.frame2_prores,
            self.frame2_24,
            self.frame2_jes,
            self.frame2_ordre,
            self.frame2_peak,
            self.frame2_tc,
            self.frame2_assignation,
            self.frame2_titre,
            self.frame2_lib,
            self.frame2_ratio,
            self.frame2_framerate,
            self.frame2_audio,
            self.frame2_mixes,
            self.frame2_subs,
        ]

        self.frame3_checks = [
            self.frame3_prores,
            self.frame3_24,
            self.frame3_mono,
            self.frame3_jes,
            self.frame3_ordre,
            self.frame3_peak,
            self.frame3_tc,
            self.frame3_assignation,
            self.frame3_titre,
            self.frame3_vod,
            self.frame3_ratio,
            self.frame3_framerate,
            self.frame3_audio,
            self.frame3_mixes,
            self.frame3_subs,
        ]

        # connect checkboxes
        for check in self.frame1_checks.keys():
            check.stateChanged.connect(lambda: self.check_complete(self.frame1_checks.keys()))

        for check in self.frame2_checks:
            check.stateChanged.connect(lambda: self.check_complete(self.frame2_checks))

        for check in self.frame3_checks:
            check.stateChanged.connect(lambda: self.check_complete(self.frame3_checks))

        # connect drop-downs
        self.op_combo.addItems(operators)
        self.op_combo.currentIndexChanged.connect(self.set_op)
        self.workflow_combo.addItems(workflows)
        self.workflow_combo.currentIndexChanged.connect(self.set_workflow)

        # connect process
        self.browse_btn.clicked.connect(self.save_report)
        self.reset_btn.clicked.connect(self.reset_app)

        # hide frames
        self.frame_valid_lib.hide()
        self.frame_valid_vod.hide()

        self.resize(self.minimumSizeHint())

        self.show()

    def set_op(self):
        self.op = self.op_combo.currentText()

    def set_workflow(self):
        if self.workflow_combo.currentText() == u"Validation Copie Zéro (eOne)":
            self.frame_valid_lib.hide()
            self.frame_valid_vod.hide()
            self.frame_valid_zero_eone.show()
            self.check_complete(self.frame1_checks.keys())

        elif self.workflow_combo.currentText() == u"Validation Librairie":
            self.frame_valid_zero_eone.hide()
            self.frame_valid_vod.hide()
            self.frame_valid_lib.show()
            self.check_complete(self.frame2_checks)

        elif self.workflow_combo.currentText() == u"Validation VOD":
            self.frame_valid_zero_eone.hide()
            self.frame_valid_lib.hide()
            self.frame_valid_vod.show()
            self.check_complete(self.frame3_checks)

        return self.resize(self.minimumSizeHint())

    def check_complete(self, frame):
        check_nb = 0

        for check in frame:
            if check.isChecked():
                check_nb += 1

        if check_nb == len(frame):
            self.complete_lbl.setText("Complete")
            self.complete_lbl.setStyleSheet("""
            .QLineEdit {
            background-color: GreenYellow;}
            """)

        else:
            self.complete_lbl.setText("Incomplete")
            self.complete_lbl.setStyleSheet("""
            .QLineEdit {
            background-color: Orange;}
            """)

    def save_report(self):
        report_path = str(QtGui.QFileDialog.getSaveFileName(
            parent=self,
            caption="Select destination and enter name for the report",
            directory=self.default_dir + "/project_dc_report_%s.txt" % time.strftime("%X"),
            filter="Text file (*.txt)"))

        self.default_dir = os.path.split(report_path)[0]

        if report_path:

            with open(report_path, "w") as report:
                if self.workflow_combo.currentText() == u"Validation Copie Zéro (eOne)":
                    for check in self.frame1_checks.keys():
                        task = self.frame1_checks[check][0]
                        status = "Done" if check.isChecked() is True else "To do"
                        operator = self.op if status == "Done" else "None"
                        report.write(task + ": " + status + "\nOperator: " + operator + "\n\n")

                elif self.workflow_combo.currentText() == u"Validation Librairie":
                    for check in self.frame2_checks:
                        report.write(str(check.isChecked()))

                elif self.workflow_combo.currentText() == u"Validation VOD":
                    for check in self.frame3_checks:
                        report.write(str(check.isChecked()))

    def reset_app(self):
        for check in self.frame1_checks:
            check.setChecked(False)

        for check in self.frame2_checks:
            check.setChecked(False)

        for check in self.frame3_checks:
            check.setChecked(False)

        self.complete_lbl.setStyleSheet("""
                    .QLineEdit {
                    background-color: White;}
                    """)

        return self.complete_lbl.clear()


def main():
    app = QtGui.QApplication(sys.argv)
    gui = PackDcApp()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
