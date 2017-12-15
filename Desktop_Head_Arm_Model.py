import numpy as np
import math


def DHMatrix(a, alpha, d, theta):
    cos_theta = math.cos(math.radians(theta))
    sin_theta = math.sin(math.radians(theta))
    cos_alpha = math.cos(math.radians(alpha))
    sin_alpha = math.sin(math.radians(alpha))


    return np.array([
        [cos_theta, -sin_theta*cos_alpha, sin_theta*sin_alpha, a*cos_theta],
        [sin_theta, cos_theta*cos_alpha, -cos_theta*sin_alpha, a*sin_theta],
        [0, sin_alpha, cos_alpha, d],
        [0, 0, 0, 1],
    ])

def DHGetJointPositions(thetaBase, thetaLower, thetaElbow, thetaGripper, Sonar):

    XYZ0 = np.array([0,0,0,1])
    T1 = DHMatrix(15, 90, 102, thetaBase) #XYZ coordinates of lower joint
    T2 = DHMatrix(150, 0, 0, thetaLower) #XYZ coordinates of Elbow joint
    T3 = DHMatrix(161, 0, 0, thetaElbow) #XYZ coordinates of Gripper/Wrist joint
    T4 = DHMatrix(38, 0, 0, thetaGripper) #XYZ coordinates of End effector/centre of sonar sensor
    TS = DHMatrix(Sonar, 0, 0, 0) #XYZ of sonar end point

    XYZ1 = np.dot(T1,XYZ0)
    XYZ2 = np.dot(T1,np.dot(T2,XYZ0))
    XYZ3 = np.dot(T1,np.dot(T2,np.dot(T3,XYZ0)))
    XYZ4 = np.dot(T1,np.dot(T2,np.dot(T3,np.dot(T4,XYZ0))))
    XYZSonar = np.dot(T1,np.dot(T2,np.dot(T3,np.dot(T4,np.dot(TS,XYZ0)))))


    #Form return array

    ReturnArray = np.array([XYZ0, 
                            XYZ1,
                            XYZ2, 
                            XYZ3,
                            XYZ4])

    return ReturnArray, XYZSonar


    



