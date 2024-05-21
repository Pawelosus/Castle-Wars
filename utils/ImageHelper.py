from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsColorizeEffect
from PyQt6.QtGui import QPixmap, QColor, QPainter
from PyQt6.QtCore import Qt

class ImageHelper:
    @staticmethod
    def apply_color_filter(pixmap, target_rgb) -> QPixmap:
        # Split the original image into non-alpha and alpha parts
        non_alpha_pixmap, _ = ImageHelper.split_pixmap(pixmap)

        # Apply color filter to the non-alpha part
        non_alpha_pixmap = ImageHelper.apply_color_filter_to_pixmap(non_alpha_pixmap, target_rgb)

        return non_alpha_pixmap

    @staticmethod
    def split_pixmap(pixmap) -> tuple[QPixmap, QPixmap]:
        rgb_pixmap = pixmap.copy()
        alpha_pixmap = QPixmap(pixmap.size())
        alpha_pixmap.fill(Qt.GlobalColor.transparent)

        return rgb_pixmap, alpha_pixmap

    @staticmethod
    def apply_color_filter_to_pixmap(pixmap, target_rgb) -> QPixmap:
        scene = QGraphicsScene()
        pixmap_item = QGraphicsPixmapItem(pixmap)
        scene.addItem(pixmap_item)

        effect = QGraphicsColorizeEffect()
        effect.setColor(QColor(*target_rgb))
        pixmap_item.setGraphicsEffect(effect)

        # Create a QPainter to render the scene onto the pixmap
        painter = QPainter()
        painter.begin(pixmap)
        scene.render(painter)
        painter.end()

        return pixmap
