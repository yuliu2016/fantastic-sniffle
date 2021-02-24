from Common_Libraries.quanser_sim_lib import QBot2e_sim


def get_pos_patch(self: QBot2e_sim):
    self._refresh()
    return self._world_xyz
QBot2e_sim.get_position = get_pos_patch