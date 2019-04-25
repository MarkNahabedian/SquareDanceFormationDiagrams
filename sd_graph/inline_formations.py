# Inline the formation SVG file contents into the graph SVG file so
# that we have a single stand-alone SVG.

import os.path
import re
import xml.dom.minidom


XLINK_NAMESPACE = 'http://www.w3.org/1999/xlink'

NUMBER_RE = re.compile('\d+')

def get_formation_group(dom):
    for g in dom.getElementsByTagName('g'):
        if g.getAttribute('class') == 'formation':
            return g
    return None


def inline_svg(graph_file_path, outfile):
    directory = os.path.dirname(graph_file_path)
    graph_dom = xml.dom.minidom.parse(graph_file_path)
    # Find image elements and replae them with target file contents,
    # adding appropriate translation and scaling.
    for image in graph_dom.getElementsByTagName('image'):
        parent = image.parentNode
        translate = 'translate(%s, %s)' % (
            image.getAttribute('x'),
            image.getAttribute('y'))
        image_width = float(NUMBER_RE.findall(image.getAttribute('width'))[0])
        image_height = float(NUMBER_RE.findall(image.getAttribute('height'))[0])
        formation_id = image.getAttributeNS(XLINK_NAMESPACE, 'href')
        formation_dom = xml.dom.minidom.parse(os.path.join(
            directory, formation_id))
        viewbox = [float(x) for x in formation_dom.documentElement.getAttribute('viewBox').split(' ')]
        width_scale = image_width / viewbox[2]
        height_scale = image_height / viewbox[3]
        scale = 'scale(%f)' % ((width_scale + height_scale) / 2.0)
        parent.setAttribute('transform', translate + ' ' + scale)
        parent.replaceChild(get_formation_group(formation_dom).cloneNode(True),
                            image)
    with open(os.path.join(directory, outfile), 'w') as f:
        graph_dom.writexml(f, addindent='  ')


