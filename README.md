# Random-ControlNet-Input
A custom script for [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). When enabled, chooses a random ControlNet input image from a custom folder path when you start the generation process.


## Installation
Put the script into the scripts folder of Stable Diffusion WebUI. Then reload the UI or restart the whole application.


## Prerequisites
You will need to have the [ControlNet extension](https://github.com/Mikubill/sd-webui-controlnet) installed for this to work.


## Basic usage
1. On the txt2img or img2img tab, scroll down to find the script selector
2. Select "Random ControlNet Input"
3. Paste the path to a folder with png files in it into the "Image source folder" input box
4. Enable ControlNet Unit 0 and adjust its settings to your liking. You do not need to select an image for it manually at any point
5. When you click "Generate" the script will select a random png file from the folder as the ControlNet Unit 0 input (it will not be displayed in the ControlNet UI)


## Extra details and special features
### Recursive file scan
PNG files in all subfolders of your defined source folder are included in the random selection by default. This can be turned off with a checkbox.

### Dynamic prompt additions with TXT files
TXT files can be used to add extra text to your prompt based on which image was randomly selected. This can be turned off with a checkbox. It works like this:
- The script looks for a TXT file with the same name as the PNG file that was selected. It will only look for this file in the folder the image is in
  - If there is no such TXT file then it looks for a file called default.txt in the same folder
    - If there is no such file either then it looks for a default.txt in every parent folder one by one until it finds one to use or it reaches the "main" parent folder defined in the UI
- If a TXT file was found then the contents of it will be appended to the positive prompt

There is an extra checkbox that can be enabled to replace the positive prompt in your UI with the contents of the TXT file if one is loaded like this. All the special syntax features explained below this point will still be applied however!

You can use the special string {default} to force the script to include the contents of the next-best default.txt in the folder tree. So you can put this into the TXT files for specific images and always have your default prompt addition included along with the more specific stuff.

### String substitution
You can define string substitutions for the positive prompt with the following syntax: `!stringA=>stringB!` - If you put this into your positive prompt then any occurrence of stringA will be replaced with stringB in the final positive prompt. The reason I added this feature is to make quick and temporary changes to the prompts defined in the TXT files a little bit easier. All string substitution syntax will be removed from the prompt before any images are generated.

### Randomize by direct subfolder
The default behavior of the script is to assign all images to the top-level folder they are in (the direct subfolders of the path you define in the UI). Each folder is given an equal weight of 1 to be selected in the randomization process. A completely random image from within that folder (or its subfolders) is then selected.

You can change this behavior by either turning off the folder-based randomization completely or by assigning custom weights to folders / files (see below). If you turn off the randomization by subfolder then all images will have an equal chance of being selected.

### Custom folder / file weights
You can define custom weights for subfolders or for specific filenames by including a special syntax in your positive prompt. Examples:
- `!favorites=4!` = The folder named favorites will have a weight of 4
- `!standing, from above.png=999!` = *All files* with the name "standing, from above.png" will have a weight of 999

If you define custom weights for any folder or filename then all images with that name or in that folder (or its subfolders) will be added to this custom pool. File names have the highest priority for weight pool matching. Lower level folders will take precedence over ones higher in the tree. Currently if you have any folders with the same names then there is no way of distinguishing between them using this syntax.

The custom weight syntax will be removed from the prompt before generation begins.


## Known issues and limitations
- I don't know how to make ControlNet use a different input image for each batch. It might not be possible
- For now I have not bothered to add support for multiple ControlNet units or even just selecting a specific unit. I will consider it if anyone asks for it
- It only looks for and loads PNG files for now because I had no need for other file types
- Custom weights can not differentiate between folders with the same name even if they have different parent folders


## Recommended extensions
- [Dynamic Prompts](https://github.com/adieyal/sd-dynamic-prompts) for randomization of prompt contents
- [Style Vars](https://github.com/SirVeggie/extension-style-vars) for assigning styles conditionally (either through the TXT files or dynamic prompting). Great for quick substitutions.

The changes made to the prompt by these extensions are applied AFTER those made by this script!
