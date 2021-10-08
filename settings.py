import os
import numpy as np

class Settings:
    log_path = '.logs'
    live_fps = 100
    frame_save_path = os.path.join('data', 'frames')
    video_out_path = os.path.join('data', 'videos')

    gravity = np.array([0, -3])
    ground_height = 100

    hurdler_height = 100
    hurdler_width = 100
    hurdler_jump_speed = 10

    hurdle_height = 50
    hurdle_width = 50
    hurdle_drift = np.array([-10, 0])
    hurdle_spawn_x = 900

    replay_fps = 60