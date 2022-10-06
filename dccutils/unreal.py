"""
Module that implements the software interface for Unreal mode.
"""
import unreal
import os
import shutil

from .software import SoftwareContext
from .exceptions import (
    CameraNotFound,
    SequenceNotFound,
    MovieAlreadyInProgress,
    ScreenshotAlreadyInProgress,
)

on_finished_callback = unreal.OnRenderMovieStopped()
automation_scheduler = unreal.AutomationScheduler()


class UnrealContext(SoftwareContext):
    def __init__(self):
        super().__init__()
        self.sequence_path = None
        self.take_movie_in_progress = False
        self.take_screenshot_in_progress = False
        self.export_in_progress_screenshot_path = None
        self.export_in_progress_movie_path = None
        self.future_screenshot_path = None
        self.future_movie_path = None

    @staticmethod
    def software_print(data):
        """
        Print to display in the Unreal Editor console.
        """
        unreal.log(data)

    @staticmethod
    def get_dcc_version():
        return unreal.SystemLibrary.get_engine_version()

    @staticmethod
    def get_dcc_name():
        return "Unreal Editor"

    @staticmethod
    def get_current_project_path():
        return os.path.abspath(unreal.Paths.get_project_file_path())

    def push_state(self):
        """
        Save the variables we need to modify.
        """
        self.current_level_sequence = (
            unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
        )
        self.level_viewport_camera_info = (
            unreal.UnrealEditorSubsystem().get_level_viewport_camera_info()
        )

    def pop_state(self):
        """
        Set back the variables we've modified.
        """
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(
            self.current_level_sequence
        )
        unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(
            self.level_viewport_camera_info[0],
            self.level_viewport_camera_info[1],
        )

    def on_render_screenshot_finished(self):
        if os.path.exists(self.export_in_progress_screenshot_path):
            shutil.move(
                self.export_in_progress_screenshot_path,
                self.future_screenshot_path,
            )
            self.export_in_progress_screenshot_path = None
            self.future_screenshot_path = None
            self.take_screenshot_in_progress = False
        else:
            automation_scheduler.add_latent_command(
                self.on_render_screenshot_finished
            )

    def take_render_screenshot(self, output_path, **kwargs):
        """
        Take a screenshot using given renderer.
        Save the image at the given path with the given extension.
        """
        if self.camera is None:
            raise CameraNotFound
        if self.take_screenshot_in_progress:
            raise ScreenshotAlreadyInProgress
        self.take_screenshot_in_progress = True
        filename = os.path.basename(output_path)
        self.export_in_progress_screenshot_path = os.path.join(
            os.path.realpath(unreal.Paths.screen_shot_dir()), filename
        )
        self.future_screenshot_path = output_path
        unreal.LevelEditorSubsystem().pilot_level_actor(self.camera)
        unreal.AutomationLibrary.take_high_res_screenshot(
            1920, 1080, filename, self.camera
        )
        unreal.LevelEditorSubsystem().eject_pilot_level_actor()
        automation_scheduler.add_latent_command(
            self.on_render_screenshot_finished
        )
        return output_path

    def take_viewport_screenshot(self, output_path, **kwargs):
        """
        Save the image at the given path with the given extension.
        take_automation_screenshot
        """
        if self.take_screenshot_in_progress:
            raise ScreenshotAlreadyInProgress
        self.take_screenshot_in_progress = True
        filename = os.path.basename(output_path)
        self.export_in_progress_screenshot_path = os.path.join(
            os.path.realpath(unreal.Paths.screen_shot_dir()), filename
        )
        self.future_screenshot_path = output_path
        unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, filename)
        automation_scheduler.add_latent_command(
            self.on_render_screenshot_finished
        )
        return output_path

    def get_sequences(self, with_path=False):
        """
        Return a list of tuple representing the Unreal sequences.
        Each tuple contains the sequence name and its path.
        """
        asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
        return [
            (str(asset.asset_name), str(asset.object_path))
            if with_path
            else (str(asset.asset_name))
            for asset in asset_reg.get_assets_by_path("/Game/", True)
            if asset.asset_class == "LevelSequence"
        ][::-1]

    def set_sequence(self, sequence):
        """
        Set the sequence.
        Check first if the sequence is well-defined.
        """
        sequence_path = None
        for s in self.get_sequences(with_path=True):
            if sequence in [s[0], s[1]]:
                sequence_path = s[1]
        if sequence_path is None:
            raise SequenceNotFound
        self.sequence_path = sequence_path
        return self.sequence_path

    def on_render_movie_finished(self, success):
        shutil.move(self.export_in_progress_movie_path, self.future_movie_path)
        self.export_in_progress_movie_path = None
        self.future_movie_path = None
        self.take_movie_in_progress = False

    def take_render_animation(self, output_path, extension, **kwargs):
        """
        Render a sequence.
        Save the video at the given path with the given extension.
        """
        if self.sequence_path is None:
            raise SequenceNotFound

        if self.take_movie_in_progress:
            raise MovieAlreadyInProgress
        self.take_movie_in_progress = True
        filename_ext = os.path.basename(output_path)
        filename, _ = os.path.splitext(filename_ext)
        self.export_in_progress_movie_path = os.path.join(
            os.path.realpath(unreal.Paths.video_capture_dir()), filename_ext
        )
        self.future_movie_path = output_path

        sequence_object = unreal.load_asset(self.sequence_path)
        unreal.LevelSequenceEditorBlueprintLibrary.open_level_sequence(
            sequence_object
        )

        capture_settings = unreal.AutomatedLevelSequenceCapture()
        capture_settings.settings.output_format = filename
        capture_settings.settings.overwrite_existing = True
        capture_settings.level_sequence_asset = unreal.SoftObjectPath(
            self.sequence_path
        )
        capture_settings.settings.resolution.res_x = 1920
        capture_settings.settings.resolution.res_y = 1080

        on_finished_callback.bind_callable(self.on_render_movie_finished)

        unreal.SequencerTools.render_movie(
            capture_settings, on_finished_callback
        )

        return output_path

    def take_viewport_animation(self, output_path, extension, **kwargs):
        """
        Take animation of the viewport.
        Save the video at the given path with the given extension.
        """
        pass

    def get_cameras(self, with_objects=False):
        """
        Return a list of tuple representing the Unreal cameras.
        Each tuple contains a camera object and its name.
        """
        return [
            (obj.get_actor_label(), obj)
            if with_objects
            else obj.get_actor_label()
            for obj in unreal.GameplayStatics.get_all_actors_of_class(
                unreal.UnrealEditorSubsystem().get_editor_world(),
                unreal.CameraActor,
            )
        ]

    def set_camera(self, camera, **kwargs):
        """
        Set the camera.
        Check first if the camera is well-defined.
        """
        camera_found = None
        if isinstance(camera, str):
            for c in self.get_cameras(with_objects=True):
                if c[0] == camera:
                    camera_found = c[1]
            camera = camera_found
        elif isinstance(camera, unreal.CameraActor):
            if camera in unreal.GameplayStatics.get_all_actors_of_class(
                unreal.UnrealEditorSubsystem().get_editor_world(),
                unreal.CameraActor,
            ):
                camera_found = camera
        if camera_found is None:
            raise CameraNotFound
        self.camera = camera_found
        return self.camera.get_actor_label()

    def get_current_color_space(self):
        """
        Return the current color space. // NOT WORKING
        """
        return unreal.TextureSourceColorSettings().color_space.name

    def set_current_color_space(self, color_space, **kwargs):
        """
        Set the current color space. // NOT WORKING
        """
        all_color_spaces = dict(
            (cs.name, cs) for cs in unreal.TextureColorSpace
        )
        unreal.TextureSourceColorSettings().color_space = all_color_spaces[
            color_space
        ]

    def get_available_renderers(self):
        """
        Return a list of renderers
        """
        return []

    def get_extensions(self, is_video):
        """
        Return a list of available extensions along with the ID of their
        compression algorithm in Blender.
        """
        return [(".avi", "AVI")] if is_video else [(".png", "PNG")]
