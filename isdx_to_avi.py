import isx
import video_helper as helper

# set the inscopix movie file name which will be converted to .mp4
file = "test/movie.isxd"
# name of the .mp4 video file
res_file = "test/test.mp4"
# pattern for splited files
split_pattern = "test/msCam"
# max frames in splited file
split_frames = 2400

# open inscopix movie file
movie = isx.Movie.read(file)

# save the inscopix movie as mp4
isx.export_movie_to_mp4(file, res_file, 0.9)

# Split video into segments of spcefied frames
helper.split_video_by_frames(res_file, split_pattern, split_frames)
