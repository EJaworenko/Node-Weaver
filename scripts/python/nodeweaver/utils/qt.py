"""Enhanced Qt components and patterns for consistent UI implementation.

This module provides a comprehensive set of base classes, mixins, and utilities
for building Qt interfaces in Houdini. It focuses on:
- Consistent styling and theming
- Reusable UI patterns
- Type-safe signal/slot connections
- State management
- Resource handling
"""

from typing import Optional, Type, TypeVar, Dict, List, Any, Callable
import contextlib
from pathlib import Path
from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtCore import Qt, Signal, Slot

T = TypeVar('T')  # Generic type for type safety
W = TypeVar('W', bound=QtWidgets.QWidget)  # Widget type constraint

class ThemeManager:
    """Manages application-wide theming and styling.

    Uses a configuration-driven approach to maintain consistent visual styling
    across the application.
    """

    def __init__(self):
        self._current_theme = "dark"
        self._themes: Dict[str, Dict[str, str]] = {
            "dark": {
                "primary": "#2B5B84",
                "secondary": "#538cc6",
                "background": "#2b2b2b",
                "surface": "#333333",
                "error": "#cf6679",
                "text": "#ffffff",
                "border": "#444444"
            },
            "light": {
                "primary": "#1976d2",
                "secondary": "#42a5f5",
                "background": "#fafafa",
                "surface": "#ffffff",
                "error": "#b00020",
                "text": "#000000",
                "border": "#e0e0e0"
            }
        }

    def get_color(self, name: str) -> str:
        """Get color value from current theme."""
        return self._themes[self._current_theme][name]

    def apply_theme(self, widget: QtWidgets.QWidget) -> None:
        """Apply current theme to widget and all children."""
        theme = self._themes[self._current_theme]
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {theme["background"]};
                color: {theme["text"]};
                font-size: 12px;
            }}

            QPushButton {{
                background-color: {theme["primary"]};
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }}

            QPushButton:hover {{
                background-color: {theme["secondary"]};
            }}

            QLineEdit {{
                padding: 8px;
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                background-color: {theme["surface"]};
            }}

            QComboBox {{
                padding: 8px;
                border: 1px solid {theme["border"]};
                border-radius: 4px;
                background-color: {theme["surface"]};
            }}
        """)

class DialogMixin:
    """Provides common dialog functionality for widgets."""

    def show_error(self, message: str, title: str = "Error") -> None:
        """Show error dialog."""
        QtWidgets.QMessageBox.critical(self, title, message)

    def show_warning(self, message: str, title: str = "Warning") -> None:
        """Show warning dialog."""
        QtWidgets.QMessageBox.warning(self, title, message)

    def confirm(self, message: str, title: str = "Confirm") -> bool:
        """Show confirmation dialog.

        Returns:
            True if user confirmed, False otherwise
        """
        return QtWidgets.QMessageBox.question(
            self, title, message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        ) == QtWidgets.QMessageBox.Yes

class WindowMixin:
    """Provides window management functionality."""

    def center_on_screen(self) -> None:
        """Center window on screen."""
        screen = QtWidgets.QDesktopWidget().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def make_stay_on_top(self) -> None:
        """Make window stay on top."""
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    @contextlib.contextmanager
    def block_signals(self):
        """Temporarily block widget signals."""
        self.blockSignals(True)
        try:
            yield
        finally:
            self.blockSignals(False)

class BaseWidget(QtWidgets.QWidget, WindowMixin, DialogMixin):
    """Base widget with common functionality."""

    theme_manager = ThemeManager()

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)
        self.setup_ui()
        self.theme_manager.apply_theme(self)

    def setup_ui(self) -> None:
        """Set up the widget's UI."""
        pass

def create_widget_with_layout(
    widget_type: Type[W],
    layout_type: Type[QtWidgets.QLayout],
    parent: Optional[QtWidgets.QWidget] = None
) -> W:
    """Create a widget with a layout in one step."""
    widget = widget_type(parent)
    layout = layout_type(widget)
    widget.setLayout(layout)
    return widget

class SearchWidget(BaseWidget):
    """Reusable search widget with common functionality."""

    search_triggered = Signal(str)  # Emitted when search should be performed

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

    def setup_ui(self) -> None:
        layout = QtWidgets.QHBoxLayout(self)

        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.textChanged.connect(self._on_text_changed)

        self.case_sensitive = QtWidgets.QCheckBox("Case Sensitive")

        layout.addWidget(self.search_input)
        layout.addWidget(self.case_sensitive)

    @Slot(str)
    def _on_text_changed(self, text: str) -> None:
        """Handle search text changes."""
        if len(text) >= 3:  # Minimum search length
            self.search_triggered.emit(text)

class ResultsList(BaseWidget):
    """Reusable widget for displaying search/operation results."""

    item_selected = Signal(dict)  # Emitted when user selects a result

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super().__init__(parent)

    def setup_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        self.status_label = QtWidgets.QLabel()

        layout.addWidget(self.status_label)
        layout.addWidget(self.list_widget)

    def set_results(self, results: List[Dict[str, Any]]) -> None:
        """Update displayed results."""
        self.list_widget.clear()
        self.status_label.setText(f"Found {len(results)} results")

        for result in results:
            item = QtWidgets.QListWidgetItem()
            item.setText(result["display_text"])
            item.setData(Qt.UserRole, result)
            self.list_widget.addItem(item)

    @Slot(QtWidgets.QListWidgetItem)
    def _on_item_clicked(self, item: QtWidgets.QListWidgetItem) -> None:
        """Handle result selection."""
        result_data = item.data(Qt.UserRole)
        self.item_selected.emit(result_data)