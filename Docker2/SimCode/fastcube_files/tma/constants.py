class MA:
    MA1 = 'MA1'
    MA2 = 'MA2'
    MA3 = 'MA3'
    MA4 = 'MA4'

class Observation:
    GROUND_AVOIDANCE = [0, 0, 0, 0, 0]

    TRACK = [0, 0, 0, 1]
    OUT_TRACK_INSIDE_SNAP = [0, 0, 1, 0]
    INSIDE_GUN = [0, 0, 1, 1]

    FLIGHT_PATH_OVERSHOOT = [0, 0, 1, 0, 0]
    DEFENSIVE_OVERSHOOT = [0, 0, 1, 0, 1]

    TAIL_CHASE = [0, 0, 1, 1, 0]
    TURN_CIRCLE_ALIGNMENT = [0, 0, 1, 1, 1]
    TURN_CIRCLE_ENTRY = [0, 1, 0, 0, 0]
    MAINTAIN_CLOSE_RANGE = [0, 1, 0, 0, 1]

    NEUTRAL_AWAY = [0, 1, 0, 1, 0]
    NEUTRAL_OPENING = [0, 1, 0, 1, 1]


class StateInfo:
    SELF_COLOR = 'blue'
    BANDIT_COLOR = 'red'

    SELF_POSITION_H_SL_FT = SELF_COLOR + "_position_h_sl_ft"

    SELF_ATTITUDE_ROLL_RAD = SELF_COLOR + "_attitude_roll_rad"
    SELF_ATTITUDE_PITCH_RAD = SELF_COLOR + "_attitude_pitch_rad"
    SELF_ATTITUDE_PSI_DEG = SELF_COLOR + "_attitude_psi_deg"

    SELF_VELOCITIES_U_FPS = SELF_COLOR + "_velocities_u_fps"
    SELF_VELOCITIES_V_FPS = SELF_COLOR + "_velocities_v_fps"
    SELF_VELOCITIES_W_FPS = SELF_COLOR + "_velocities_w_fps"

    SELF_VELOCITIES_P_RAD_SEC = SELF_COLOR + "_velocities_p_rad_sec"
    SELF_VELOCITIES_Q_RAD_SEC = SELF_COLOR + "_velocities_q_rad_sec"
    SELF_VELOCITIES_R_RAD_SEC = SELF_COLOR + "_velocities_r_rad_sec"

    SELF_ACCELERATIONS_UDOT_FT_SEC2 = SELF_COLOR + "_accelerations_udot_ft_sec2"
    SELF_ACCELERATIONS_VDOT_FT_SEC2 = SELF_COLOR + "_accelerations_vdot_ft_sec2"
    SELF_ACCELERATIONS_WDOT_FT_SEC2 = SELF_COLOR + "_accelerations_wdot_ft_sec2"

    SELF_ACCELERATIONS_PDOT_RAD_SEC2 = SELF_COLOR + "_accelerations_pdot_rad_sec2"
    SELF_ACCELERATIONS_QDOT_RAD_SEC2 = SELF_COLOR + "_accelerations_qdot_rad_sec2"
    SELF_ACCELERATIONS_RDOT_RAD_SEC2 = SELF_COLOR + "_accelerations_rdot_rad_sec2"

    SELF_AERO_ALPHA_DEG = SELF_COLOR + "_aero_alpha_deg"
    SELF_AERO_BETA_DEG = SELF_COLOR + "_aero_beta_deg"

    SELF_FCS_AILERON_POS_NORM = SELF_COLOR + "_fcs_aileron_pos_norm"
    SELF_FCS_ELEVATOR_POS_NORM = SELF_COLOR + "_fcs_elevator_pos_norm"
    SELF_FCS_RUDDER_POS_NORM = SELF_COLOR + "_fcs_rudder_pos_norm"
    SELF_FCS_THROTTLE_POS_NORM = SELF_COLOR + "_fcs_throttle_pos_norm"

    SELF_FCS_PROPULSION_TOTAL_FUEL_LBS = SELF_COLOR + "_propulsion_total_fuel_lbs"
    SELF_SIMULATION_TIME_SEC = SELF_COLOR + "_simulation_sim_time_sec"
    SELF_PROPULSION_ENGINE_THRUST_LBS = SELF_COLOR + "_propulsion_engine_thrust_lbs"
    SELF_PROPULSION_ENGINE_1_THRUST_LBS = SELF_COLOR + "_propulsion_engine_1_thrust_lbs"

    SELF_X_POSITION = SELF_COLOR + "_x_position_ft"
    SELF_Y_POSITION = SELF_COLOR + "_y_position_ft"
    SELF_Z_POSITION = SELF_COLOR + "_z_position_ft"

    SELF_DISTANCE_FT = SELF_COLOR + "_distance_ft"

    SELF_TRACK_ANG_RAD = SELF_COLOR + "_track_ang_rad"
    SELF_SCORE_BLUE_SNAPPED = SELF_COLOR + "_score_" + SELF_COLOR + "_snapped"
    SELF_SCORE_TRACK_STATE = SELF_COLOR + "_score_track_state"
    SELF_SCORE_FLOOR_HEIGHT = SELF_COLOR + "_score_floor_height"
    SELF_SCORE_WALL_NEAR = SELF_COLOR + "_score_wall_near"
    SELF_SCORE_BANDIT_SNAPPED = SELF_COLOR + "_score_" + BANDIT_COLOR + "_snapped"

    BANDIT_POSITION_H_SL_FT = BANDIT_COLOR + "_position_h_sl_ft"

    BANDIT_ATTITUDE_ROLL_RAD = BANDIT_COLOR + "_attitude_roll_rad"
    BANDIT_ATTITUDE_PITCH_RAD = BANDIT_COLOR + "_attitude_pitch_rad"
    BANDIT_ATTITUDE_PSI_DEG = BANDIT_COLOR + "_attitude_psi_deg"

    BANDIT_VELOCITIES_U_FPS = BANDIT_COLOR + "_velocities_u_fps"
    BANDIT_VELOCITIES_V_FPS = BANDIT_COLOR + "_velocities_v_fps"
    BANDIT_VELOCITIES_W_FPS = BANDIT_COLOR + "_velocities_w_fps"

    BANDIT_VELOCITIES_P_RAD_SEC = BANDIT_COLOR + "_velocities_p_rad_sec"
    BANDIT_VELOCITIES_Q_RAD_SEC = BANDIT_COLOR + "_velocities_q_rad_sec"
    BANDIT_VELOCITIES_R_RAD_SEC = BANDIT_COLOR + "_velocities_r_rad_sec"

    BANDIT_X_POSITION = BANDIT_COLOR + "_x_position_ft"
    BANDIT_Y_POSITION = BANDIT_COLOR + "_y_position_ft"
    BANDIT_Z_POSITION = BANDIT_COLOR + "_z_position_ft"