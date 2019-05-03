import discord

from lab import LabyrinthWalker, letters_reversed, ROAD, WALL

CENTER_ICON = "\u2718"

LEFT_ARROW = "\u21d0"

DOWN_ARROW = "\u21d3"

RIGHT_ARROW = "\u21d2"

UP_ARROW = "\u21d1"

CLOSED_ICON = "\u26d4"


class Labyrinth:
    def __init__(self, lab: LabyrinthWalker, folder: discord.CategoryChannel, up, right, down, left, center):
        self.lab = lab
        self.folder = folder
        self.up = up
        self.right = right
        self.down = down
        self.left = left
        self.center = center
        self.channels = {up, right, center, down, left}
        self.channel_to_direction = {
            self.up: 'N',
            self.right: 'E',
            self.down: 'S',
            self.left: 'W'
        }
        self.direction_to_channel = {
            'N': self.up,
            'E': self.right,
            'S': self.down,
            'W': self.left
        }
        self.channel_to_true_name = {
            self.up: UP_ARROW,
            self.right: RIGHT_ARROW,
            self.down: DOWN_ARROW,
            self.left: LEFT_ARROW
        }

    async def update_channels(self):
        for channel in self.channels:
            if channel == self.center:
                continue
            direction = self.channel_to_direction[channel]
            wall = letters_reversed[direction]
            if self.lab.curr.walls[wall] == ROAD and channel.name != self.channel_to_true_name[channel]:
                await channel.edit(name=self.channel_to_true_name[channel])
            elif self.lab.curr.walls[wall] == WALL and channel.name != CLOSED_ICON:
                await channel.edit(name=CLOSED_ICON)

    def is_wall(self, channel):
        direction = self.channel_to_direction[channel]
        wall = letters_reversed[direction]
        return self.lab.curr.walls[wall] == WALL
