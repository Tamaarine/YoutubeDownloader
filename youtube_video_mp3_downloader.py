from tkinter import *
import tkinter.ttk as ttk
import pytube as pt
from moviepy.editor import *
import threading

# https://simply-python.com/2019/01/02/downloading-youtube-videos-and-converting-to-mp3/
# reference link

# TODO Double click to open up the file maybe?
# TODO Perhaps add a delete button to delete certain files

class YoutubeApplication:
    def __init__(self, master):
        # The title for our little application
        master.title("Youtube Downloader")
        
        # Making the frame where we will keep our link input
        self.link_frame = Frame(master)
        self.link_frame.pack() # Just pack it in there
        
        # Then we will define a label 
        self.app_label = Label(self.link_frame, text="Youtube MP3/Playlist Downloader")
        self.app_label.config(font=("Calibri", 40), foreground="blue")
        self.app_label.pack(side=TOP)
        
        # Then we will define a entry to put our link
        self.link_entry = Entry(self.link_frame, width=60)
        self.link_entry.pack(side=LEFT, expand=1, fill=X)
        
        # Add a button to download single video
        self.download_button = Button(self.link_frame, text="Download Video", command=self.get_link_from_entry_video)
        self.download_button.pack()
        
        # Add a button to download entire playlist
        self.playlist_download_button = Button(self.link_frame, text="Download playlist", command=self.get_link_from_entry_playlist)
        self.playlist_download_button.pack()
        
        
        # We add a second frame for the bottom part of our application which is for
        # displaying the current songs we have downloaded/progress bar/refresh button
        self.display_frame = Frame(master)
        self.display_frame.pack()
        
        self.display_label = Label(self.display_frame, text="Current downloaded file", anchor="e", width=20)
        self.display_label.pack()
        
        # Then we add a listbox for displayign the current song in the directory
        self.listbox = Listbox(self.display_frame, width=150)
        self.listbox.pack(side=LEFT)
        
        # Add a scrollbar to it 
        self.scrollbar = Scrollbar(self.display_frame)
        self.scrollbar.pack(side=LEFT, fill=BOTH) # So it will take up more spaces to display
        
        # Attaching the scrollbar to the listbox
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.bind('<Double-Button-1>', self.open_double_clicked_file)
        
        # After finishing listbox we call the listbox method to update what we have in the directory already
        self.fill_listbox()
        
        
        # Need to make another frame that is for the browse folder button
        self.folder_frame = Frame(master)
        self.folder_frame.pack()
        
        # Add in the button for browsering folder
        self.folder_button = Button(self.folder_frame, text="Open Folder", command=self.browse_folder)
        self.folder_button.pack(fill=Y, expand=True, side=LEFT)
        
        # Add a button for deleting the highlighted song
        self.delete_song = Button(self.folder_frame, text="Delete selected song")
        self.delete_song.pack(side=LEFT, fill=Y, expand=True)
        
        # Add a button for deleting the entire mp3 and mp4 folder
        self.delete_all = Button(self.folder_frame, text="Delete ALL")
        self.delete_all.pack(side=LEFT,fill=Y, expand=True)
        
        
        
        # Progressbar frame
        self.progressbar_frame = Frame(root)
        self.progressbar_frame.pack()
        
        # We also add in a progressbar for keeping track of the downloading progress
        self.progressbar = ttk.Progressbar(self.progressbar_frame, orient=HORIZONTAL, length=100, mode='determinate')
        self.progressbar.pack(pady=5)
        
        # Also an additional label for more expressiveness
        self.progressbar_label = Label(self.progressbar_frame, text="Awaiting for task")
        self.progressbar_label.pack()
        
        
    def get_link_from_entry_video(self):
        
        # Entry function to download just a youtube video
        self.progressbar_label.config(text="Obtaining link")
                        
        link = self.link_entry.get()
         
        new_thread_to_download = threading.Thread(target=self.download_youtube_video, args=(link,), daemon=True)
        new_thread_to_download.start()
        
        
    def download_youtube_video(self, link):
        '''
        This function will be the one that actually download the youtube video with the given link
        '''
        
        try:
            # Getting our youtube object
            youtube = pt.YouTube(link)
            
            # Add callback while downloading
            youtube.register_on_progress_callback(self.on_progress)
            youtube.register_on_complete_callback(self.on_complete)

            # Download it into the mp4 folder
            video_path = youtube.streams.filter(type='audio').first().download(output_path="mp4")

            # Gettign the title of the video 
            last_slash = video_path.rindex("\\")
            extension_mp4 = video_path.rindex(".mp4")
            video_name = video_path[last_slash+1:extension_mp4]
            print(video_name)
            
            self.progressbar_label.config(text="Proceeding to convert mp4 to mp3")
                    
            # Better version of conversion using os.path
            audioclip = AudioFileClip(video_path)
            
            audioclip.write_audiofile(os.path.join(os.getcwd(), "mp3", video_name + ".mp3"), bitrate="200k")
            # # Conversion from mp4 to mp3 using moviepy at 200k bitrate
            # audioclip = AudioFileClip(".\\mp4\\" + video_name + ".mp4")
            # audioclip.write_audiofile(".\\mp3\\" + video_name + ".mp3", bitrate="200k")
            
            self.progressbar_label.config(text="Conversion complete!")
            
            # Update the listbox after we finish downloading a song
            self.fill_listbox()
        except:
            # Will give the error if anything is wrong with the link
            self.progressbar_label.config(text="Invalid link given")
        
    
    def get_link_from_entry_playlist(self):
        
        # Entry function to donwload a whole playlist of videos
        self.progressbar_label.config(text="Obtaining link")
                        
        link = self.link_entry.get()
         
        new_thread_to_download = threading.Thread(target=self.download_youtube_playlist, args=(link,), daemon=True)
        new_thread_to_download.start()
        
    
    def download_youtube_playlist(self, playlist_link):
        '''
        Keep in mind that playlist_link could be watch? or playlist?
        '''
        
        try:
            # Make the playlist object first
            playlist = pt.Playlist(playlist_link)
            
            # Then we cycle through each link and download each video separately
            for link in playlist.video_urls:
                self.download_youtube_video(link)
        except:
            self.progressbar_label.config(text="Invalid link given")
        
        
    def fill_listbox(self):
        '''
        This function is responsible for fillling the listbox with the songs that are already downloaded
         in the mp3 directory
        '''
        
        # Delete all the entry that was in the listbox before 
        self.listbox.delete('0', 'end')
        
        # No changing directories or else it will mess up everything else
        # What I will do is append full path to every file in the directory
        files = os.listdir('./mp3') # Getting the list of files
        
        # Get the current working directory
        directory = os.getcwd()
        
        # Then we will append the full path to the list of file names
        for i, _ in enumerate(files):
            files[i] = os.path.join(directory, "mp3", files[i])
                
        files.sort(key=os.path.getctime, reverse=True)        
        
        # Then updating the listbox with the new file in the directory
        for filename in files:
            self.listbox.insert('end', filename[filename.rindex('\\') + 1:])
        
    
    def browse_folder(self):
        '''
        This function will be the function called to open up the mp3 folder
        '''
        
        os.startfile("mp3")
        
    
    def on_progress(self, stream, chunk, byte_remaining):
        total_size = stream.filesize
        
        byte_downloaded = total_size - byte_remaining
        
        percentage = int((byte_downloaded / total_size) * 100)
        
        self.progressbar['value'] = percentage
        self.progressbar_label.config(text=str(percentage))
        
    
    def on_complete(self, stream, file_path):
        self.progressbar_label.config(text="Completed!")
        self.progressbar['value'] = 100
        
        
    def open_double_clicked_file(self, event):
        clicked_filename = self.listbox.get(ACTIVE) 
        
        current_directory = os.getcwd()
        
        os.startfile(os.path.join(current_directory, "mp3", clicked_filename))
        
        
    
    
