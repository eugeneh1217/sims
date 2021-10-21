import os
import numpy as np

class Settings:
    log_path = '.logs'
    live_fps = 100
    frame_save_path = os.path.join('sims', 'data', 'hurdles', 'frames')
    video_out_path = os.path.join('/mnt', 'c', 'Users', 'eugen', 'Desktop', 'simsdata', 'new')
    video_fps = 30

    map_size = np.array([640, 480])
    gravity = np.array([0, -1])
    ground_height = 100
    frames = 200

    hurdler_height = 30
    hurdler_width = 30
    hurdler_x_spawn = 100
    hurdler_jump_speed = 17
    jump_interval = 15

    hurdle_height = 50
    hurdle_width = 50
    hurdle_drift = np.array([-10, 0])
    hurdle_spawn_x = 480
