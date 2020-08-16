import os
import sys
import spotipy
import spotipy.util as util
import json
import numpy as np
from itertools import compress
import tkinter as tk
from tkinter import ttk
import urllib.request # for saving images
import pprint 
pp = pprint.PrettyPrinter(indent=4)

# pyinstaller.exe --onefile --icon=spotify_icon_white.ico AlbumCoverDL.py

os.environ['SPOTIPY_CLIENT_ID'] = '2267d409940a4e4e840d4da871bb217d'
os.environ['SPOTIPY_CLIENT_SECRET'] = '8db865dbe4444584929ffc9b5bb26c11'
os.environ['SPOTIPY_REDIRECT_URI']= 'http://google.com/'

print('Hi, to use this app, please agree to the permissions,\n\
then copy and paste the URL you are redirected to below:')

def authorize():
    # get username
    username = sys.argv[0]
    # print(username)

    # erase cache and ask for permissions
    try:
        token = util.prompt_for_user_token(username)
    except:
        os.remove(f".cache-{username}")
        token = util.prompt_for_user_token(username)

    # create spotipyObject
    spotObj = spotipy.Spotify(auth=token)
    return spotObj

spotObj = authorize() # authorize

class PlaceholderEntry(ttk.Entry):
    '''
    customizing placeholder text behavior
    '''
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.placeholder = placeholder

        self.field_style = kwargs.pop("style", "TEntry")
        self.placeholder_style = kwargs.pop("placeholder_style", self.field_style)
        self["style"] = self.placeholder_style

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self["style"] == self.placeholder_style:
            self.delete("0", "end")
            self["style"] = self.field_style

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = self.placeholder_style

def search_API(dummy=1):    
    global image_urls
    global current_artist
    global artist_id
    
    artist = search_field.get() # get artist search query
    # handle empty search query
    if artist == '':
        display.configure(state=tk.NORMAL)
        display.insert(tk.END, 'the search field is empty\n')
        display.update()
    else:
        # let user know we are searching...
        display.configure(state=tk.NORMAL)
        display.insert(tk.END, 'searching for artist...\n')
        display.update()
        display.configure(state=tk.DISABLED)
        
        # artist found
        search_results = spotObj.search(artist,limit=1,offset=0,type='artist') # change limit to >1 to allow more than 1 artist returned
        artist_info = search_results['artists']['items'][0]
        artist_name = artist_info['name']
        current_artist = artist_name
        artist_id = artist_info['id'] # use artist id to find albums
        
        display.configure(state=tk.NORMAL)
        display.delete("end-2l","end-1l")
        display.insert(tk.END,'GENERATE ',("a"))
        display.insert(tk.END,'(Ctrl + G or Alt + G) if this is the artist:\n' + current_artist + '\n')
        display.configure(state=tk.DISABLED)
        
def generate_links(dummy=1):
    global image_urls
    global artist_id
    global current_artist
    global album_names

    display.configure(state=tk.NORMAL)
    display.insert(tk.END, 'grabbing images...\n')
    display.update()
    display.configure(state=tk.DISABLED)

    artist_releases = spotObj.artist_albums(artist_id)['items'] # all of artists releases 
    release_type = [release['album_type'] for release in artist_releases]
    album_indices = [_type == 'album' for _type in release_type]
    artist_albums = list(compress(artist_releases, album_indices)) # only albums
    
    release_type = [release['album_type'] for release in artist_releases]
    album_indices = [_type == 'album' for _type in release_type]
    artist_albums = list(compress(artist_releases, album_indices)) # only albums
#         print(json.dumps(artist_albums,sort_keys=True,indent=4))
    
    # store album names and images
    unique_names = [] # to prevent duplciates
    image_urls = [] # clear image url list
    for album in artist_albums:
        album_name = album['name']
        # first ensure album is a unique entry 
        if album_name not in unique_names:
            if album['images']: # then check that image list not empty for album
                image_url = album['images'][0]['url']
                image_urls.append(image_url)
                unique_names.append(album_name)
    album_names = unique_names  
        
    display.config(state=tk.NORMAL)
    display.delete("end-2l","end-1l")
    display.insert(tk.END,'%d '% len(image_urls),("a")) 
    display.insert(tk.END,'album images found\n')
    display.insert(tk.END,'SAVE ',("a"))
    display.insert(tk.END,'(or Ctrl + S) if this seems reasonable\n' )
    display.config(state=tk.DISABLED)
  
