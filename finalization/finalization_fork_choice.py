#! /usr/bin/env python

from graph_tool.all import *
import math


def rgb(r, g, b):
    return [r / 255, g / 255, b / 255, 1]


WHITE = rgb(255, 255, 255)
BLACK = rgb(0, 0, 0)
RED = rgb(255, 82, 82)
ORANGE = rgb(255, 179, 0)
GREEN = rgb(129, 199, 132)
BLUE = rgb(187, 222, 251)
BROWN = rgb(141, 110, 99)
DARK_ORANGE = rgb(245, 124, 0)
PURPLE = rgb(179, 136, 255)

img_width = 400
img_length = 940
vertex_size = 40
edge_length = 2.5 * vertex_size
edge_pen_width = vertex_size / 6
big_edge_pen_width = vertex_size / 2

root = None
pos = None
level = None
vf_color = None
vb_color = None
v_final = None
e_color = None
e_text = None
e_votes = None
e_pointer = None
e_cpoints = None
e_pen_width = None


def init_graph():
    global root
    global pos
    global level
    global vf_color
    global vb_color
    global e_color
    global e_text
    global e_votes
    global e_pointer
    global v_final
    global e_cpoints
    global e_pen_width

    g = Graph()
    g.set_directed(True)
    root = g.add_vertex()
    pos = g.new_vertex_property("vector<double>")
    level = g.new_vertex_property("int")
    vf_color = g.new_vertex_property("vector<double>")
    vb_color = g.new_vertex_property("vector<double>")
    v_final = g.new_vertex_property("bool")

    e_color = g.new_edge_property("vector<double>")
    e_text = g.new_edge_property("vector<double>")
    e_votes = []
    e_pointer = g.new_edge_property("string")
    e_cpoints = g.new_edge_property("vector<double>")
    e_pen_width = g.new_edge_property("double")

    pos[root] = (img_width / 2 - vertex_size, img_length + 2 * vertex_size)
    level[root] = 0
    vf_color[root] = WHITE
    vb_color[root] = BLACK
    v_final[root] = True

    return g


g = init_graph()


def mine_block(source, hpos=0, border=BLACK, fill=WHITE, final=False):
    v = g.add_vertex()

    level[v] = level[source] + 1
    pos[v] = (img_width / 2 - vertex_size + hpos * 100, img_length - level[v] * edge_length + 20)
    vf_color[v] = fill
    vb_color[v] = border
    e = g.add_edge(source, v)
    e_color[e] = BLACK
    e_pointer[e] = "none"
    e_pen_width[e] = edge_pen_width
    v_final[v] = final
    return v


def choose_fork(v, reset=True, finalize=False):
    global e_pen_width
    if reset:
        for e in g.edges():
            if e not in e_votes:
                e_color[e] = BLACK
                e_pen_width[e] = edge_pen_width

    for e in v.in_edges():
        if e in e_votes:
            continue

        if finalize:
            e_color[e] = PURPLE
            e_pen_width[e] = big_edge_pen_width
        else:
            e_color[e] = ORANGE

        parent = e.source()
        if parent == root:
            return
        else:
            choose_fork(parent, False, finalize)


def vote(source, checkpoint, color):
    e = g.add_edge(source, checkpoint)
    e_color[e] = color
    e_votes.append(e)
    e_pointer[e] = "arrow"
    d = math.sqrt(sum((pos[e.source()].a - pos[e.target()].a) ** 2)) / 4
    e_cpoints[e] = [0.0, 0.0, 0.3, d, 0.7, d, 1.0, 0.0]


def graph():
    global g

    i = 0
    c0 = mine_block(root, final=True, fill=BLUE)
    choose_fork(c0)
    yield i

    v1 = mine_block(c0, final=True)
    vote(v1, c0, BLUE)
    choose_fork(v1)
    i += 1
    yield i

    v = mine_block(c0, hpos=1)
    vote(v, c0, BLUE)
    choose_fork(v)
    i += 1
    yield i

    v = mine_block(v, hpos=1)
    choose_fork(v)
    i += 1
    yield i

    v = mine_block(v1, final=True)
    i += 1
    yield i

    mine_block(v1, hpos=-1)
    i += 1
    yield i

    v1 = mine_block(v, final=True)
    choose_fork(v1)
    i += 1
    yield i

    c1 = mine_block(v1, fill=RED)
    choose_fork(c1)
    i += 1
    yield i

    c2 = mine_block(v1, fill=GREEN, hpos=1, final=True)
    i += 1
    yield i

    v1 = mine_block(c1)
    choose_fork(v1)
    vote(v1, c1, RED)
    vote(v1, c2, GREEN)
    i += 1
    yield i

    v1 = mine_block(v1)
    choose_fork(v1)
    i += 1
    yield i

    v2_1 = mine_block(c2, hpos=1, final=True)
    vote(v2_1, c2, GREEN)
    i += 1
    yield i

    v2 = mine_block(v2_1, hpos=1, final=True)
    vote(v2, c2, GREEN)
    i += 1
    yield i

    v = mine_block(v2_1, hpos=2, final=True)
    i += 1
    yield i

    v = mine_block(v2, hpos=1, final=True)
    choose_fork(v)
    vote(v, c2, GREEN)
    i += 1
    yield i

    choose_fork(c2, finalize=True, reset=False)
    i += 1
    yield i

    g.set_vertex_filter(v_final)
    i += 1
    yield i

    v2 = mine_block(v, hpos=1, final=True, fill=BROWN)
    choose_fork(v2)
    choose_fork(c2, finalize=True, reset=False)
    i += 1
    yield i

    v2 = mine_block(v, hpos=0, final=True, fill=BLUE)
    choose_fork(c2, finalize=True, reset=False)
    i += 1
    yield i

    v2 = mine_block(v2, hpos=0, final=True)
    choose_fork(v2)
    choose_fork(c2, finalize=True, reset=False)
    i += 1
    yield i


for i in graph():
    graph_draw(g,
               pos=pos,
               bg_color=WHITE,
               vertex_shape="square",
               vertex_font_size=18,
               vertex_fill_color=vf_color,
               vertex_color=vb_color,
               edge_color=e_color,
               output_size=(img_width, img_length),
               vertex_size=vertex_size,
               fit_view=False,
               edge_control_points=e_cpoints,
               edge_pen_width=edge_pen_width,
               output=f'{i}.png')

