import math
import Material
import numpy as np
from numpy.linalg import norm
from log_ import *



class Element:

    def __init__(self, id, start_node, end_node, cross_section, material_id, local_dirs):
        self.id = id
        self.start_node = start_node
        self.end_node = end_node
        self.cross_section = cross_section
        self.material_id = material_id
        self.local_dirs = local_dirs

        yDiff = abs(start_node.p_y - end_node.p_y)
        xDiff = abs(start_node.p_x - end_node.p_x)
        zDiff = abs(start_node.p_z - end_node.p_z)

        self.length = math.sqrt(math.pow(yDiff, 2) + math.pow(xDiff, 2) + math.pow(zDiff, 2))

        # local_x = np.array([local_dirs[0]["x"], local_dirs[0]["y"], local_dirs[0]["z"]])
        # local_y = np.array([local_dirs[1]["x"], local_dirs[1]["y"], local_dirs[1]["z"]])
        # local_z = np.array([local_dirs[2]["x"], local_dirs[2]["y"], local_dirs[2]["z"]])

        global_x = np.array([1, 0, 0])
        global_y = np.array([0, 1, 0])
        global_z = np.array([0, 0, 1])

        local_x = np.array([local_dirs[0]["x"], local_dirs[0]["y"], local_dirs[0]["z"]])
        local_y = np.cross(global_z, local_x)

        if local_y[0]<0 and local_y[1]==0 and local_y[2]==0:
            local_y = -global_x
        elif np.linalg.norm(local_y)==0:
            local_y=global_x

        local_z = np.cross(local_x, local_y)


        # print("local_y", local_y)
        # print("local_z", local_z)

        self.theta_x_e = math.acos(np.inner(local_x, global_x) / (norm(local_x) * norm(global_x)))
        self.theta_y_e = math.acos(np.inner(local_x, global_y) / (norm(local_x) * norm(global_y)))
        self.theta_z_e = math.acos(np.inner(local_x, global_z) / (norm(local_x) * norm(global_z)))
        # print("Element id",self.id)
        # print("self.theta_x_e", self.theta_x_e)
        # print("self.theta_y_e", self.theta_y_e)
        # print("self.theta_z_e", self.theta_z_e)


    def transform(self):
        l = math.cos(self.theta_x_e)
        m = math.cos(self.theta_y_e)
        n = math.cos(self.theta_z_e)

        D = math.sqrt(math.pow(l, 2) + math.pow(m, 2))
        # print("l,m,n", [l, m, n])
        mat = np.array([[l, m, n],
                        [-m / D, l / D, 0],
                        [-l * n / D, -m * n / D, D]])

        trans_matrix = np.zeros((12, 12))
        trans_matrix[0:3, 0:3] += mat
        trans_matrix[3:6, 3:6] += mat
        trans_matrix[6:9, 6:9] += mat
        trans_matrix[9:12, 9:12] += mat

        # trans_matrix = np.array([[l, m, n, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                          [-m / D, l / D, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                          [-l * n / D, -m * n / D, D, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        #                          [0, 0, 0, l, m, n, 0, 0, 0, 0, 0, 0],
        #                          [0, 0, 0, -m / D, l / D, 0, 0, 0, 0, 0, 0, 0],
        #                          [0, 0, 0, -l * n / D, -m * n / D, D, 0, 0, 0, 0, 0, 0],
        #                          [0, 0, 0, 0, 0, 0, l, m, n, 0, 0, 0],
        #                          [0, 0, 0, 0, 0, 0, -m / D, l / D, 0, 0, 0, 0],
        #                          [0, 0, 0, 0, 0, 0, -l * n / D, -m * n / D, D, 0, 0, 0],
        #                          [0, 0, 0, 0, 0, 0, 0, 0, 0, l, m, n],
        #                          [0, 0, 0, 0, 0, 0, 0, 0, 0, -m / D, l / D, 0],
        #                          [0, 0, 0, 0, 0, 0, 0, 0, 0, -l * n / D, -m * n / D, D]])

        # print("trans_matrix\n",trans_matrix)
        return trans_matrix

    def K_element_local(self):

        material = Material.material_models[self.material_id]

        E = material.get_e()  # young's modulus
        G = material.get_g()  # shear modulus
        A = self.cross_section.get_area()  # area of the cross section
        L = self.length  # element length

        intertia = self.cross_section.calculate_inertia()

        J = intertia[0]
        Iy = intertia[1]
        Iz = intertia[2]

        a = E * A / L
        b = G * J / L

        c3 = (E * Iz) / (L ** 3)
        c2 = (E * Iz) / (L ** 2)  # value of mat_3
        c1 = (E * Iz) / (L)  # value of mat_3

        d3 = (E * Iy) / (L ** 3)  # value of mat_4
        d2 = (E * Iy) / (L ** 2)  # value of mat_4
        d1 = (E * Iy) / (L)  # value of mat_4

        # local_k_mat 12*12 element matrix
        local_k_mat = np.array([[a, 0, 0, 0, 0, 0, -a, 0, 0, 0, 0, 0],

                                [0, 12 * c3, 0, 0, 0, 6 * c2, 0, -12 * c3, 0, 0, 0, 6 * c2],

                                [0, 0, 12 * d3, 0, -6 * d2, 0, 0, 0, -12 * d3, 0, -6 * d2, 0],

                                [0, 0, 0, b, 0, 0, 0, 0, 0, -b, 0, 0],

                                [0, 0, -6 * d2, 0, 4 * d1, 0, 0, 0, 6 * d2, 0, 2 * d1, 0],

                                [0, 6 * c2, 0, 0, 0, 4 * c1, 0, -6 * c2, 0, 0, 0, 2 * c1],

                                [-a, 0, 0, 0, 0, 0, a, 0, 0, 0, 0, 0],

                                [0, -12 * c3, 0, 0, 0, -6 * c2, 0, 12 * c3, 0, 0, 0, -6 * c2],

                                [0, 0, -12 * d3, 0, 6 * d2, 0, 0, 0, 12 * d3, 0, 6 * d2, 0],

                                [0, 0, 0, -b, 0, 0, 0, 0, 0, b, 0, 0],

                                [0, 0, -6 * d2, 0, 2 * d1, 0, 0, 0, 6 * d2, 0, 4 * d1, 0],

                                [0, 6 * c2, 0, 0, 0, 2 * c1, 0, -6 * c2, 0, 0, 0, 4 * c1]])
        # print("local_k_mat \n", local_k_mat)

        return local_k_mat

    def K_element_global(self):
        trans_matrix = self.transform()
        mat1 = np.matmul(np.transpose(trans_matrix), self.K_element_local())

        global_k_mat = np.matmul(mat1, trans_matrix)

        # print("after transformation\n", global_k_mat[7][11])
        return global_k_mat
