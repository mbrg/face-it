"""
Implements conversion functions between a 2D plane (a square) and 1D curves.
"""

class Curve_2D(object):

    def __init__(self, n, start_coor):
        """
        Initializes a curve object
        :param n: number of coordinates in each row/col.
        :param start_coor: 2D coordinate. options: from (0,0) to (n-1,n-1).
        """
        assert(0<=start_coor[0]<=n-1 and 0<=start_coor[1]<=n-1)

        self._n = n
        self._start_coor = start_coor
        self._cur_coor = start_coor

    def next_coor(self):
        """
        Iterate to and return the next coordinate in the curve.
        If curve ends, returns to start_coor.
        """
        self._cur_coor = self._next_coor()
        return self._cur_coor

    def _next_coor(self):
        """
        Return the next coordinate in the curve.
        To be overridden by inheriting classes.
        """
        return self._start_coor


class Hilbert_Curve(Curve_2D):

    def __init__(self, n, start_coor):
        """
        Initializes a curve object
        :param n: length of the curve
        :param start_coor: 2D coordinate
        """
        assert (Hilbert_Curve._is_power_of_two(n))
        super(Hilbert_Curve, self).__init__(n, start_coor)

    def _next_coor(self):
        """
        Return the next coordinate in the Hilbert curve.
        """
        next_distance = self.coor_to_distance(self._n, self._cur_coor) + 1

        # verify curve hasn't added
        if next_distance<(pow(self._n, 2) - 1):
            return self.distance_to_coor(self._n, next_distance)
        else:
            return self._start_coor

    @staticmethod
    def coor_to_distance(n, coor):
        """
        Converts a 2D coordinate to a 1D coordinate on a Hilbert curve of length n
        :param n: number of coordinates in each row/col. n must be a power of 2.
        :param coor: 2D coordinate
        :return: 1D coordinate on a Hilbert curve of range 0 to n^2 -1
        """
        assert(Hilbert_Curve._is_power_of_two(n))

        # variables
        d = 0
        s = n//2
        x, y = coor

        while s>0:
            rx = (x & s) > 0
            ry = (y & s) > 0
            d += pow(s,2) * ((3 * rx) ^ ry)
            x, y = Hilbert_Curve._rotation(s, (x, y), rx, ry)
            s //= 2  # iteration
        return d

    @staticmethod
    def distance_to_coor(n, d):
        """
        Converts a 1D coordinate on a Hilbert curve of length n to a 2D coordinate
        :param n: number of coordinates in each row/col. n must be a power of 2.
        :param d: 1D coordinate on a Hilbert curve of range 0 to n^2 -1
        :return: 2D coordinate
        """
        assert(Hilbert_Curve._is_power_of_two(n))
        assert(d<=(pow(n,2)-1))

        # variables
        t = d
        s = 1
        x = y = 0

        while s<n:
            rx = 1 & (t // 2)
            ry = 1 & (t ^ rx)
            x, y = Hilbert_Curve._rotation(s, (x, y), rx, ry)
            x += s * rx
            y += s * ry
            t //= 4
            s *= 2  # iteration
        return x, y

    @staticmethod
    def _rotation(n, coor, rx, ry):
        """
        rotate/flip a quadrant appropriately
        :param n: number of coordinates in each row/col. n must be a power of 2.
        :param coor: 2D coordinate
        :param rx: to rotate x?
        :param ry: to rotate y?
        :return: rotated coor
        """
        assert (Hilbert_Curve._is_power_of_two(n))

        # variables
        x, y = coor

        if (ry == 0):
            if rx == 1:
                x = n - 1 - x
                y = n - 1 - y

            # Swap x and y
            t  = x
            x = y
            y = t

        return x, y

    @staticmethod
    def _is_power_of_two(n):
        return ((n!=0) and ((n & (n-1)) == 0))


class Line_Curve(Curve_2D):

    def __init__(self, n, start_coor):
        """
        Initializes a curve object
        :param n: number of coordinates in each row/col.
        :param start_coor: 2D coordinate
        """
        super(Line_Curve, self).__init__(n, start_coor)

    def _next_coor(self):
        """
        Return the next coordinate in the curve.
        To be overridden by inheriting classes.
        """

        # variable
        coor = self._cur_coor
        n = self._n

        # reached end
        if coor == (n-1, n-1):
            return self._start_coor
        # reached right corner, going right
        if coor[1]==n-1 and coor[0]%2==0:
            return coor[0]+1 ,n-1
        # reached left corner, going left
        if coor[1]==0 and coor[0]%2==1:
            return coor[0]+1 ,0

        # going left
        if coor[0] % 2 == 1:
            return coor[0], coor[1] - 1
        # going right
        if coor[0] % 2 == 0:
            return coor[0], coor[1] + 1

        if coor[1]==n-1:
            return coor[0]+1 ,0