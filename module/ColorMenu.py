import cv2 as cv
import numpy as np
import enum


class ColorItem:
    def __init__(self, color_id, title, color_code, hit_box, size):
        self.id = id
        self.color_code = color_code
        self.title = title
        self.hit_box = hit_box  # (top_left_position, bottom_right_position)
        self.size = size

    def is_inside(self, pos):
        x1, y1 = self.hit_box[0]
        x2, y2 = self.hit_box[1]

        return (x1 < pos[0] < x2) and (y1 < pos[1] < y2)

    def rounded_rectangle(self, cv2, src, radius=1, thickness=1, line_type=cv.LINE_AA):
        #  corners:
        #  p1 - p2
        #  |     |
        #  p4 - p3

        top_left = self.hit_box[0]
        bottom_right = self.hit_box[1]

        # print(f'{self.title} topl {top_left} bl {bottom_right}')

        p1 = top_left
        p2 = (bottom_right[0], top_left[1])
        p3 = bottom_right
        p4 = (top_left[0], bottom_right[1])

        height = abs(bottom_right[1] - top_left[1])

        if radius > 1:
            radius = 1

        corner_radius = int(radius * (self.size[1] / 2))

        if thickness < 0:
            # big rect
            top_left_main_rect = (int(p1[0] + corner_radius), int(p1[1]))
            bottom_right_main_rect = (int(p3[0] - corner_radius), int(p3[1]))

            top_left_rect_left = (p1[0], p1[1] + corner_radius)
            bottom_right_rect_left = (p4[0] + corner_radius, p4[1] - corner_radius)

            top_left_rect_right = (p2[0] - corner_radius, p2[1] + corner_radius)
            bottom_right_rect_right = (p3[0], p3[1] - corner_radius)

            all_rects = [
                [top_left_main_rect, bottom_right_main_rect],
                [top_left_rect_left, bottom_right_rect_left],
                [top_left_rect_right, bottom_right_rect_right]]

            [cv2.rectangle(src, rect[0], rect[1], self.color_code, thickness) for rect in all_rects]

        # draw straight lines
        cv2.line(src, (p1[0] + corner_radius, p1[1]), (p2[0] - corner_radius, p2[1]), self.color_code, abs(thickness),
                 line_type)
        cv2.line(src, (p2[0], p2[1] + corner_radius), (p3[0], p3[1] - corner_radius), self.color_code, abs(thickness),
                 line_type)
        cv2.line(src, (p3[0] - corner_radius, p4[1]), (p4[0] + corner_radius, p3[1]), self.color_code, abs(thickness),
                 line_type)
        cv2.line(src, (p4[0], p4[1] - corner_radius), (p1[0], p1[1] + corner_radius), self.color_code, abs(thickness),
                 line_type)

        # draw arcs
        cv2.ellipse(src, (p1[0] + corner_radius, p1[1] + corner_radius), (corner_radius, corner_radius), 180.0, 0, 90,
                    self.color_code, thickness, line_type)
        cv2.ellipse(src, (p2[0] - corner_radius, p2[1] + corner_radius), (corner_radius, corner_radius), 270.0, 0, 90,
                    self.color_code, thickness, line_type)
        cv2.ellipse(src, (p3[0] - corner_radius, p3[1] - corner_radius), (corner_radius, corner_radius), 0.0, 0, 90,
                    self.color_code, thickness, line_type)
        cv2.ellipse(src, (p4[0] + corner_radius, p4[1] - corner_radius), (corner_radius, corner_radius), 90.0, 0, 90,
                    self.color_code, thickness, line_type)

        return src


class ColorMenu:
    def __init__(self, frame_size, items=[], start_point=(0, 0)):
        horizontal_padding = 40
        vertical_padding = 10
        vertical_spacing = 100

        frame_width = frame_size[0]
        frame_height = frame_size[1]

        left_x = start_point[0]

        self.item_size = int(
            (frame_height - vertical_padding - vertical_spacing) // len(items) - vertical_padding)

        item_width = self.item_size
        item_height = self.item_size

        if start_point[0] == frame_width:
            left_x = left_x - (2 * horizontal_padding + item_width)

        self.color_items = []
        current_point = (left_x + horizontal_padding, start_point[1] + vertical_padding)

        for i, item in enumerate(items):
            item_top_left = current_point
            item_bottom_right = (item_top_left[0] + item_width, item_top_left[1] + item_height)
            current_point = (current_point[0], item_bottom_right[1] + vertical_padding)
            self.color_items.append(ColorItem(
                color_id=i,
                title=item[0],
                color_code=item[1],
                hit_box=(item_top_left, item_bottom_right),
                size=(item_width, item_height)
            ))

        menu_bottom_right = (2 * horizontal_padding + item_width, current_point[1] + vertical_padding)

        self.hit_box = ((left_x, start_point[1]), menu_bottom_right)

        self.selected_color_item_index = 0
        self.select_color(self.selected_color_item_index)

    def select_color(self, index):
        self.selected_color_item_index = index
        self.selected_color = self.color_items[index].color_code

    def draw(self, cv2, img):
        for idx, item in enumerate(self.color_items):
            img = item.rounded_rectangle(
                cv2, img,
                radius=1 if idx == self.selected_color_item_index else 0.5,
                thickness=-1
            )

    def select_color_item_if_possible(self, current_position):
        for idx, item in enumerate(self.color_items):
            if item.is_inside(current_position):
                self.selected_color_item_index = idx
                self.select_color(self.selected_color_item_index)
                return self.color_items[self.selected_color_item_index]
        return self.color_items[self.selected_color_item_index]


def main():
    cap = cv.VideoCapture(0, cv.CAP_DSHOW)

    frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))

    color_items = [
        ("Navy", (102, 35, 0)),
        ("Peach", (114, 128, 250)),
        ("Blue", (207, 201, 100)),
        ("Beige", (64, 183, 255)),
        ("Black", (50, 32, 8)),
        ("Orange", (41, 76, 255)),
        ("Purple", (109, 45, 81)),
        ("Red", (94, 72, 248)),
        ("Teal", (212, 193, 0)),
        ("Green", (191, 255, 40)),
        ("Pink", (192, 143, 240))
    ]

    menu = ColorMenu((frame_width, frame_height), color_items)

    while True:
        success, img = cap.read()

        menu.draw(cv, img)

        cv.imshow("Image", img)

        if cv.waitKey(1) == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()


if __name__ == "__main__":
    main()
