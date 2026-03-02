from fx import *
from tools.selection import outputAndTarget
from tools.renderer import Renderer
from tools.solo import SoloState
from tools.string import to_filename
import os

# ===============================================
# Solo Layer Renderer
# Menu: Tools → Solo Layers
# ===============================================

class LayerFileTreeRenderer(Renderer):
    def __init__(self, node):
        # Only main/top-level visible layers
        self.objects = [l for l in node.children if isinstance(l, Layer) and l.visible]
        self.folder = None

    # Return sub-folder based on layer label
    def getSubFolder(self, layer):
        return to_filename(layer.label)

    # Override buildPath to append sub-folders
    def buildPath(self, output, frame):
        path = Renderer.buildPath(self, output, frame)
        if self.folder:
            folder, filename = os.path.split(path)
            folder = os.path.join(folder, self.folder)
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = os.path.join(folder, filename)
        return path

    # Render each layer solo
    def renderFrame(self, frame):
        for layer in self.objects:
            self.folder = self.getSubFolder(layer)

            # Override suffix for output
            for output in self.outputs:
                output.suffix = '_' + to_filename(layer.label)

            state = SoloState(layer)
            state.solo()
            result = Renderer.renderFrame(self, frame)
            state.restore()

            if not result:
                print(f"Rendering stopped at layer: {layer.label}")
                return False
        return True

class RenderLayersToFileTree(Action):
    """Renders all main visible Layers in the target Roto Node, each to its own file, organized by layer name."""

    def __init__(self):
        # Menu path: Tools → Solo Layers
        Action.__init__(self, "Tools|Solo Layers", features="render")

    def available(self):
        try:
            output, roto = outputAndTarget()
        except AssertionError:
            return False
        layers = [l for l in roto.children if isinstance(l, Layer) and l.visible]
        return len(layers) > 0

    def execute(self):
        try:
            output, roto = outputAndTarget()
        except AssertionError as e:
            print(f"❌ {e}")
            return

        session = activeSession()
        progress = PreviewProgressHandler()
        progress.preview = True
        progress.pixelAspect = session.pixelAspect
        options = {"session": session, "progress": progress}

        r = LayerFileTreeRenderer(roto)
        r.render(options, nodes=[output])

# Add action to Silhouette menu
addAction(RenderLayersToFileTree())

# ===============================================
# Footer / Author Info
# Created by: Karthick Annadurai
# Email: a.karthickvag@gmail.com
# Created / Published: 24.09.2025
# ===============================================
