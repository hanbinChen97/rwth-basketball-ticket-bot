import sys
import logging
from src.config import load_config
import src.bot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        config = load_config()
    except Exception as e:
        logger.error(f"Configuration error: {e}")
        return

    # Allow overriding Kursnr from command line
    kursnr = config.user_info.kursnr
    if len(sys.argv) > 1:
        kursnr = sys.argv[1]

    if not kursnr:
        logger.error("No Kursnr provided in config or command line")
        return

    logger.info(f"Starting bot for Kursnr: {kursnr}")
    
    with src.bot.create_client(config) as client:
        booking_info = src.bot.find_course(client, config, kursnr)
        if booking_info:
            logger.info(f"Booking Info found: {booking_info}")
            success = src.bot.process_booking(client, config, booking_info)
            if success:
                logger.info("Process completed successfully.")
            else:
                logger.error("Process failed during booking.")
        else:
            logger.error("Failed to find booking info")

if __name__ == "__main__":
    main()
