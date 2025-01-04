#In def update_counter(), before if Image is none
image = rc_utils.crop(image(50, 0), (rc.camera.get_height(), rc.camera.get_width()))

    hsv_lower = (10, 50, 50)
    hsv_upper = (20, 255, 255)

    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)
    mask = cv.inRange(image, hsv_lower, hsv_upper)

    contours, _ = cv.findContours(mask, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)

    contours_filtered = []
    for contour in contours:
        if cv.contourArea(contour) > MIN_CONTOUR_AREA:
            contours_filtered.append(contour)
        
    cv.drawContours(image, contours_filtered, -1, (0, 255, 0), 3)

    rc.display.show_color_image(image)

#else statement for if image is none
max_contour = 1

        if len(contours) > 0:
            max_contour = contours[0]
        for contour in contours_filtered:
            if cv.contourArea(contour) > MIN_CONTOUR_AREA:
                if cv.contourArea(contour) > cv.contourArea(max_contour):
                    max_contour = contour
    try:
        cv.drawContours(image, [max_contour], 0, (0, 255, 0), 3)
    except:
        pass
    
    contour_center = rc_utils.get_contour_center(max_contour)
    cv.circle(image,(contour_center[1], contour_center[0]), 6, (0, 255, 255), -1)
