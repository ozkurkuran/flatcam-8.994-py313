import numpy as np
import pytest
import ezdxf
from shapely.geometry import Polygon, MultiPolygon, MultiLineString, LineString
from svg.path import parse_path

from appCommon.geometry import geometry_parts
from appParsers.ParseSVG import path2shapely
from appParsers.ParseDXF import getdxfgeo
from descartes.patch import PolygonPath


def test_multipart_iteration_preserves_components():
    parts = [Polygon([(0, 0), (1, 0), (1, 1)]), Polygon([(3, 0), (4, 0), (4, 1)])]
    assert list(geometry_parts(MultiPolygon(parts))) == parts
    assert geometry_parts(parts) is parts
    assert geometry_parts(parts[0]) is parts[0]


def test_flatten_nested_multipart_geometry():
    from camlib import Geometry
    geometry = Geometry.__new__(Geometry)
    lines = [LineString([(0, 0), (1, 1)]), LineString([(2, 2), (3, 3)])]
    assert geometry.flatten([MultiLineString(lines)], pathonly=True) == lines


def test_svg_preserves_open_subpaths_and_scale():
    result = path2shapely(parse_path('M1,2 L3,4 M10,20 L30,40'), 'geometry', factor=2)
    assert len(result) == 2
    assert list(result[0].coords) == [(2, 4), (6, 8)]
    assert list(result[1].coords) == [(20, 40), (60, 80)]


def test_svg_preserves_holes_and_disconnected_contours():
    path = parse_path('M0,0 L10,0 L10,10 L0,10 Z M2,2 L4,2 L4,4 L2,4 Z M20,0 L22,0 L22,2 L20,2 Z')
    result = path2shapely(path, 'geometry')
    assert sorted(p.area for p in result) == [4, 96]
    assert sum(len(p.interiors) for p in result) == 1


def test_matplotlib_polygon_patch_and_empty_geometry():
    polygon = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)], [[(2, 2), (4, 2), (4, 4), (2, 4)]])
    path = PolygonPath(polygon)
    assert path.vertices.shape == (10, 2)
    assert np.isfinite(path.vertices).all()
    assert PolygonPath(Polygon()).vertices.shape == (0, 2)


def test_current_ezdxf_import():
    drawing = ezdxf.new()
    drawing.modelspace().add_line((1, 2), (3, 4))
    shapes = getdxfgeo(drawing)
    assert len(shapes) == 1
    assert list(shapes[0].coords) == [(1, 2), (3, 4)]


def test_qt6_double_slider_and_text_editor(qtbot):
    from appGUI.GUIElements import FCSliderWithDoubleSpinner, FCTextAreaExtended
    widget = FCSliderWithDoubleSpinner(min=0, max=10.5, step=0.1)
    qtbot.addWidget(widget)
    widget.slider.set_value(1.25)
    assert widget.slider.value() == pytest.approx(1.25)
    assert widget.spinner.value() == pytest.approx(1.25)
    editor = FCTextAreaExtended()
    qtbot.addWidget(editor)
    editor.setPlainText('G00 X0 Y0\nG01 X10 Y10')
    editor.show()
    assert editor.toPlainText().startswith('G00')


def test_cli_arguments_are_explicit():
    from app_Main import App
    App.configure_command_line(['--headless=1', '--shellfile=example.tcl'])
    assert App.cmd_line_headless == 1
    assert App.cmd_line_shellfile == 'example.tcl'
    App.cmd_line_headless = None
    App.cmd_line_shellfile = ''
