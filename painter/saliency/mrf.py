# -*- coding: utf-8 -*-
"""
Implements a MRF compilation using LBF
"""

import sys
from datetime import datetime
from functools import reduce
import logging

import numpy as np
from scipy import misc
import math
from sklearn.metrics.pairwise import pairwise_distances
from sklearn.preprocessing import normalize

from painter.saliency.curves import Hilbert_Curve, Line_Curve


# globals
NUM_OF_VALUES = 256             # number of possible values
V_MAX = 50                      # default v_max for phi
PHI = None                      # memoization of PHI function
EPS = np.finfo(np.float64).eps  # infinitesimal
MSG_METHOD = 'log'              # use 'log' of messages or 'regular' message
INIT_MSG = np.zeros(NUM_OF_VALUES) if MSG_METHOD == 'log' else np.ones(NUM_OF_VALUES)  # initiation message
DEBUG = False                   # controls debug prints


class Vertex(object):

    def __init__(self, row, col, name='', y=None, neighs=None, in_msgs=None, observed=True):
        self._name = '%s,%s' % (row, col)                   # verbose name
        self._y = y                                         # original pixel
        self._neighs = set() if neighs is None else neighs  # set of neighbour node's coordinates
        self._in_msgs = {} if in_msgs is None else in_msgs  # dictionary mapping neighbour coordinates to their messages
        self._is_observed = observed                        # is vertex observed
        self._coor = (row, col)                             # vertex row,col for grid graph

    # graph methods

    def add_neigh(self, vertex):
        self._neighs.add(vertex.get_coor())

    def rem_neigh(self, vertex):
        self._neighs.remove(vertex)

    def __str__(self):
        ret = "Name: " + self._name
        ret += "\nNeighbours:"
        neigh_list = ""
        for n in self._neighs:
            neigh_list += " " + n._name
        ret += neigh_list
        return ret

    # LBF methods

    def get_belief(self):
        if MSG_METHOD == 'log':
            return reduce(np.add, self._in_msgs.values())
        else:
            return reduce(np.multiply, self._in_msgs.values())

    def get_max_belief(self):
        """
        Get max belief value
        """
        return np.argmax(self.get_belief())

    def snd_msg(self, neigh):
        """ Combines messages from all other neighbours
            to propagate a message to the neighbouring Vertex 'neigh'.
        """

        if MSG_METHOD== 'log':
            # the product part of the message function
            filtered_msgs = remove_dict_key(self._in_msgs, neigh.get_coor())
            in_msg_mult = reduce(np.add, filtered_msgs.values())

            # the total message function, not normalized
            msg_self_neigh_unnormed = np.add(phi(), in_msg_mult.reshape(-1, 1))

            # MAP
            if self._is_observed:
                msg_self_neigh_map = msg_self_neigh_unnormed[int(self._y % NUM_OF_VALUES), :]
            else:
                msg_self_neigh_map = np.max(msg_self_neigh_unnormed, axis=0).reshape(1, -1)

            # normalize
            msg_self_neigh_map_normed = normalize(msg_self_neigh_map.reshape(1, -1), norm='l1').reshape(
                NUM_OF_VALUES)
        else:
            # the product part of the message function
            filtered_msgs = remove_dict_key(self._in_msgs, neigh.get_coor())
            in_msg_mult = reduce(np.multiply, filtered_msgs.values())

            # the total message function, not normalized
            msg_self_neigh_unnormed = np.multiply(phi(), in_msg_mult)

            # MAP
            if self._is_observed:
                msg_self_neigh_map = msg_self_neigh_unnormed[int(self._y % NUM_OF_VALUES), :]
            else:
                msg_self_neigh_map = np.max(msg_self_neigh_unnormed, axis=0).reshape(1, -1)

            # normalize while keeping minimal values as eps
            msg_self_neigh_map_eps = np.maximum(msg_self_neigh_map, np.ones(NUM_OF_VALUES)*EPS)  # used to avoid zero probabilities
            msg_self_neigh_map_normed = normalize(msg_self_neigh_map_eps.reshape(1, -1), norm='l1').reshape(NUM_OF_VALUES)

        return msg_self_neigh_map_normed

    # getters / setters

    def set_in_msg(self, neigh_coor, m):
        """
        Sets a vertex in_msgs from neighbor neigh to be m
        """
        self._in_msgs[neigh_coor] = m

    def get_neighbors(self):
        return self._neighs

    def get_coor(self):
        return self._coor

    def get_is_observed(self):
        return self._is_observed

    def get_original_value(self):
        return self._y


