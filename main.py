import subprocess
import os
import asyncio

#file extensions to find
extensions = [".mp4", ".avi", ".mkv"]
#path that will be scanned for files using the aforementioned extensions
mainPath = "/home/ahmed349/usb data/"
#path for generating and writing cache
cachePath = os.getcwd() + "/cache.log"

#function to get all videos in given path
def get_all_videos(path):
    #variable for storing our results
    result = []
    #using os.walk() find every file
    for (dirpath, dirnames, filenames) in os.walk(path):
        #loop over every file
        for f in filenames:
            #for each extension, if it exists in the filename then we append thus filename to our result
            for ext in extensions:
                if ext in f:
                    #append the full path of the file
                    result.append((dirpath, f))
    #return the list we created
    return result

#function for using ffmpeg to check the integrity of files
def verify_integrity(path, file):     
    #full command for reference
    #ffmpeg -v error -i file -f null - >error.log 2>&1
    integrityCommand = ["ffmpeg", "-v", "error", "-i", f"{path}/{file}", "-f", "null", "-"]
    #run the command and return its output                                                                    
    return subprocess.run(integrityCommand, text=True, capture_output=True).stderr

def main():
    #get all the absolute paths to all the videos in the main path
    videos = get_all_videos(mainPath)

    #variable for storing all integrity output we generate for overview
    fullOutput = ""
    #for storing processed videos paths
    processedVideos = []

    #create cache if it doesnt exist
    if not os.path.exists(cachePath): open(cachePath, 'x').close()

    #loop over every video we found
    for (path, name) in videos:
        print(f"({len(processedVideos)}/{len(videos)}) Processsing {path}/{name}")

        #check if video has been verified before in cache
        cacheFile = open(cachePath, 'r')
        if f"{path}/{name}" in cacheFile.read():
            print("File already processed before!!")
            #remove video path from videos list if we already processed it
            videos.remove((path, name))
            cacheFile.close()
            continue
        cacheFile.close()

        #get the integrity data
        integrityData = verify_integrity(path, name)

        #add video path to processed video paths list
        processedVideos.append((path, name))

        #append all data we get to the full output using the video path as a header with some whitespace
        fullOutput = "\n\n" + path + "/" + name + "\n" + integrityData
        
        #create a file for each video for its integrity data (if we got the data)
        if len(integrityData.strip()) > 0:
            #create file called {videoname}-error.log, ex: spiderman movie-error.log
            f = open(path + "/" + os.path.splitext(name)[0] + "-error.log", 'w')
            #write the data
            f.write(integrityData)
            #close file stream
            f.close()
        
        #write our full integrity data to a file
        f = open(mainPath + "/" + "output.log", 'a')
        f.write(fullOutput)
        f.close()

        #add processed video to cache file
        cacheFile = open(cachePath, 'a')
        cacheFile.write(f"{path}/{name}\n")
        cacheFile.close()

        #our status will be "Found errors" if the integrity data contains data, else the file is valid
        status = "Found errors" if len(integrityData.strip()) > 0 else "File is valid!"
        print (f"Done! - {status}")
    #print total videos processed
    print(f"Processed {len(processedVideos)} Videos!")

main()