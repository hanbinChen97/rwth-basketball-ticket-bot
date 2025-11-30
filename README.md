<div align="center">
  <img src="https://via.placeholder.com/800x200?text=RWTH+Basketball+Ticket+Bot" alt="RWTH Basketball Ticket Bot Banner" width="100%" />

  # RWTH Basketball Ticket Bot

  <p>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python Version">
    </a>
    <a href="https://github.com/astral-sh/uv">
      <img src="https://img.shields.io/badge/uv-managed-purple.svg" alt="uv managed">
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
    </a>
  </p>

  <p>
    <b>Fast, lightweight automated booking system for RWTH Aachen University Sports.</b>
  </p>
</div>

## 📖 Introduction

This bot automates the process of booking sports slots at RWTH Aachen University. It uses **Python** and **httpx** to interact directly with the booking system, making it significantly faster and more reliable than browser-based automation.

## 📂 Project Structure

```text
rwth-basketball-ticket-bot/
├── config/
│   └── settings.toml    # Configuration: User Info, URLs, Headers
├── src/
│   ├── bot.py           # Core bot logic (finding courses, booking)
│   ├── config.py        # Configuration loader
│   └── main.py          # Entry point
├── pyproject.toml       # Project dependencies
└── uv.lock              # Dependency lock file
```

## 🚀 Getting Started

### Prerequisites

- **Python 3.12+**
- **[uv](https://github.com/astral-sh/uv)** (Recommended) or `pip`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hanbinChen97/rwth-basketball-ticket-bot.git
    cd rwth-basketball-ticket-bot
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    # OR
    pip install httpx beautifulsoup4 loguru toml
    ```

### Configuration

1.  Open `config/settings.toml`.
2.  Fill in your personal details in the `[userInfo]` section.
3.  Set the `kursnr` to the course number you want to book.

```toml
[userInfo]
gender = "männlich"
firstName = "Max"
lastName = "Mustermann"
# ... other fields
kursnr = "1234567"
```

### Usage

**Run the Bot:**

You can run the bot using `uv` (recommended) or directly with python.

```bash
# Run with default Kursnr from config
uv run python -m src.main

# Run with a specific Kursnr (overrides config)
uv run python -m src.main 1234567
```

## 🛠️ How it Works

1.  **Find Course**: The bot fetches the main sports page and searches for the row containing the specified `Kursnr`.
2.  **Get Booking Link**: It extracts the booking URL (or form action) from that row.
3.  **Access Booking Page**: It navigates to the booking popup/page.
4.  **Enter Registration**: It finds the "Buchen" button, submits it, and enters the registration form.
5.  **Fill & Submit**: It fills the form with your configured data (handling dynamic fields like Student ID) and submits it.
6.  **Confirm**: It handles the final "Verbindlich buchen" confirmation step.

---
<div align="center">
  Made with ❤️ by Hanbin
</div>
