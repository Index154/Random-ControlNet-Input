# Random ControlNet Input
A custom script for [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). When enabled chooses a random input image for ControlNet unit 0 from a custom folder path every time you start a generation process. With additional features such as dynamic prompt modifications for the positive prompt, randomized flipping of the input image and custom weights for select subfolders or files.


## Installation
1. Install the [ControlNet extension](https://github.com/Mikubill/sd-webui-controlnet)
2. In the WebUI navigate to: Extensions -> Install from URL
4. Paste this link into the "URL for extension's git repository" box: https://github.com/Index154/Random-ControlNet-Input
5. Click on Install and wait for it to finish installing
6. Select the "Installed" tab and click on "Apply and restart UI"


## Basic usage
1. On the txt2img or img2img tab scroll down to find the script selector
2. Select "Random ControlNet Input"
3. Paste the path to a folder with PNG files in it into the "Image source folder" input box
4. Enable ControlNet Unit 0 and adjust its settings to your liking. You do not need to select an image for it manually at any point
5. When you click "Generate" the script will select a random PNG file from the folder as the ControlNet Unit 0 input (it will not be displayed in the ControlNet UI)

If you increase the batch count then each batch will use a different randomly selected ControlNet input image!


## Extra details and special features
All available settings for the script are found directly below the Script selector in the WebUI after selecting the script.

### Recursive file scan
PNG files in all subfolders of your defined source folder are included in the random selection by default. This can be turned off with a checkbox.

### Random horizontal flipping
There is a 50% chance for the input image to be flipped horizontally. You can disable this feature with a checkbox.

### Dynamic prompt additions with TXT files
TXT files can be used to add extra text to your prompt based on which image was randomly selected. This can be turned off with a checkbox. It works like this:
- The script looks for a TXT file with the same name as the PNG file that was selected. It will only look for this file in the folder the image is in
  - If there is no such TXT file then it looks for a file called default.txt in the same folder
    - If there is no such file either then it looks for a default.txt in every parent folder one by one until it finds one to use or it reaches the "main" parent folder defined in the UI
- If a TXT file was found then the contents of it will be appended to the positive prompt
- If no TXT file was found then no actions are taken

There is an extra checkbox that can be enabled to replace the positive prompt in your UI with the contents of the TXT file if one is loaded like this. All the special syntax features explained below this point will still be applied however!

You can use the string {default} to force the script to include the contents of the next-best default.txt in the folder tree of the selected input image. The idea is to put this into the TXT files for specific images so you can always have your default prompt addition included along with the more specific stuff. If you ever decide to modify the defaults then you won't have to edit every single TXT file.

### String substitution
You can define string substitutions for the positive prompt with the following syntax: `!stringA=>stringB!` - If you put this into your positive prompt then any occurrence of stringA will be replaced with stringB in the final positive prompt. This feature is useful for making quick and temporary changes to the prompts defined in the TXT files. All string substitution syntax will be removed from the prompt before any images are generated.

### Randomize by direct subfolder
The default behavior of the script is to assign all images to the top-level folder they are in (the direct subfolders of the path you define in the UI). Each folder is given an equal weight of 1 to be selected in the randomization process. Images placed directly in the main folder are assigned a weight of 1 each just like the folders. When you begin generating the script randomly selects one of these folders or images with assigned weights. If what was selected is a folder then it will randomly select one of the images assigned to that folder.

You can change this behavior by either turning off the folder-based randomization completely or by assigning custom weights to folders / files (see below). If you turn off the randomization by subfolder then all images will have an equal chance of being selected.

### Custom folder / file weights
You can define custom weights for subfolders or for specific filenames by including a special syntax in your positive prompt. Examples:
- `!favorites=4!` = All folders named favorites will have a weight of 4
- `!standing, from above.png=999!` = *All files* with the name "standing, from above.png" will have a weight of 999

If you define custom weights for any folder or filename then all images with that name or in that folder (or its subfolders) will be added to this custom "pool". File names have the highest priority for weight pool matching. Lower level folders will take precedence over ones higher in the tree. Currently if you have any folders with the same names then there is no way of distinguishing between them using this syntax.

You can enable a setting to make the script treat your custom weight names as regular expressions. With this feature turned on the image files will be assigned to a weight pool if their names or the names of any of their parent folders match the given expression. Example expression:
- `!.*from below.*=20!` = Any file with "from below" in its name will be assigned to this pool. The same goes for files inside folders with "from below" in their name

The custom weight syntax will be removed from your prompt before generation begins.

### Force-enable ControlNet
There is a checkbox you can enable so unit 0 of ControlNet will always be enabled automatically at runtime when you generate images as long as the script is active. This can be useful since having ControlNet be turned on by default through ui-config.json seemed to not work when I tried it.


## Known issues & limitations
- For now I have not bothered to add support for multiple ControlNet units or even just selecting a specific unit. I will consider it if anyone asks for it
- It only looks for and loads PNG files for now because I had no need for other file types
- The script only reads special syntax from positive prompts for now and only positive prompts can be modified through the TXT files
- Custom weights can not differentiate between folders and files with the same name even if they have different parent folders


## Recommended extensions
- [Dynamic Prompts](https://github.com/adieyal/sd-dynamic-prompts) for randomization of prompt contents
- [Style Vars](https://github.com/SirVeggie/extension-style-vars) for assigning styles conditionally (either through the TXT files or dynamic prompting). Great for quick substitutions

The changes made to the prompt by these extensions are applied AFTER those made by this script!
