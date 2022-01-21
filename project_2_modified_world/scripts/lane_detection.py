import cv2
import numpy as np
import time
from traceback import print_exc


from cv_bridge import CvBridge

pub = None

curveList = []
avgVal = 10

def set_publisher(publisher):
    global pub
    pub = publisher

def get_boundaries(width, height, lines, resolution=10):
    left_points = set()
    right_points = set()
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x1 < width // 2:
            left_points.add((x1, y1))
            left_points.add((x2, y2))
            left_points.add(((x1 + x2) // 2, (y1 + y2) // 2))
        else:
            right_points.add((x1, y1))
            right_points.add((x2, y2))
            right_points.add(((x1 + x2) // 2, (y1 + y2) // 2))
    return (left_points, right_points)

def draw_curve(img, points):
    if len(points) == 0:
        return
    points = np.array(list(zip(*points)))
    z = np.polyfit(points[1], points[0], 2)
    x = np.array([i for i in range(0, img.shape[0], 10)])
    y = np.polyval(z, x)
    for i in range(1, len(x)):
        cv2.line(img, (int(y[i]), x[i]), (int(y[i - 1]), x[i - 1]), color=(0,255,255), thickness=3)
    return img

def draw_lane(img, left_points, right_points):
    if len(left_points) == 0 or len(right_points) == 0:
        return

    left_points = np.array(list(zip(*left_points)))
    right_points = np.array(list(zip(*right_points)))
    left_coeff = np.polyfit(left_points[1], left_points[0], 2)
    right_coeff = np.polyfit(right_points[1], right_points[0], 2)
    x = np.array([i for i in range(0, img.shape[0], 10)])
    y_left = map(int, np.polyval(left_coeff, x))
    y_right = map(int, np.polyval(right_coeff, x))
    
    new_left_points = list(zip(y_left, x))
    new_right_points = list(zip(y_right, x))
    
    # for point in new_left_points:
    #     cv2.circle(img, point, 2, (255, 255, 255), thickness=-1)
    # for point in new_right_points:
    #     cv2.circle(img, point, 2, (255, 255, 255), thickness=-1)

    polypoints = np.array(new_left_points + new_right_points[::-1])   # WHYYYYY [::-1] ??

    cv2.fillPoly(img, [polypoints], color=(255, 255, 0))
    return polypoints

def mask_histogram(img, polypoints):
    zeros = np.zeros((img.shape[0],img.shape[1],3),np.uint8)

    if polypoints is None or len(polypoints) == 0:
        return zeros

    hist_mask = cv2.fillPoly(zeros, [polypoints], color=(255, 255, 0))
    hist_mask = cv2.cvtColor(hist_mask,cv2.COLOR_BGR2GRAY)
    #cv2.imshow("mask", hist_mask)
    return hist_mask

def get_histogram(img, minPer = 0.1, display = False, region=1):
    if region ==1:
        histValues = np.sum(img, axis=0)
    else:
        histValues = np.sum(img[img.shape[0]//region:,:], axis=0)
 
    #print(histValues)
    maxValue = np.max(histValues)
    minValue = minPer*maxValue
 
    indexArray = np.where(histValues >= minValue)
    basePoint = np.average(indexArray)
    #print(basePoint)
 
    return basePoint

def get_curve_val(img):
    upperAvergaePoint = get_histogram(img[img.shape[0] // 2:, :],display=True,minPer=0.9)
    lowerAveragePoint = get_histogram(img[:img.shape[0] // 2, :], display=True, minPer=0.9)
    curveAveragePoint = get_histogram(img, display=True, minPer=0.9)
    curveRaw = (lowerAveragePoint - upperAvergaePoint) + (curveAveragePoint - img.shape[1] // 2)

    curveList.append(curveRaw)
    if len(curveList)>avgVal:
        curveList.pop(0)
    curve = sum(curveList)/len(curveList)

    #### NORMALIZATION
    curve = curve/200
    if curve>1: curve = 1
    if curve<-1:curve = -1

    return curve

def prespective_transform(img):
    pts1 = np.float32([[0, img.shape[0]], [img.shape[1], img.shape[0]],
                       [110, img.shape[0] // 2 + 80], [img.shape[1] - 110, img.shape[0] // 2 + 80]])
    pts2 = np.float32([[0, img.shape[0]], [img.shape[1], img.shape[0]],
                       [0, 0], [img.shape[1], 0]])
    
    result = img
    for pt in pts1:
        cv2.circle(result, (pt[0], pt[1]), 5, (0, 255, 255), thickness=-1)
     
    # Apply Perspective Transform Algorithm
    # matrix = cv2.getPerspectiveTransform(pts1, pts2)
    # result = cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))
    return result

def get_lane_value(img):
    img = cv2.resize(img, None, fx=0.5, fy=0.5)
    #img = cv2.blur(img, (5,5))

    img = prespective_transform(img)

    edges = cv2.Canny(img, 75, 150)

    # img = prespective_transform(img)
    edges = prespective_transform(edges)

    lines = cv2.HoughLinesP(edges, 3, 3 * np.pi/180, 60, maxLineGap=200)
    
    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    # for line in lines:
    #     x1, y1, x2, y2 = line[0]
    #     cv2.line(edges, (x1, y1), (x2,y2), (0, 255, 0), thickness=3)

    if lines is not None:
        # left_points, right_points = get_boundaries(img.shape[1], img.shape[0], lines)
        # polypoints = draw_lane(img, left_points, right_points)
        # hist_mask = mask_histogram(img, polypoints)
        # curve = get_curve_val(hist_mask)
        if pub is not None:
            # cv2.putText(img, str(curve), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, 2)
            ros_img = CvBridge().cv2_to_imgmsg(img, encoding="bgr8")
            pub.publish(ros_img)
        # return curve
    else:
        return None   
