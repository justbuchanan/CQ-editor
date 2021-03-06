from spyder.widgets.sourcecode.codeeditor import  CodeEditor
from PyQt5.QtCore import pyqtSignal, QFileSystemWatcher
from PyQt5.QtWidgets import QAction, QFileDialog

import cadquery as cq
import imp
import sys

from pyqtgraph.parametertree import Parameter

from ..mixins import ComponentMixin
from ..cq_utils import find_cq_objects

from ..icons import icon

class Editor(CodeEditor,ComponentMixin):
    
    name = 'Code Editor'

    # This signal is emitted whenever the currently-open file changes and
    # autoreload is enabled.
    triggerRerender = pyqtSignal(bool)
    
    preferences = Parameter.create(name='Preferences',children=[
        {'name': 'Font size', 'type': 'int', 'value': 12},
        {'name': 'Autoreload', 'type': 'bool', 'value': False},
        {'name': 'Color scheme', 'type': 'list',
         'values': ['Spyder','Monokai','Zenburn'], 'value': 'Spyder'}])
    
    EXTENSIONS = '*.py'
    
    def __init__(self,parent=None):
        
        super(Editor,self).__init__(parent)
        ComponentMixin.__init__(self) 
        
        self._filename = ''
        
        self.setup_editor(linenumbers=True,
                          markers=True,
                          edge_line=False,
                          tab_mode=False,
                          show_blanks=True,
                          language='Python')
        
        self._actions =  \
                {'File' : [QAction(icon('new'),
                                  'New',
                                  self,triggered=self.new),
                          QAction(icon('open'),
                                  'Open',
                                  self,triggered=self.open),
                          QAction(icon('save'),
                                  'Save',
                                  self,triggered=self.save),
                          QAction(icon('save_as'),
                                  'Save as',
                                  self,triggered=self.save_as),
                          QAction(icon('autoreload'),
                                  'Automatic reload and preview',
                                  self,triggered=self.autoreload,
                                  checkable=True,
                                  checked=False,
                                  objectName='autoreload'),
                          ]}
        
        for a in self._actions.values():
            self.addActions(a)


        self._fixContextMenu()                   
        self.updatePreferences()

        # autoreload support
        self._file_watcher = QFileSystemWatcher(self)
        self._watched_file = None
        self._file_watcher.fileChanged.connect(self._file_changed)

    def _fixContextMenu(self):
        
        menu = self.menu
        
        menu.removeAction(self.run_cell_action)
        menu.removeAction(self.run_cell_and_advance_action)
        menu.removeAction(self.run_selection_action)
        menu.removeAction(self.re_run_last_cell_action)

    def updatePreferences(self,*args):
        
        self.set_color_scheme(self.preferences['Color scheme'])
        
        font = self.font()
        font.setPointSize(self.preferences['Font size'])
        self.set_font(font)

        self.findChild(QAction, 'autoreload') \
            .setChecked(self.preferences['Autoreload'])

    def new(self):
        
        self.filename = ''
        self.set_text('')

    def open(self):
        
        fname,_ = QFileDialog.getOpenFileName(self,filter=self.EXTENSIONS)
        if fname is not '':
            self.load_from_file(fname)

    def load_from_file(self,fname):
        
        self.set_text_from_file(fname)
        self.filename = fname

    def save(self):
        
        if self._filename is not '':
            with open(self._filename,'w') as f:
                f.write(self.get_text_with_eol())
        else:
            self.save_as()

    def save_as(self):
        
        fname,_ = QFileDialog.getSaveFileName(self,filter=self.EXTENSIONS)
        if fname is not '':
            with open(fname,'w') as f:
                f.write(self.get_text_with_eol())
                self.filename = fname

    def _update_filewatcher(self):
        if self._watched_file and (self._watched_file != self.filename or not self.preferences['Autoreload']):
            self._file_watcher.removePath(self._watched_file)
            self._watched_file = None
        if self.preferences['Autoreload'] and self.filename and self.filename != self._watched_file:
            self._watched_file = self._filename
            self._file_watcher.addPath(self.filename)

    @property
    def filename(self):
      return self._filename
    @filename.setter
    def filename(self, fname):
        self._filename = fname
        self._update_filewatcher()

    # callback triggered by QFileSystemWatcher
    def _file_changed(self, val):
        self.set_text_from_file(self._filename)
        self.triggerRerender.emit(True)

    # Turn autoreload on/off.
    def autoreload(self, enabled):
        self.preferences['Autoreload'] = enabled
        self._update_filewatcher()

        
if __name__ == "__main__":
    
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    editor = Editor()
    editor.show()
    
    sys.exit(app.exec_())
        