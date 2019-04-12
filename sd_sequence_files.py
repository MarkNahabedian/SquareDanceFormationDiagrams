#!python3

# Program to read the sequence files written by William Ackerman's
# "sd, A Square Dance Caller's Helper" (see
# http://www.challengedance.org/sd/sd_doc.pdf).

import re
import os
import os.path
from collections import defaultdict
from yattag import Doc


sd_dancer_re = re.compile('''[1234][BG][><V^]''')

SVG_NAMESPACE = 'http://www.w3.org/2000/svg'


class Graph (object):
    def __init__(self):
        self.calls = []
        self.formations = []
        
    def intern_formation(self, formation):
        '''intern_formation returns the one true Formation that matches formation.'''
        for f in self.formations:
            if formation == f:
                return f
        self.formations.append(formation)
        formation.id = len(self.formations)
        return formation

    def intern_call(self, call):
        '''note_call ensures that we only remember one instance of a Call.'''
        for c in self.calls:
            if call == c:
                return c 
        self.calls.append(call)
        return call

    def parse_sd_file(self, filepath):
        with open(filepath, 'r') as f:
            return self.parse_sd_text(f.read())

    def parse_sd_text(self, text):
        previous_formation = self.intern_formation(squared_set())
        # session accumulates calls and text so we can review what was
        # read from the file.  Mostly for debugging.
        session = []
        # formation accumumates the dancers of a given formation as we
        # read each line of input.
        formation = []
        def last_call():
            warning = 'Warning:'
            for i in range(len(session) - 1,-1, -1):
                c = session[i]
                if isinstance(c, Call):
                    return None
                if warning in c:
                    continue
                return i
            return None
        def finish_formation():
            nonlocal formation, previous_formation
            f = self.intern_formation(Formation(formation).regrid())
            if previous_formation and isinstance(session[-1], str):
                last_call_index = last_call()
                if last_call_index:
                    c = self.intern_call(Call(session[last_call_index], previous_formation, f))
                session[last_call_index] = c
            formation = []
            previous_formation = f
        for line_number, line in enumerate(text.split('\n')):
            if len(line) == 0:
                continue
            dancers = []
            for dmo in sd_dancer_re.finditer(line):
                # dmo is a match object
                dancers.append(Dancer(x=dmo.start(), y=line_number,
                                      token=line[dmo.start(): dmo.end()]))
            if len(dancers) > 0:
                formation.extend(dancers)
            else:
                if len(formation) > 0:
                    finish_formation()
                session.append(line)
        finish_formation()
        return session

    def write_dot_file(self, directory):
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass
        with open(os.path.join(directory, 'graph.dot'), 'w') as f:
            f.write('strict digraph {\n')
            for formation in self.formations:
                formation_svg_file = '%s.svg' % formation.dot_id()
                with open(os.path.join(directory, formation_svg_file), 'w') as ff:
                    doc, tag, text = Doc().tagtext()
                    with tag('svg',
                             ('xmlns', SVG_NAMESPACE),
                             ('viewBox', '0 0 %d %d' % (
                                 formation.dancer_spacing * (1 + max([d.x for d in formation.dancers])),
                                 formation.dancer_spacing * (1 + max([d.y for d in formation.dancers])))),
                             ('width', 100),
                             ('height', 100)):
                        doc.asis(xml_text(formation.toSVG()))
                    ff.write(xml_text(doc))
                f.write('%s [image="%s"];\n' % (formation.dot_id(), formation_svg_file))
            for c in self.calls:
                f.write('%s -> %s [label="%s"];\n' % (
                    c.from_formation.dot_id(),
                    c.to_formation.dot_id(),
                    c.text))
            f.write('}\n')


class Formation(object):
    def __init__(self, dancers):
        self.id = None
        self.dancer_size = 20
        self.dancer_spacing = self.dancer_size * 1.3
        self.dancer_nose_radius = 3
        self.dancers = dancers
        for d in dancers:
            d.formation = self

    def __repr__(self):
        return 'Formation(%r)' % self.dancers
        
    def dot_id(self):
        assert self.id != None
        return('f%d' % self.id)

    def regrid(self):
        xs = defaultdict(list)
        ys = defaultdict(list)
        for d in self.dancers:
            xs[d.x].append(d)
            ys[d.y].append(d)
        for i, k in enumerate(sorted(xs.keys())):
            for d in xs[k]:
                d.x = i
        for i, k in enumerate(sorted(ys.keys())):
            for d in ys[k]:
                d.y = i
        return self

    def __eq__(self, other):
        if len(self.dancers) != len(other.dancers):
            return False
        # The dancers alweays appear in geometric order in sd's output
        # file and that order is preserved by the code in this file.
        for i in range(len(self.dancers)):
            if self.dancers[i] != other.dancers[i]:
                return False
        return True

    def toJavaScript(self):
        return ('Floor([' +
                ', '.join([d.toJavaScript() for d in self.dancers]) +
                '])')

    def toSVG(self):
        doc, tag, text = Doc().tagtext()
        with tag('g',
                 ('class', 'formation')):
            for d in self.dancers:
                doc.asis(xml_text(d.toSVG()))
        return doc


