import cv2
import time
import numpy as np


class Menu:

    def __init__(self, cv2, width=500, height=100):
        self.MENU_WIDTH = width
        self.MENU_HEIGHT = height
        self.MENU_ITEM_WIDTH = 48
        self.SELECTED_COLOR = [253, 159, 0]
        self.UN_SELECTED_COLOR = [0, 0, 0]
        self.BORDER_WIDTH = 3
        self.ITEM_MARGIN = 10
        self.itemCount = 5

        item_size = (self.MENU_ITEM_WIDTH, self.MENU_ITEM_WIDTH)

        self.menuItems = [
            MenuItem(cv2, '../assets/brush.png',
                     (self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # brush
            MenuItem(cv2, '../assets/thickness.png',
                     (self.MENU_ITEM_WIDTH + 2 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # thickness
            MenuItem(cv2, '../assets/palette.png',
                     (2 * self.MENU_ITEM_WIDTH + 3 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # color
            MenuItem(cv2, '../assets/eraser.png',
                     (3 * self.MENU_ITEM_WIDTH + 4 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # eraser
            MenuItem(cv2, '../assets/hand.png',
                     (4 * self.MENU_ITEM_WIDTH + 5 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # hand
        ]
        self.selectedMenuItemIndex = 0
        self.selectedImage = self.menuItems[self.selectedMenuItemIndex].img
        self.select(self.selectedMenuItemIndex, cv2)

    def select(self, index, cv2):
        self.selectedImage = self.removeBorder(cv2, self.selectedImage)
        self.selectedMenuItemIndex = index
        self.selectedImage = self.menuItems[self.selectedMenuItemIndex].img
        self.selectedImage = self.drawBorder(cv2, self.selectedImage)

    def drawBorder(self, cv2, img):
        img = cv2.copyMakeBorder(img, self.BORDER_WIDTH, self.BORDER_WIDTH, self.BORDER_WIDTH,
                                 self.BORDER_WIDTH, cv2.BORDER_CONSTANT, value=self.SELECTED_COLOR)
        mask = np.all(img == self.UN_SELECTED_COLOR, axis=-1)
        img[mask] = self.SELECTED_COLOR
        return img

    def removeBorder(self, cv2, img):
        img = cv2.copyMakeBorder(img, 0, 0, 0, 0, cv2.BORDER_CONSTANT, value=self.SELECTED_COLOR)
        mask = np.all(img == self.SELECTED_COLOR, axis=-1)
        img[mask] = self.UN_SELECTED_COLOR
        # img[np.all(im == self.SELECTED_COLOR), axi]
        return img

    def draw(self, cv2):
        menu_img = np.zeros([self.MENU_HEIGHT, self.MENU_WIDTH, 3])
        # menu_img = np.zeros((5, self.MENU_HEIGHT, self.MENU_WIDTH, 3))
        # menu_img  = menu_img.reshape((5, self.MENU_HEIGHT, self.MENU_WIDTH, 3))

        item = self.menuItems[0]
        menu_img[item.position[0]:, item.position[1]:, :] = item.img

        # for item in self.menuItems:
        #     print(item.img.shape)






        # cv2.imshow(menu_img, "MenuIMG")
        # for item in self.menuItems:
        #     menu_img[item.position[0]:][item]


    def refresh(self, cv2):
        self.draw(self, cv2)


class MenuItem:

    def __init__(self, cv2, path, position, size):
        self.img = cv2.imread(path)
        self.position = position
        self.size = size
        self.img = cv2.resize(self.img, self.size, interpolation=cv2.INTER_AREA)
        # print(self.img.shape)


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# initialize menu
menu = Menu(cv2)

min_icon_width = 80
min_icon_height = 80


def overlay_transparent(background, overlay, x, y):
    background_width = background.shape[1]
    background_height = background.shape[0]

    if x >= background_width or y >= background_height:
        return background

    h, w = overlay.shape[0], overlay.shape[1]

    if x + w > background_width:
        w = background_width - x
        overlay = overlay[:, :w]

    if y + h > background_height:
        h = background_height - y
        overlay = overlay[:h]

    if overlay.shape[2] < 4:
        overlay = np.concatenate(
            [
                overlay,
                np.ones((overlay.shape[0], overlay.shape[1], 1), dtype=overlay.dtype) * 255
            ],
            axis=2,
        )

    overlay_image = overlay[..., :3]
    mask = overlay[..., 3:] / 255.0

    background[y:y + h, x:x + w] = (1.0 - mask) * background[y:y + h, x:x + w] + mask * overlay_image

    return background


while True:
    success, img = cap.read()
    window_width = img.shape[1]
    window_height = img.shape[0]

    item_width = window_width / 16  # half then 5 items (2 pixel apart

    # print(menu.selectedImage)
    img = overlay_transparent(img, menu.selectedImage, 100, 100)

    menu.draw(cv2)

    cv2.imshow("Image", img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
