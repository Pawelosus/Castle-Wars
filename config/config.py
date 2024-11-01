import configparser
from typing import List, Tuple

class Config:
    def __init__(self, file_path='config/config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    @property
    def window_width(self) -> str:
        return self.config.get('Window', 'Width')

    @property
    def window_height(self) -> str:
        return self.config.get('Window', 'Height')

    @property
    def default_castle_colors(self) -> List[Tuple[int, int, int]]:
        colors_str = self.config.get('UI', 'DefaultCastleColors')
        colors = [tuple(map(int, color.split(','))) for color in colors_str.split('|')]
        return colors

    @property
    def default_fence_color(self) -> List[int]:
        color_str = self.config.get('UI', 'DefaultFenceColor')
        colors = [int(color) for color in color_str.split(',')]
        return colors

    @property
    def base_castle_y_level(self) -> int:
        return self.config.getint('UI', 'BaseCastleYLevel')

    @property
    def base_fence_y_level(self) -> int:
        return self.config.getint('UI', 'BaseFenceYLevel')

    @property
    def button_width(self) -> int:
        return self.config.getint('UI', 'ButtonWidth')

    @property
    def button_height(self) -> int:
        return self.config.getint('UI', 'ButtonHeight')

    @property
    def default_player_name(self) -> str:
        return self.config.get('Defaults', 'PlayerName')

    @property
    def default_cpu_name(self) -> str:
        return self.config.get('Defaults', 'CPUName')

    @property
    def enable_logs(self) -> bool:
        return self.config.getboolean('Logs', 'EnableLogs')

