# candlecleaner

A GUI application that allows the user to select a directory and remove a specified string from the names of the files within all its directory. Additionally, it supports a smart cleaning feature that utilizes regular expressions to clean each subdirectory based on a more specific selection.
Prerequisites

    Python 3.10.6
    Tkinter

How to use

    Clone the repository and navigate to the project directory.
    Run the candlecleaner.py script in a terminal enviroment.
    Click the 'Select Directory button' to select a directory.
    Enter the string you want removed in the 'Text to remove' field, this will search the entire file name for the inputted string.
    Click the 'Update Right Column' button to display the updated list of files.
    
    *If you want to use the smart cleaning feature, check the 'Candle Clean' box, this will disable and override whatever is in the 'Text to remove' field.
    
    Review the updated file names and make sure they are correct.
    Click the 'Rename Files' button to rename the files with the names displayed on the right.