def generate_links_s(dummy=1):
    global image_urls
    global image_urls_s
    global artist_id
    global current_artist
    global album_names
    global single_names

    display.configure(state=tk.NORMAL)
    display.insert(tk.END, 'grabbing images...\n')
    display.update()
    display.configure(state=tk.DISABLED)
    
    # get albums
    artist_releases_a = spotObj.artist_albums(artist_id,limit=50)['items'] # all of artists releases 
    album_indices = [release['album_type'] == 'album' and release['album_group'] == 'album' for release in artist_releases_a]
    artist_albums = list(compress(artist_releases_a, album_indices)) # only albums
    # print(json.dumps(artist_albums,sort_keys=True,indent=4))
    
    # get singles
    artist_releases = []
    results = spotObj.artist_albums(artist_id,limit = 50)
    while results['next']: # doing this allows us to go over 50
        results = spotObj.next(results)
        artist_releases.extend(results['items'])
    release_types = {release['name']:[release['album_type'],release['album_group']] for release in artist_releases}
    # pp.pprint(release_types)
    single_indices = [release['album_type'] == 'single' and release['album_group'] == 'single' for release in artist_releases]
    artist_singles = list(compress(artist_releases, single_indices))
    
    
    # store album names and images
    unique_names = [] # to prevent duplciates
    image_urls = [] # clear image url list
    for album in artist_albums:
        album_name = album['name']
        # first ensure album is a unique entry 
        if album_name not in unique_names:
            if album['images']: # then check that image list not empty for album
                image_url = album['images'][0]['url']
                image_urls.append(image_url)
                unique_names.append(album_name)
    album_names = unique_names  
    
    # store single names and images
    unique_names_s = [] # to prevent duplciates
    image_urls_s = [] # clear image url list
    for single in artist_singles:
        single_name = single['name']
        # first ensure single is a unique entry 
        if single_name not in unique_names_s:
            if single['images']: # then check that image list not empty for single
                image_url = single['images'][0]['url']
                image_urls_s.append(image_url)
                unique_names_s.append(single_name)
    single_names = unique_names_s
        
    display.config(state=tk.NORMAL)
    display.delete("end-2l","end-1l")
    display.insert(tk.END,'%d '% len(image_urls),("a")) 
    display.insert(tk.END,'album images found\n')
    display.insert(tk.END,'%d '% len(image_urls_s),("a")) 
    display.insert(tk.END,'and single images found\n')
    display.insert(tk.END,'SAVE ',("a"))
    display.insert(tk.END,'(or Ctrl + S) if this seems reasonable\n' )
    display.config(state=tk.DISABLED)

def save_images(dummy=1):
    global album_names
    global image_urls
    global single_names
    global image_urls_s
    global current_artist

    name = current_artist.replace(' ','_')
    restricted_chars =  ['<', '>',':','"','\\','/','|','?','*','!']

    for char in restricted_chars:
        name = name.replace(char, '')
    folder = name
        
    display.config(state=tk.NORMAL)
    display.insert(tk.END, 'creating folder...\n')
    display.config(state= tk.DISABLED)
    display.update()
    
    # create folder to hold images
    if not os.path.isdir(folder):
        os.mkdir(folder)
    else:
        for i in range(1,21):
            if i == 20:
                display.config(state=tk.NORMAL)
                display.insert(tk.END, 'unable to create folder, too many folders with the name:\n' + folder)
                display.config(state= tk.DISABLED)
                return
            folder = folder + '(%d)' % i
            if not os.path.isdir(folder):
                os.mkdir(folder)
                break
            folder = name
        
    display.config(state=tk.NORMAL)
    display.delete("end-2l","end-1l")
    display.insert(tk.END, 'saving images...\n')
    display.config(state= tk.DISABLED)
    display.update()
    
    # save images with urlretrieves
    for i,image_url in enumerate(image_urls):
        album = album_names[i]
        for char in restricted_chars:
            album = album.replace(char, '')
        path = folder + '/' + album + '.jpg'
        urllib.request.urlretrieve(image_url, path)
    
    # make singles subfolder and save images if there are singles
    if single_names:

        subfolder = name + '_singles'
        os.mkdir(folder + '/' + subfolder)
        for i,image_url in enumerate(image_urls_s):
            single = single_names[i]
            for char in restricted_chars:
                single = single.replace(char, '')
            path = folder + '/' + subfolder + '/' + single + '.jpg'
            urllib.request.urlretrieve(image_url, path)
        
    display.config(state=tk.NORMAL)
    display.delete("end-2l","end-1l")
    display.insert(tk.END, 'all images saved, check the folder named: ')
    display.insert(tk.END,folder + '\n',("a"))
    display.insert(tk.END, 'you may continue searching for artists if you\'d like\n\n')
    display.config(state= tk.DISABLED)
    display.update()
    
