# ##########################################################
# FlatCAM: 2D Post-processing for Manufacturing            #
# http://flatcam.org                                       #
# Author: Juan Pablo Caram (c)                             #
# Date: 12/18/2015                                         #
# MIT Licence                                              #
#                                                          #
# SVG Features supported:                                  #
#  * Groups                                                #
#  * Rectangles (w/ rounded corners)                       #
#  * Circles                                               #
#  * Ellipses                                              #
#  * Polygons                                              #
#  * Polylines                                             #
#  * Lines                                                 #
#  * Paths                                                 #
#  * All transformations                                   #
#                                                          #
#  Reference: www.w3.org/TR/SVG/Overview.html              #
# ##########################################################

# import xml.etree.ElementTree as ET
from appCommon.geometry import geometry_parts
from svg.path import Line, Arc, CubicBezier, QuadraticBezier, parse_path
# from svg.path.path import Move
# from svg.path.path import Close
import svg.path
from shapely.geometry import LineString, MultiLineString, Point
from shapely.affinity import skew, affine_transform, rotate
import numpy as np

from appParsers.ParseFont import *

log = logging.getLogger('base2')


def svgparselength(lengthstr):
    """
    Parse an SVG length string into a float and a units
    string, if any.

    :param lengthstr:   SVG length string.
    :return:            Number and units pair.
    :rtype:             tuple(float, str|None)
    """

    integer_re_str = r'[+-]?[0-9]+'
    number_re_str = r'(?:[+-]?[0-9]*\.[0-9]+(?:[Ee]' + integer_re_str + ')?' + r')|' + \
                    r'(?:' + integer_re_str + r'(?:[Ee]' + integer_re_str + r')?)'
    length_re_str = r'(' + number_re_str + r')(em|ex|px|in|cm|mm|pt|pc|%)?'

    if lengthstr:
        match = re.search(length_re_str, lengthstr)
        if match:
            return float(match.group(1)), match.group(2)
    else:
        return 0, 0

    return


def svgparse_viewbox(root):
    val = root.get('viewBox')
    if val is None:
        return 1.0

    res = [float(x) for x in val.split()] or [float(x) for x in val.split(',')]
    w = svgparselength(root.get('width'))[0]
    # h = svgparselength(root.get('height'))[0]

    v_w = res[2]
    # v_h = res[3]

    return w / v_w


def path2shapely(path, object_type, res=1.0, units='MM', factor=1.0):
    """
    Converts an svg.path.Path into a Shapely
    Polygon or LinearString.

    :param path:        svg.path.Path instance
    :param object_type:
    :param res:         Resolution (minimum step along path)
    :param units:       FlatCAM units
    :type units:        str
    :param factor:      correction factor due of virtual units
    :type factor:       float
    :return:            Shapely geometry object
    :rtype :            Polygon
    :rtype :            LineString
    """

    points = []
    closed_rings = []
    geometry = []

    def finish(closed=False):
        nonlocal points
        if len(points) >= 2:
            if closed or (len(points) > 2 and points[0] == points[-1]):
                if points[0] != points[-1]:
                    points.append(points[0])
                if len(points) >= 4:
                    closed_rings.append(Polygon(points))
            else:
                geometry.append(LineString(points))
        points = []

    for component in path:
        if isinstance(component, svg.path.Move):
            finish()
            points = [(factor * component.end.real, factor * component.end.imag)]
        elif isinstance(component, svg.path.Close):
            finish(closed=True)
        elif isinstance(component, (Line, Arc, CubicBezier, QuadraticBezier)):
            if not points:
                points.append((factor * component.start.real, factor * component.start.imag))
            steps = 1 if isinstance(component, Line) else max(
                10, int(component.length(res / 10.0)) * 2 * (25 if units == 'IN' else 1))
            for i in range(1, steps + 1):
                point = component.point(i / steps)
                xy = (factor * point.real, factor * point.imag)
                if points[-1] != xy:
                    points.append(xy)
        else:
            log.warning("Unsupported SVG path component: %s", component)
    finish()

    # Preserve disconnected contours and assign contained rings as holes.
    parents = []
    for index, polygon in enumerate(closed_rings):
        containers = [i for i, other in enumerate(closed_rings)
                      if i != index and other.area > polygon.area and other.contains(polygon)]
        parents.append(min(containers, key=lambda i: closed_rings[i].area) if containers else None)
    depths = []
    for parent in parents:
        depth = 0
        while parent is not None:
            depth += 1
            parent = parents[parent]
        depths.append(depth)
    for index, polygon in enumerate(closed_rings):
        if depths[index] % 2 == 0:
            holes = [list(ring.exterior.coords) for i, ring in enumerate(closed_rings) if parents[i] == index]
            geometry.append(Polygon(polygon.exterior.coords, holes))
    return geometry


