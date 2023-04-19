# Python code for optimized painting strategy that minimize paint consumption and maximize speed
import cv2
import numpy as np
def analyze_paint_coverage(facade_image):

    # Convert the image to grayscale
    gray = cv2.cvtColor(facade_image, cv2.COLOR_BGR2GRAY)
    # Apply thresholding
    ret,th1 = cv2.threshold(gray,127,255,cv2.THRESH_BINARY)
    # Find contours on the image
    contours,hierarchy = cv2.findContours(th1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    painting_order = []

    # Get a new array that matches the input image size
    blank_image = np.zeros_like(facade_image)

    # Draw contours of each object with a different color
    colors = np.random.randint(0,255,(len(contours),3))
    color_index = 0
    for contour in contours:
            # Add the paint order
            painting_order.append(colors[color_index])
            # Draw the current object to a black image
            painting_hulls = cv2.convexHull(contour)
            cv2.drawContours(blank_image, [painting_hulls], -1, colors[color_index], -1)

            color_index = (color_index+1)%len(colors)

    # Save the painting image to file
    cv2.imwrite('optimized_painting_image.jpg', blank_image)

    # Generate a human readable version of the painting order
    readable_order = [f'Paint {list(group)[0]} with color {color}' for color, group in groupby(painting_order)]
    optimized_painting_strategy = "\n".join(readable_order)

    # Write the optimized painting strategy to a file
    with open("optimized_painting_strategy.py", "w") as f:
        f.write(optimized_painting_strategy)

    # Return the optimized painting strategy as output
    return optimized_painting_strategy