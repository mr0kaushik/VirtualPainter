import cv2 as cv
import numpy as np


class Menu:

    def __init__(self, cv2, paths=[], width=500, height=100):
        self.MENU_WIDTH = width
        self.MENU_HEIGHT = height
        self.MENU_ITEM_WIDTH = 48
        self.SELECTED_COLOR = [253, 159, 0]
        self.UN_SELECTED_COLOR = [0, 0, 0]
        self.BORDER_WIDTH = 3
        self.ITEM_MARGIN_HEIGHT = 15
        self.ITEM_MARGIN_WIDTH = 50

        self.itemCount = len(paths)

        item_size = (self.MENU_ITEM_WIDTH, self.MENU_ITEM_WIDTH)

        self.menuItems = []

        for idx, path in enumerate(paths):
            self.menuItems.append(MenuItem(cv2, path,
                                           (idx * self.MENU_ITEM_WIDTH + (idx + 1) * self.ITEM_MARGIN_WIDTH, self.ITEM_MARGIN_HEIGHT),
                                           size=item_size))
        #
        # self.menuItems = [
        #     MenuItem(cv2, '../assets/brush.png',
        #              (self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # brush
        #     MenuItem(cv2, '../assets/thickness.png',
        #              (self.MENU_ITEM_WIDTH + 2 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # thickness
        #     MenuItem(cv2, '../assets/palette.png',
        #              (2 * self.MENU_ITEM_WIDTH + 3 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # color
        #     MenuItem(cv2, '../assets/eraser.png',
        #              (3 * self.MENU_ITEM_WIDTH + 4 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # eraser
        #     MenuItem(cv2, '../assets/hand.png',
        #              (4 * self.MENU_ITEM_WIDTH + 5 * self.ITEM_MARGIN, self.ITEM_MARGIN), size=item_size),  # hand
        # ]
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

    def draw(self, cv2, img):
        # img = np.zeros([self.MENU_HEIGHT, self.MENU_WIDTH, 3])
        masked_img = img
        for idx, item in enumerate(self.menuItems):
            # if idx == self.selectedMenuItemIndex:
            #     item.img = self.drawBorder(cv2, item.img)
            masked_img = self.overlay_transparent(masked_img, item.img, item.position[0], item.position[1])

        return masked_img


    # https://stackoverflow.com/questions/14063070/overlay-a-smaller-image-on-a-larger-image-python-opencv
    def overlay_transparent(self, background, overlay, x, y):
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


class MenuItem:

    def __init__(self, cv2, path, position, size):
        self.img = cv2.imread(path)
        print(self.img.shape)
        self.position = position
        self.size = size
        self.img = cv2.resize(self.img, self.size, interpolation=cv2.INTER_AREA)


def main():
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    menu_item_paths = ['../assets/brush.png', '../assets/thickness.png',
                       '../assets/palette.png', '../assets/eraser.png', '../assets/hand.png']
    menu = Menu(cv, paths=menu_item_paths)

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
