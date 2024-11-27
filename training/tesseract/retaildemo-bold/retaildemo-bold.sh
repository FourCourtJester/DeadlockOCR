#!/bin/bash

# Make the fonts folder for the current session
mkdir -p ~/.fonts
cp retaildemo-bold.otf ~/.fonts

# Refresh fonts cache
fc-cache -fv

# Optional: Ensure the font is there
fc-list | grep "Retail Demo"

# Generate the base font shapes
text2image --text ./charset.txt --ptsize 32 --outputbase retaildemo-bold --font "Retail Demo Bold" --fonts_dir .

# Generate the language model training data for specifically single lines
tesseract ./retaildemo-bold.tif retaildemo-bold ./lstm.train

# Generate the training files index
ls ./*.lstmf > ./training_files.txt

# Get the latest training data
wget https://github.com/tesseract-ocr/tessdata_best/raw/main/eng.traineddata -P ./eng

# Extract the layers of the training data
combine_tessdata -u ./eng/eng.traineddata ./eng

# Generate the checkpoints
lstmtraining --model_output retaildemo-bold --continue_from ./eng/eng.lstm --traineddata ./eng/eng.traineddata --train_listfile training_files.txt --max_iterations 1000

# Generate extra training

lstmtraining --model_output retaildemo-bold --continue_from ./<n>.checkpoint --traineddata ./eng/eng.traineddata --train_listfile training_files.txt --max_iterations 5000

# Combine checkpoints into training data
lstmtraining --stop_training --continue_from ./<n>.checkpoint --traineddata ./eng/eng.traineddata --model_output ./retaildemo-bold.traineddata

# Move the file to the tesseract directory
cp retaildemo-bold.traineddata /usr/share/tesseract-ocr/5/tessdata/

# Ensure it copied
# 'retaildemo-bold' should be among them
tesseract --list-langs