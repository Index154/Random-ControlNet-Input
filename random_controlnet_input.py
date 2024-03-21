import modules.scripts as scripts
import gradio as gr
import os
from modules.processing import process_images, Processed

class Script(scripts.Script):

    def title(self):
        return "Random ControlNet Input"


    def ui(self, is_img2img):
        uiActive = gr.Checkbox(True, label="Activate script")
        uiFolderPath = gr.Textbox(label="Image source folder", lines=1)
        uiRecursive = gr.Checkbox(True, label="Include subfolders")
        uiModifyPrompt = gr.Checkbox(False, label="Add contents of txt file with same filename as the selected image to positive prompt (If no matching txt is found the script will look for a default.txt in the same folder and in the image source folder)")
        uiIgnorePrompt = gr.Checkbox(True, label="Ignore the positive prompt in WebUI if a txt file is used")
        return [uiActive, uiRecursive, uiFolderPath, uiModifyPrompt, uiIgnorePrompt]

    def run(self, p, uiActive, uiRecursive, uiFolderPath, uiModifyPrompt, uiIgnorePrompt):
    
        # Abort if the script is inactive
        if(not uiActive):
            return
        
        # Error if there is no path supplied
        if(uiFolderPath == ""):
            raise Exception("<Random Controlnet Input> - Please enter an image source folder path")
            return
        
        # Error if folder does not exist
        if(not os.path.isdir(uiFolderPath)):
            raise Exception("<Random Controlnet Input> - Image source folder not found")
        
        # Additional imports
        import glob
        import base64
        import random
        import importlib
        controlNetModule = importlib.import_module('extensions.sd-webui-controlnet.scripts.external_code', 'external_code')
        
        # Abort if ControlNet is turned off
        controlNetList = controlNetModule.get_all_units_in_processing(p)
        if(not controlNetList[0].enabled):
            return
        
        # Get list of files in folder
        if(uiRecursive):
            searchPath = os.path.join(uiFolderPath, '**', '*.png')
        else:
            searchPath = os.path.join(uiFolderPath, '*.png')
        files = [f for f in glob.glob(searchPath, recursive=True) if os.path.isfile(f)]
        
        # Error if there are no files
        if(len(files) < 1):
            raise Exception("<Random Controlnet Input> - No png files found in image source folder")
            return
        
        # Select a random image and convert it
        imgName = random.choice(files)
        imgPath = os.path.join(uiFolderPath, imgName)
        try:
            with open(imgPath, "rb") as imageFile:
                imgData = controlNetModule.to_base64_nparray(base64.b64encode(imageFile.read()).decode())
        except:
            raise Exception("<Random Controlnet Input> - Error loading the image file " + imgName)
            return
            
        # Function for txt file reading
        def readTxt(txtPath):
            try:
                with open(txtPath, 'r') as txtFile:
                    txtContent = txtFile.read().replace('\n', '')
            except:
                raise Exception("<Random Controlnet Input> - Failed to read txt file " + txtPath)
            return txtContent
            
        # Add text from txt file with same filename to prompt if enabled. If no file is found, look for default.txt in the same folder. Also check in the main folder entered by the user if necessary
        if(uiModifyPrompt):
            txtPath = imgPath[:-4] + '.txt'
            separator = os.path.join('a', 'a')[1:2]
            splitTxtPath = txtPath.split(separator)
            defaultPath = os.path.join(separator.join(splitTxtPath[:-1]), "default.txt")
            mainDefaultPath = os.path.join(uiFolderPath, 'default.txt')
            
            loadedTxt = ''
            if(os.path.isfile(txtPath)):
                loadedTxt = readTxt(txtPath)
            elif(os.path.isfile(defaultPath)):
                loadedTxt = readTxt(defaultPath)
            elif(mainDefaultPath != defaultPath and os.path.isfile(mainDefaultPath)):
                loadedTxt = readTxt(mainDefaultPath)
                
            if(loadedTxt != ''):
                p.prompt += " "
                if uiIgnorePrompt : p.prompt = ''
                p.prompt += loadedTxt
        
        # Change the controlnet input image to the selected one
        controlNetList[0].image = imgData
        controlNetModule.update_cn_script_in_processing(p, controlNetList)
        
        # Begin generating
        proc = process_images(p)
        return proc