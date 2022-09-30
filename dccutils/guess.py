from .software import SoftwareContext

GuessedContext = SoftwareContext

try:
    from .blender import BlenderContext

    GuessedContext = BlenderContext
except:
    try:
        from .houdini import HoudiniContext

        GuessedContext = HoudiniContext
    except:
        try:
            from .maya import MayaContext

            GuessedContext = MayaContext
        except:
            try:
                from .unreal import UnrealContext

                GuessedContext = UnrealContext
            except:
                pass
