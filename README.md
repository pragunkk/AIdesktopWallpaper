
# AI Wallpaper Generator

Generate beautiful-looking wallpapers for your desktop on your favourite theme.

## Features

- Set once, Enjoy forever
- Theme selection
- Auto screen resolution detection
- Auto-update on custom intervals
- Runs in the background
- Easy access through the tray
- Intuitive UI to set your preferences


## Installation

1. This repo contains the pre-built binaries and the source code for Windows
2. Run ```dist/wallpaper_utils/wallpaper_utils.exe```
3. Access the GUI to set preferences from the tray in the taskbar

    
## FAQ

1. #### How do I run this?

- Download this project. 
- Unzip the file
- Navigate to ```dist/wallpaper_utils```
- Run wallpaper_utils.exe
- Open the GUI by right-clicking the tray icon and clicking "show"
- Set preferences

2. #### How do I enable automatic updating of the wallpaper?

In the preferences, use the "toggles auto refresh" button to enable the automatic wallpaper updating and set the interval in minutes in the text box above.

3. #### Does the GUI need to be running always?

No! Once you set your preferences, you can close the GUI and it will keep working in the background to generate your favourite wallpapers.

4. #### How about resource usage? Does this drain a lot of battery?

This app is built to run very lightly in the background. Hence it consumes very little resources when running in the background.




## Future Version Plans

- Bring support for MacOS and Linux based systems
- Improve GUI by using native libraries
- Create an installer for easy installation and distribution
- Improve theme library based on user feedback
## Tech Stack

### Backend
 #### Python
 - Pystray
 - Threading
 - JSON
 - PIL for image processing

### Frontend
 #### Python
 - Tkinter
 - Threading
 - JSON
 - PIL for image processing

### Binaries
- Pyinstaller

## Screenshots

![alt text](./screenshots/SampleImage1.jpg)
![alt text](./screenshots/SampleImage2.jpg)
![alt text](./screenshots/SampleImage3.jpg)
![alt text](./screenshots/SampleImage4.jpg)
![alt text](./screenshots/SampleImage5.jpg)
![alt text](./screenshots/SampleImage6.jpg)