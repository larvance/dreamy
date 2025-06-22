# Dreamy

Dreamy is a digital instrument you can play using your mouse or your hands (via camera input).

It maps screen position to frequency and dynamically generates sound with expressive control.

There are 6 vertical lines displayed on the screen, each representing one of the base notes I recommend using.  
You can also play any frequency in between these lines for continuous pitch variation.

- Up and down movements control the decibel (volume).
- Left and right movements control the frequency (pitch).

This project is inspired by the work of [Mehmet Ünal](https://www.instagram.com/mehmetunal_studio),  
specifically [this post](https://www.instagram.com/p/DLCXRtZsS6a).

## Requirements

- Python 3.10 or higher (tested on Python 3.10.6)

## Installation

```bash
git clone https://github.com/larvance/dreamy.git
cd dreamy
pip install -r requirements.txt
````

## Usage

### Mouse-based control

Press and hold the left mouse button to start playing.

```bash
python -m dreamy mouse
```

### Camera-based control (hand tracking)

The tip of your index finger controls the position on the screen.

```bash
python -m dreamy camera
```

### Camera-based control (face and hand skeleton only)

```bash
python -m dreamy camera_black
```

## Concept

To create Dreamy, I studied the behavior of the instrument shown in the inspiration video. Using audio analysis tools, I
identified key frequencies and their relative positions on screen by measuring hand placement.

I then mapped horizontal screen position to frequency by fitting a quadratic regression model, creating a smooth
continuous function from position to pitch.

Additionally, I observed the sound characteristics, including harmonic echoes at multiples of the base frequency with
decreasing loudness. I implemented this effect to replicate the tonal richness I heard.

All sound synthesis and instrument behavior were implemented from scratch using Python and
the [pyo](https://ajaxsoundstudio.com/software/pyo/) audio library. Other dependencies are used mainly for visuals and
input handling.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project was inspired by the work of [Mehmet Ünal](https://www.instagram.com/mehmetunal_studio) and his innovative
approach to digital musical instruments.
