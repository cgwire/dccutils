"""
Module that implements the software interface for Maya mode.
NOT WORKING YET, WIP !
"""

import maya.cmds as cmds
import maya.mel as mel

from .software import SoftwareContext


class MayaContext(SoftwareContext):
    def list_cameras(self):
        """
        Return a list of tuple representing the Maya cameras.
        Each tuple contains a camera name and its shape name.
        """
        res = []
        camera_names = cmds.listCameras()
        for camera_name in camera_names:
            camera_shape = cmds.listRelatives(
                camera_name, type="camera", s=True
            )[0]
            res.append((camera_name, camera_shape))
        return res

    def set_camera(self, camera_shape):
        """
        Set the rendering camera.
        Check first if the camera is well-defined.
        Then set the camera as renderable, and all the others as non renderable
        """
        all_camera_shapes = cmds.ls(type="camera")
        assert camera_shape in all_camera_shapes
        for shape in all_camera_shapes:
            cmds.setAttr(shape + ".renderable", shape == camera_shape)

    def take_viewport_screenshot(self, output_path, extension):
        """
        Take a screenshot of the current view.
        """
        file_extension, _ = extension
        cmds.refresh(cv=True, fe=file_extension, fn=output_path)

    def take_render_screenshot(
        self, output_path, extension, use_view_transform=True, **kwargs
    ):
        """
        Take a render.
        """
        _, id_ext = extension
        self.set_current_id_extension(id_ext)
        cmds.setAttr(
            "defaultRenderGlobals.imageFilePrefix", output_path, type="string"
        )
        cmds.setAttr("defaultRenderGlobals.imageFormat", id_ext)
        renderer = kwargs["renderer"]
        command = cmds.renderer(renderer, query=True, renderProcedure=True)
        camera = kwargs["camera"]
        layer = "-layer defaultRenderLayer "
        if self.is_color_management_available(renderer):
            self.activate_color_management(use_view_transform)

        if renderer == "mayaSoftware":
            command = "render"
            tmp_output_path = mel.eval(command + layer + camera)
            cmds.sysFile(tmp_output_path, rename=output_path)
            pass
        elif renderer == "mayaHardware2":
            pass
        elif renderer == "arnold":
            pass

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

    def get_render_procedure(self):
        """
        Return the procedure called by each renderer to launch its render.
        """
        renderer = self.get_current_renderer()
        cmds.renderer(query=True, renderProcedure=renderer)

    def get_current_id_extension(self):
        """
        Return the id associated to the output format
        """
        return cmds.getAttr("defaultRenderGlobals.imageFormat")

    def set_current_id_extension(self, id_extension):
        cmds.setAttr("defaultRenderGlobals.imageFormat", int(id_extension))

    def get_available_renderers(self):
        """
        Return a list of available renderers.
        """
        return cmds.renderer(query=True, namesOfAvailableRenderers=True)

    def get_current_renderer(self):
        return cmds.getAttr("defaultRenderGlobals.currentRenderer")

    def set_current_renderer(self, renderer):
        cmds.setAttr(
            "defaultRenderGlobals.currentRenderer", renderer, type="string"
        )

    def is_color_management_available(self, renderer):
        """
        Return if given renderer supports color management.
        For more info see **[Maya docs](https://knowledge.autodesk.com/support/maya/learn-explore/caas/CloudHelp/cloudhelp/2019/ENU/Maya-Rendering/files/GUID-4ABC6724-9DB0-45D5-AAF2-5C2FF135247D-htm.html) **
        """
        return renderer in ["mayaHardware2", "arnold"]

    def list_extensions(self, is_video):
        """
        Return a list of available extensions along with the IDs of their compression
        algorithm in Maya.
        """
        return (
            [(".mov", 22)]
            if is_video
            else [(".png", ("png", 32)), (".jpg", ("jpg", 8))]
        )

    def get_current_color_space(self):
        return cmds.colorManagementPrefs(q=True, viewTransformName=True)

    def set_current_color_space(self):
        color_space = self.get_current_color_space()
        if color_space:
            cmds.colorManagementPrefs(e=True, viewTransformName=color_space)
        else:
            cmds.colorManagementPrefs(e=True, viewTransformName="sRGB gamma")

    def activate_color_management(self, enabled):
        cmds.colorManagementPrefs(edit=True, cmEnabled=enabled)
        if enabled:
            self.set_current_color_space()
