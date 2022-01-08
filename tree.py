from typing import List, Union


class Company:
    _name: str = ''
    _unique_id: str = ''
    _sector: str = ''

    def __init__(self, name: str = '', unique_id: str = '', sector: str = ''):
        self._name = name
        self._unique_id = unique_id
        self._sector = sector

    def __ge__(self, other):
        return self._name > other.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def sector(self) -> str:
        return self._sector

    def __repr__(self):
        return f'{self._name} ({self._unique_id}, {self._sector})'


class TreeNodeBase:
    _corp_info_lst: List[Company]
    _ident: str = ''
    _text: str = ''

    def __init__(self, ident: str, text: str, corp_info_lst: List[Company] = None):
        self._ident = ident
        self._text = text
        self._corp_info_lst = list()
        if corp_info_lst is not None:
            self._corp_info_lst.extend(corp_info_lst)
            self._corp_info_lst.sort(key=lambda x: x.name)

    def getIdent(self) -> str:
        return self._ident

    def getText(self) -> str:
        return self._text

    def getCorpInfoList(self) -> List[Company]:
        result = list()
        for child in self.getChildren():
            corp_info_lst = child.getCorpInfoList()
            result.extend(corp_info_lst)
        result.extend(self._corp_info_lst)
        return result

    def setParentNode(self, node):
        pass

    def addChildNode(self, node):
        pass

    def hasChildNode(self, node) -> bool:
        return False

    def getChildren(self) -> list:
        return []

    def __repr__(self):
        return f'{self._text}({self._ident})'


class TreeNode(TreeNodeBase):
    _parent: Union[TreeNodeBase, None]
    _children: List[TreeNodeBase]

    def __init__(self, ident: str, text: str, corp_info_lst: List[Company] = None):
        super().__init__(ident, text, corp_info_lst)
        self._parent = None
        self._children = list()

    def setParentNode(self, node: TreeNodeBase):
        self._parent = node
        if not self._parent.hasChildNode(self):
            self._parent.addChildNode(self)

    def addChildNode(self, node: TreeNodeBase):
        self._children.append(node)

    def hasChildNode(self, node: TreeNodeBase) -> bool:
        return node in self._children

    def getChildren(self) -> List[TreeNodeBase]:
        return self._children

    def getChildNode(self, ident: int) -> Union[TreeNodeBase, None]:
        filterted = list(filter(lambda x: x.getIdent() == ident, self._children))
        if len(filterted) == 1:
            return filterted[0]
        else:
            return None

    def __eq__(self, other: TreeNodeBase):
        return self._ident == other.getIdent()


class Tree:
    _node_list: List[TreeNode]

    def __init__(self):
        self._node_list = list()  # 여러개의 최상위 노드를 담을 수 있게 일단은 구성

    def add_leaf_node(self, ident: str, text: str, parents: List[dict], corp_info_lst: List[Company] = None):
        iter_node: Union[TreeNode, None] = None

        for i, elem in enumerate(parents):
            temp_ident = elem.get('id')
            temp_text = elem.get('text')
            temp_node = TreeNode(temp_ident, temp_text)
            if iter_node is None:  # 최초 iteration
                if temp_node in self._node_list:  # 최상위 노드가 트리의 노드 리스트에 있을 경우
                    temp_node = list(filter(lambda x: x.getIdent() == temp_ident, self._node_list))[0]
                else:  # 최상위 노드가 트리의 노드 리스트에 없을 경우 (추가)
                    self._node_list.append(temp_node)
            else:  # 자식 노드 iteration
                if iter_node.hasChildNode(temp_node):  # 이전 노드의 자식으로 이미 포함되어 있을 경우
                    temp_node = iter_node.getChildNode(temp_ident)
                else:  # 이전 노드의 자식에 없을 경우 (추가)
                    iter_node.addChildNode(temp_node)
            iter_node = temp_node
        node = TreeNode(ident, text, corp_info_lst)
        iter_node.addChildNode(node)

    def add_leaf_node_dict(self, leaf_node_dict: dict):
        ident = leaf_node_dict.get('node_id')
        text = leaf_node_dict.get('node_text')
        parents = leaf_node_dict.get('parents')
        corp_info_arr = leaf_node_dict.get('corp_info_arr')
        corp_info_lst = []
        for elem in corp_info_arr:
            info = Company(elem.get('name'), elem.get('code'), elem.get('sector'))
            corp_info_lst.append(info)
        self.add_leaf_node(ident, text, parents, corp_info_lst)

    def add_leaf_nodes(self, leaf_node_dict_list: List[dict]):
        [self.add_leaf_node_dict(x) for x in leaf_node_dict_list]

    def printHierarchy(self):
        txt = ''

        def iter_print(node_: TreeNodeBase, level: int = 0):
            txt_node = '-' * (level * 4) + node_.getText() + f'({node_.getIdent()})\n'
            if len(node_.getChildren()) > 0:
                for child in node_.getChildren():
                    txt_node += iter_print(child, level + 1)
            return txt_node

        for node in self._node_list:
            txt += iter_print(node)

        print(txt)

    def getNodeList(self) -> List[TreeNode]:
        return self._node_list


if __name__ == "__main__":
    import pickle
    with open('./result_list.pkl', 'rb') as fp:
        node_list = pickle.load(fp)
    tree = Tree()
    tree.add_leaf_nodes(node_list)
