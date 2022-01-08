from typing import List
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QSplitter, QHeaderView, QAbstractItemView
from tree import Tree, TreeNodeBase, Company


class CorpTreeItem(QTreeWidgetItem):
    def __init__(self, node: TreeNodeBase):
        super().__init__()
        self._node = node
        self._sector = node.getIdent()
        text = node.getText() + ' (' + node.getIdent() + ')'
        self.setText(0, text)

    def getCorpInfoList(self) -> List[Company]:
        return self._node.getCorpInfoList()

    def getSector(self) -> str:
        return self._sector


class CorpTreeViewWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._tree = QTreeWidget()
        self._treeitems: List[CorpTreeItem] = list()
        self._table = QTableWidget()
        self._splitter = QSplitter(Qt.Horizontal, self)
        self.initControl()
        self.initLayout()

    def initControl(self):
        self._tree.itemSelectionChanged.connect(self.onItemSelectionChanged)
        self._tree.setHeaderHidden(True)
        self._table.setColumnCount(3)
        self._table.setHorizontalHeaderLabels(['이름', '고유번호', '업종코드'])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.itemDoubleClicked.connect(self.onTableItemDoubleClicked)

    def initLayout(self):
        self._splitter.addWidget(self._tree)
        self._splitter.addWidget(self._table)

    def setCorpTree(self, tree_: Tree):
        self._tree.clear()
        tree_node_list = tree_.getNodeList()
        for top_node in tree_node_list:
            def addTreeItem(tree_node: TreeNodeBase, tree_item: CorpTreeItem = None):
                if tree_item is None:
                    tree_item = CorpTreeItem(tree_node)
                    self._tree.addTopLevelItem(tree_item)
                    self._treeitems.append(tree_item)
                else:
                    tree_child_item = CorpTreeItem(tree_node)
                    tree_item.addChild(tree_child_item)
                    self._treeitems.append(tree_child_item)
                    tree_item = tree_child_item
                for child_node in tree_node.getChildren():
                    addTreeItem(child_node, tree_item)

            addTreeItem(top_node)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self._splitter.resize(self.width(), self.height())

    def onItemSelectionChanged(self):
        selitems = self._tree.selectedItems()
        corp_info_lst = []
        if len(selitems) > 0:
            for elem in selitems:
                if isinstance(elem, CorpTreeItem):
                    corp_info_lst.extend(elem.getCorpInfoList())
        self._table.setRowCount(len(corp_info_lst))
        for i in range(self._table.rowCount()):
            item = QTableWidgetItem()
            item.setText(corp_info_lst[i].name)
            item.setFlags(Qt.ItemFlags(int(item.flags()) ^ Qt.ItemIsEditable))
            item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self._table.setItem(i, 0, item)
            item = QTableWidgetItem()
            item.setText(corp_info_lst[i].unique_id)
            item.setFlags(Qt.ItemFlags(int(item.flags()) ^ Qt.ItemIsEditable))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self._table.setItem(i, 1, item)
            item = QTableWidgetItem()
            item.setText(corp_info_lst[i].sector)
            item.setFlags(Qt.ItemFlags(int(item.flags()) ^ Qt.ItemIsEditable))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self._table.setItem(i, 2, item)

    def onTableItemDoubleClicked(self):
        item = self._table.selectedItems()
        rows = list(set([x.row() for x in item]))
        if len(rows) == 1:
            row = rows[0]
            sector = self._table.item(row, 2).text()
            tree_item = list(filter(lambda x: x.getSector() == sector, self._treeitems))
            if len(tree_item) == 1:
                self._tree.setCurrentItem(tree_item[0])


if __name__ == "__main__":
    import sys
    import pickle
    from PyQt5.QtWidgets import QApplication

    with open('./result_list.pkl', 'rb') as fp:
        node_list = pickle.load(fp)

    app = QApplication(sys.argv)
    wgt_ = CorpTreeViewWidget()
    wgt_.resize(600, 600)
    wgt_.show()
    corp_tree = Tree()
    corp_tree.add_leaf_nodes(node_list)
    wgt_.setCorpTree(corp_tree)
    app.exec_()