# Create our basic root window
root = Tk()

# Change the title
root.title("Youtube Downloader")

# Puts the window in the middle of the screen
# This stays here and not have to be in the class
win_width = 1080
win_height = 720
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_cord = int((screen_width/2) - (win_width/2))
y_cord = int((screen_height/2) - (win_height/2))

root.geometry("{}x{}+{}+{}".format(win_width, win_height, x_cord, y_cord))

# Creating our applicaiton
youtubeApp = YoutubeApplication(root)

# Calling the mainloop
root.mainloop()


'''

Legacy code down below

'''

# # Functions here
# def download_youtube_video(link):
#     """
#     This function will actually be the function that downloads the youtube video
#     """
    
#     youtube = pt.YouTube(link)
    
#     # Downloading the video
#     print("Downloading the audio file in the current directory")
    
#     # Getting the name of the video
#     video_name = youtube.streams.filter(type='audio').first().title
    
#     # Download it into the mp4 folder
#     youtube.streams.filter(type='audio').first().download(output_path="mp4")
    
#     print("File downloaded")
    
    
#     # Conversion from mp4 to mp3 using moviepy at 200k bitrate
#     audioclip = AudioFileClip(".\\mp4\\" + video_name + ".mp4")
#     audioclip.write_audiofile(".\\mp3\\" + video_name + ".mp3", bitrate="200k")
    
#     print("Conversion completed")
    
#     # youtube.streams.filter(type='audio').first().download(filename='test.mp3')
#     # print(*youtube.streams.filter(type='audio'), sep='\n')
        
    
    
    

# def get_link_from_entry():
#     print("Getting the link from entry")
    
#     link = link_entry.get()
    
#     print("Proceeding to donwload the video")
    
#     new_thread_to_download = threading.Thread(target=download_youtube_video, args=(link,))
#     new_thread_to_download.start()

# # Make a frame so that's where we will keep our link input stuff
# link_frame = Frame(root)
# link_frame.pack() # Just pack it

# # Put a label
# app_label = Label(link_frame, text="Youtube MP3 Downloader")
# app_label.config(font=("Calibri", 40), foreground="blue")
# app_label.pack(side=TOP)

# # So we definitely need a entry to put our link in
# link_entry = Entry(link_frame, width=60)
# link_entry.pack(side=LEFT, expand=1, fill=X)

# # Add a button to download
# download_button = Button(link_frame, text="Donwload Video", command=get_link_from_entry)
# download_button.pack()


# # New frame for the bottom
# display_frame = Frame(root)
# display_frame.pack()

# # Add a listbox for displaying the current song in the directory
# listbox = Listbox(display_frame, width=150)

# listbox.pack(side=LEFT, fill=BOTH)

# scrollbar = Scrollbar(display_frame)
# scrollbar.pack(side=RIGHT, fill=BOTH)

# listbox.config(yscrollcommand=scrollbar.set)
# scrollbar.config(command=listbox.yview)


# def fill_listbox():
#     '''
#     This function is responsible for filling the listbox with the songs that are already donwloaded in
#     in the mp3 directory
#     '''
#     listbox.delete('0', 'end')
    
#     for filename in os.listdir(os.path.join(os.getcwd(), "mp3")):
#         listbox.insert('end', filename)
    
    

# refresh_button = Button(display_frame, text="Refresh", command=fill_listbox)
# refresh_button.pack(fill=Y, expand=True)


# root.mainloop()