class Dancer(object):
    # In a squared set, couple 1's facing direction is 0.
    # Direction increases by 1 going counterclockwise.
    DIRECTIONS = {
        '^': 0, 
        '<': 1,
        'V': 2,
        '>': 3,
    }
    
    GENDER = {
        'B': 'guy',
        'G': 'gal'
    }

    def __init__(self, token=None, couple_number=0, gender='B', direction=0, x=0, y=0):
        self.formation = None
        self.x = x
        self.y = y
        if token != None:
            self.couple_number = ord(token[0]) - ord('0')
            self.gender = token[1]
            self.direction = self.__class__.DIRECTIONS[token[2]]
        else:
            self.couple_number = couple_number
            self.gender = gender
            self.direction = direction
            
    def __repr__(self):
        return ('Dancer(couple_number=%d, gender=%s, direction=%d, x=%d, y=%d)' % (
            self.couple_number, self.gender, self.direction, self.x, self.y))

    def __eq__(self, other):
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        if self.direction != other.direction:
            return False
        if self.couple_number != other.couple_number:
            return False
        if self.gender != other.gender:
            return False
        return True

    def toJavaScript(self):
        return ('Dancer(%d, %d, %d, %d, "%s", color)' % {
            self.x, self.y, self.direction, self.couple_number,
            self.__class__.GENDER[self.gender]})

    def toSVG(self):
        doc, tag, text = Doc().tagtext()
        offset = self.formation.dancer_spacing
        with tag('g',
                 ('class', 
                  ('dancer couple%d %s' % (
                      self.couple_number,
                      self.__class__.GENDER[self.gender]))),
                 ('transform',
                  (('rotate(%d)' % (180 - 90 * self.direction)) + ' ' +
                   ('translate(%d, %d)' % (
                       offset + self.x * self.formation.dancer_spacing,
                       offset + self.y * self.formation.dancer_spacing))))):
            if self.gender == 'B':
                doc.stag('rect',
                         ('fill', 'none'),
                         ('stroke', 'black'),
                         ('width', self.formation.dancer_size),
                         ('height', self.formation.dancer_size),
                         ('x', self.formation.dancer_size / 2),
                         ('y', self.formation.dancer_size / 2))
            else:
                doc.stag('circle',
                         ('fill', 'none'),
                         ('stroke', 'black'),
                         ('r', self.formation.dancer_size / 2),
                         ('x', 0),
                         ('y', 0))
            # Nose:
            doc.stag('circle',
                     ('class', 'nose'),
                     ('r', self.formation.dancer_nose_radius),
                     ('cx', 0),
                     ('cy', - self.formation.dancer_size / 2),
                     ('stroke', 'none'),
                     ('fill', 'black'))
            # Label:
            with tag('text',
                     ('class', 'dancer-label'),
                     ('stroke', 'black'),
                     ('text-anchor', 'middle'),
                     ('alignment-baseline', 'middle')):
                text(self.couple_number)
        return doc


def squared_set():
    return Formation([
        Dancer(x=2, y=4, direction=0, couple_number=1, gender='B'),
        Dancer(x=3, y=4, direction=0, couple_number=1, gender='G'),
        Dancer(x=4, y=3, direction=1, couple_number=2, gender='B'),
        Dancer(x=4, y=2, direction=1, couple_number=2, gender='G'),
        Dancer(x=1, y=2, direction=2, couple_number=3, gender='B'),
        Dancer(x=1, y=3, direction=2, couple_number=3, gender='G'),
        Dancer(x=3, y=1, direction=3, couple_number=4, gender='B'),
        Dancer(x=2, y=1, direction=3, couple_number=4, gender='G')]).regrid()


def xml_text(yattag_doc):
    '''xml_text renders yattag_doc as XML text.'''
    return '\n'.join(yattag_doc.result)


class Call (object):
    def __init__(self, text, from_formation, to_formation):
        self.text = text
        self.from_formation = from_formation
        self.to_formation = to_formation

    def __eq__(self, other):
        if self.text != other.text:
            return False
        if self.from_formation != other.from_formation:
            return False
        if self.to_formation != other.to_formation:
            return False
        return True

    def __str__(self):
        return ('%d -> %s -> %d' % (
            self.from_formation.id,
            self.text,
            self.to_formation.id))


graph = Graph()
session = graph.parse_sd_file('c:/Sd/08apr19_Plus_with_pictures.txt')
for i, s in enumerate(session): print('%3d:  %s' % (i, s))
graph.write_dot_file('chicken_plucker')
# for i, o in enumerate(sequence): print(i, repr(o))

# dot -ochicken_plucker.svg -Tsvg chicken_plucker.dot

