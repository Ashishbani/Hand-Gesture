import cv2
import numpy as np
import math

cap = cv2.VideoCapture(0)

while (True):

    try:  # an error comes if it does not find anything in window as it cannot find contour of max area
        # therefore this try error statement

        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        kernel = np.ones((5, 5), np.uint8)

        # defining region of interest
        roi = frame[100:300, 100:300]

        cv2.rectangle(frame, (100, 100), (300, 300), (255, 0, 0), 0)
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # define range of skin color in HSV
        lowerskin = np.array([0, 58, 30], dtype=np.uint8)
        upperskin = np.array([33, 255, 255], dtype=np.uint8)

        # extracting skin colur image
        mask = cv2.inRange(hsv, lowerskin, upperskin)

        # extrapolate the hand to fill dark spots within
        mask = cv2.dilate(mask, kernel, iterations=6)

        # blur the image
        mask = cv2.GaussianBlur(mask, (5, 5), 100)

        # find contours
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #b=cv2.drawContours(roi,contours,-1,(255,255,0),3)
        #cv2.imshow("contours",b)

        # find contour of max area(hand)
        cnt = max(contours, key=lambda x: cv2.contourArea(x))

        # approx the contour a little
        epsilon = 0.0004 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)

        # make convex hull around hand
        hull = cv2.convexHull(cnt)

        # define area of hull and area of hand
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)

        # find the percentage of area not covered by hand in convex hull
        arearatio = ((areahull - areacnt) / areacnt) * 100

        # find the defects in convex hull with respect to hand
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

        # l = no. of defects
        l = 0

        # code for finding no. of defects due to fingers
        for i in range(defects.shape[0]):
            s, e, f, d = defects[i, 0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])
            pt = (100, 180)

            # find length of all sides of triangle
            a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
            b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
            c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)
            s = (a + b + c) / 2
            ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

            # distance between point and convex hull
            distance = (2 * ar) / a

            # apply cosine rule here
            angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

            # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
            if angle <= 90 and distance > 30:
                l += 1
                cv2.circle(roi, far, 3, [0, 0, 255], -1)

            # draw lines around hand
            cv2.line(roi, start, end, [0, 255, 0], 2)

        l += 1 # no.of defects + 1 =l

        # print corresponding gestures which are in their ranges
        font = cv2.FONT_HERSHEY_SIMPLEX
        if l == 1:
            if areacnt < 2000:
                cv2.putText(frame, 'Place the fingers', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)
            else:
                if arearatio < 12:
                    cv2.putText(frame, 'zero', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)
                elif arearatio < 17.5:
                    cv2.putText(frame, 'All the best', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

                else:
                    cv2.putText(frame, 'one', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

        elif l == 2:
            cv2.putText(frame, 'two', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

        elif l == 3:

            if arearatio < 27:
                cv2.putText(frame, 'three', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)
            else:
                cv2.putText(frame, 'ok', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

        elif l == 4:
            cv2.putText(frame, 'four', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

        elif l == 5:
            cv2.putText(frame, 'five', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

        elif l == 6:
            cv2.putText(frame, 'reposition fingers', (0, 50), font, 2, (255, 0, 0), 3, cv2.LINE_AA)

        # show the windows
        cv2.imshow('mask', mask)
        cv2.imshow('frame', frame)
    except:
        pass

    k = cv2.waitKey(5)
    if k == ord("q"):
        break

cv2.destroyAllWindows()
cap.release()





