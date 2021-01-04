from nodes import Node

# no = User('ef2607b740534db4a708db8b6feb6e2f', '410147f8a9be40fc8630a12ae1ccf0b3', 'titooooo27',
#           scope='user-read-recently-played')
# no.recently_played_popularity()
# no.song_popularity()
# no.rank_albums_by_popularity()
# no.albums_popularity(yessir, "13")
# print(no.current_song())
# no.make()
# no.get_album_name_and_ids('0epOFNiUfyON9EYx7Tpr6V')


class Organize(object):
    root: Node
    # I want data to be a dictionary. key = albumName. Value = score

    # instantiates the album: popularity df as a node.
    # if df has more than 1, call helper to sort it properly
    def __init__(self, data):
        if data.size <= 2:
            if not data:
                raise Exception('no data (album: popularity) is passed')
            raise Exception('need more than titles in the dataFrame')
        if data.size == 1:  # there is only 1 item in the dict
            self.root = Node(data)
            print(self.root)
        else:  # get the top of the df and assign to root
            self.root = Node(data)
            self.add(data)

    def add(self, data):
        pass
    #   for keys in data


