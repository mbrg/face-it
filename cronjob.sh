source activate saliency
for file in /home/dsteam/repos/face-it/web-service/tmp/*; do
 filename=$({file%.*g})
 vid_output=$(filename.mp4)
 gif_output=$(filename.gif)
 python /home/dsteam/repos/face-it/painter/main.py --frame_msec 6 --out $vid_output  --image $d --frame_limit 20000 --fps 166
 wait
 ffmpeg -i $vid_output -vf scale=320:-1 -r 10 -f image2pipe -vcodec ppm - | convert -delay 5 -loop 0 - $gif_output
 wait
 rm /home/dsteam/repos/face-it/web-service/tmp/*.jpg
 wait
 rm /home/dsteam/repos/face-it/web-service/tmp/*.mp4
done
source deactivate