"""
Module that implements the software interface for Blender mode.
"""
import bpy

from .software import SoftwareContext
from .exceptions import CameraNotFound


class BlenderContext(SoftwareContext):
    @staticmethod
    def software_print(data):
        """
        Print to display in the Blender console.
        """
        for window in bpy.context.window_manager.windows:
            screen = window.screen
            for area in screen.areas:
                if area.type == "CONSOLE":
                    override = {
                        "window": window,
                        "screen": screen,
                        "area": area,
                    }
                    for line in str(data).split("\n"):
                        bpy.ops.console.scrollback_append(
                            override, text=str(line), type="OUTPUT"
                        )

    @staticmethod
    def get_dcc_version():
        return ".".join(str(v) for v in bpy.app.version)

    @staticmethod
    def get_dcc_name():
        return "Blender"

    @staticmethod
    def get_current_project_path():
        return bpy.data.filepath

    def push_state(self):
        """
        Save the variables we need to modify.
        """
        scene = self.get_current_scene()
        self.saved_extension = scene.render.image_settings.file_format
        self.saved_output_path = scene.render.filepath
        self.saved_codec = scene.render.ffmpeg.codec
        self.saved_format = scene.render.ffmpeg.format
        self.saved_camera = scene.camera
        self.saved_color_space = scene.sequencer_colorspace_settings.name
        self.renderer = scene.render.engine

    def pop_state(self):
        """
        Set back the variables we've modified.
        """
        scene = self.get_current_scene()
        scene.render.image_settings.file_format = self.saved_extension
        scene.render.filepath = self.saved_output_path
        scene.render.ffmpeg.codec = self.saved_codec
        scene.render.ffmpeg.format = self.saved_format
        scene.render.engine = self.renderer
        scene.camera = self.saved_camera
        scene.sequencer_colorspace_settings.name = self.saved_color_space

    def setup_preview(self, output_path, extension):
        """
        Setup preview context.
        :param output_path: Output path for the preview
        :param extension: Format setting for Blender
        """
        bpy.context.scene.render.image_settings.file_format = extension
        bpy.context.scene.render.filepath = output_path

    def setup_render(self, renderer):
        """
        Setup render.
        :param renderer: Id of the renderer in Blender
        """
        bpy.context.scene.render.engine = renderer

    def setup_colorspace_settings(self, use_colorspace):
        if use_colorspace:
            colorspace = self.get_current_color_space()
        else:  # to change to use custom colorspace
            for enum_colorspace in (
                type(bpy.context.scene.sequencer_colorspace_settings)
                .bl_rna.properties["name"]
                .enum_items
            ):
                if "sRGB".lower() in enum_colorspace.name.lower():
                    colorspace = enum_colorspace.name
        self.set_current_color_space(colorspace)

    def setup_preview_animation(self, output_path, extension, container):
        """
        Setup preview context for animations.
        The codec is set at H.264.
        :param output_path: Output path for the preview
        :param extension: Format setting for Blender
        :param container: Container.
        """
        self.setup_preview(output_path, extension)
        bpy.context.scene.render.ffmpeg.codec = "H264"
        bpy.context.scene.render.ffmpeg.format = container

    def take_render_screenshot(
        self, renderer, output_path, extension, use_colorspace=True, **kwargs
    ):
        """
        Take a screenshot using given renderer.
        Save the image at the given path with the given extension.
        """
        self.setup_render(renderer)
        self.setup_preview(output_path, extension)
        self.setup_colorspace_settings(use_colorspace)
        bpy.ops.render.render(write_still=True)
        return output_path

    def take_viewport_screenshot(self, output_path, extension, **kwargs):
        """
        Take a screenshot using OpenGL.
        Save the image at the given path with the given extension.
        """
        self.setup_preview(output_path, extension)
        if self.get_blender_version() < (2, 80, 0):
            bpy.ops.render.opengl(write_still=True)
        else:
            bpy.context.scene.view_settings.view_transform = "Standard"
            bpy.ops.render.opengl(write_still=True)
        return output_path

    def take_render_animation(
        self, renderer, output_path, extension, use_colorspace=True, **kwargs
    ):
        """
        Take an animation using given renderer.
        Save the video at the given path with the given extension (container).
        """
        self.setup_render(renderer)
        self.setup_preview_animation(output_path, "FFMPEG", extension)
        self.setup_colorspace_settings(use_colorspace)
        bpy.ops.render.render(animation=True, write_still=True)
        return output_path

    def take_viewport_animation(self, output_path, extension, **kwargs):
        """
        Take an animation using OpenGL.
        Save the video at the given path with the given extension (container).
        """
        self.setup_preview_animation(output_path, "FFMPEG", extension)
        if self.get_blender_version() < (2, 80, 0):
            bpy.ops.render.opengl(animation=True, write_still=True)
        else:
            bpy.context.scene.view_settings.view_transform = "Standard"
            bpy.ops.render.opengl(animation=True, write_still=True)
        return output_path

    def get_cameras(self, with_objects=False):
        """
        Return a list of tuple representing the Blender cameras.
        Each tuple contains a camera object and its name.
        """
        return [
            (obj.name, obj) if with_objects else obj.name
            for obj in bpy.data.objects
            if obj.type == "CAMERA"
        ]

    def set_camera(self, camera, **kwargs):
        """
        Set the rendering camera.
        Check first if the camera is well-defined.
        """
        camera_found = None
        if isinstance(camera, str):
            camera_found = bpy.data.objects.get(camera)
        elif isinstance(camera, bpy.types.Object):
            if camera in bpy.data.objects.values():
                camera_found = camera
        if camera_found is None or camera_found.type != "CAMERA":
            raise CameraNotFound
        self.camera = camera_found
        bpy.context.scene.camera = self.camera
        return self.camera

    def get_current_scene(self):
        return bpy.context.scene

    def get_current_color_space(self):
        """
        Return the current color space.
        """
        scene = self.get_current_scene()
        return scene.sequencer_colorspace_settings.name

    def set_current_color_space(self, color_space, **kwargs):
        """
        Set the current color space.
        """
        scene = self.get_current_scene()
        scene.sequencer_colorspace_settings.name = color_space

    def get_available_renderers(self):
        """
        Return a list of ids of available renderers.
        For now there is no function from the Blender API to retrieve all the
        renderers, which leads to some workaround.
        """
        # Get all the render registered as subclasses of RenderEngine class.
        # This does not include the internal renderers of Blender, only those
        # registered with Python add-ons (by the user or Blender directly)
        renderers = bpy.types.RenderEngine.__subclasses__()
        external_renderer_ids = [(r.bl_label, r.bl_idname) for r in renderers]

        # Get the internal renderers
        rna_type = type(bpy.context.scene.render)
        prop_str = "engine"
        prop = rna_type.bl_rna.properties[prop_str]
        internal_renderer_ids = [
            (e.name, e.identifier) for e in prop.enum_items
        ]

        # For some reason this last procedure didn't include Blender_workbench
        # So we add it manually.
        internal_renderer_ids.append(("Workbench", "BLENDER_WORKBENCH"))

        return (external_renderer_ids + internal_renderer_ids)[::-1]

    def get_extensions(self, is_video):
        """
        Return a list of available extensions along with the ID of their
        compression algorithm in Blender.
        """
        return (
            [(".mp4", "MPEG4"), (".mov", "QUICKTIME")]
            if is_video
            else [(".png", "PNG"), (".jpg", "JPEG")]
        )
