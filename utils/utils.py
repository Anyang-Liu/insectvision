import numpy as np
import numpy.linalg as la


def rotation_matrix(theta):
    return np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])


def angle_between(ang1, ang2, sign=True):
    d = (ang1 - ang2 + np.pi) % (2 * np.pi) - np.pi
    if not sign:
        d = np.abs(d)
    return d


def sph2vec(theta, phi=None, rho=1.):
    """
    Transforms the spherical coordinates to a cartesian 3D vector.
    :param theta: elevation
    :param phi:   azimuth
    :param rho:   radius length
    :return vec:    the cartessian vector
    """
    if phi is None:
        if theta.ndim == 1:
            phi = theta[1]
            if theta.shape[0] > 2:
                rho = theta[2]
            theta = theta[0]
        else:
            phi = theta[..., 1]
            if theta.shape[1] > 2:
                rho = theta[..., 2]
            theta = theta[..., 0]

    x = rho * (np.sin(phi) * np.cos(theta))
    y = rho * (np.cos(phi) * np.cos(theta))
    z = rho * np.sin(theta)

    return np.asarray([x, y, z]).T


def vec2sph(vec):
    """
    Transforms a cartessian vector to spherical coordinates.
    :param vec:     the cartessian vector
    :return theta:  elevation
    :return phi:    azimuth
    :return rho:    radius
    """
    rho = la.norm(vec, axis=-1)  # length of the radius

    if vec.ndim == 1:
        if rho == 0:
            rho = 1.
        v = vec / rho  # normalised vector
        phi = np.arctan2(v[0], v[1])  # azimuth
        theta = np.pi / 2 - np.arccos(v[2])  # elevation
    else:
        rho[rho == 0] = 1.
        v = vec / rho  # normalised vector
        phi = np.arctan2(v[..., 0], v[..., 1])  # azimuth
        theta = np.pi / 2 - np.arccos(v[..., 2])  # elevation

    theta, phi = sphadj(theta, phi)  # bound the spherical coordinates
    return np.asarray([theta, phi, rho]).T


# conditions to restrict the angles to correct quadrants
def eleadj(theta):
    """
    Adjusts the elevation in [-pi, pi]
    :param theta:   the elevation
    """
    theta, _ = sphadj(theta=theta)
    return theta


def aziadj(phi):
    """
    Adjusts the azimuth in [-pi, pi].
    :param phi: the azimuth
    """
    _, phi = sphadj(phi=phi)
    return phi


def sphadj(theta=None, phi=None,
           theta_min=-np.pi / 2, theta_max=np.pi / 2,  # constrains
           phi_min=-np.pi, phi_max=np.pi):
    """
    Adjusts the spherical coordinates using the given bounds.
    :param theta:       the elevation
    :param phi:         the azimuth
    :param theta_min:   the elevation lower bound (default -pi/2)
    :param theta_max:   the elevation upper bound (default pi/2)
    :param phi_min:     the azimuth lower bound (default -pi)
    :param phi_max:     the azimuth upper bound (default pi)
    """

    # change = np.any([theta < -np.pi / 2, theta > np.pi / 2], axis=0)
    if theta is not None:
        if (theta >= theta_max).all():
            theta = np.pi - theta
            if np.all(phi):
                phi += np.pi
        elif (theta < theta_min).all():
            theta = -np.pi - theta
            if np.all(phi):
                phi += np.pi
        elif (theta >= theta_max).any():
            theta[theta >= theta_max] = np.pi - theta[theta >= theta_max]
            if np.all(phi):
                phi[theta >= theta_max] += np.pi
        elif (theta < theta_min).any():
            theta[theta < theta_min] = -np.pi - theta[theta < theta_min]
            if np.all(phi):
                phi[theta < theta_min] += np.pi

    if phi is not None:
        while (phi < phi_min).all():
            phi += 2 * np.pi
        while (phi >= phi_max).all():
            phi -= 2 * np.pi
        while (phi < phi_min).any():
            phi[phi < phi_min] += 2 * np.pi
        while (phi >= phi_max).any():
            phi[phi >= phi_max] -= 2 * np.pi

    return theta, phi


def vec2pol(vec, y=None):
    """
    Converts a vector to polar coordinates.
    """
    if y is None:
        rho = np.sqrt(np.square(vec[..., 0:1]) + np.square(vec[..., 1:2]))
        phi = np.arctan2(vec[..., 1:2], vec[..., 0:1])

        return np.append(rho, phi, axis=-1)
    else:
        rho = np.sqrt(np.square(vec) + np.square(y))
        phi = np.arctan2(vec, y)

        return rho, phi


def pol2vec(pol, phi=None):
    """
    Convert polar coordinates to vector.
    """
    if phi is None:
        rho = pol[..., 0:1]
        phi = pol[..., 1:2]

        return rho * np.append(np.cos(phi), np.sin(phi), axis=-1)
    else:
        return pol * np.cos(phi), pol * np.sin(phi)


def azirot(vec, phi):
    """
    Rotate a vector horizontally and clockwise.
    :param vec: the 3D vector
    :param phi: the azimuth of the rotation
    """
    Rz = np.asarray([
        [np.cos(phi), -np.sin(phi), 0],
        [np.sin(phi), np.cos(phi), 0],
        [0, 0, 1]]
    )

    return Rz.dot(vec)


if __name__ == "__main__":
    v = np.array([[1, 0, 0]], dtype=float)
    s = vec2sph(v)
    print np.rad2deg(s)
    print sph2vec(s)
