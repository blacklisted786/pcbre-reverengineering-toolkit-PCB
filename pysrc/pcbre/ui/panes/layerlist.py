from qtpy import QtCore, QtWidgets
from pcbre.model.project import Project
from pcbre.model.stackup import Layer
import pcbre.ui.boardviewwidget

from typing import Any, Optional

# Adapter to provide a view over the project list entries
class LayerListModel(QtCore.QAbstractListModel):
    def __init__(self, project: Project, parent: Optional[QtCore.QObject]=None) -> None:
        QtCore.QAbstractListModel.__init__(self, parent)
        self.p = project

        # TODO: Figure out story for changed stackup detection
        #project.stackup.changed.connect(self._changed)

    #def _changed(self, reason):
    #    self.layoutChanged.emit()

    def rowCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
        b = len(self.p.stackup.layers)
        return b

    def data(self, index: QtCore.QModelIndex, role: int=QtCore.Qt.DisplayRole) -> Any:
        if role == QtCore.Qt.DisplayRole:
            return self.p.stackup.layers[index.row()].name
        return None

    # Retrieve the index opaque type for a layer object
    def index_for(self, layer: Layer) -> QtCore.QModelIndex:
        row = self.p.stackup._order_for_layer(layer)
        return self.index(row)


class LayerListWidget(QtWidgets.QDockWidget):
    def __init__(self, win: QtWidgets.QMainWindow, project: Project, viewState: 'pcbre.ui.boardviewwidget.ViewState') -> None:
        super(LayerListWidget, self).__init__("Layer List")
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea) # type: ignore

        self.win = win
        self.model = LayerListModel(project)

        self.layer_list = QtWidgets.QListView(self)
        self.layer_list.setModel(self.model)
        self.layer_list.selectionModel().selectionChanged.connect(self.layer_selection_changed)

        self.win.layerChanged.connect(self.changeSelection)

        self.setWidget(self.layer_list)

        self.suppress_sel_change = False

    def changeSelection(self, layer: Layer) -> None:
        self.suppress_sel_change = True
        self.layer_list.selectionModel().select(
            self.model.index_for(layer),
            QtCore.QItemSelectionModel.SelectCurrent)

        self.suppress_sel_change = False

    def layer_selection_changed(self, selected: QtCore.QItemSelection, deselected: QtCore.QItemSelection) -> None:
        if self.suppress_sel_change:
            return
        layer_index = selected.indexes()[0].row()
        self.win.changeViewLayer(self.win.project.stackup.layers[layer_index])