def svgrect2shapely(rect, n_points=32, factor=1.0):
    """
    Converts an SVG rect into Shapely geometry.

    :param rect:        Rect Element
    :type rect:         xml.etree.ElementTree.Element
    :param n_points:    number of points to approximate rectangles corners when having rounded corners
    :type n_points:     int
    :param factor:      correction factor due of virtual units
    :type factor:       float
    :return:            shapely.geometry.polygon.LinearRing
    """
    w = svgparselength(rect.get('width'))[0]
    h = svgparselength(rect.get('height'))[0]

    x_obj = rect.get('x')
    if x_obj is not None:
        x = svgparselength(x_obj)[0] * factor
    else:
        x = 0

    y_obj = rect.get('y')
    if y_obj is not None:
        y = svgparselength(y_obj)[0] * factor
    else:
        y = 0

    rxstr = rect.get('rx')
    rxstr = rxstr * factor if rxstr else rxstr
    rystr = rect.get('ry')
    rystr = rystr * factor if rystr else rystr

    if rxstr is None and rystr is None:  # Sharp corners
        pts = [
            (x, y), (x + w, y), (x + w, y + h), (x, y + h), (x, y)
        ]

    else:  # Rounded corners
        rx = 0.0 if rxstr is None else svgparselength(rxstr)[0]
        ry = 0.0 if rystr is None else svgparselength(rystr)[0]

        n_points = int(n_points / 4 + 0.5)
        t = np.arange(n_points, dtype=float) / n_points / 4

        x_ = (x + w - rx) + rx * np.cos(2 * np.pi * (t + 0.75))
        y_ = (y + ry) + ry * np.sin(2 * np.pi * (t + 0.75))

        lower_right = [(x_[i], y_[i]) for i in range(n_points)]

        x_ = (x + w - rx) + rx * np.cos(2 * np.pi * t)
        y_ = (y + h - ry) + ry * np.sin(2 * np.pi * t)

        upper_right = [(x_[i], y_[i]) for i in range(n_points)]

        x_ = (x + rx) + rx * np.cos(2 * np.pi * (t + 0.25))
        y_ = (y + h - ry) + ry * np.sin(2 * np.pi * (t + 0.25))

        upper_left = [(x_[i], y_[i]) for i in range(n_points)]

        x_ = (x + rx) + rx * np.cos(2 * np.pi * (t + 0.5))
        y_ = (y + ry) + ry * np.sin(2 * np.pi * (t + 0.5))

        lower_left = [(x_[i], y_[i]) for i in range(n_points)]

        pts = [(x + rx, y), (x - rx + w, y)] + \
            lower_right + \
            [(x + w, y + ry), (x + w, y + h - ry)] + \
            upper_right + \
            [(x + w - rx, y + h), (x + rx, y + h)] + \
            upper_left + \
            [(x, y + h - ry), (x, y + ry)] + \
            lower_left

    return Polygon(pts).buffer(0)
    # return LinearRing(pts)


def svgcircle2shapely(circle, n_points=64, factor=1.0):
    """
    Converts an SVG circle into Shapely geometry.

    :param circle:      Circle Element
    :type circle:       xml.etree.ElementTree.Element
    :param n_points:    circle resolution; nr of points to b e used to approximate a circle
    :type n_points:     int
    :param factor:
    :type factor:       float
    :return:            Shapely representation of the circle.
    :rtype:             shapely.geometry.polygon.LinearRing
    """
    # cx = float(circle.get('cx'))
    # cy = float(circle.get('cy'))
    # r = float(circle.get('r'))
    cx = svgparselength(circle.get('cx'))[0]  # TODO: No units support yet
    cx = cx * factor if cx else cx
    cy = svgparselength(circle.get('cy'))[0]  # TODO: No units support yet
    cy = cy * factor if cy else cy
    r = svgparselength(circle.get('r'))[0]  # TODO: No units support yet
    r = r * factor if r else r

    return Point(cx, cy).buffer(r, resolution=n_points)


