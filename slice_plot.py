
from enthought.chaco.api import ArrayPlotData, Plot, gray, GridContainer, \
    OverlayPlotContainer, GridDataSource, HPlotContainer
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance, DelegatesTo, \
    on_trait_change, Enum, Array, Int, Str
from enthought.traits.ui.api import Item, View
from enthought.chaco.tools.cursor_tool import CursorTool, BaseCursorTool
from enthought.enable.api import BaseTool
from enthought.chaco.tools.api import LineInspector


# File IO imports
from enthought.traits.api import File, Button
from enthought.traits.ui.api import HGroup
from enthought.traits.ui.file_dialog import open_file


# Nipy stuff
#import nipy as ni
import nifti

def load_image():
    file_name = File
    file_name = open_file()
    if file_name != '':
        print 'Opened file:', file_name
        #img = ni.load_image(file_name)
        img = nifti.NiftiImage(file_name)
        return img, file_name

class Crosshairs(BaseTool):
    event_state = Enum("normal", "mousedown")
    
    def map_data(self, event):
        # Map event coords to data coords.
        x = self.component.x_mapper.map_data(event.x)
        y = self.component.y_mapper.map_data(event.y)
        return x, y

    def normal_left_down(self, event):
        self.event_state = 'mousedown'
        #print 'normal_left_down:', event.x, event.y

        for olay in self.component.overlays:
            # Set initial position of the CursorTool if there is one.
            #print 'olay:', olay
            if hasattr(olay, 'current_position'):
                #print 'current_position!'
                x, y = self.map_data(event)
                olay.current_position = x, y
        event.handled = True

    def mousedown_mouse_move(self, event):
        # XXX this func unnecessary as the CursorTool sets position
        x, y = self.map_data(event)
        #print 'mousedown_mouse_move', x, y

    def mousedown_left_up(self, event):
        #print 'mousedown_left_up'
        self.event_state = "normal"
        event.handled = True

class Voxel(HasTraits):
    x = Int
    y = Int
    z = Int

    #@on_trait_change('x, y, z')
    def _anytrait_changed(self, name, old, new):
        #print 'Voxel changed:', name, old, new
        pass

class SlicePlot(Plot):
    cursor = Instance(BaseCursorTool)
    cursor_pos = DelegatesTo('cursor', prefix='current_position')
    voxel = Instance(Voxel)
    xindex = Int
    yindex = Int

    def __init__(self, data, **kwtraits):
        super(SlicePlot, self).__init__(data, **kwtraits)
        self.voxel = kwtraits.get('voxel') # XXX what to set for default?

    def set_slice(self, name):
        self.renderer = self.img_plot(name, hide_grids=False)[0]
        self.slicename = name
        self.init_cursor()

    def init_cursor(self):
        # Adding a cursor to the axial plot to test cursor
        # functionality in Chaco
        self.cursor = CursorTool(self.renderer, drag_button='left', 
                                 color='blue')
        x, y = self.data.get_data(self.slicename).shape
        self.cursor.current_position = x/2, y/2
        #self.cursor.current_position = self.voxel.x, self.voxel.y
        self.renderer.overlays.append(self.cursor)
        self.renderer.tools.append(Crosshairs(self.renderer))


    @on_trait_change('xindex, yindex')
    def _index_changed(self, name, old, new):
        #print '_index_changed:', name, old, new
        self.cursor.current_position = self.xindex, self.yindex

    def _cursor_pos_changed(self, name, old, new):
        self.xindex, self.yindex = self.cursor_pos
        #print 'cursor_pos (%d, %d)' % (x, y)
        #print 'voxel:', self.voxel.get('x', 'y', 'z')
        #print 'intensity:', self.data[y,x]


class Viewer(HasTraits):
    plot = Instance(GridContainer)
    container = GridContainer(shape=(2,2))

    traits_view = View(
            Item('plot', editor=ComponentEditor(), show_label=False), 
            width=800, height=600,
            resizable=True,
            title = "Image Plot")

    def __init__(self):
        super(Viewer, self).__init__()

        # Load image
        img, filename = load_image()
        if img is None:
            raise IOError('No image to show!')
        # pynifti image
        zdim, ydim, xdim = img.data.shape
        axial = img.data[zdim/2, :, :]
        coronal = img.data[:, ydim/2, :]
        sagittal = img.data[:, :, xdim/2]

        self.voxel = Voxel(x=xdim/2, y=ydim/2, z=zdim/2)

        # Create array data container
        self.plotdata = ArrayPlotData(axial=axial, sagittal=sagittal, 
                                 coronal=coronal)
        axl_plt = SlicePlot(self.plotdata, voxel=self.voxel)
        axl_plt.set_slice('axial')
        axl_plt.sync_trait('xindex', self.voxel, alias='x')
        axl_plt.sync_trait('yindex', self.voxel, alias='y')

        cor_plt = SlicePlot(self.plotdata, voxel=self.voxel)
        cor_plt.set_slice('coronal')
        cor_plt.sync_trait('xindex', self.voxel, alias='x')
        cor_plt.sync_trait('yindex', self.voxel, alias='z')

        sag_plt = SlicePlot(self.plotdata, voxel=self.voxel)
        sag_plt.set_slice('sagittal')
        sag_plt.sync_trait('xindex', self.voxel, alias='y')
        sag_plt.sync_trait('yindex', self.voxel, alias='z')

        # Add our plots to the GridContainer
        self.container.add(axl_plt)
        self.container.add(cor_plt)
        self.container.add(sag_plt)

        self.plot = self.container
        

if __name__ == '__main__':
    viewer = Viewer()
    viewer.configure_traits()
