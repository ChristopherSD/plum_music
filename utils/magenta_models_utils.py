import requests
from pathlib import Path

from config.config import get_constants_dict

import tensorflow as tf
from magenta.models.music_vae import TrainedModel, configs


def download_checkpoint(model_name: str,
                        checkpoint_name: str,
                        target_dir: str):
    """
    Adapted from
    https://github.com/PacktPublishing/hands-on-music-generation-with-magenta/blob/master/Chapter04/chapter_04_example_01.py.
    :param model_name:
    :param checkpoint_name:
    :param target_dir:
    :return:
    """
    tf.io.gfile.makedirs(target_dir)
    checkpoint_target = Path(target_dir) / checkpoint_name
    if not checkpoint_target.exists():
        response = requests.get(
            f"https://storage.googleapis.com/magentadata/models/"
            f"{model_name}/checkpoints/{checkpoint_name}"
        )
        data = response.content
        with checkpoint_target.open('wb') as f:
            f.write(data)


def get_model(name: str, batch_size: int = 8):
    constants = get_constants_dict()

    checkpoint = name + ".tar"
    download_checkpoint("music_vae", checkpoint, constants["MODELS_MUSICVAE_PATH"])

    return TrainedModel(
        config=configs.CONFIG_MAP[name],
        batch_size=batch_size,
        checkpoint_dir_or_path=str(Path(constants["MODELS_MUSICVAE_PATH"], checkpoint))
    )
