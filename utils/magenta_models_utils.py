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


def _get_multitrack_model(name: str = 'hier-multiperf_vel_1bar_med', batch_size: int = 8) -> TrainedModel:
    """
    Download the musicVAE multitrack model and returns a TrainedModel with the given batch size.
    This model (hier-multiperf_vel_1bar_med_chords or hier-multiperf_vel_1bar_med) is not listed on the official
    Github repository. The checkpoints have to be downloaded manually with the gsutil command line tool:
    gsutil -m cp gs://download.magenta.tensorflow.org/models/music_vae/multitrack/* <output_dir>

    :param name: One of 'hier-multiperf_vel_1bar_med_chords' or 'hier-multiperf_vel_1bar_med' (default).
    Whether to load the chord conditioned or the unconditioned model.
    :param batch_size: The batch size for the TrainedModel to build the model graph with.
    :return: A musicVAE.TrainedModel with the given configuration.
    """
    constants = get_constants_dict()

    if "chords" in name:
        checkpoint = Path(constants["MODELS_MUSICVAE_PATH"], "multitrack", "conditioned",
                          constants["CHECKPOINT_MUSICVAE_MULTITRACK_CONDITIONED"])
    else:
        checkpoint = Path(constants["MODELS_MUSICVAE_PATH"], "multitrack", "unconditioned",
                          constants["CHECKPOINT_MUSICVAE_MULTITRACK"])

    return TrainedModel(
        config=configs.CONFIG_MAP[name],
        batch_size=batch_size,
        checkpoint_dir_or_path=str(checkpoint)
    )


def get_model(name: str, batch_size: int = 8) -> TrainedModel:
    """
    Download the musicVAE model given by name and return a TrainedModel according to its config.
    :param name: The name of the model retrieve. One of:
    - cat-mel_2bar_big
    - hierdec-trio_16bar
    - hierdec-mel_16bar
    - cat-drums_2bar_small.hikl
    - hier-multiperf_vel_1bar_med_chords
    - hier-multiperf_vel_1bar_med
    :param batch_size: The batch size for the TrainedModel to build the model graph with.
    :return: A musicVAE.TrainedModel with the given configuration.
    """
    constants = get_constants_dict()

    if "multiperf" in name.lower():
        model = _get_multitrack_model(name, batch_size)
        return model

    checkpoint = name + ".tar"
    download_checkpoint("music_vae", checkpoint, constants["MODELS_MUSICVAE_PATH"])

    return TrainedModel(
        config=configs.CONFIG_MAP[name],
        batch_size=batch_size,
        checkpoint_dir_or_path=str(Path(constants["MODELS_MUSICVAE_PATH"], checkpoint))
    )
