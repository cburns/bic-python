
from numpy import linspace, sin
from enthought.chaco.api import ArrayPlotData, Plot, gray, GridContainer
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, View

# File IO imports
from enthought.traits.api import File, Button
from enthought.traits.ui.api import HGroup
from enthought.traits.ui.file_dialog import open_file

# Nipy stuff
import nipy as ni

def load_image():
    file_name = File
    file_name = open_file()
    if file_name != '':
        print 'Opened file:', file_name
        img = ni.load_image(file_name)
        return img, file_name
    

class ImagePlot(HasTraits):

    plot = Instance(GridContainer)
    container = GridContainer(shape=(2,2))

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
        zdim, ydim, xdim = img.shape
        image = img._data[:, :, xdim/2]
        axial = img._data[:, :, xdim/2]
        sagittal = img._data[:, ydim/2, :]
        coronal = img._data[zdim/2, :, :]

        #plotdata = ArrayPlotData(image=image)
        plotdata = ArrayPlotData(axial=axial, sagittal=sagittal, coronal=coronal)
        # Create a Plot and associate it with the PlotData
        axl_plt = Plot(plotdata)
        axl_plt.img_plot('axial', colormap=gray)
        sag_plt = Plot(plotdata)
        sag_plt.img_plot('sagittal', colormap=gray)
        cor_plt = Plot(plotdata)
        cor_plt.img_plot('coronal', colormap=gray)
        # Set the title
        #plot.title = filename

        self.container.add(axl_plt)
        self.container.add(sag_plt)
        self.container.add(cor_plt)

        #[axl_plt, sag_plt, cor_plt])
        #container = GridPlotContainer(axl_plt, sag_plt, cor_plt)
        # Assign it to our self.plot attribute
        self.plot = self.container


if __name__ == "__main__":
    ImagePlot().configure_traits()

