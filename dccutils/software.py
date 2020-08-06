"""
Module that act as a (loose) interface. Its purpose is to uniform the results
coming from different contexts (Standalone, Blender, Maya, ...).
"""


class SoftwareContext(object):
    def __init__(self):
        self.output_path = None
        self.camera = None
        self.extension = None
        self.color_space = None

    def take_render_screenshot(
        self, renderer, output_path, extension, use_colorspace=True
    ):
        """
        Take a rendered screenshot
        """
        pass

    def take_viewport_screenshot(self, output_path, extension):
        """
        Take a viewport screenshot
        """
        pass

    def take_render_animation(
        self, renderer, output_path, container, use_colorspace=True
    ):
        """
        Take a rendered animation
        """
        pass

    def take_viewport_animation(self, output_path, container):
        """
        Take a viewport animation
        """
        pass

    def push_state(self):
        """
        A function to save the current state (global variables) of the software.
        """
        pass

    def pop_state(self):
        """
        A function to set back the old state (global variables) of the software.
        """
        pass

    def list_extensions(self, is_video):
        """
        Return a list of tuple representing the extensions.
        Each tuple contains an extension object and its name.
        """
        pass

    def get_current_color_space(self, **kwargs):
        """
        Return the current color space.
        """
        pass

    def set_current_color_space(self, color_space, **kwargs):
        """
        Set the current color space.
        """
        pass

    def set_camera(self, camera, **kwargs):
        pass

    def list_cameras(self):
        """
        Return a list of tuple representing the cameras.
        Each tuple contains a camera object and its name.
        """
        pass

    def get_available_renderers(self):
        """
        Return a list of renderers or of render nodes, depending on the context.
        """
        pass

    @staticmethod
    def software_print(data):
        pass
