from wand.image import Image


class ImageAttachment:
    def __init__(self, location):
        self.image = Image(filename=location)
        self.details = self.__get_details()

    def __get_details(self):
        return {
            'frame_width': self.image.width,
            'frame_height': self.image.height,
            'color_profile': ' | '.join(self.__get_color_profiles()),
            'color_space': self.image.colorspace,
            'format_name': self.image.format,
            'compression_scheme': self.image.compression,
            'file_size': self.image.length_of_bytes,
            'bits_per_sample': self.image.depth,
            'xresolution': f"{self.image.resolution[0]} {self.image.units}"
        }

    def __get_color_profiles(self):
        return [k for k, v in self.image.profiles.items()]


if __name__ == "__main__":
    x = ImageAttachment('https://digital.lib.utk.edu/collections/islandora/object/acwiley:280/datastream/OBJ')
    print(x.details)
