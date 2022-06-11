# file_indexer.py
# Written by Steve D. J. on 2022/6/10 for FTP_Explorer.

import ftplib


class TreeNode:
    """ A node of the tree structure.

    -parent: parent TreeNode object of this node.
    -is_root: boolean to sign if this node a root node of a tree, the node will be a root node if self.parent=None.
    -is_leaf: boolean to sign if this node a leaf node of a tree, the node will be a leaf node if self.children=[].
    -content: data stored in this node.
    -children: list of child node(s).
    """

    def __init__(self, parent=None, content=None):
        """ Initialize the FileTree object.

        :param parent: the parent TreeNode object (the node will be a root node if parent=None)
        :param content: content stored in this node (can be any type of data)
        """
        self.parent = parent
        if parent is None:
            self.is_root = True
        else:
            self.is_root = False
        self.is_leaf = True
        self.content = content
        self.children = []

    def add_child(self, child):
        """ Add a child node to this node.

        :param child: child node to add (TreeNode object)
        :return: None
        """
        self.children.append(child)
        self.is_leaf = False

    def get_children(self):
        """ Return the children of this node.

        :return: children list or None when this node is a leaf.
        """
        if self.is_leaf is True:
            return None
        else:
            return self.children


class FileIndexer:
    """ Index file structure of the FTP server, store it as a tree and write the tree to the disk.

    """

    def __init__(self, ip):
        """ Initialize the FileIndexer object.

        :param ip: IP of the FTP server (str)
        """
        self.file_tree = TreeNode(parent=None, content=ip)  # This is a tree root, actually.
        self.host = ip
        self.ftp = ftplib.FTP()
        self.ftp.connect(self.host, 21, 2.0)
        self.ftp.login(user='anonymous', passwd='example@email.com')
        self.present_node = self.file_tree
        self.level_ct = 0

    def index(self):
        """ Traverse folders and files on the FTP server and update the file_tree with file/folder names.

        :return: None
        """
        # get file list at present dir
        file_list = self.ftp.nlst()
        for file in file_list:
            new_node = TreeNode(parent=self.present_node, content=file)
            self.present_node.add_child(new_node)
            try:  # it's a folder
                self.ftp.cwd(file)
                new_node.is_leaf = False
                self.present_node = new_node
                self.index()
                self.ftp.cwd('../')
                self.present_node = new_node.parent
            except:  # it's a file
                pass

    def get_file_tree(self, file):
        """ Print and save the file tree.

        Create a new TXT file named with the host IP in folder "file_trees" and write the file tree in it.

        :param file: file object to save the file tree (file)
        :return: None
        """
        cache = self.level_ct * '\t' + self.present_node.content
        print(cache)
        file.write(cache + '\n')
        children_list = self.present_node.get_children()
        if children_list is not None:   # folder
            for child in children_list:
                self.present_node = child
                self.level_ct += 1
                self.get_file_tree(file)
                self.present_node = child.parent
                self.level_ct -= 1
        else:   # file or empty folder
            pass

    def save_file_tree(self):
        """ Create a new TXT file named with the host IP in folder "file_trees" and write the file tree in it.

        :return: None
        """
        file = open('./file_trees/' + self.host + '.txt', 'w')
        self.get_file_tree(file)
        file.close()

        # re-initialize the present_node and level_ct
        self.present_node = self.file_tree
        self.level_ct = 0


if __name__ == '__main__':
    my_indexer = FileIndexer('42.192.44.52')
    my_indexer.index()
    my_indexer.save_file_tree()
    my_indexer.ftp.quit()
