import math

def angleToRad(angle):
    angle = angle % 360
    if angle > 180:
        angle = angle - 360
    return math.radians(angle)

def angleToDeg(angle):
    angle = math.degrees(angle)
    if angle > 180:
        return angle - 360
    else:
        return angle

def quaternion_to_angle_axis(x, y=0, z=0, w=0, fusion=False):
    # convert to angle-axis from ([x, y, z, w], fusion=False) or (x, y, z, w, fusion=False) or ({"qx":x, "qy":y, "qz":z, "qw":w}, fusion=False) Quaternion angle
    # return [angle, x, y, z] angle-axis angle if fusion is false
    # return [x, y, z] angle*axis angle if fusion is true

    if isinstance(x,dict): # only one parameter ==> dict
        w = x["qx"]
        y = x["qy"]
        z = x["qz"]
        x = x["qw"]
    if isinstance(x,(tuple, list)): # only one parameter ==> list
        y = x[1]
        z = x[2]
        w = x[3]
        x = x[0]
    
    longueur = math.sqrt(x * x + y * y + z * z + w * w) #normalization
    x = x / longueur
    y = y / longueur
    z = z / longueur
    w = w / longueur

    angle = 2 * math.acos(w)
    if (1 - (w * w) < 0.0001): #axe aleatoire => doesnt matter => fixed to z
        X = 0
        Y = 0
        Z = 1
    else:
        # http://www.euclideanspace.com/maths/geometry/rotations/conversions/quaternionToAngle/
        s = math.sqrt(1 - (w * w))
        X = x / s
        Y = y / s
        Z = z / s

    if fusion:
        return [X*angle, Y*angle, Z*angle]
    else:
        return [angle, X, Y, Z]

def quaternion_to_euler(x, y=0, z=0, w=0):
    #convert to euler from ([x, y, z, w]) or (x, y, z, w) or {"qx":x, "qy":y, "qz":z, "qw":w} Quaternion angle
    # return x, y, z euler angle 
    if isinstance(x,dict): # only one parameter ==> dict
        w = x["qx"]
        y = x["qy"]
        z = x["qz"]
        x = x["qw"]
    if isinstance(x,(tuple, list)): # only one parameter ==> list
        y = x[1]
        z = x[2]
        w = x[3]
        x = x[0]

    ysqr = y * y

    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + ysqr)
    X = math.atan2(t0, t1)

    t2 = +2.0 * (w * y - z * x)

    t2 = max(min(t2, 1), -1)
    Y = math.asin(t2)

    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (ysqr + z * z)
    Z = math.atan2(t3, t4)

    return [X, Y, Z]

def euler_to_quaternion(yaw, pitch=0, roll=0):
        if isinstance(yaw,(tuple, list)):
            pitch = yaw[1]
            roll = yaw[2]
            yaw = yaw[0]
        qx = math.sin(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) - math.cos(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)
        qy = math.cos(roll/2) * math.sin(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.cos(pitch/2) * math.sin(yaw/2)
        qz = math.cos(roll/2) * math.cos(pitch/2) * math.sin(yaw/2) - math.sin(roll/2) * math.sin(pitch/2) * math.cos(yaw/2)
        qw = math.cos(roll/2) * math.cos(pitch/2) * math.cos(yaw/2) + math.sin(roll/2) * math.sin(pitch/2) * math.sin(yaw/2)

        return [qx, qy, qz, qw]

# print("done")