class Graph(object):

    def __init__(self, vertex_dict=None):
        """
        Initializes a graph object
        :param vertex_dict:  A mapping of coordicates to vertex. If no dict is given, an empty one will be used.
        """
        self._vertex_dict = {} if vertex_dict is None else vertex_dict

    # graph methods

    def vertices(self):
        """ returns the vertices of a graph"""
        return list(self._vertex_dict.values())

    def edges(self):
        """ returns the edges of a graph """
        return self._generate_edges()

    def add_edge(self, edge):
        """ assumes that edge is of type set, tuple, or list;
            between two vertices can be multiple edges.
        """
        (v1, v2) = tuple(edge)
        v1.add_neigh(v2)
        v2.add_neigh(v1)
        self._vertex_dict[v1.get_coor()] = v1
        self._vertex_dict[v2.get_coor()] = v2

    def _generate_edges(self):
        """ A static method generating the edges of the
            graph "graph". Edges are represented as sets
            with one or two vertices
        """
        e = set()
        for v in self.vertices():
            for neigh in v.get_neighbors():
                e.update({v, neigh})
        return e

    def add_vertex(self, vertex):
        """
        Adds a vertex to the vertex_dict, with it's coordinate as it's key.
        If the vertex is already in the graph, the old vertex is overridden.
        """
        self._vertex_dict[vertex.get_coor()] = vertex

    def get_vertex_by_coor(self, coor):
        return self._vertex_dict.get(coor)

    def __str__(self):
        res = "V: "
        for k in self.vertices():
            res += str(k) + " "
        res += "\nE: "
        for edge in self._generate_edges():
            res += str(edge) + " "
        return res

    # LBF method

    def init_in_msgs(self):
        """
        init in_msgs for all vertices to be msg_func
        """
        for v in self.vertices():
            for neigh_coor in v.get_neighbors():
                v.set_in_msg(neigh_coor, INIT_MSG)

    def send_msgs(self, vertex):
        """
        vertex sends message to it's neighbors, given it's current in_msgs
        :param vertex: vertex to send msgs
        """

        for neigh_coor in vertex.get_neighbors():
            neigh = self.get_vertex_by_coor(neigh_coor)
            if not neigh.get_is_observed():
                neigh.set_in_msg(vertex.get_coor(), vertex.snd_msg(neigh))


