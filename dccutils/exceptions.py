class CameraNotFound(Exception):
    """
    Error raised when camera is not found.
    """

    pass


class SequenceNotFound(Exception):
    """
    Error raised when sequence is not found.
    """

    pass


class ScreenshotAlreadyInProgress(Exception):
    """
    Error raised when an other screenshot is already in progress.
    """

    pass


class MovieAlreadyInProgress(Exception):
    """
    Error raised when an other movie is already in progress.
    """

    pass
