# Experiment Setup and Execution Guide
26.01.2025

---

## Overview

This experiment uses a Python-based application and is designed specifically for use with a Wacom Cintiq 16 tablet and its pen. The purpose of this document is to guide you through the setup and execution of the experiment.

---

## Pre-Experiment Setup

### Download and Install Wacom Driver
Visit [Wacom Support - Drivers](https://www.wacom.com/en-us/support/product-support/drivers) and download the most recent driver for your device. Follow the installation instructions provided by Wacom.

### Configure Tablet Settings
1. Open the **Wacom Tablet Properties** application (installed with the driver).
2. Ensure the following settings are applied:
   - **Tip Feel**: Set to default (Level 4) to standardize pressure measurements.
   - **Pen Side Buttons**: Disable all side buttons to prevent unintended interruptions.
   - **Other Settings**: Leave all other settings at their default values.

---

## Running the Experiment

### Staring the 

- #### Start the Application
  Run main.py
- #### Enter Subject ID
  Input the subject's ID in the "Enter ID" text box.
- #### Begin the Experiment
  Click the "Start" button or press the Enter key to start the experiment.

---

## During the Experiment

### Recording Gestures
The subject's pen gestures on the tablet screen will be recorded and displayed.

### Experimenter Controls
- **Press Enter**: Clears the screen and starts a new trial.
- **Press Esc**: Ends the experiment.
- 
---
## Results
The results of each run are saved to a local folder `./results/` under the running directory. 
Each run is stored as a JSON file with the filename: `DateTime_SubjectID_shape_tracking.json`.

Each JSON file contains the following data sampled at a rate of **140 Hz**:
- **x, y coordinates**: Screen coordinates in a resolution of **1920x1080**.
- **x, y pen tilt**: The tilt of the pen in both the x and y axes.
- **Pen pressure**: The pressure of the pen, ranging from **0 to 1**.
- **Timestamp**: The timestamp for each sample, in a consistent format.

---
## Contact

For any issues or inquiries regarding this experiment, please contact:

**Email**: [Omer.Rizhiy@mail.huji.ac.il](Omer.Rizhiy@mail.huji.ac.il)  
