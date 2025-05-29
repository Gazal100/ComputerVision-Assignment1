import cv2
from matplotlib import pyplot as plt
import numpy as np

# Show the following menu:
def show_menu():
    print("""
        ==== Mini Photo Editor ====
        1. Adjust Brightness
        2. Adjust Contrast
        3. Convert to Grayscale
        4. Add Padding (choose border type)
        5. Apply Thresholding (binary or inverse)
        6. Blend with Another Image (manual alpha)
        7. Undo Last Operation
        8. View History of Operations
        9. Save and Exit
        """)
    
def show_side_by_side(original, preview, title1='Original', title2='Preview'):
    plt.figure(figsize=(10,5))
    plt.subplot(1,2,1)
    plt.imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
    plt.title(title1)
    plt.axis('off')
    plt.subplot(1,2,2)
    plt.imshow(cv2.cvtColor(preview, cv2.COLOR_BGR2RGB))
    plt.title(title2)
    plt.axis('off')
    plt.show()

# Brightness/Contrast
def adjust_brightness_contrast(img, brightness=0, contrast=0):
    if brightness != 0:
        img = cv2.convertScaleAbs(img, alpha=1, beta=brightness)
    if contrast != 0:
        img = cv2.convertScaleAbs(img, alpha=(contrast + 100) / 100.0, beta=0)
    return img

# Gray-scale image
def convert_to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Padding: Ask the user to specify the padding size and border type (constant, reflect, replicate, etc.). 
# Additionally, include an option for the user to choose the padding proportion: Square, Rectangle, Custom Ratio (e.g., 4:5)
# If the user selects a custom ratio like 4:5, your program should calculate and apply the padding 
# so that the final image respects the chosen aspect ratio, regardless of the original size. 
# The user should also be able to adjust the total padding size, and your code must maintain the proportion accordingly. 
# (add smallest padding at the beginning to make it rectangle, then increase or decrease the padding size of the user wants)
def pad_image(img, pad_size, border_type='constant', aspect=None):
    h, w = img.shape[:2]
    
    if aspect:
        target_w = w
        target_h = h
        w_ratio, h_ratio = aspect
        if w * h_ratio > h * w_ratio: 
            target_h = int(np.ceil(w * h_ratio / w_ratio))
        else:  
            target_w = int(np.ceil(h * w_ratio / h_ratio))
        
        # minimum padding 
        aspect_top = (target_h - h) // 2
        aspect_bottom = target_h - h - aspect_top
        aspect_left = (target_w - w) // 2
        aspect_right = target_w - w - aspect_left
    else:
        aspect_top = aspect_bottom = aspect_left = aspect_right = 0
    
    # Add user-specified padding
    total_top = aspect_top + pad_size
    total_bottom = aspect_bottom + pad_size
    total_left = aspect_left + pad_size
    total_right = aspect_right + pad_size
    
    # Apply border
    border_types = {
        'constant': cv2.BORDER_CONSTANT,
        'reflect': cv2.BORDER_REFLECT,
        'replicate': cv2.BORDER_REPLICATE
    }
    border_type = border_types.get(border_type.lower(), cv2.BORDER_CONSTANT)
    padded = cv2.copyMakeBorder(
        img,
        total_top, total_bottom, total_left, total_right,
        border_type,
        value=[0, 0, 0] if border_type == cv2.BORDER_CONSTANT else None
    )
    return padded

# Thresholding: Let user choose between cv2.THRESH_BINARY and cv2.THRESH_BINARY_INV.
def threshold_image(img, ttype='binary'):
    if len(img.shape) == 2:
        gray = img
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if ttype == 'binary':
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    elif ttype == 'inv':
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    else:
        print("Invalid threshold type. Defaulting to binary.")
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    return thresh 

# Blending: Ask for a second image path and alpha (0 to 1).
def blend_images(img1, img2_path, alpha=0.5):
    img2 = cv2.imread(img2_path)
    if img2 is None:
        print("Second image not found.")
        return img1
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    img = ((1 - alpha) * img1 + alpha * img2)
    return img

