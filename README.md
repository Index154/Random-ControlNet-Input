## Random-ControlNet-Input
A custom script for [Stable Diffusion WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui). When enabled, chooses a random ControlNet input image from a custom folder path when you start the generation process.

### Installation
Put the script into the scripts folder of Stable Diffusion WebUI. Then reload the UI or restart the whole application.

### Prerequisites
You will need to have the [ControlNet extension](https://github.com/Mikubill/sd-webui-controlnet) installed for this to work.

### Basic usage
1. On the txt2img or img2img tab, scroll down to find the script selector
2. Select "Random ControlNet Input"
3. Paste the path to a folder with png files in it into the "Image source folder" input box
4. Enable ControlNet Unit 0 and adjust its settings to your liking. You do not need to select an image for it manually at any point
5. When you click "Generate" the script will select a random png file from the folder as the ControlNet Unit 0 input (it will not be displayed in the ControlNet UI)

### Extra details and features
PNG files in all subfolders of your defined source folder are included in the random selection by default. This can be turned off with a checkbox.

TXT files can be used to add extra keywords to your prompt based on the image that was randomly selected. It works like this:
- If the corresponding checkbox is set, the script will look for a TXT file with the same name as the PNG file that was selected. It will only look for this file in the folder the image is in
- If there is no such TXT file then it will look for a file called default.txt in the same folder
- If there is no such file either then it will look for a default.txt in the path you have set as the main image source folder
- If it finds a TXT file then the contents of it will be appended to the positive prompt
- There is one more checkbox that can be activated to make it so the prompt in your UI will be ignored entirely when a TXT file is loaded like this

You can define string substitutions for the positive prompt with the following syntax: `!replace:stringA=>stringB!` If you put this into your prompt then any occurrence of stringA will be replaced with stringB in the final prompt. This functionality works even if your UI prompt is set to be ignored through the corresponding checkbox option. The reason I added this feature is to make quick and temporary changes to the prompts defined in the TXT files a little bit easier.

### Known issues and limitations
- I don't know how to make ControlNet use a different input image for each batch. It might not be possible
- For now I have not bothered to add support for multiple ControlNet units or even just selecting a specific unit. I will consider it if anyone asks for it
- It only looks for and loads PNG files for now because I had no need for other file types
- A way to control the weight / probability of subfolders or specific images for the randomization would probably be nice to have. I might add this later

### Recommended extensions
- [Dynamic Prompts](https://github.com/adieyal/sd-dynamic-prompts) for randomization of prompt contents
- [Style Vars](https://github.com/SirVeggie/extension-style-vars) for assigning styles conditionally (either through the TXT files or dynamic prompting). Great for quick substitutions.
The changes made to the prompt by these extensions are applied AFTER those made by this script!
