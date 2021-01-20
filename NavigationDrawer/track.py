import numpy as np
import math
import csv

def read_csv(path):
    time = []
    x_acceleration = []
    y_acceleration = []
    z_acceleration = []
    x_rotation = []
    y_rotation = []
    z_rotation = []
    with open(path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            time.append(row[0])
            x_acceleration.append(row[1])
            y_acceleration.append(row[2])
            z_acceleration.append(row[3])
            x_rotation.append(row[4])
            y_rotation.append(row[5])
            z_rotation.append(row[6])
    return time, x_acceleration, y_acceleration, z_acceleration, x_rotation, y_rotation, z_rotation

def integrate(accvals, t):
    velocity = cumtrapz(accvals, t, initial=0)
    position = cumtrapz(velocity, t, initial=0)
    return position


def moving_average(data, window=10):
    cumsum_vec = np.cumsum(np.insert(data, 0, 0))
    ma_vec = (cumsum_vec[window:] - cumsum_vec[:-window]) / window
    return ma_vec



def rotation_matrix(x, y, z, vx, vy, vz):
    pos = []
    for i in range(len(x)):
        xangle = vx[i]
        yangle = vy[i]
        zangle = vz[i]
        if i == 0:
            distx = 0
            disty = 0
            distz = 0
        else:
            distx = x[i] - x[i - 1]
            disty = y[i] - y[i - 1]
            distz = z[i] - z[i - 1]
        RX = np.array([[1, 0, 0],
                       [0, math.cos(xangle), -math.sin(xangle)],
                       [0, math.sin(xangle), math.cos(xangle)]])
        RY = np.array([[math.cos(yangle), 0, math.sin(yangle)],
                       [0, 1, 0],
                       [-math.sin(yangle), 0, math.cos(yangle)]])
        RZ = np.array([[math.cos(zangle), -math.sin(zangle), 0],
                       [math.sin(zangle), math.cos(zangle), 0],
                       [0, 0, 1]])
        R = RX.dot(RZ.dot(RY))
        R = np.squeeze(np.asarray(R))
        vector = np.array([[distx],
                           [disty],
                           [distz]])
        coordinates = R.dot(vector)
        pos.append(coordinates)
    return pos

def tupleset(t, i, value):
    l = list(t)
    l[i] = value
    return tuple(l)

def cumtrapz(y, x=None, dx=1.0, axis=-1, initial=None):
    """
    Cumulatively integrate y(x) using the composite trapezoidal rule.

    Parameters
    ----------
    y : array_like
        Values to integrate.
    x : array_like, optional
        The coordinate to integrate along. If None (default), use spacing `dx`
        between consecutive elements in `y`.
    dx : float, optional
        Spacing between elements of `y`. Only used if `x` is None.
    axis : int, optional
        Specifies the axis to cumulate. Default is -1 (last axis).
    initial : scalar, optional
        If given, insert this value at the beginning of the returned result.
        Typically this value should be 0. Default is None, which means no
        value at ``x[0]`` is returned and `res` has one element less than `y`
        along the axis of integration.

    Returns
    -------
    res : ndarray
        The result of cumulative integration of `y` along `axis`.
        If `initial` is None, the shape is such that the axis of integration
        has one less value than `y`. If `initial` is given, the shape is equal
        to that of `y`.

    See Also
    --------
    numpy.cumsum, numpy.cumprod
    quad: adaptive quadrature using QUADPACK
    romberg: adaptive Romberg quadrature
    quadrature: adaptive Gaussian quadrature
    fixed_quad: fixed-order Gaussian quadrature
    dblquad: double integrals
    tplquad: triple integrals
    romb: integrators for sampled data
    ode: ODE integrators
    odeint: ODE integrators

    """
    y = np.asarray(y)
    if x is None:
        d = dx
    else:
        x = np.asarray(x)
        if x.ndim == 1:
            d = np.diff(x)
            # reshape to correct shape
            shape = [1] * y.ndim
            shape[axis] = -1
            d = d.reshape(shape)
        elif len(x.shape) != len(y.shape):
            raise ValueError("If given, shape of x must be 1-D or the "
                             "same as y.")
        else:
            d = np.diff(x, axis=axis)

        if d.shape[axis] != y.shape[axis] - 1:
            raise ValueError("If given, length of x along axis must be the "
                             "same as y.")

    nd = len(y.shape)
    slice1 = tupleset((slice(None),) * nd, axis, slice(1, None))
    slice2 = tupleset((slice(None),) * nd, axis, slice(None, -1))
    res = np.cumsum(d * (y[slice1] + y[slice2]) / 2.0, axis=axis)

    if initial is not None:
        if not np.isscalar(initial):
            raise ValueError("`initial` parameter should be a scalar.")

        shape = list(res.shape)
        shape[axis] = 1
        res = np.concatenate([np.full(shape, initial, dtype=res.dtype), res],
                             axis=axis)

    return res




def calculate_path(path):
    time, x_acc, y_acc, z_acc, x_rot, y_rot, z_rot = read_csv(path)

    for i in range(len(time)):
        time[i] = float(time[i])
    tsim = time[4] - time[3]


    for i in range(len(x_acc)):
        x_acc[i] = float(x_acc[i])
        y_acc[i] = float(y_acc[i])
        z_acc[i] = float(z_acc[i])
        x_rot[i] = float(x_rot[i])
        y_rot[i] = float(y_rot[i])
        z_rot[i] = float(z_rot[i])

    x_acc_off = (sum(x_acc) / len(x_acc))
    y_acc_off = (sum(y_acc) / len(y_acc))
    z_acc_off = (sum(z_acc) / len(z_acc))
    x_rot_off = (sum(x_rot) / len(x_rot))
    y_rot_off = (sum(y_rot) / len(y_rot))
    z_rot_off = (sum(z_rot) / len(z_rot))

    for i in range(len(x_acc)):
        x_acc[i] = float(x_acc[i]) - x_acc_off
        y_acc[i] = float(y_acc[i]) - y_acc_off
        z_acc[i] = float(z_acc[i]) - z_acc_off
        x_rot[i] = float(x_rot[i]) - x_rot_off
        y_rot[i] = float(y_rot[i]) - y_rot_off
        z_rot[i] = float(z_rot[i]) - z_rot_off

    x_acc_filtered = moving_average(x_acc)
    y_acc_filtered = moving_average(y_acc)
    z_acc_filtered = moving_average(z_acc)
    x_rot_filtered = moving_average(x_rot)
    y_rot_filtered = moving_average(y_rot)
    z_rot_filtered = moving_average(z_rot)

    t_int = np.linspace(0, len(x_acc_filtered) * tsim, len(x_acc_filtered))

    x_angle_f = cumtrapz(x_rot_filtered, t_int, initial=0)
    y_angle_f = cumtrapz(y_rot_filtered, t_int, initial=0)
    z_angle_f = cumtrapz(z_rot_filtered, t_int, initial=0)

    y_pos_f = integrate(y_acc_filtered, t_int)
    x_pos_f = integrate(x_acc_filtered, t_int)
    z_pos_f = integrate(z_acc_filtered, t_int)

    position = rotation_matrix(x_pos_f, y_pos_f, z_pos_f, x_angle_f, y_angle_f, z_angle_f)

    pos_x = []
    pos_y = []
    pos_z = []

    for i in range(len(position)):
        pos_x.append(float(position[i][0]))
        pos_y.append(float(position[i][1]))
        pos_z.append(float(position[i][2]))

    return pos_x, pos_y, pos_z