def svgellipse2shapely(ellipse, n_points=64, factor=1.0):
    """
    Converts an SVG ellipse into Shapely geometry

    :param ellipse:     Ellipse Element
    :type ellipse:      xml.etree.ElementTree.Element
    :param n_points:    Number of discrete points in output.
    :type n_points:     int
    :param factor:
    :type factor:       float
    :return:            Shapely representation of the ellipse.
    :rtype:             shapely.geometry.polygon.LinearRing
    """

    cx = svgparselength(ellipse.get('cx'))[0]   # TODO: No units support yet
    cx = cx * factor if cx else cx
    cy = svgparselength(ellipse.get('cy'))[0]   # TODO: No units support yet
    cy = cy * factor if cy else cy

    rx = svgparselength(ellipse.get('rx'))[0]   # TODO: No units support yet
    rx = rx * factor if rx else rx
    ry = svgparselength(ellipse.get('ry'))[0]   # TODO: No units support yet
    ry = ry * factor if ry else ry

    t = np.arange(n_points, dtype=float) / n_points
    x = cx + rx * np.cos(2 * np.pi * t)
    y = cy + ry * np.sin(2 * np.pi * t)
    pts = [(x[i], y[i]) for i in range(n_points)]

    return Polygon(pts).buffer(0)
    # return LinearRing(pts)


def svgline2shapely(line, factor=1.0):
    """

    :param line:        Line element
    :type line:         xml.etree.ElementTree.Element
    :param factor:      correction factor due of virtual units
    :type factor:       float
    :return:            Shapely representation on the line.
    :rtype:             shapely.geometry.polygon.LineString
    """

    x1 = svgparselength(line.get('x1'))[0] * factor
    y1 = svgparselength(line.get('y1'))[0] * factor
    x2 = svgparselength(line.get('x2'))[0] * factor
    y2 = svgparselength(line.get('y2'))[0] * factor

    return LineString([(x1, y1), (x2, y2)])


def svgpolyline2shapely(polyline, factor=1.0):
    """

    :param polyline:    Polyline element
    :type polyline:     xml.etree.ElementTree.Element
    :param factor:      correction factor due of virtual units
    :type factor:       float
    :return:            Shapely representation of the PolyLine
    :rtype:             shapely.geometry.polygon.LineString
    """

    ptliststr = polyline.get('points')
    points = parse_svg_point_list(ptliststr, factor)

    return LineString(points)


def svgpolygon2shapely(polygon, n_points=64, factor=1.0):
    """
    Convert a SVG polygon to a Shapely Polygon.

    :param polygon:
    :type polygon:
    :param n_points:    circle resolution; nr of points to b e used to approximate a circle
    :type n_points:     int
    :param factor:      correction factor due of virtual units
    :type factor:       float
    :return:            Shapely Polygon
    """

    ptliststr = polygon.get('points')
    points = parse_svg_point_list(ptliststr, factor)

    return Polygon(points).buffer(0, resolution=n_points)
    # return LinearRing(points)


