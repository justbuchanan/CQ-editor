import cadquery as cq
import cqparts
import car

def show_cqparts_obj(cqobj):
    cqobj.build(recursive=True)
    def _show_recursive(cqobj, prefix=''):
        if isinstance(cqobj, cqparts.Part):
            # cq-editor detects cadquery objects in the global namespace
            shape = cqobj.world_obj
            shape._color = cqobj._render.color
            globals()[prefix] = shape
        elif isinstance(cqobj, cqparts.Assembly):
            if prefix: prefix = prefix + "_"
            for name, subobj in cqobj.components.items():
                _show_recursive(subobj, prefix + name)
    _show_recursive(cqobj)


show_cqparts_obj(car.Car())
