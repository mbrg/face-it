
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
        self.mrf_graph = build_grid_graph(self.n, self.m, self.image_2d, np.zeros((self.n, self.m)))
        self.mrf_graph.init_in_msgs()

        # compute saliency
        maps = saliency_map(im=image, is_markMaxima=False)
        self.intensity = cv2.resize(maps.intensity, image_shape)


    def max_saliency(self):
        # mrf graph to value and observe matrices
        mat, obs = grid2mat(self.mrf_graph, self.n, self.m, unobserved_to_belief=False)

        # obscured intensity by observed cells
        self.intensity[(obs == 1)] = self.observed_value

        # argmax coor
        argmax_coor = np.unravel_index(self.intensity.argmax(), self.intensity.shape)

        return self.mrf_graph.get_vertex_by_coor(argmax_coor), self.intensity, obs


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
            else:
                # cicle complete
                logging.info('Cicle complete. Passed through %d coors' % cntr)
                break

            # move by distribution
            next_v = self.mrf_graph.move(cur_v, v_max=self.dist_scale_thresh, exp_v_max=self.dist_scale_exp)
            if cntr % 1000 == 0:
                logging.info('Moving to coor=%s' % str(next_v._coor if next_v else ''))

            if next_v is None:
                if 0 <= cntr % 1000 <= 100:
                    logging.info('Jumping to next salient location, no unobserved neighs, number=%d' % cntr)

                # no unobserved neighs
                next_v, cur_intens, cur_obs = self.max_saliency()

                # print current img
                cur_image_segment = self.image_2d.copy()
                cur_image_segment[(cur_obs == 0)] = 255
                yield cur_image_segment

            cur_v = next_v

    def min_num_frames(self):
        return np.count_nonzero(self.intensity==0)