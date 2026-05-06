from dataset import Dataset
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def download_datasets():
    logger.info("Initializing dataset downloader...")
    
    # We want to download the Network-Flows for CIC-IDS2017
    logger.info("Downloading CIC-IDS2017 Network Flows...")
    cic_dataset = Dataset(dataset='CIC-IDS2017', subset=['Network-Flows'], files='all')
    cic_dataset.download()
    
    logger.info("Downloads complete. Data is cached in the huggingface cache and symlinked to the project directory.")
    
    # We can also merge it to a single parquet file if we wanted, but dataset.py already provides a way to read it.
    # We will copy the downloaded flow file to the ai/datasets folder so pipeline.py can use it.
    import shutil
    from pathlib import Path
    
    # dataset.py downloads to CIC-IDS2017/Network-Flows/CICIDS_Flow.parquet
    source_file = Path("CIC-IDS2017/Network-Flows/CICIDS_Flow.parquet")
    dest_dir = Path("ai/datasets")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "network_traffic.parquet"
    
    if source_file.exists():
        logger.info(f"Copying {source_file} to {dest_file}")
        shutil.copy(source_file, dest_file)
        logger.info("Dataset successfully prepared for pipeline.py!")
    else:
        logger.warning(f"Could not find {source_file}. Did the download fail?")

if __name__ == "__main__":
    download_datasets()
