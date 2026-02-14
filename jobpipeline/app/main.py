from __future__ import annotations

import sys
import webbrowser

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QTextEdit, QSplitter
)

from jobpipeline.core.models import SearchProfile
from jobpipeline.core.pipeline import PipelineService
from jobpipeline.utils.config import load_config


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("JobPipeline")
        self.cfg = load_config()
        self.pipeline = PipelineService(self.cfg)
        self.jobs = []
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        self.dashboard = QWidget()
        d_layout = QVBoxLayout(self.dashboard)
        self.summary = QLabel("Last run: none")
        run_btn = QPushButton("Run now")
        run_btn.clicked.connect(self.run_pipeline)
        d_layout.addWidget(self.summary)
        d_layout.addWidget(run_btn)
        tabs.addTab(self.dashboard, "Dashboard")

        tabs.addTab(QLabel("Profiles managed via config.yaml"), "Profiles")
        tabs.addTab(QLabel("Sources managed via config.yaml"), "Sources")

        self.results_widget = QWidget()
        r_layout = QVBoxLayout(self.results_widget)
        splitter = QSplitter()
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Company", "Title", "Grade", "Score", "Source", "Link"])
        self.detail = QTextEdit()
        self.detail.setReadOnly(False)
        splitter.addWidget(self.table)
        splitter.addWidget(self.detail)
        r_layout.addWidget(splitter)
        open_btn = QPushButton("Open selected link")
        open_btn.clicked.connect(self.open_selected)
        r_layout.addWidget(open_btn)
        tabs.addTab(self.results_widget, "Results")
        tabs.addTab(QLabel("Settings in config.yaml: excel path, discovery, js fetch, throttle, hours"), "Settings")

    def run_pipeline(self) -> None:
        p = SearchProfile(**self.cfg["profiles"][0])
        self.jobs = self.pipeline.run(p)
        self.summary.setText(f"Last run collected: {len(self.jobs)}")
        self.table.setRowCount(len(self.jobs))
        for row, job in enumerate(self.jobs):
            self.table.setItem(row, 0, QTableWidgetItem(job.company))
            self.table.setItem(row, 1, QTableWidgetItem(job.title))
            self.table.setItem(row, 2, QTableWidgetItem(job.fit_grade))
            self.table.setItem(row, 3, QTableWidgetItem(str(job.fit_score)))
            self.table.setItem(row, 4, QTableWidgetItem(job.source_name))
            self.table.setItem(row, 5, QTableWidgetItem(job.job_url))

    def open_selected(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            webbrowser.open(self.table.item(row, 5).text())


def main() -> None:
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
