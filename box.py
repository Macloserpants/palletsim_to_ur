# box.py
class Box:
    def __init__(self, x, y, width, height, box_id, angle, layer):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle
        self.id = box_id  # Unique identifier for each box
        self.layer = layer  # The layer this box belongs to

    def __repr__(self):
        return f"Box(id={self.id}, x={self.x}, y={self.y}, width={self.width}, height={self.height}, angle={self.angle}, layer={self.layer})"

    # Add additional methods if needed (like for rotating, resizing, etc.)