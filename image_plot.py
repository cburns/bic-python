
from numpy import linspace, sin
from enthought.chaco.api import ArrayPlotData, Plot, gray, GridContainer, \
    OverlayPlotContainer, GridDataSource
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance, DelegatesTo, \
    on_trait_change, Enum
from enthought.traits.ui.api import Item, View
from enthought.chaco.tools.cursor_tool import CursorTool, BaseCursorTool
from enthought.enable.api import BaseTool
from enthought.chaco.tools.api import LineInspector


# File IO imports
from enthought.traits.api import File, Button
from enthought.traits.ui.api import HGroup
from enthought.traits.ui.file_dialog import open_file


from enthought.chaco.api import AbstractController  
class EventPrinter(AbstractController):
    def dispatch(self, event, suffix): 
        # We are assuming that self.component is an X-Y plot  
        x = self.component.x_mapper.map_data(event.x)  
        y = self.component.y_mapper.map_data(event.y)
        if suffix is 'left_down':
            print 'Data coord (%d, %d)' % (x, y)
        # event' is a MouseEvent or KeyEvent object from the enable2  
        # package, and suffix is a text string  
        #print suffix, "event received at (%d,%d)" % (event.x, event.y)  
  
# Nipy stuff
import nipy as ni

def load_image():
    file_name = File
    file_name = open_file()
    if file_name != '':
        print 'Opened file:', file_name
        #img = ni.load_image(file_name)
        import nifti
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



class ImagePlot(HasTraits):

    plot = Instance(GridContainer)
    container = GridContainer(shape=(2,2))
    
    cursor = Instance(BaseCursorTool)
    cursor_pos = DelegatesTo('cursor', prefix='current_position')

    traits_view = View(
            Item('plot', editor=ComponentEditor(), show_label=False), 
            width=500, height=500,
            resizable=True,
            title = "Image Plot")

    def __init__(self):
        super(ImagePlot, self).__init__()

        # Load image
        img, filename = load_image()
        if img is None:
            raise IOError('No image to show!')

        # pynifti image
        zdim, ydim, xdim = img.data.shape
        axial = img.data[zdim/2, :, :]
        coronal = img.data[:, ydim/2, :]
        sagittal = img.data[:, :, xdim/2]
        """
        # nipy image
        xdim, ydim, zdim = img.shape
        axial = img._data[:, :, zdim/2]
        coronal = img._data[:, ydim/2, :]
        sagittal = img._data[xdim/2, :, :]
        """
        # Create array data container
        self.plotdata = ArrayPlotData(axial=axial, sagittal=sagittal, 
                                 coronal=coronal)

        """
        self.plotdata = GridDataSource(axial=axial, sagittal=sagittal, 
                                 coronal=coronal)
                                 """
        # Create a Plot and associate it with the PlotData
        axl_plt = Plot(self.plotdata)
        axl_img = axl_plt.img_plot('axial', colormap=gray)
        axl_img = axl_img[0] # img_plot returns a list

        sag_plt = Plot(self.plotdata)
        sag_img = sag_plt.img_plot('sagittal', colormap=gray)[0]
        
        # Crosshairs
        #sag_imgplt.tools.append(Crosshairs(sag_imgplt))

        cor_plt = Plot(self.plotdata)
        cor_img = cor_plt.img_plot('coronal', colormap=gray)[0]

        # Connect plots
        #sag_img.index = axl_img.value

        """
        overlays = self.cor_imgplt.overlays
        overlays.append(LineInspector(self.cor_imgplt, 
                                      axis='value',
                                      write_metadata=True,
                                      metadata_name='mouse',
                                      color='red', width=2.0))
        overlays.append(LineInspector(self.cor_imgplt, axis='index',
                                      write_metadata=True,
                                      metadata_name='mouse',
                                      color='red', width=2.0))

        self.cor_imgplt.tools.append(EventPrinter(self.cor_imgplt))
        """

        # Set the title
        #plot.title = filename

        self.container.add(axl_plt)
        self.container.add(sag_plt)
        self.container.add(cor_plt)
        """
        self.container.add(axl_img)
        self.container.add(sag_img)
        self.container.add(cor_img)
        """
        # Adding a cursor to the axial plot to test cursor
        # functionality in Chaco
        self.cursor = CursorTool(axl_img, drag_button='left', color='blue')
        self.cursor.current_position = zdim/2, ydim/2
        axl_img.overlays.append(self.cursor)
        axl_img.tools.append(Crosshairs(axl_img))

        # Assign it to our self.plot attribute
        self.plot = self.container


    """
    @on_trait_change('cursor.current_position')
    def cursor_func(self, name, old, new):
        print 'cursor_func:', name
        x, y = self.cursor_pos
        print 'cursor_pos (%.2f, %.2f)', x, y 
        print 'intesity:', self.axial[int(x), int(y)]
    """

    def _cursor_pos_changed(self, name, old, new):
        print '_cursor_pos_changed:', name
        x, y = self.cursor_pos
        print 'cursor_pos (%d, %d)' % (x, y)
        arr = self.plotdata['axial']
        print 'intesity:', arr[y,x]

if __name__ == "__main__":
    ImagePlot().configure_traits()

