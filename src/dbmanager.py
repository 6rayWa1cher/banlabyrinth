import sqlite3

import discord.ext.commands
from discord.utils import find

from entities.labyrinth import Labyrinth
# noinspection PyUnresolvedReferences
from lab import LabyrinthWalker, LabyrinthSchema

c = sqlite3.connect("../database.sqlite")


def setup():
    with c:
        c.execute('''
        CREATE TABLE IF NOT EXISTS labyrinth (
            folder_id INTEGER NOT NULL PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            up_channel_id INTEGER NOT NULL UNIQUE,
            right_channel_id INTEGER NOT NULL UNIQUE,
            down_channel_id INTEGER NOT NULL UNIQUE,
            left_channel_id INTEGER NOT NULL UNIQUE,
            center_channel_id INTEGER NOT NULL UNIQUE,
            lab_data TEXT NOT NULL
        )
        ''')
        c.commit()


def push_lab_to_db(lab: Labyrinth):
    with c:
        c.execute('''
        INSERT INTO labyrinth VALUES (?,?,?,?,?,?,?,?)
        ''', (lab.folder.id, lab.folder.guild.id, lab.up.id, lab.right.id, lab.down.id, lab.left.id, lab.center.id,
              repr(lab.lab)))
        c.commit()


def update_lab_data_in_db(lab: Labyrinth):
    with c:
        c.execute('''
        UPDATE labyrinth SET lab_data = ? WHERE folder_id = ?
        ''', (repr(lab.lab), lab.folder.id))
        c.commit()


def delete_lab_from_db(folder_id: int):
    with c:
        c.execute('''
        DELETE FROM labyrinth WHERE folder_id = ?
        ''', (folder_id,))
        c.commit()


def collect_data_from_db(bot: discord.ext.commands.Bot) -> dict:
    with c:
        cursor = c.execute('''
        SELECT * FROM labyrinth
        ''')
        channel_to_lab = dict()
        for row in cursor.fetchall():
            folder_id, guild_id, up_channel_id, right_channel_id, down_channel_id, \
            left_channel_id, center_channel_id, lab_data = row
            guild = bot.get_guild(guild_id)
            channels = list()
            flag = False
            for ch_id in [up_channel_id, right_channel_id, down_channel_id, left_channel_id, center_channel_id]:
                ch = guild.get_channel(ch_id)
                if ch is None:
                    flag = True
                    break
                channels.append(ch)
            if flag:
                delete_lab_from_db(folder_id)
                continue
            folder = find(lambda a: a.id == folder_id, guild.categories)
            lab_walker = eval(lab_data)
            lab = Labyrinth(lab_walker, folder, *channels)
            channel_to_lab.update({i: lab for i in channels})
        return channel_to_lab
