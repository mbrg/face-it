
import matplotlib.pyplot as plt
from matplotlib import animation, rc, use
use('Agg')

from os.path import join
import sys
import argparse
from subprocess import Popen, PIPE

import logging

import cv2
import numpy as np

OBSERVED_VALUE = 0
IMAGE_SHAPE = (512, 512)


def argument_parser():
    parser = argparse.ArgumentParser(description='Painter')
    parser.add_argument('--thresh', dest='dist_treshold', default=40, type=int)
    parser.add_argument('--frame_limit', dest='frame_limit', default=8000, type=int)
    parser.add_argument('--frame_msec', dest='msecs_per_frame', default=6, type=int)
    parser.add_argument('--fps', dest='frames_per_sec', default=None, type=int)

    parser.add_argument('--root', dest='project_root', default='/home/dsteam/repos/face-it/', type=str)
    parser.add_argument('--out', dest='output_path', default='painter/or_vid.mp4', type=str)
    parser.add_argument('--image', dest='image_path', default='painter/examples/or.jpg', type=str)
    parser.add_argument('--prepro', dest='image_prepro', default='painter/image_preprocessor.py', type=str)
    parser.add_argument('--tmp', dest='tmp_path', default='painter/examples/tmp.jpg', type=str)
    parser.add_argument('--xml', dest='xml_path', type=str, default='data/haarcascade_frontalface_alt.xml')

    return parser.parse_args()


def main():
    args = argument_parser()

    # Dependecies imports
    sys.path.extend([args.project_root, ])
    from painter.saliency.vid_painter import Painter

    # read image
    cmnd = "source activate image_pp; %s --image='%s' --grey='%s' --xml='%s'; source deactivate" \
           % (join(args.root,args.image_prepro), join(args.root,args.image_path),
              join(args.root, args.tmp_path), join(args.root, args.xml_path))
    process = Popen(cmnd, shell=True, stdout=PIPE)
    process.wait()
    image_segment = cv2.imread(join(args.root, args.tmp_path))

    # create an MRF and Saliancy agent
    painter = Painter(image_segment, dist_scale_thresh=args.dist_treshold, image_shape=IMAGE_SHAPE, observed_value=OBSERVED_VALUE)
    frame_gen = painter.frame_gen()

    # prepare figure
    fig = plt.figure()
    plt.axis('off')

    # init video variables
    blank_img = np.multiply(np.ones(IMAGE_SHAPE), 255).astype(np.int)
    blank_img[0] = 0
    im = plt.imshow(blank_img, 'gray', animated=True)
    cur_frame, frame_cntr = None, 0

    # define frame producing function
    def updatefig(*args):
        global frame_cntr
        frame_cntr += 1
        if frame_cntr % 1000 == 0:
            logging.info('**********Recoded frame number %d**********' % frame_cntr)
        try:
            cur_frame = frame_gen.next()
        except StopIteration:
            pass
        im.set_array(cur_frame)
        return im,

    # animate and record
    ani = animation.FuncAnimation(fig, updatefig, frames=args.frame_limit, interval=args.msecs_per_frame, blit=True)
    rc('animation', html='html5')
    writer = animation.FFMpegWriter()
    ani.save(args.join(args.root, args.output_path), writer=writer, fps=args.fps)

if __name__ == '__main__':
    main()
