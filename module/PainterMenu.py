import cv2 as cv
import numpy as np
import enum


class MenuMode(enum.Enum):
    paint = 0
    thickness = 1
    color = 2
    eraser = 3
    hand = 4


class Menu:

    def __init__(self, cv2, items=[], width=500, height=100):
        self.MENU_WIDTH = width
        self.MENU_HEIGHT = height
        self.MENU_ITEM_WIDTH = 48
        self.SELECTED_COLOR = [253, 159, 0, 255]
        self.UNSELECTED_COLOR = [0, 0, 0, 255]
        self.BORDER_WIDTH = 3
        self.ITEM_MARGIN_HEIGHT = 15
        self.ITEM_MARGIN_WIDTH = 50

        self.itemCount = len(items)

        item_size = (self.MENU_ITEM_WIDTH, self.MENU_ITEM_WIDTH)

        self.menuItems = []
        for idx, val in enumerate(items):
            top_left = ((idx * self.MENU_ITEM_WIDTH + (idx + 1) * self.ITEM_MARGIN_WIDTH), self.ITEM_MARGIN_HEIGHT)
            bottom_right = (top_left[0] + self.MENU_ITEM_WIDTH, top_left[1] + self.MENU_ITEM_WIDTH)
            self.menuItems.append(MenuItem(val, cv2, (top_left, bottom_right), size=item_size))

        self.selectedMenuItemIndex = 0
        self.current_item = self.menuItems[self.selectedMenuItemIndex]
        self.selectedImage = self.menuItems[self.selectedMenuItemIndex].img
        self.select(self.selectedMenuItemIndex, cv2)

    def select(self, index, cv2):
        self.selectedImage = self.removeBorder(cv2, self.selectedImage)
        self.selectedMenuItemIndex = index
        self.current_item = self.menuItems[index]
        self.selectedImage = self.menuItems[self.selectedMenuItemIndex].img
        self.selectedImage = self.drawBorder(cv2, self.selectedImage)
        mask = np.all(self.selectedImage == self.UNSELECTED_COLOR, axis=-1)
        self.selectedImage[mask] = self.SELECTED_COLOR

    def drawBorder(self, cv2, img):
        img = cv2.copyMakeBorder(img, self.BORDER_WIDTH, self.BORDER_WIDTH, self.BORDER_WIDTH,
                                 self.BORDER_WIDTH, cv2.BORDER_CONSTANT, value=self.SELECTED_COLOR)
        mask = np.all(img == self.UNSELECTED_COLOR, axis=-1)
        img[mask] = self.SELECTED_COLOR
        return img

    def removeBorder(self, cv2, img):
        img = cv2.copyMakeBorder(img, 0, 0, 0, 0, cv2.BORDER_CONSTANT, value=self.SELECTED_COLOR)
        mask = np.all(img == self.SELECTED_COLOR, axis=-1)
        img[mask] = self.UNSELECTED_COLOR
        # img[np.all(im == self.SELECTED_COLOR), axi]
        return img

    def draw(self, cv2, img):
        # img = np.zeros([self.MENU_HEIGHT, self.MENU_WIDTH, 3])
        masked_img = img
        for idx, item in enumerate(self.menuItems):
            if idx == self.selectedMenuItemIndex:
                masked_img = self.transparent_overlay(masked_img, self.selectedImage, pos=item.hit_box[0])
            else:
                masked_img = self.transparent_overlay(masked_img, item.img, pos=item.hit_box[0])

        return masked_img

    def select_menu_item_if_possible(self, cv2, current_position):
        for idx, item in enumerate(self.menuItems):
            if item.is_inside(current_position):
                print(f'Selected Index {idx}')
                self.select(self.selectedMenuItemIndex, cv2)
                return item
        return self.current_item

    def select_by_mode(self, mode: MenuMode, cv2):
        self.select(mode.value, cv2)

    @staticmethod
    def transparent_overlay(src, overlay, pos=(0, 0), scale=1):
        # overlay = cv2.resize(overlay, (0, 0), fx=scale, fy=scale)
        h, w, _ = overlay.shape  # Size of overlay
        rows, cols, _ = src.shape  # Size of background Image
        y, x = pos[0], pos[1]  # Position of foreground/overlay image

        for i in range(h):
            for j in range(w):
                if x + i >= rows or y + j >= cols:
                    continue
                alpha = float(overlay[i][j][3] / 255.0)  # read the alpha channel
                src[x + i][y + j] = alpha * overlay[i][j][:3] + (1 - alpha) * src[x + i][y + j]
        return src


class MenuItem:

    def __init__(self, data, cv2, hit_box, size):
        self.title = data[0]
        self.mode = data[2]
        self.img = cv2.imread(data[1], cv2.IMREAD_UNCHANGED)
        self.hit_box = hit_box  # (top_left_position, bottom_right_position)
        self.size = size
        self.img = cv2.resize(self.img, self.size, interpolation=cv2.INTER_AREA)
        print(f'Image shape {self.img.shape}')

    def is_inside(self, pos):
        x1, y1 = self.hit_box[0]
        x2, y2 = self.hit_box[1]

        return (x1 < pos[0] < x2) and (y1 < pos[1] < y2)


def main():
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    menu_item_paths = [
        ('Brush', '../assets/brush.png', MenuMode.paint),
        ('Thickness', '../assets/thickness.png', MenuMode.thickness),
        ('Color', '../assets/palette.png', MenuMode.color),
        ('Eraser', '../assets/eraser.png', MenuMode.eraser),
        ('Hand', '../assets/hand.png', MenuMode.hand)
    ]
    menu = Menu(cv, items=menu_item_paths)

    while True:
        success, img = cap.read()
        img = menu.draw(cv, img)
        cv.imshow("Image", img)

        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
