import isx
import numpy as np
import video_helper as helper
import os

# folder with videos to convert to the .isxd file.
# all video files with .avi extension in this folder will be concateneted in to one .isxd file.
# is there more than one file they need to have proper names, becase they are sorted alphabetically:
# e.g. video10.avi comes for video2.avi. right names can look like: video02.avi and video10.avi
folder = "minian"

files_to_convert = []
total_frames = 0
fps = 0
width = 0
height = 0
for file in os.listdir(folder):
    if file.endswith(".avi"):
        files_to_convert.append(file)

        info = helper.get_video_info(f"{folder}/{file}")
        total_frames += info["frame_count"]
        fps = info["fps"]
        width = info["width"]
        height = info["height"]


timing = isx.Timing(num_samples=total_frames, period=isx.Duration.from_msecs(1000/fps))
spacing = isx.Spacing(num_pixels=(height, width))
data_type = np.float32

try:
    os.remove(f"{folder}/movie.isxd")
except:
    pass

movie = isx.Movie.write(f"{folder}/movie.isxd", timing, spacing, np.float32)

video_nbr = 0
for f in files_to_convert:
    video_nbr += 1
    print(f"convert video: {f} - {video_nbr} from {len(files_to_convert)}")
    frames = helper.read_video_all_frames(f"{folder}/{f}", grayscale=True)
    for i in range(len(frames)):
        frame = frames[i].astype(np.float32) / 255
        movie.set_frame_data(i, frame)

movie.flush()
print("done!")