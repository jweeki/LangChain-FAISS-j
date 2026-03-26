import sys
import traceback

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSpinBox,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from common import (
    create_embeddings,
    get_storage_paths,
    load_vector_store,
    search_documents,
)


DEFAULT_TOP_K = 5


class SearchBackend:
    def __init__(self) -> None:
        self.embeddings = None
        self.vector_store = None
        self.paths = get_storage_paths()

    def initialize(self) -> None:
        if self.vector_store is not None:
            return
        self.embeddings = create_embeddings()
        self.vector_store = load_vector_store(self.embeddings)

    def search(self, query: str, k: int):
        self.initialize()
        return search_documents(self.vector_store, query, k=k)


class Worker(QObject):
    finished = pyqtSignal(object)
    failed = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs) -> None:
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self) -> None:
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception:
            self.failed.emit(traceback.format_exc())
        else:
            self.finished.emit(result)


class SearchWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.backend = SearchBackend()
        self.worker_thread = None
        self.worker = None

        self.setWindowTitle("FAISS 检索工具")
        self.resize(980, 720)

        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("请输入检索内容")
        self.query_input.returnPressed.connect(self.handle_search)

        self.topk_spin = QSpinBox()
        self.topk_spin.setRange(1, 100)
        self.topk_spin.setValue(DEFAULT_TOP_K)

        self.load_button = QPushButton("加载模型和索引")
        self.load_button.clicked.connect(self.handle_initialize)

        self.search_button = QPushButton("开始检索")
        self.search_button.clicked.connect(self.handle_search)

        self.clear_button = QPushButton("清空结果")
        self.clear_button.clicked.connect(self.clear_results)

        self.path_info = QPlainTextEdit()
        self.path_info.setReadOnly(True)
        self.path_info.setPlainText(
            "模型目录: {model_dir}\n向量库目录: {vector_store_dir}".format(
                model_dir=self.backend.paths["model_dir"],
                vector_store_dir=self.backend.paths["vector_store_dir"],
            )
        )

        self.results_table = QTableWidget(0, 4)
        self.results_table.setHorizontalHeaderLabels(["序号", "置信度", "内容", "来源"])
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.ResizeToContents)
        header.setSectionResizeMode(1, header.ResizeToContents)
        header.setSectionResizeMode(2, header.Stretch)
        header.setSectionResizeMode(3, header.Stretch)
        self.results_table.setWordWrap(True)

        self.meta_output = QPlainTextEdit()
        self.meta_output.setReadOnly(True)
        self.meta_output.setPlaceholderText("这里显示结果附加信息")

        top_bar = QHBoxLayout()
        top_bar.addWidget(QLabel("检索词"))
        top_bar.addWidget(self.query_input, 1)
        top_bar.addWidget(QLabel("Top K"))
        top_bar.addWidget(self.topk_spin)
        top_bar.addWidget(self.load_button)
        top_bar.addWidget(self.search_button)
        top_bar.addWidget(self.clear_button)

        layout = QVBoxLayout()
        layout.addLayout(top_bar)
        layout.addWidget(QLabel("路径信息"))
        layout.addWidget(self.path_info)
        layout.addWidget(QLabel("检索结果"))
        layout.addWidget(self.results_table, 1)
        layout.addWidget(QLabel("附加信息"))
        layout.addWidget(self.meta_output)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def set_busy(self, busy: bool, message: str) -> None:
        self.load_button.setEnabled(not busy)
        self.search_button.setEnabled(not busy)
        self.clear_button.setEnabled(not busy)
        self.query_input.setEnabled(not busy)
        self.topk_spin.setEnabled(not busy)
        self.status_bar.showMessage(message)

    def set_controls_enabled(self, enabled: bool) -> None:
        self.load_button.setEnabled(enabled)
        self.search_button.setEnabled(enabled)
        self.clear_button.setEnabled(enabled)
        self.query_input.setEnabled(enabled)
        self.topk_spin.setEnabled(enabled)

    def run_in_thread(self, fn, on_success, busy_message: str, *args, **kwargs) -> None:
        if self.worker_thread is not None:
            QMessageBox.information(self, "提示", "当前已有任务在执行，请稍后再试。")
            return

        self.set_busy(True, busy_message)
        self.worker_thread = QThread(self)
        self.worker = Worker(fn, *args, **kwargs)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(on_success)
        self.worker.finished.connect(self.cleanup_thread)
        self.worker.failed.connect(self.handle_worker_error)
        self.worker.failed.connect(self.cleanup_thread)
        self.worker_thread.start()

    def cleanup_thread(self, *_args) -> None:
        if self.worker_thread is not None:
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.worker_thread.deleteLater()
        if self.worker is not None:
            self.worker.deleteLater()
        self.worker_thread = None
        self.worker = None
        self.set_controls_enabled(True)

    def handle_worker_error(self, error_text: str) -> None:
        self.meta_output.setPlainText(error_text)
        self.status_bar.showMessage("执行失败")
        QMessageBox.critical(self, "执行失败", error_text)

    def handle_initialize(self) -> None:
        self.run_in_thread(
            self.backend.initialize,
            self.on_initialize_success,
            "正在加载模型和向量库，请稍候...",
        )

    def on_initialize_success(self, _result) -> None:
        self.meta_output.setPlainText("模型和向量库加载完成，可以开始检索。")
        self.status_bar.showMessage("加载完成")

    def handle_search(self) -> None:
        query = self.query_input.text().strip()
        if not query:
            QMessageBox.warning(self, "输入为空", "请输入检索内容。")
            return

        top_k = self.topk_spin.value()
        self.run_in_thread(
            self.backend.search,
            self.on_search_success,
            "正在执行相似度检索...",
            query,
            top_k,
        )

    def on_search_success(self, results) -> None:
        self.results_table.setRowCount(0)
        self.meta_output.clear()

        if not results:
            self.meta_output.setPlainText("没有检索到匹配内容。")
            self.status_bar.showMessage("检索完成，无结果")
            return

        detail_lines = []
        for row_index, (doc, score) in enumerate(results, start=1):
            confidence = 1 / (1 + score)
            self.results_table.insertRow(row_index - 1)
            self.results_table.setItem(row_index - 1, 0, QTableWidgetItem(str(row_index)))
            self.results_table.setItem(
                row_index - 1, 1, QTableWidgetItem(f"{confidence:.10f}")
            )
            self.results_table.setItem(row_index - 1, 2, QTableWidgetItem(doc.page_content))
            self.results_table.setItem(
                row_index - 1, 3, QTableWidgetItem(str(doc.metadata.get("source", "")))
            )

            extra = {k: v for k, v in doc.metadata.items() if k != "source"}
            detail_lines.append(
                "\n".join(
                    [
                        f"[{row_index}] score={score:.10f}",
                        f"source={doc.metadata.get('source', '')}",
                        f"metadata={extra if extra else '{}'}",
                    ]
                )
            )

        self.meta_output.setPlainText("\n\n".join(detail_lines))
        self.results_table.resizeRowsToContents()
        self.status_bar.showMessage(f"检索完成，返回 {len(results)} 条结果")

    def clear_results(self) -> None:
        self.results_table.setRowCount(0)
        self.meta_output.clear()
        self.status_bar.showMessage("结果已清空")


def main() -> int:
    app = QApplication(sys.argv)
    window = SearchWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
