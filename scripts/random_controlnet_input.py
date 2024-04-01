import gradio as gr
import os
import modules.scripts as scripts
from modules.processing import process_images, process_images_inner, Processed
from modules.shared import state

import random
import copy
from PIL import Image
from io import BytesIO
import base64
import re
import importlib
import glob

class Script(scripts.Script):

    def title(self):
        return "Random ControlNet Input Batch"

    def ui(self, is_img2img):
        uiActive = gr.Checkbox(True, label="Activate script")
        uiFolderPath = gr.Textbox(label="Image source folder", lines=1)
        uiRecursive = gr.Checkbox(True, label="Include subfolders")
        uiFolderRandom = gr.Checkbox(True, label="Randomize by direct subfolder")
        uiFlip = gr.Checkbox(True, label="Flip input image horizontally 50% of the time")
        uiModifyPrompt = gr.Checkbox(True, label="Dynamic prompt additions with TXT files")
        uiIgnorePrompt = gr.Checkbox(False, label="Replace positive UI prompt with TXT contents")
        uiRegex = gr.Checkbox(False, label="Read custom weight names as regular expressions")
        uiForceControlNet = gr.Checkbox(False, label="Force-enable ControlNet Unit 0")
        return [uiActive, uiRecursive, uiFolderPath, uiModifyPrompt, uiIgnorePrompt, uiFolderRandom, uiForceControlNet, uiFlip, uiRegex]

    def run(self, p, uiActive, uiRecursive, uiFolderPath, uiModifyPrompt, uiIgnorePrompt, uiFolderRandom, uiForceControlNet, uiFlip, uiRegex):
    
        # Function for replacing text in string
        def replaceText(text):
            for replace in replaces:
                if(replace is not None):
                    parts = replace[1:-1].split('=>')
                    text = text.replace(parts[0], '=>'.join(parts[1:]))
            return text
        
        # Function for loading a random image
        def generateImage(p):
            p2 = copy.copy(p)
            
            # Function for txt file reading
            def readTxt(txtPath):
                try:
                    with open(txtPath, 'r') as txtFile:
                        txtContent = txtFile.read().replace('\n', '')
                except:
                    raise Exception("<Random Controlnet Input> - Failed to read text file " + txtPath)
                return txtContent
            
            # Function for loading default.txt
            def getDefault(txtPath):
                splitTxtPath = txtPath.split(separator)
                mainDefaultPath = os.path.join(uiFolderPath, 'default.txt')
                
                loaded = ''
                index = -1
                while index < len(splitTxtPath) and loaded == '':
                    path = os.path.join(separator.join(splitTxtPath[:index]), "default.txt")
                    if os.path.isfile(path): loaded = readTxt(path)
                    if path == mainDefaultPath : break
                    index -= 1
                return loaded
            
            # Enable ControlNet if turned off
            controlNetList = controlNetModule.get_all_units_in_processing(p2)
            if(not controlNetList[0].enabled):
                if uiForceControlNet : controlNetList[0].enabled = True
                else: return
        
            # Select a random image
            roll = random.randrange(1, totalWeight + 1)
            selectedImg = ''
            weightCheck = 0
            i = 0
            while i < len(folders) and selectedImg == '':
                weightCheck += folders[i]['value']
                if(roll <= weightCheck):
                    if (len(folders[i]['images']) > 0):
                        selectedImg = random.choice(folders[i]['images'])
                i += 1
            if selectedImg == '' : raise Exception("<Random Controlnet Input> - The randomization ended without a chosen image even though other checks should have prevented this from happening. Please test the reproducability of this and report the issue")
            
            # Load image
            try:
                with Image.open(selectedImg) as img:
                    if uiFlip and random.choice([True, False]) : img = img.transpose(Image.FLIP_LEFT_RIGHT)
                    io = BytesIO()
                    img.save(io, format='PNG')
                    imgData = controlNetModule.to_base64_nparray(base64.b64encode(io.getvalue()).decode())
            except:
                raise Exception("<Random Controlnet Input> - Failed to read image file " + selectedImg)
                return
            
            # Add text from txt file with same filename to prompt if enabled. If no file is found, look for default.txt in the same folder and in the main folder entered by the user
            if(uiModifyPrompt):
                txtPath = selectedImg[:-4] + '.txt'
                loadedTxt = ''
                if(os.path.isfile(txtPath)):
                    loadedTxt = readTxt(txtPath)
                else:
                    loadedTxt = getDefault(txtPath)
                    
                if(loadedTxt != ''):
                    p2.prompt += ", "
                    if uiIgnorePrompt or batch_count > 1 : p2.prompt = ''
                    p2.prompt += loadedTxt
                    if '{default}' in p2.prompt : p2.prompt = p2.prompt.replace('{default}', getDefault(txtPath))  # Replace {default} with contents from default.txt
                    p2.prompt = replaceText(p2.prompt)
            
            # Change the controlnet input image to the selected one
            controlNetList[0].image = imgData
            controlNetModule.update_cn_script_in_processing(p2, controlNetList)
            proc = process_images(p2)
            return proc
        
    
        # Get substitution strings from prompt and remove them
        pattern = r'!.*?=>.*?!'
        replaces = re.findall(pattern, p.prompt)
        p.prompt = re.sub(pattern, '', p.prompt)
        separator = os.path.join('a', 'a')[1:2]
        
        # Get custom weight pools from prompt and remove them
        pattern = r'!.*?=.*?!'
        weights = re.findall(pattern, p.prompt)
        p.prompt = re.sub(pattern, '', p.prompt)
        folders = []
        totalWeight = 0
        for weight in weights:
            weightSplit = weight[1:-1].split('=')
            weightSplit[1] = int(weightSplit[1])
            if weightSplit[1] < 1 : weightSplit[1] = 1
            totalWeight += weightSplit[1]
            newWeight = {'name': weightSplit[0], 'value': weightSplit[1], 'images': []}
            folders.append(newWeight)
    
        # Abort if the script is inactive (still do the text replacing anyway)
        if(not uiActive):
            p.prompt = replaceText(p.prompt)
            proc = process_images(p)
            return proc
        
        # Error if controlnet is missing
        try:
            controlNetModule = importlib.import_module('extensions.sd-webui-controlnet.scripts.external_code', 'external_code')
        except:
            raise Exception("<Random ControlNet Input> - ControlNet extension not found!")
            return
        
        # Error if there is no path supplied
        if(uiFolderPath == ""):
            raise Exception("<Random ControlNet Input> - Please enter an image source folder path")
            return
        
        # Error if folder does not exist
        if(not os.path.isdir(uiFolderPath)):
            raise Exception("<Random ControlNet Input> - Image source folder not found")
        
        # Get list of files in folder
        if(uiRecursive):
            searchPath = os.path.join(uiFolderPath, '**', '*.png')
        else:
            searchPath = os.path.join(uiFolderPath, '*.png')
        files = [f for f in glob.glob(searchPath, recursive=True) if os.path.isfile(f)]
        
        # Error if there are no files
        if(len(files) < 1):
            raise Exception("<Random ControlNet Input> - No PNG files found in image source folder")
            return
            
        # Assign every image to a weight pool
        for f in files:
            f2 = f.replace(uiFolderPath, '').replace(separator + separator, separator)
            f2 = f2.split(separator)
            assigned = False
            if not uiFolderRandom : f2[1] = 'unassigned'   # If uiFolderRandom is turned off, assign all images not matching a custom weight pool to one shared pool called unassigned
            for index, folder in enumerate(folders):
                i = len(f2) - 1
                while i > 0:
                    if(uiRegex):
                        if(re.match(folder['name'].lower(), f2[i].lower()) is not None):
                            folders[index]['images'].append(f)
                            assigned = True
                            break
                    else:
                        if(f2[i].lower() == folder['name'].lower()):
                            folders[index]['images'].append(f)
                            assigned = True
                            break
                    i -= 1
            # If an image could not be assigned to a pool, create a new folder weight for the highest level directory of its path, excluding the main path entered by the user
            if(not assigned):
                totalWeight += 1
                newWeight = {'name': f2[1], 'value': 1, 'images': [f]}
                folders.append(newWeight)
        
        # Log all weight pools and remove empty pools
        print('')
        print('<Random ControlNet Input> - Weight pools:')
        for f in folders:
            print('    ' + f['name'] + ': Weight = ' + str(f['value']) + ' & image count = ' + str(len(f['images'])))
            if len(f['images']) < 1 : raise Exception("<Random Controlnet Input> - The custom weight for \"" + f['name'] + "\" is affecting no images! Please check for typos")
        print('')
        
        # Begin generating
        batch_results = None
        batch_count = p.n_iter
        p.n_iter = 1
        print(f"Will process {batch_count} images, creating {p.batch_size} new images for each.")
        state.job_count = batch_count
        for i in range(batch_count):
            state.job = f"{i+1} out of {batch_count}"
            if state.skipped:
                state.skipped = False

            if state.interrupted or state.stopping_generation:
                break
            proc = generateImage(p)
            
            if proc is not None:
                if batch_results:
                    batch_results.images.extend(proc.images)
                    batch_results.infotexts.extend(proc.infotexts)
                else:
                    batch_results = proc
            
        return batch_results