def getsvggeo(node, object_type, root=None, units='MM', res=64, factor=1.0):
    """
    Extracts and flattens all geometry from an SVG node
    into a list of Shapely geometry.

    :param node:        xml.etree.ElementTree.Element
    :param object_type:
    :param root:
    :param units:       FlatCAM units
    :param res:         resolution to be used for circles buffering
    :param factor:      correction factor due of virtual units
    :type factor:       float
    :return:            List of Shapely geometry
    :rtype:             list
    """
    if root is None:
        root = node

    kind = re.search('(?:\{.*\})?(.*)$', node.tag).group(1)
    geo = []

    # Recurse
    if len(node) > 0:
        for child in node:
            subgeo = getsvggeo(child, object_type, root=root, units=units, res=res, factor=factor)
            if subgeo is not None:
                geo += subgeo
    # Parse
    elif kind == 'path':
        log.debug("***PATH***")
        P = parse_path(node.get('d'))
        P = path2shapely(P, object_type, units=units, factor=factor)
        # for path, the resulting geometry is already a list so no need to create a new one
        geo = P

    elif kind == 'rect':
        log.debug("***RECT***")
        R = svgrect2shapely(node, n_points=res, factor=factor)
        geo = [R]

    elif kind == 'circle':
        log.debug("***CIRCLE***")
        C = svgcircle2shapely(node, n_points=res, factor=factor)
        geo = [C]

    elif kind == 'ellipse':
        log.debug("***ELLIPSE***")
        E = svgellipse2shapely(node, n_points=res, factor=factor)
        geo = [E]

    elif kind == 'polygon':
        log.debug("***POLYGON***")
        poly = svgpolygon2shapely(node, n_points=res, factor=factor)
        geo = [poly]

    elif kind == 'line':
        log.debug("***LINE***")
        line = svgline2shapely(node, factor=factor)
        geo = [line]

    elif kind == 'polyline':
        log.debug("***POLYLINE***")
        pline = svgpolyline2shapely(node, factor=factor)
        geo = [pline]

    elif kind == 'use':
        log.debug('***USE***')
        # href= is the preferred name for this[1], but inkscape still generates xlink:href=.
        # [1] https://developer.mozilla.org/en-US/docs/Web/SVG/Element/use#Attributes
        href = node.attrib['href'] if 'href' in node.attrib else node.attrib['{http://www.w3.org/1999/xlink}href']
        ref = root.find(".//*[@id='%s']" % href.replace('#', ''))
        if ref is not None:
            geo = getsvggeo(ref, object_type, root=root, units=units, res=res, factor=factor)

    else:
        log.warning("Unknown kind: " + kind)
        geo = None

    # ignore transformation for unknown kind
    if geo is not None:
        # Transformations
        if 'transform' in node.attrib:
            trstr = node.get('transform')
            trlist = parse_svg_transform(trstr)
            # log.debug(trlist)

            # Transformations are applied in reverse order
            for tr in trlist[::-1]:
                if tr[0] == 'translate':
                    geo = [translate(geoi, tr[1], tr[2]) for geoi in geometry_parts(geo)]
                elif tr[0] == 'scale':
                    geo = [scale(geoi, tr[1], tr[2], origin=(0, 0))
                           for geoi in geometry_parts(geo)]
                elif tr[0] == 'rotate':
                    geo = [rotate(geoi, tr[1], origin=(tr[2], tr[3]))
                           for geoi in geometry_parts(geo)]
                elif tr[0] == 'skew':
                    geo = [skew(geoi, tr[1], tr[2], origin=(0, 0))
                           for geoi in geometry_parts(geo)]
                elif tr[0] == 'matrix':
                    geo = [affine_transform(geoi, tr[1:]) for geoi in geometry_parts(geo)]
                else:
                    raise Exception('Unknown transformation: %s', tr)

    return geo