def build_grid_graph(n, m, img_mat, obs_mat):
    """ Builds an nxm grid graph, with vertex values corresponding to pixel intensities.
    n: num of rows
    m: num of columns
    img_mat = np.ndarray of shape (n,m) of pixel intensities
    obs_mat = binary np.ndarray of shape (n,m) of pixel is_observed
    returns the Graph object corresponding to the grid
    """
    g = Graph()

    # add vertices
    for i in range(n * m):
        row, col = (i // m, i % m)
        v = Vertex(row=row, col=col, name="v" + str(i), y=img_mat[row][col], observed=bool(obs_mat[row][col]))
        g.add_vertex(v)

    # add edges
    for i in range(n * m):
        row, col = (i // m, i % m)
        v = g.get_vertex_by_coor((row, col))

        if (col != 0):   g.add_edge( (v, g.get_vertex_by_coor((row, col-1))) )  # has left edge
        if (col != n-1): g.add_edge( (v, g.get_vertex_by_coor((row, col+1))) )  # has right edge
        if (row != 0):   g.add_edge( (v, g.get_vertex_by_coor((row-1, col))) )  # has up edge
        if (row != n-1): g.add_edge( (v, g.get_vertex_by_coor((row+1, col))) )  # has down edge

    return g


def grid2mat(grid, n, m):
    """ convertes grid graph to a np.ndarray
    n: num of rows
    m: num of columns
    returns: np.ndarray of shape (n,m)
    """
    mat = np.zeros((n, m))
    l = grid.vertices()  # list of vertices
    for v in l:
        row, col = v.get_coor()
        mat[row][col] = v.get_original_value() if v.get_is_observed() else v.get_max_belief()
    return mat


def phi(x1=None, x2=None, v_max=V_MAX):
    """
    If x1 is provided, returns phi(x1,x1)
    If x1,x2 are provided, returns phi(x1,x2)
    If None are provided, returns phi(0,..255,0..255)
    """
    global PHI
    if x1 is None:
        if PHI is None:
            PHI = phi(np.arange(0, NUM_OF_VALUES), None, v_max)
            if MSG_METHOD == 'log':
                PHI = np.log(PHI)
        return PHI
    else:
        if x2 is None:
            dist = pairwise_distances(x1.reshape(-1, 1), metric='l1')
        else:
            dist = pairwise_distances(x1.reshape(-1, 1), x2.reshape(-1, 1), metric='l1')
        return np.exp(-np.minimum(dist, v_max))


def LBP(g, n, curve_type='line', iterations=1000):
    """
    Loopy Belief Propagation
    :param g: graph
    :param n: rows/columns. If curve_type=hilbert, must be a power of 2.
    :param curve_type: method to go through vertices in each iteration. options: {hilbert, line}
    :param iterations: number of iteration
    """

    # verify arguments
    assert(curve_type!='hilbert' or Hilbert_Curve._is_power_of_two(n))

    # init
    g.init_in_msgs()                                             # set in_msgs := INIT_MSG
    start_c = 0, 0                                               # start coor
    Curve = Line_Curve if curve_type=='line' else Hilbert_Curve  # curve type
    logging.info('Started LBP, line=%s, iterations=%d' % (curve_type, iterations))

    # iterate
    for t in range(iterations):
        curve = Curve(n, start_c)              # curve mapping object
        cur_v = None                           # current vertex
        belief_list = []
        timer = datetime.now()

        # do while
        while True:
            if cur_v is not None: # neglect first iteration

                # cur_v sends message to it's neighbors given it's in_msgs
                g.send_msgs(cur_v)

                # calculate current vertex belief
                belief_list.append(cur_v.get_max_belief())

            # iterate to next vertex
            cur_c = curve.next_coor()
            cur_v = g.get_vertex_by_coor(cur_c)

            if cur_c==start_c:
                # Curve objects return to starting coordinate when curve has ended
                break

        # compare current and next beliefs, to measure progress
        next_belief = np.ones(len(belief_list)) if t==0 else cur_belief.copy()
        cur_belief = np.array(belief_list)
        belief_change = np.linalg.norm(next_belief - cur_belief)

        logging.info('iteration %d/%d, %dsec, belief change: %.2f'
              % (t+1, iterations, (datetime.now()-timer).seconds, belief_change))


def remove_dict_key(d, key):
    """
    Removes a key from a dict d w/o mutating the original dict
    """
    r = dict(d)
    del r[key]
    return r


def rgb2gray(rgb_image):
    return np.dot(rgb_image[...,:3], [0.299, 0.587, 0.114])


def api(image, obs_mat, curve='line', iterations=1000, verbose=False, v_max=50, num_of_values=256, msg_method='log'):

    image = rgb2gray(image)

    assert (curve in ['line', 'hilbert']), 'curve must be in {line, hilbert}'
    assert (msg_method in ['log', 'norm']), 'curve must be in {log, norm}'
    assert (image.shape == obs_mat.shape), 'image and obs_mat must have the same first two dimensions'

    # set global parameters
    global  DEBUG, V_MAX, NUM_OF_VALUES, MSG_METHOD
    DEBUG = verbose
    V_MAX = v_max
    NUM_OF_VALUES = num_of_values
    MSG_METHOD = msg_method

    # take an n*n square over the unobserved area, where n is a power of two (for use of a Hilbert curve)
    largest_powof2 = min(int(math.log(image.shape[0], 2)), int(math.log(image.shape[1], 2)))
    margins = ((image.shape[0] - pow(2, largest_powof2)) / 2, (image.shape[1] - pow(2, largest_powof2)) / 2)
    image_segment = image[margins[0]:margins[0] + pow(2, largest_powof2), margins[1]:margins[1] + pow(2, largest_powof2)]
    observed_segment = obs_mat[margins[0]:margins[0] + pow(2, largest_powof2), margins[1]:margins[1] + pow(2, largest_powof2)]
    n, m = image_segment.shape

    # build grid:
    g = build_grid_graph(n, m, image_segment, observed_segment)

    # process grid:
    LBP(g, n, curve, iterations)

    # convert grid to image:
    inferred_img = grid2mat(g, n, m)

    return inferred_img