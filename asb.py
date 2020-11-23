from math import sqrt, atan2, pi
from random import randint
import matplotlib.pyplot as plt
import numpy as np

def make_line(coord1, S):
    """
    Returns the equation of the line that passes through coord1 and S
    :param coord1: (latitude, longitude) tuple -- is either A or B in the ASB method
    :param S: (latitude, longitude) tuple -- these are the coordinates of the busstop
    :return: (a, b, c) tuple -- parameters of the equation of the line passing through coord1 and S
                (where ax + by + c = 0)
    """
    x1, y1 = coord1
    x2, y2 = S
    a = y1 - y2
    b = x2 - x1
    c = (x1 - x2) * y1 + (y2 - y1) * x1
    return a, b, c

def lines_intersection(line1, line2):
    """
    Get the coordinate at which two lines intersect
    Used to assert that the lines cross at the busstop S
    :param line1: (a1, b1, c1) tuple -- parameters of the equation of line 1
    :param line2: (a2, b2, c2) tuple -- parameters of the equation of line 2
    :return: (latitude, longitude) tuple -- coordinate of the intersection of line 1 and 2
    """
    a1, b1, c1 = line1
    a2, b2, c2 = line2
    x = (b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1)
    y = (c1 * a2 - a1 * c2) / (a1 * b2 - a2 * b1)
    return x, y

def distance(coord1, coord2):
    x1, y1 = coord1
    x2, y2 = coord2
    return sqrt(((x1 - x2) ** 2) + ((y1 - y2) ** 2))


def get_angle_bisector(A, S, B):
    """
    Finds and returns the equation of the line that bisects the lines between A-S and S-B such that the angles
    between those lines are equal
    :param S: (latitude, longitude) tuple -- busstop coordinates
    :param A: (latitude, longitude) tuple -- first time in proximity of busstop coordinates
    :param B: (latitude, longitude) tuple -- last time in proximity of busstop coordinates
    :return: (a, b, c) tuple -- parameters of the equation of the angle bisector of lines A-S and S-B
    """

    # below is not completely correct, but an approximation to the angle bisector;
    # works if A and B do not have distances from S that are too different
    # Since in our case A and B are both approx r (=300?) away from S, this should work.
    midpoint_AB = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
    return make_line(midpoint_AB, S)

    # correct way, but does not work for all cases for some reason...
    """ 
    a1, b1, c1 = make_line(A, S)
    a2, b2, c2 = make_line(B, S)

    print(S)
    print(lines_intersection((a1, b1, c1), (a2, b2, c2)))

    denom1 = sqrt(a1 ** 2 + b1 ** 2)
    denom2 = sqrt(a2 ** 2 + b2 ** 2)

    # angle between A, S, and B
    angle_ASB = atan2(B[1] - S[1], B[0] - S[0]) - atan2(A[1] - S[1], A[0] - S[0])

    ASB_is_obtuse = False  # flag whether ASB angle > 0.5*pi
    if abs(angle_ASB) > 0.5 * pi:
        ASB_is_obtuse = True

    bisector1 = (a1 / denom1 - a2 / denom2,
                 b1 / denom1 - b2 / denom2,
                 c1 / denom1 - c2 / denom2)

    # if bisector1 has tan(theta) > 1, then it bisects the obtuse angle
    if abs((a1 * bisector1[1] - bisector1[0] * b1) / (a1 * bisector1[0] + b1 * bisector1[1])) > 1 and ASB_is_obtuse:
        return bisector1
    else:
        bisector2 = (a1 / denom1 + a2 / denom2,
                     b1 / denom1 + b2 / denom2,
                     c1 / denom1 + c2 / denom2)
        return bisector2
    """


def is_past_angle_bisector(A, coord, angle_bisector):
    """
    Checks whether a coordinate is on the other side of the angle bisector compared to A
    :param A: (latitude, longitude) tuple --  the coordinates where the bus is coming from (coordinates of when the bus
    enters the circle around the busstop for the first time)
    :param coord: (latitude, longitude) tuple -- the coordinates for which we want to check
    whether it is on the other side of the line compared to A or not
    :param angle_bisector: (a, b, c) tuple -- parameters of the equation of the angle bisector
    :return: True if coord is on the other side of the line compared to A, False otherwise
    """
    a1, b1, c1 = angle_bisector
    value_A = a1 * A[0] + b1 * A[1] + c1
    value_coord = a1 * coord[0] + b1 * coord[1] + c1

    if (value_A <= 0 and value_coord <= 0) or (value_A >= 0 and value_coord >= 0):
        return False
    else:
        return True

def visualize_ASB(A, S, B, coord, R=2):
    # plot lines
    a1, b1, c1 = make_line(A, S)
    a2, b2, c2 = make_line(B, S)

    # line AS
    x1 = np.linspace(S[0] - R * 1.25, S[0] + R * 1.25, 100)
    y1 = -a1/b1 * x1 - c1/b1
    plt.plot(x1, y1, '-g', label='line AS')

    # line BS
    x2 = np.linspace(S[0] - R * 1.25, S[0] + R * 1.25, 100)
    y2 = -a2/b2 * x2 - c2/b2
    plt.plot(x2, y2, '-b', label='line BS')

    # angle bisector
    a3, b3, c3 = get_angle_bisector(A, S, B)
    x3 = np.linspace(S[0] - R * 1.25, S[0] + R * 1.25, 100)
    y3 = -a3 / b3 * x3 - c3 / b3
    plt.plot(x3, y3, '-r', label='Angle Bisector')

    # A, S, B
    plt.plot(A[0], A[1], 'go')
    plt.plot(B[0], B[1], 'bo')
    plt.plot(S[0], S[1], 'ro')

    # coord
    plt.plot(coord[0], coord[1], 'ro')

    plt.title(f'Coord is past angle bisector? {is_past_angle_bisector(A, coord, (a3, b3, c3))}')

    # circle with radius R centered around S
    """ TODO
    theta = np.linspace(0, 2 * np.pi, 100)
    x1 = R * np.cos(theta)
    x2 = R * np.sin(theta)
    plt.plot(x1, x2, color='black')
    """

    plt.xlabel('x', color='#1C2833')
    plt.ylabel('y', color='#1C2833')
    plt.legend(loc='upper left')
    plt.grid()
    plt.show()