def getsvgtext(node, object_type, units='MM'):
    """
    Extracts and flattens all geometry from an SVG node
    into a list of Shapely geometry.

    :param node:        xml.etree.ElementTree.Element
    :param object_type:
    :param units:       FlatCAM units
    :return:            List of Shapely geometry
    :rtype:             list
    """
    kind = re.search('(?:\{.*\})?(.*)$', node.tag).group(1)
    geo = []

    # Recurse
    if len(node) > 0:
        for child in node:
            subgeo = getsvgtext(child, object_type, units=units)
            if subgeo is not None:
                geo += subgeo

    # Parse
    elif kind == 'tspan':
        current_attrib = node.attrib
        txt = node.text
        style_dict = {}
        parrent_attrib = node.getparent().attrib
        style = parrent_attrib['style']

        try:
            style_list = style.split(';')
            for css in style_list:
                style_dict[css.rpartition(':')[0]] = css.rpartition(':')[-1]

            pos_x = float(current_attrib['x'])
            pos_y = float(current_attrib['y'])

            # should have used the instance from FlatCAMApp.App but how? without reworking everything ...
            pf = ParseFont()
            pf.get_fonts_by_types()
            font_name = style_dict['font-family'].replace("'", '')

            if style_dict['font-style'] == 'italic' and style_dict['font-weight'] == 'bold':
                font_type = 'bi'
            elif style_dict['font-weight'] == 'bold':
                font_type = 'bold'
            elif style_dict['font-style'] == 'italic':
                font_type = 'italic'
            else:
                font_type = 'regular'

            # value of 2.2 should have been 2.83 (conversion value from pixels to points)
            # but the dimensions from Inkscape did not corelate with the ones after importing in FlatCAM
            # so I adjusted this
            font_size = svgparselength(style_dict['font-size'])[0] * 2.2
            geo = [pf.font_to_geometry(txt,
                                       font_name=font_name,
                                       font_size=font_size,
                                       font_type=font_type,
                                       units=units,
                                       coordx=pos_x,
                                       coordy=pos_y)
                   ]

            geo = [(scale(g, 1.0, -1.0)) for g in geometry_parts(geo)]
        except Exception as e:
            log.debug(str(e))
    else:
        geo = None

    # ignore transformation for unknown kind
    if geo is not None:
        # Transformations
        if 'transform' in node.attrib:
            trstr = node.get('transform')
            trlist = parse_svg_transform(trstr)
            # log.debug(trlist)

            # Transformations are applied in reverse order
            for tr in trlist[::-1]:
                if tr[0] == 'translate':
                    geo = [translate(geoi, tr[1], tr[2]) for geoi in geometry_parts(geo)]
                elif tr[0] == 'scale':
                    geo = [scale(geoi, tr[1], tr[2], origin=(0, 0))
                           for geoi in geometry_parts(geo)]
                elif tr[0] == 'rotate':
                    geo = [rotate(geoi, tr[1], origin=(tr[2], tr[3]))
                           for geoi in geometry_parts(geo)]
                elif tr[0] == 'skew':
                    geo = [skew(geoi, tr[1], tr[2], origin=(0, 0))
                           for geoi in geometry_parts(geo)]
                elif tr[0] == 'matrix':
                    geo = [affine_transform(geoi, tr[1:]) for geoi in geometry_parts(geo)]
                else:
                    raise Exception('Unknown transformation: %s', tr)

    return geo


def parse_svg_point_list(ptliststr, factor):
    """
    Returns a list of coordinate pairs extracted from the "points"
    attribute in SVG polygons and polyline's.

    :param ptliststr:       "points" attribute string in polygon or polyline.
    :param factor:          correction factor due of virtual units
    :type factor:           float
    :return:                List of tuples with coordinates.
    """

    pairs = []
    last = None
    pos = 0
    i = 0

    for match in re.finditer(r'(\s*,\s*)|(\s+)', ptliststr.strip(' ')):

        val = float(ptliststr[pos:match.start()])

        if i % 2 == 1:
            pairs.append((factor * last, factor * val))
        else:
            last = val * factor

        pos = match.end()
        i += 1

    # Check for last element
    val = float(ptliststr[pos:])
    if i % 2 == 1:
        pairs.append((factor * last, factor * val))
    else:
        log.warning("Incomplete coordinates.")

    return pairs


