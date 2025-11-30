import sys
import time
import logging
from src.config import load_config
import src.bot

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
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
        while True:
            try:
                booking_info = src.bot.find_course(client, config, kursnr)
                if booking_info:
                    logger.info(f"Booking Info found: {booking_info}")
                    success = src.bot.process_booking(client, config, booking_info)
                    if success:
                        logger.info("Process completed successfully.")
                        break # Exit loop on success
                    else:
                        logger.error("Process failed during booking. Retrying...")
                else:
                    logger.info("Course not yet available or booking info not found. Waiting...")
                
                time.sleep(0.5)
            except KeyboardInterrupt:
                logger.info("Bot stopped by user.")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred: {e}")
                time.sleep(1) # Wait a bit longer on error before retrying

if __name__ == "__main__":
    main()