# Define globals and constants
HEIGHT = 400
WIDTH = 500
cols = np.array([['#ede1e4','#783042'],['#e6ede1','#4d752f'],['#e1e9ed','#345c70'],['#ffffff','#c2c2c2']])
s = ''
idx = np.random.randint(4, size=1)
# print(idx)
BG_COL = s.join(cols[idx,0])
BTN_COL = s.join(cols[idx,1])

# define some globals
album_names = []
single_names = []
image_urls = []
image_urls_s = []
current_artist = ''

# Define root properties
root = tk.Tk()
root.title('Album Cover Downloader')
root.iconbitmap('spotify_icon_white.ico')
root.resizable(False, False)
canvas = tk.Canvas(root, height=HEIGHT, width=WIDTH)
canvas.pack()

# Frames
frame0 = tk.Frame(root,bg=BG_COL,bd=0) # frame containing search bar
frame0.place(relx=0.5, rely=0, relwidth=1,relheight=0.1,anchor='n')

frame1 = tk.Frame(root,bg=BG_COL,bd=0) # frame with main displays
frame1.place(relx=0.5, rely = 0.1,relwidth=1,relheight=0.7,anchor='n')

frame2 = tk.Frame(root,bg=BG_COL,bd=2) # frame with generate button
frame2.place(relx=0.5, rely = 0.8,relwidth=1,relheight=0.2,anchor='n')

# Labels
  

# using text over label for more customizability and scrolling
w = tk.Canvas(frame1, width=150,height=20)
w.pack(side=tk.LEFT,fill=tk.BOTH,padx=10,pady=10)
scrollbar = tk.Scrollbar(w,orient='vertical') # add scrollbar to display
display = tk.Text(w,font=('Calibri',11),bg='#ffffff',
                  width=60,height=20,
                  yscrollcommand = scrollbar.set)
display.tag_config("a", font=('Calibri',11,'bold'))
display.config(state=tk.NORMAL)
s = 'Welcome to Album Cover Downloader!\n\n\
Enter an artist in the search bar above, then\n(1) '
display.insert(tk.END, s)
s = 'SEARCH '
display.insert(tk.END, s, ("a"))
s = '(or Enter) to search\n\n(2) '
display.insert(tk.END, s)
s = 'GENERATE '
display.insert(tk.END, s, ("a"))
s = '(or Ctrl + G) to generate album covers for that artist\n\
      (Alt + G to include singles)\n\n(3) '
display.insert(tk.END, s)
s = 'SAVE '
display.insert(tk.END, s, ("a"))
s = '(or Ctrl + S) to save the album covers to your computer\n\n'
display.insert(tk.END, s)
display.pack(side=tk.LEFT,fill=tk.BOTH)
display.config(state= tk.DISABLED)
display.insert(tk.END, s)
scrollbar.pack(side = tk.RIGHT, fill = tk.Y)
scrollbar.config(command=display.yview) #for vertical scrollbar

# Entry fields
search_field = PlaceholderEntry(frame0,"Search Artist")
search_field.grid(row=0,column=0, padx=10, pady=10)
search_field.config(width = 32)

# Buttons
search_button = tk.Button(frame0, text='Search',command=lambda: search_API())
search_button.grid(row=0,column=1,padx=10, pady=10)
search_button.config(height = 1, width = 12,background=BG_COL,activebackground=BTN_COL)

generate_button = tk.Button(frame2, text='Generate',command=lambda: generate_links())
generate_button.grid(row=3,column=1,padx=10, pady=10)
generate_button.config(height = 1, width = 12,background=BG_COL,activebackground=BTN_COL)

save_button = tk.Button(frame2, text='Save',command=lambda: save_images())
save_button.grid(row=3,column=2,padx=10, pady=10)
save_button.config(height = 1, width = 12,background=BG_COL,activebackground=BTN_COL)

root.bind('<Return>',search_API)
root.bind('<Control-g>',generate_links)
root.bind('<Alt-g>',generate_links_s)
root.bind('<Control-s>',save_images)

root.mainloop()
