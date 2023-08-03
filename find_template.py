import cv2 as cv
import numpy as np

def find_fish(template_img,  img, score):
    w, h = template_img.shape[1], template_img.shape[0]
    res = cv.matchTemplate(img, template_img, cv.TM_CCOEFF_NORMED)
    minval, maxval, minloc, maxloc = cv.minMaxLoc(res)

    if maxval < score:
        return img, False

    top_left = maxloc
    roi_rows, roi_cols = template_img.shape[:2]
    cv.rectangle(img, top_left, (top_left[0] + roi_cols, top_left[1] + roi_rows)
                 , (0, 0, 255), 5)
    return img, True
    # cv.imshow('img', img)
    # cv.waitKey()

if __name__ == '__main__':
    template_img_path = '2.png'
    img_path = 'img/309.png'
    template_img = cv.imread(template_img_path)
    img = cv.imread(img_path)

    img = find_fish(template_img, img)
    cv.imshow('img', img)
    cv.waitKey()