# Prompt-to-Song-Generation-using-Large-Language-Models

Here's a README.md file for the GitHub repository codebase:

# Prompt-to-Song Generation using Large Language Models

This project implements a system for generating musical compositions from textual prompts by leveraging large language models (LLMs). Given a thematic prompt specifying elements like title, artist, genre, and verse ideas, our system generates song lyrics, predicts the musical genre, and composes a chord progression to produce a complete song.

## Table of Contents

- [Introduction](#introduction)
- [Dataset](#dataset)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Results](#results)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

Generating complete songs from textual prompts is a challenging task that requires understanding the semantics of the prompt, generating stylistically and thematically relevant lyrics, identifying the appropriate musical genre, and composing melodic and harmonic elements to create the final song. This project leverages the power of LLMs to tackle these challenges and enables controllable music creation.

## Dataset

The project utilizes the [Chords Lyric Dataset](https://www.kaggle.com/datasets/eitanbentora/chords-and-lyrics-dataset) from Kaggle, which contains lyrics aligned with chord labels for multiple genres. The dataset is preprocessed to construct input prompts, summarize lyrics, and extract chord progressions. The final dataset contains 9,000 curated prompts, full lyrics, genre labels, and chord progressions.

## Architecture

The system architecture consists of three main components:

1. **Lyric Generation**: Fine-tuned FlanT5 and Llama models are used to generate lyrics from the input prompts.
2. **Genre Classification**: Pre-trained BERT-based models (e.g., DistilBERT) are employed to predict the genre of the generated lyrics.
3. **Chord Progression Generation**: Two approaches are explored:
   - Transformer-2-Sequence model: A two-stage encoder-decoder architecture with a frozen DistilBERT encoder and an LSTM decoder.
   - Reinforcement Learning with Human Feedback (RLHF): A policy network is trained to select chords step-by-step, optimized using feedback from a learned reward model.

## Getting Started

To get started with the project, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/your-username/prompt-to-song.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Download the dataset and place it in the `data/` directory.
4. Preprocess the dataset by running the preprocessing script:
   ```
   python preprocess_data.py
   ```

## Usage

To generate a song from a textual prompt, run the following command:
```
python generate_song.py --prompt "Your prompt here"
```

The generated song will be saved in the `output/` directory.

## Results

The project achieves promising results in generating thematically and stylistically relevant songs from textual prompts. The Transformer-2-Sequence model generates complex and varied chord progressions, while the RLHF approach produces simpler but more coherent progressions. The generated lyrics capture the semantics of the prompt and align with the predicted genre.

For detailed results and analysis, please refer to the [project report](docs/project_report.pdf).

## Contributing

Contributions to the project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request. Make sure to follow the [contribution guidelines](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

We would like to thank Maria Pushparaj from team Pheonix for her assistance in understanding and curating the chords dataset. We also acknowledge the creators of the Chords Lyric Dataset and the open-source libraries used in this project.
