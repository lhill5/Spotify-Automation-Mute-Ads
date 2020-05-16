from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from spotify_sound import Sound
from math import inf
import time
import keyboard
# import sys
# import msvcrt


class Spotify:
    def __init__(self):
        self.filename = 'disliked_songs.txt'
        self.time_limit = 'forever'
        self.bad_songs = []
        self.start_time = None
        self.current_time = None
        self.song_title = None
        self.song_time = None
        self.song_length = None
        self.wait_time = None
        self.is_muted = False
        self.paused = False
        self.pause_time = None


    def openBrowser(self):
        self.browser = webdriver.Chrome('C:\\Users\\lhill5\\Downloads\\chromedriver_win32\\chromedriver.exe')
        self.browser.get('https://accounts.spotify.com/en/login?continue=https:%2F%2Fopen.spotify.com%2Fbrowse%2Ffeatured')
        
        # 2 minutes to login
        timeout = 120
        try:
            element_present = EC.presence_of_element_located((By.ID, 'main'))
            WebDriverWait(self.browser, timeout).until(element_present)
        except TimeoutException:
            print ("Timed out waiting for page to load")
        
        self.browser.implicitly_wait(100)


    def automateSpotify(self):
        self.play = self.browser.find_element_by_xpath("//button[@title='Play']")
        self.next = self.browser.find_element_by_xpath("//button[@title='Next']")
        self.prev = self.browser.find_element_by_xpath("//button[@title='Previous']")
        Sound.volume_set(30)
        # self.play.click()
        # self.start_time = time.time()
        time.sleep(1)
        # self.browser.implicitly_wait(500)


    def run(self):
        # self.song_title = self.browser.find_element_by_xpath('//*[@class="Root__now-playing-bar"]//*[@class="now-playing"]').text
        self.song_title = self.browser.find_element_by_xpath('//footer[@class="now-playing-bar-container"]').get_attribute('data-testid')
        print(self.song_title)
        self.current_time = time.time()
        # while self.current_time - self.start_time < self.end_time:
        while True:
            # if current time is 5 seconds from end of song, loops until new song title appears
            if self.isSongOver():
                print('song over')
                if not self.is_muted:
                    Sound.mute()
                    self.is_muted = True
            if self.isNewSong():
                print('new song')
                self.song_title = self.browser.find_element_by_xpath('//footer[@class="now-playing-bar-container"]').get_attribute('data-testid')
                # while not keyboard.is_pressed('a'):
                #     pass
                if 'ad-type-ad' in self.song_title:
                    if not self.is_muted:
                        Sound.mute()
                        self.is_muted = True
                else:
                    if self.is_muted:
                        Sound.mute()    # unmutes sound if not advertisement
                        self.is_muted = False

            if 'ad-type-ad' in self.song_title:
                if self.song_title in self.bad_songs:
                    self.muteAndSkip()
                skip_song, song_direction = self.isSkip()
                if skip_song:
                    self.muteAndSkip(song_direction)
            # if self.play.get_attribute("title") == "Play" and not self.paused:
            #     self.play.click()
            self.current_time = time.time()

        self.browser.quit()


    def time_delay(self, seconds):
        if self.pause_time is None:
            return True
        elif time.time() - self.pause_time < seconds:
            return False
        else:
            self.pause_time = None
            return True


    # breaks program if song is greater than 10 minutes, x[2:] for 10:19 gets [:19] and converts to int
    def muteAndSkip(self, direction=None):
        if not self.is_muted:
            Sound.mute()
            self.is_muted = True
        if direction is not None:
            self.skipSong(direction)
        else:
            self.skipSong()


    def isSongOver(self):
        self.getSongTimes()
        try:
            seconds = lambda x: int(x[0]) * 60 + int(x[2:])
            if seconds(self.song_length) - seconds(self.song_time) <= 1:
                return True
            else:
                return False
        except:
            self.next.click()


    def isNewSong(self):
        self.getSongTimes()
        try:
            seconds = lambda x: int(x[0]) * 60 + int(x[2:])
            if seconds(self.song_time) <= 1:
                return True
            else:
                return False
        except:
            self.next.click()


    def getSongTimes(self):
        song_times = self.browser.find_elements_by_xpath("//div[@class='playback-bar__progress-time']")
        self.song_time = song_times[0].text
        self.song_length = song_times[1].text


    def isSkip(self):
        start_time = time.time()
        while time.time() - start_time <= 1:
            if keyboard.is_pressed('ctrl'):
                if keyboard.is_pressed('up') and self.time_delay(1):
                    self.pause_time = time.time()
                    self.paused = not self.paused
                    self.play.click()
                    return False, None
                elif keyboard.is_pressed('right'):
                    return True, "next"
                elif keyboard.is_pressed('left'):
                    return True, "previous"
                elif keyboard.is_pressed('down'):
                    with open(self.filename, 'a') as disliked:
                        disliked.write(self.song_title + '\n')
                    self.getDislikedSongs()
                    return True, "next"
        return False, None


    def skipSong(self, song_direction="next"):
        if song_direction == "next":
            self.next.click()
        elif song_direction == "previous":
            self.prev.click()
        self.song_title = self.browser.find_element_by_xpath(
            '//div[@class="track-info__name ellipsis-one-line"]').text
        # print('song title ', self.song_title)
        time.sleep(0.1)


    def getDislikedSongs(self):
        disliked_songs = []
        with open(self.filename, 'r') as disliked:
            for song in disliked:
                disliked_songs.append(song.strip())
        self.bad_songs = disliked_songs


    # def convertTime(self, time_limit):
    #     try:
    #         int(time_limit[0:-1])
    #     except:
    #         return None
    #
    #     multiplier = time_limit[-1]
    #     weights = [1, 60, 3600, 86400]
    #     time_units = ['s', 'm', 'h', 'd']
    #     if not multiplier in time_units:
    #         return None
    #     else:
    #         seconds = int(time_limit[0:-1]) * weights[time_units.index(multiplier)]
    #         return seconds
    #
    # def getEndTime(self):
    #     if self.convertTime(self.time_limit) is not None:
    #         self.end_time = self.convertTime(self.time_limit)
    #     else:
    #         self.end_time = inf

# def skipSong():
#     start_time = time.time()
#     while time.time() - start_time <= 1:
#         if msvcrt.kbhit():
#             c = msvcrt.getch()
#             c = chr(c[-1])
#             if c == ' ':
#                 sys.stdout.flush()
#                 return True
#     sys.stdout.flush()
#     return False

# time_limit = input('How long do you want to play music? [30m/1h/forever]: ')

print("\n"*10)
print("Press ctrl + right arrowkey to skip song!")
music = Spotify()
music.getDislikedSongs()
# music.getEndTime()
music.openBrowser()
music.automateSpotify()
print('here')
music.run()


print('program ended')
