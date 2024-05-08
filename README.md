# Prompt-to-Song Generation using Large Language Models


## Lyric Generation from the textual prompt


## Genre Classification of Lyrics
1. Go to 'genre_classifier' folder
2. Run the following command: python3 trainer.py --transformer_name distilbert-base-uncased --tokenizer_name distilbert-base-uncased --freeze_transformer True --batch_size 128 --learning_rate 3e-4 --epochs 100
3. It will generate model for every epoch in models folder. Keep which you felt have good accuracy and delete rest.

## Chord Progression Conditoned on the Lyrics and Genre

### Transformer-2-Sequence
1. Go to 'transformer_2_sequence' folder
2. Copy model saved in 'genre_classifier' folder to 'artifacts' in the current path and rename it to 'encoder.pth'
3. Run the following command: python3 trainer.py --batch_size 128 --learning_rate 3e-4 --epochs 50
4. It will generate model for every epoch in models folder. Keep which you felt have good accuracy and delete rest.

### RHLF

#### Reward Model
1. Go to 'rhlf/reward_model' folder
2. Run the following command: python3 trainer.py --batch_size 128 --learning_rate 3e-4 --epochs 50
3. It will generate model for every epoch in models folder. Keep which you felt have good accuracy and delete rest.

#### Reinforcement using Policy Gradient
1. Go to 'rhlf/policy_gradient' folder
2. Copy model saved in 'genre_classifier' folder to 'artifacts' in the current path and rename it to 'encoder.pth'
3. Copy model saved in 'rhlf/reward_model' folder to 'artifacts' in the current path and rename it to 'reward_model.pth'
4. python3 trainer.py --batch_size 128 --learning_rate 3e-4 --epochs 50
5. It will generate model for every epoch in models folder. Keep which you felt have good accuracy and delete rest.


## Final Pipeline
1. Go to 'pipeline' folder
2. Copy model saved in 'genre_classifier' folder to 'artifacts' in the current path and rename it to 'encoder.pth'
3. Copy model saved in 'transformer_2_sequence' folder to 'artifacts' in the current path and rename it to 'decoder_tf_2_seq.pth'
4. Copy model saved in 'rhlf/policy_gradient' folder to 'artifacts' in the current path and rename it to 'decoder_rhlf.pth'
5. Got to 'input.ipynb' notebook and play accordingly