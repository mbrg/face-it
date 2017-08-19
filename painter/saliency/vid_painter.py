
import numpy as np
import cv2
import logging

from painter.saliency.mrf import build_grid_graph, grid2mat
from painter.saliency.saliency_map import api as saliency_map

class Painter(object):


    def __init__(self, image, dist_scale_thresh=40, image_shape=(512, 512), observed_value=0):

        assert (len(image.shape)==3), 'Image should have three dimensions'

        # configs
        self.dist_scale_thresh = dist_scale_thresh
        self.dist_scale_exp = np.exp(-dist_scale_thresh)
        self.observed_value = observed_value

        # init MRF graph
        self.image = image
        self.image_2d = image[:,:,0]  # MRF handles 2D grayscale

        self.n, self.m = self.image_2d.shape
        self.obs_mat = np.zeros((self.n, self.m))
        self.mrf_graph = build_grid_graph(self.n, self.m, self.image_2d, self.obs_mat)
        #TODO delete if this doesn't cause isues
        self.mrf_graph.init_in_msgs()

        # compute saliency
        maps = saliency_map(im=image, is_markMaxima=False)
        self.intensity = cv2.resize(maps.intensity, image_shape)

        blank_img = np.multiply(np.ones((self.n, self.m)), 255).astype(np.int)
        blank_img[0] = 0

        # changing image versions
        _='''self.obsed_indecies = []
        self.observed_image = blank_img
        self.unobserved_intensity = self.intensity.copy()'''


    def max_saliency(self):
        # mrf graph to value and observe matrices
        mat, obs = self.image_2d, self.obs_mat

        # obscured intensity by observed cells
        self.intensity[(obs == 1)] = self.observed_value

        # argmax coor
        argmax_coor = np.unravel_index(self.intensity.argmax(), self.intensity.shape)

        return self.mrf_graph.get_vertex_by_coor(argmax_coor), self.intensity, obs

    _='''
    def new_saliency(self):
        # obs values to nparray
        self.obsed_indecies = np.asarray(self.obsed_indecies, dtype=int)

        # update obs_mat
        self.obs_mat[self.obsed_indecies] = 1

        # update unobserved_intensity
        self.unobserved_intensity[self.obsed_indecies] = self.observed_value

        # update observed image
        self.observed_image[self.obsed_indecies] = self.image_2d[self.obsed_indecies]

        # forget mem of changes
        self.obsed_indecies = []

        # argmax coor
        argmax_coor = np.unravel_index(self.unobserved_intensity.argmax(), self.unobserved_intensity.shape)

        return self.mrf_graph.get_vertex_by_coor(argmax_coor), self.unobserved_intensity, self.obs_mat'''


    def frame_gen(self):

        cur_v, cur_intens, cur_obs = self.max_saliency()
        next_v, cntr = None, 0

        while True:
            if cntr % 1000 == 0:
                logging.info('Started coor=%s, number=%d' % (cur_v._coor, cntr))
            cntr += 1

            if cur_v._is_observed == False:
                # observe current
                cur_v._is_observed = True
                self.obs_mat[cur_v._coor[0], cur_v._coor[1]] = 1
                #self.obsed_indecies.append(cur_v._coor)
            else:
                # cicle complete
                logging.info('Cicle complete. Passed through %d coors' % cntr)
                break

            # move by distribution
            next_v = self.mrf_graph.move(cur_v, v_max=self.dist_scale_thresh, exp_v_max=self.dist_scale_exp)
            if cntr % 1000 == 0:
                logging.info('Moving to coor=%s' % str(next_v._coor if next_v else ''))

            if next_v is None:
                if 0 <= cntr % 1000 <= 5:
                    logging.info('Jumping to next salient location, no unobserved neighs, number=%d' % cntr)

                # no unobserved neighs
                next_v, cur_intens, cur_obs = self.max_saliency()

                # print current img
                cur_image_segment = self.image_2d.copy()
                cur_image_segment[(cur_obs == 0)] = 255
                yield cur_image_segment
                #yield self.observed_image

            cur_v = next_v

    def min_num_frames(self):
        return np.count_nonzero(self.intensity)