def main():
    history = []
    log = []
    img_path = input("Enter image filename: ")
    img = cv2.imread(img_path)
    if img is None:
        print("Image not found.")
        return
    history.append(img.copy())

    while True:
        show_menu()
        choice = input("Choose an option: ")

        if choice == '1':
            b = int(input("Brightness (-100 to 100): "))
            preview = adjust_brightness_contrast(img, brightness=b, contrast=0)
            show_side_by_side(img, preview, 'Original', 'Brightness Adjusted')
            img = preview
            history.append(img.copy())
            log.append(f"brightness {b}")

            cv2.imwrite('brightness_adjusted.jpg', img)
            print("Brightness adjusted. Current image state saved.")

        elif choice == '2':
            c = int(input("Contrast (-100 to 100): "))
            preview = adjust_brightness_contrast(img, brightness=0, contrast=c)
            show_side_by_side(img, preview, 'Original', 'Contrast Adjusted')
            img = preview
            history.append(img.copy())
            log.append(f"contrast {c}")
            cv2.imwrite('contrast_adjusted.jpg', img)
            print("Contrast adjusted. Current image state saved.")
        
        elif choice == '3':
            preview = convert_to_grayscale(img)
            show_side_by_side(img, preview, 'Original', 'Grayscale')
            img = preview
            history.append(img.copy())
            log.append("converted to grayscale")
            cv2.imwrite('grayscale.jpg', img)
            print("Converted to grayscale. Current image state saved.")

        elif choice == '4':
            pad_size = int(input("Padding size (pixels): "))
            border = input("Border type (constant/reflect/replicate): ").strip().lower()
            ratio_choice = input("Aspect ratio:\n1. Square (1:1)\n2. Rectangle (4:3)\n3. Custom\n4. None\nChoice: ")
            
            if ratio_choice == '1':
                aspect = (1, 1)
            elif ratio_choice == '2':
                aspect = (4, 3)
            elif ratio_choice == '3':
                w, h = map(int, input("Enter ratio as w:h (e.g., 4:5): ").split(':'))
                aspect = (w, h)
            else:
                aspect = None
            
            preview = pad_image(img, pad_size, border, aspect)
            show_side_by_side(img, preview, 'Original', 'Padded Image')
            img = preview
            aspect_str = f"{aspect[0]}:{aspect[1]}" if aspect else "none"
            log.append(f"padding: {pad_size}px {border} ratio={aspect_str}")
            history.append(img.copy())
            cv2.imwrite('padded_image.jpg', img)
            print("Padding applied. Current image state saved.")

        elif choice == '5':
            ttype = input("Threshold type (binary/inv): ")
            preview = threshold_image(img, ttype)
            show_side_by_side(img, preview, 'Original', 'Threshold')
            img = preview
            history.append(img.copy())
            log.append(f"threshold {ttype}")
            cv2.imwrite('thresholded_image.jpg', img)
            print("Thresholding applied. Current image state saved.")

        elif choice == '6':
            img2_path = input("Second image filename: ")
            alpha = float(input("Alpha (0-1): "))
            preview = blend_images(img, img2_path, alpha)
            show_side_by_side(img, preview, 'Original', 'Blended Image')
            img = preview
            history.append(img.copy())
            log.append(f"blended with {img2_path} alpha {alpha}")
            cv2.imwrite('blended_image.jpg', img)
            print("Blending applied. Current image state saved.")

        elif choice == '7':
            if len(history) > 1:
                history.pop()
                img = history[-1].copy()
                log.append("undo")
                print("Undo successful.")
            else:
                print("Nothing to undo.")

        elif choice == '8':
            print("History Log:")
            for action in log:
                print(action)

        elif choice == '9':
            print("History Log:")
            for action in log:
                print(action)
            fname = input("Filename to save as: ")
            cv2.imwrite(fname, img)
            break
        else:
            print("Invalid choice.")
            break

if __name__ == "__main__":
    main()


