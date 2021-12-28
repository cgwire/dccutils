"""
Module that implements the software interface for Houdini mode.
"""

import hou
import os

from .software import SoftwareContext


class HoudiniContext(SoftwareContext):
    def __init__(self):
        super(HoudiniContext, self).__init__()
        self.renderers = {
            "ifd": {"name": "mantra", "parm_camera": "camera"},
            "opengl": {"name": "opengl", "parm_camera": "camera"},
            "rib": {"name": "renderman", "parm_camera": "camera"},
            "Redshift_ROP": {
                "name": "redshift",
                "parm_camera": "RS_renderCamera",
            },
            "vray_renderer": {"name": "vray", "parm_camera": "render_camera"},
        }

    def push_state(self):
        """
        Save the variables we need to modify.
        """
        pass

    def pop_state(self):
        """
        Set back the variables we've modified.
        """
        pass

    def setup_preview(self, output_path, extension):
        """
        Setup preview context.
        :param output_path: Output path for the preview
        :param extension: Format setting for Blender
        """
        pass

    def setup_preview_animation(self, output_path, extension, container):
        """
        Setup preview context for animations.
        :param output_path: Output path for the preview
        :param extension: Format setting
        :param container: Container.
        :return:
        """
        pass

    def get_viewport_camera(self):
        """
        Return the name of the viewport camera.
        """
        cur_desktop = hou.ui.curDesktop()
        desktop = cur_desktop.name()
        panetab = cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer).name()
        persp = (
            cur_desktop.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().name()
        )
        camera_path = desktop + "." + panetab + "." + "world" "." + persp
        return camera_path

    def take_viewport_screenshot(self, output_path, extension):
        """
        Take a screenshot of the viewport.
        Save the image at the given path with the given extension.
        """
        camera_path = self.get_viewport_camera()
        frame = hou.frame()
        hou.hscript(
            "viewwrite -f %d %d %s '%s'" % (frame, frame, camera_path, output_path)
        )
        self.software_print("Generated screenshot at path " + output_path)

    def take_render_screenshot(
        self, renderer, output_path, extension, use_viewtransform=True
    ):
        """
        Take a screenshot.
        Save the image at the given path with the given extension.
        """
        self.setup_preview(output_path, extension)
        render_node = renderer
        render_node.render(output_file=output_path, output_format=extension)
        self.software_print("Generated screenshot at path " + output_path)

    def take_viewport_animation(self, output_path, container):
        """
        Take an animation.
        Save the video at the given path with the given extension (container).
        """
        pass

    def take_render_animation(
        self, renderer, output_path, container, use_viewtransform=True
    ):
        """
        Take an animation.
        Save the video at the given path with the given extension (container).
        """
        pass

    def list_cameras(self):
        """
        Return a list of tuple representing the Houdini cameras.
        Each tuple contains a camera node and its name.
        """
        cameras = []
        cam_nodes = hou.nodeType(hou.objNodeTypeCategory(), "cam").instances()
        for cam_node in cam_nodes:
            cameras.append((cam_node.name(), cam_node))
        return cameras

    def set_camera(self, camera_node, **kwargs):
        """
        Set camera. The camera settings depends on the renderer used.
        """
        render_node = kwargs["render_node"]
        renderer = self.get_node_render_type(render_node)
        parm_camera = self.renderers[renderer]["parm_camera"]
        render_node.parm(parm_camera).set(camera_node.path())

    def get_current_color_space(self):
        pass

    def set_current_color_space(self, color_space, **kwargs):
        pass

    def get_available_renderers(self):
        """
        Return the available render nodes of the scene.
        """
        render_nodes = []
        root_node = hou.node("/out")
        for node in root_node.allSubChildren():
            if isinstance(node, hou.RopNode):
                render_nodes.append((node.name(), node))
        return render_nodes

    def list_extensions(self, is_video):
        """
        Return a list of available extensions.
        """
        return [] if is_video else [(".png", ".png"), (".jpg", ".jpg")]

    def get_all_nodes(self):
        """
        Get all nodes of the current hip file.
        """
        return hou.node("/").allSubChildren()

    def check_node(self, node):
        """
        Check if a given node is valid.
        """
        return node and node in self.get_all_nodes()

    def get_node_render_type(self, render_node):
        """
        Return type name of the render node.
        """
        return render_node.type().name()