def parse_svg_transform(trstr):
    """
    Parses an SVG transform string into a list
    of transform names and their parameters.

    Possible transformations are:

    * Translate: translate(<tx> [<ty>]), which specifies
      a translation by tx and ty. If <ty> is not provided,
      it is assumed to be zero. Result is
      ['translate', tx, ty]

    * Scale: scale(<sx> [<sy>]), which specifies a scale operation
      by sx and sy. If <sy> is not provided, it is assumed to be
      equal to <sx>. Result is: ['scale', sx, sy]

    * Rotate: rotate(<rotate-angle> [<cx> <cy>]), which specifies
      a rotation by <rotate-angle> degrees about a given point.
      If optional parameters <cx> and <cy> are not supplied,
      the rotate is about the origin of the current user coordinate
      system. Result is: ['rotate', rotate-angle, cx, cy]

    * Skew: skewX(<skew-angle>), which specifies a skew
      transformation along the x-axis. skewY(<skew-angle>), which
      specifies a skew transformation along the y-axis.
      Result is ['skew', angle-x, angle-y]

    * Matrix: matrix(<a> <b> <c> <d> <e> <f>), which specifies a
      transformation in the form of a transformation matrix of six
      values. matrix(a,b,c,d,e,f) is equivalent to applying the
      transformation matrix [a b c d e f]. Result is
      ['matrix', a, b, c, d, e, f]

    Note: All parameters to the transformations are "numbers",
    i.e. no units present.

    :param trstr: SVG transform string.
    :type trstr: str
    :return: List of transforms.
    :rtype: list
    """
    trlist = []

    assert isinstance(trstr, str)
    trstr = trstr.strip(' ')

    integer_re_str = r'[+-]?[0-9]+'
    number_re_str = r'(?:[+-]?[0-9]*\.[0-9]+(?:[Ee]' + integer_re_str + ')?' + r')|' + \
                    r'(?:' + integer_re_str + r'(?:[Ee]' + integer_re_str + r')?)'

    # num_re_str = r'[\+\-]?[0-9\.e]+'  # TODO: Negative exponents missing
    comma_or_space_re_str = r'(?:(?:\s+)|(?:\s*,\s*))'
    translate_re_str = r'translate\s*\(\s*(' + \
                       number_re_str + r')(?:' + \
                       comma_or_space_re_str + \
                       r'(' + number_re_str + r'))?\s*\)'
    scale_re_str = r'scale\s*\(\s*(' + \
                   number_re_str + r')' + \
                   r'(?:' + comma_or_space_re_str + \
                   r'(' + number_re_str + r'))?\s*\)'
    skew_re_str = r'skew([XY])\s*\(\s*(' + \
                  number_re_str + r')\s*\)'
    rotate_re_str = r'rotate\s*\(\s*(' + \
                    number_re_str + r')' + \
                    r'(?:' + comma_or_space_re_str + \
                    r'(' + number_re_str + r')' + \
                    comma_or_space_re_str + \
                    r'(' + number_re_str + r'))?\s*\)'
    matrix_re_str = r'matrix\s*\(\s*' + \
                    r'(' + number_re_str + r')' + comma_or_space_re_str + \
                    r'(' + number_re_str + r')' + comma_or_space_re_str + \
                    r'(' + number_re_str + r')' + comma_or_space_re_str + \
                    r'(' + number_re_str + r')' + comma_or_space_re_str + \
                    r'(' + number_re_str + r')' + comma_or_space_re_str + \
                    r'(' + number_re_str + r')\s*\)'

    while len(trstr) > 0:
        match = re.search(r'^' + translate_re_str, trstr)
        if match:
            trlist.append([
                'translate',
                float(match.group(1)),
                float(match.group(2)) if (match.group(2) is not None) else 0.0
            ])
            trstr = trstr[len(match.group(0)):].strip(' ')
            continue

        match = re.search(r'^' + scale_re_str, trstr)
        if match:
            trlist.append([
                'scale',
                float(match.group(1)),
                float(match.group(2)) if (match.group(2) is not None) else float(match.group(1))
            ])
            trstr = trstr[len(match.group(0)):].strip(' ')
            continue

        match = re.search(r'^' + skew_re_str, trstr)
        if match:
            trlist.append([
                'skew',
                float(match.group(2)) if match.group(1) == 'X' else 0.0,
                float(match.group(2)) if match.group(1) == 'Y' else 0.0
            ])
            trstr = trstr[len(match.group(0)):].strip(' ')
            continue

        match = re.search(r'^' + rotate_re_str, trstr)
        if match:
            trlist.append([
                'rotate',
                float(match.group(1)),
                float(match.group(2)) if match.group(2) else 0.0,
                float(match.group(3)) if match.group(3) else 0.0
            ])
            trstr = trstr[len(match.group(0)):].strip(' ')
            continue

        match = re.search(r'^' + matrix_re_str, trstr)
        if match:
            trlist.append(['matrix'] + [float(x) for x in match.groups()])
            trstr = trstr[len(match.group(0)):].strip(' ')
            continue

        # raise Exception("Don't know how to parse: %s" % trstr)
        log.error("[ERROR] Don't know how to parse: %s" % trstr)

    return trlist

# if __name__ == "__main__":
#     tree = ET.parse('tests/svg/drawing.svg')
#     root = tree.getroot()
#     ns = re.search(r'\{(.*)\}', root.tag).group(1)
#     print(ns)
#     for geo in getsvggeo(root):
#         print(geo)
