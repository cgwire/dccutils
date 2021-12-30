"""
Module that implements the software interface for Maya mode.
"""

import os
import subprocess
import maya.cmds as cmds
import maya.mel as mel

from .software import SoftwareContext

from gazupublisher.exceptions import RenderNotSupported


class MayaContext(SoftwareContext):
    def push_state(self):
        # Save renderable cameras
        self.cameras = []
        for cam_shape in cmds.ls(type="camera"):
            is_cam_renderable = cmds.getAttr(cam_shape + ".renderable")
            self.cameras.append((cam_shape, is_cam_renderable))

    def pop_state(self):
        for cam_shape, is_cam_renderable in self.cameras:
            cmds.setAttr(cam_shape + ".renderable", is_cam_renderable)

    def take_viewport_screenshot(self, output_path, extension):
        """
        Take a screenshot of the current view.
        """
        file_extension, _ = extension
        cmds.refresh(cv=True, fe=file_extension, fn=output_path)

    def take_render_screenshot(
        self, renderer, output_path, extension, use_view_transform=True
    ):
        """
        Take a render.
        """
        string_ext, id_ext = extension
        self.set_current_id_extension(int(id_ext))
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", output_path, type="string")
        camera = self.get_camera()
        layer = "-layer defaultRenderLayer "
        if self.is_color_management_available(renderer):
            self.activate_color_management(use_view_transform)

        if renderer == "mayaSoftware":
            command = "render"
            tmp_output_path = mel.eval(command + layer + camera)
            cmds.sysFile(tmp_output_path, rename=output_path)

        elif renderer == "arnold":
            from mtoa.cmds.arnoldRender import arnoldRender

            string_ext = "jpeg" if string_ext == "jpg" else string_ext
            cmds.setAttr("defaultArnoldDriver.ai_translator", string_ext, type="string")
            path_without_extension = os.path.splitext(output_path)[0]
            cmds.setAttr(
                "defaultArnoldDriver.pre", path_without_extension, type="string"
            )
            arnoldRender(1920, 1080, True, True, camera, layer)

        elif renderer == "your_favourite_renderer":
            # Launch the render...
            pass
        else:
            raise RenderNotSupported(
                "The %s renderer is currently not supported. "
                "But you can still adapt the code to make the render accessible. "
                "You might want to look at the file %s" % (renderer, __file__)
            )

    def take_viewport_animation(self, output_path, extension):
        """
        Take a playblast of the current view.
        """
        cmds.playblast(
            filename=output_path,
            forceOverwrite=True,
            quality=100,
            percent=100,
            viewer=False,
            format="qt",
        )

    def take_render_animation(
        self, renderer, output_path, extension, use_view_transform=True
    ):
        """
        Take a render animation.
        """
        camera = self.get_camera()
        if self.is_color_management_available(renderer):
            self.activate_color_management(use_view_transform)

        command = os.path.join(os.environ["MAYA_LOCATION"], "bin", "Render")
        dirname = os.path.dirname(output_path)
        basename = os.path.basename(output_path)
        filename, ext = os.path.splitext(basename)
        current_file = self.get_current_file_path()
        output_format = "qt" if ext == ".mov" else None

        if renderer == "mayaSoftware":
            renderer_id = "sw"
            self.launch_render(
                command,
                renderer_id,
                dirname,
                filename,
                output_format,
                camera,
                current_file,
            )

        elif renderer == "mayaHardware2":
            renderer_id = "hw2"
            self.launch_render(
                command,
                renderer_id,
                dirname,
                filename,
                output_format,
                camera,
                current_file,
            )

        elif renderer == "arnold":
            raise RenderNotSupported(
                "Arnold can't render videos, only image "
                "sequences. Please select another renderer"
            )

        elif renderer == "your_favourite_renderer":
            # Launch the render...
            pass
        else:
            raise RenderNotSupported(
                "The %s renderer is currently not supported. "
                "But maybe you can still adapt the code to make the render accessible. "
                "You might want to look at the file %s" % (renderer, __file__)
            )

    def launch_render(
        self,
        command,
        renderer_id,
        dirname,
        filename,
        output_format,
        camera,
        current_file,
    ):
        command_list = [
            command,
            "-r",
            renderer_id,
            "-rd",
            dirname,
            "-im",
            filename,
            "-of",
            output_format,
            "-cam",
            camera,
            current_file,
        ]
        subprocess.call(command_list)

    def list_cameras(self):
        """
        Return a list of tuple representing the Maya cameras.
        Each tuple contains a camera name and its shape name.
        """
        res = []
        camera_names = cmds.listCameras()
        for camera_name in camera_names:
            camera_shape = cmds.listRelatives(camera_name, type="camera", s=True)[0]
            res.append((camera_name, camera_shape))
        return res

    def set_camera(self, camera_shape, **kwargs):
        """
        Set the rendering camera.
        Check first if the camera is well-defined.
        Then set the camera as renderable, and all the others as non renderable
        """
        all_camera_shapes = cmds.ls(type="camera")
        assert camera_shape in all_camera_shapes
        for shape in all_camera_shapes:
            cmds.setAttr(shape + ".renderable", shape == camera_shape)

    def get_camera(self):
        """
        Get the rendering cameras.
        """
        all_camera_shapes = cmds.ls(type="camera")
        for shape in all_camera_shapes:
            if cmds.getAttr(shape + ".renderable"):
                return shape
        return None

    def set_current_id_extension(self, id_extension):
        cmds.setAttr("defaultRenderGlobals.imageFormat", id_extension)

    def get_available_renderers(self):
        """
        Return a list of available renderers.
        """
        res = []
        renderers = cmds.renderer(query=True, namesOfAvailableRenderers=True)
        for renderer in renderers:
            renderer_ui_name = cmds.renderer(renderer, query=True, rendererUIName=True)
            res.append((renderer_ui_name, renderer))
        return res

    def get_current_color_space(self):
        return cmds.colorManagementPrefs(q=True, viewTransformName=True)

    def set_current_color_space(self, **kwargs):
        color_space = self.get_current_color_space()
        if color_space:
            cmds.colorManagementPrefs(e=True, viewTransformName=color_space)
        else:
            cmds.colorManagementPrefs(e=True, viewTransformName="sRGB gamma")

    def get_current_file_path(self):
        return cmds.file(q=True, sn=True)

    def is_color_management_available(self, renderer):
        """
        Return if given renderer supports color management.
        For more info see **[Maya docs](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/Maya-Rendering/files/GUID-4ABC6724-9DB0-45D5-AAF2-5C2FF135247D-htm.html) **
        """
        return renderer in ["mayaHardware2", "arnold"]

    def activate_color_management(self, enabled):
        cmds.colorManagementPrefs(edit=True, cmEnabled=enabled)
        if enabled:
            self.set_current_color_space()

    def list_extensions(self, is_video):
        """
        Return a list of available extensions along with the IDs of their compression
        algorithm in Maya.
        """
        return (
            [(".mov", ("mov", 22))]
            if is_video
            else [(".png", ("png", 32)), (".jpg", ("jpg", 8))]
        )
