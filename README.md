# candlecleaner

A GUI application that allows the user to select a directory and remove a specified string from the names of the files within the selected directory recursively.
Features a smart cleaning feature which generates regular expressions to remove, by normalizing (all lowercase, with spaces and hyphens turned into underscores) all 
file names and finding a common prefix for each subdirectory.

Prerequisites

    Python 3.10.6
    Tkinter
    Pillow
    Pyinstaller

How to use:

* Clone the repository and navigate to the project directory.
* Run the candlecleaner.py script in a terminal environment.
* Click the 'Select Directory button' to select a directory.
* Enter the string you want removed in the 'Text to remove' field, this will search the entire file name for the inputted string.
* Click the 'Update Right Column' button to display the updated list of files.
* If you want to use the smart cleaning feature, check the 'Candle Clean' box, this will disable and override whatever is in the 'Text to remove' field.
* Review the updated file names and make sure they are correct.
* Click the 'Rename Files' button to rename the files with the names displayed on the right.