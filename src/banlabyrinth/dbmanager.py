import sqlite3

import discord.ext.commands
from discord import Permissions
from discord.utils import find

from banlabyrinth import configmanager
from banlabyrinth.entities.labyrinth import Labyrinth
# noinspection PyUnresolvedReferences
from banlabyrinth.lab import LabyrinthWalker, LabyrinthSchema

DB_PATH = configmanager.get_db_path()
c = sqlite3.connect(DB_PATH)

def setup():
    with c:
        c.execute('PRAGMA foreign_keys = ON;')
        c.execute('''
        CREATE TABLE IF NOT EXISTS labyrinth (
            folder_id INTEGER NOT NULL PRIMARY KEY,
            guild_id INTEGER NOT NULL,
            up_channel_id INTEGER NOT NULL,
            right_channel_id INTEGER NOT NULL,
            down_channel_id INTEGER NOT NULL,
            left_channel_id INTEGER NOT NULL,
            center_channel_id INTEGER NOT NULL,
            lab_data TEXT NOT NULL
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS member_roles (
            folder_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            allow INTEGER,
            deny INTEGER,
            FOREIGN KEY (folder_id) REFERENCES labyrinth (folder_id) ON DELETE CASCADE,
            PRIMARY KEY (folder_id, channel_id)
        )
        ''')
        c.execute('''
        CREATE TABLE IF NOT EXISTS box_member_roles (
            box_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            allow INTEGER,
            deny INTEGER,
            PRIMARY KEY (box_id, channel_id)
        )
        ''')
        c.commit()


def push_box_member_roles(box_id, member_roles: dict):
    with c:
        c.executemany('''
        INSERT INTO box_member_roles (box_id, channel_id, allow, deny) VALUES (?,?,?,?)
        ''', ((box_id, i.id, member_roles[i][0].value, member_roles[i][1].value) for i in
              member_roles.keys()))
        c.commit()


def push_lab_to_db(lab: Labyrinth):
    with c:
        c.execute('''
        INSERT INTO labyrinth VALUES (?,?,?,?,?,?,?,?)
        ''', (lab.folder.id, lab.folder.guild.id, lab.up.id, lab.right.id, lab.down.id, lab.left.id, lab.center.id,
              repr(lab.lab)))
        member_roles = lab.previous_member_roles
        c.executemany('''
        INSERT INTO member_roles (folder_id, channel_id, allow, deny) VALUES (?,?,?,?)
        ''', ((lab.folder.id, i.id, member_roles[i][0].value, member_roles[i][1].value) for i in
              member_roles.keys()))
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


def delete_box_member_roles(box_id: int):
    with c:
        c.execute('''
        DELETE FROM box_member_roles WHERE box_id = ?
        ''', (box_id,))
        c.commit()


def get_member_roles(guild: discord.Guild, folder_id: int) -> dict:
    with c:
        cursor = c.execute('''
        SELECT * FROM member_roles WHERE folder_id = ?
        ''', (folder_id,))
        previous_member_roles = dict()
        for row in cursor.fetchall():
            folder_id, channel_id, allow_int, deny_int = row
            channel = guild.get_channel(channel_id)
            if channel is not None:
                previous_member_roles[channel] = (Permissions(allow_int), Permissions(deny_int))
        return previous_member_roles


def get_box_member_roles(guild: discord.Guild, box_id: int) -> dict:
    with c:
        cursor = c.execute('''
        SELECT * FROM box_member_roles WHERE box_id = ?
        ''', (box_id,))
        previous_member_roles = dict()
        for row in cursor.fetchall():
            folder_id, channel_id, allow_int, deny_int = row
            channel = guild.get_channel(channel_id)
            if channel is not None:
                previous_member_roles[channel] = (Permissions(allow_int), Permissions(deny_int))
        return previous_member_roles


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
            lab = Labyrinth(lab_walker, folder, get_member_roles(guild, folder_id), *channels)
            channel_to_lab.update({i: lab for i in channels})
        return channel_to_lab


if __name__ == '__main__':
    setup()
