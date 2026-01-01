# album-spectrum

A Python tool that organizes album covers into a nice grid based on their colors

---

## How It Works

1. Reads images from specified directory
2. Computes each image’s average color (in HLS)
3. Images are sorted based on hue (for column) and lightness (for rows)
4. Outputs a single combined grid image

*(Optional)* Renamed, ordered `.jpg` files for organization in a separate directory

---

## (Default) Project Structure

```bash
album-spectrum/
├── main.exe
├── main.py
├── config.json
├── images/
│ └── original/ # input images
│ └── new/      # organized images
├── output/
│ └── final.png # final grid image
```
> You can provide your own album covers locally by changing the config

---

## Configuration

All settings live in `config.json`:

```json
{
    "input_directory": "./images/original",
    "output_directory": "./output",
    "ordering_directory": "./images/new",
    "resolution": 500,
    "ordered": true
}
```

1. "input_directory" is the folder that will contain all the original images that will be used to generate the final grid
2. "output_directory" is the folder where the final grid that will be generated
3. "ordering_directory" is the folder that will contain the same original images but renamed to be ordered as in the final grid
4. "resolution" is the value (in pixels) that the program will crop to a square (i.e. every image will be cropped to 500x500 resolution in the final grid as shown in the example)
5. "ordered" is the value to determine if the original images will be copied and renamed to `ordering_directory`, and values are either true or false

## Usage

Use `main.exe` executable to run the program. Once run, the program will automatically generate the final grid image based on its input and configuration settings in `config.json`
