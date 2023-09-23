import numpy as np
import cv2, imutils, pytesseract, time
import pandas as pd

image_path = 'train_data/10.jpg'
original_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
resized_image = imutils.resize(original_image, width=500)

gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
filtered_image = cv2.bilateralFilter(gray_image, 11, 17, 17)
edged_image = cv2.Canny(filtered_image, 170, 200)

contours = cv2.findContours(edged_image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
contours = contours[0] if len(contours) == 2 else contours[1]
sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
license_plate_contour = None

for contour in sorted_contours:
    perimeter = cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, 0.02 * perimeter, True)
    if len(approx) == 4:
        license_plate_contour = approx
        break

mask = np.zeros(gray_image.shape, np.uint8)
license_plate_mask = cv2.drawContours(mask, [license_plate_contour], 0, 255, -1)
segmented_license_plate = cv2.bitwise_and(resized_image, resized_image, mask=license_plate_mask)

tesseract_config = ('-l eng --oem 1 --psm 3')

recognized_text = str(pytesseract.image_to_string(segmented_license_plate, config=tesseract_config))

current_time = time.asctime(time.localtime(time.time()))
data = {'date': [current_time], 'license_plate_number': [recognized_text]}
df = pd.DataFrame(data, columns=['date', 'license_plate_number'])
df.to_csv('data.csv')

print(recognized_text)
cv2.waitKey(0)
cv2.destroyAllWindows()estroyAllWindows()ctime( time.localtime(time.time()) )], 
        'v_number': [text]}

df = pd.DataFrame(raw_data, columns = ['date', 'v_number'])
df.to_csv('data.csv')

# Print recognized text
print(text)
cv2.waitKey(0)




# Print recognized text
print(text)
cv2.waitKey(0)


