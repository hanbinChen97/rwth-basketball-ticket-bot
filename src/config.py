import toml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class UserInfo:
    gender: str
    first_name: str
    last_name: str
    address: str
    zip_city: str
    status: str
    student_id: str
    email: str
    phone: str
    accept_terms: bool
    kursnr: str

@dataclass
class Config:
    target_url: str
    kurs_row: int
    user_headers: dict
    user_info: UserInfo

def load_config(config_path: str = "config/settings.toml") -> Config:
    """Load configuration from a TOML file."""
    root_dir = Path(__file__).parent.parent
    config_file = root_dir / config_path
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
        
    data = toml.load(config_file)
    
    user_info_data = data.get("userInfo", {})
    user_info = UserInfo(
        gender=user_info_data.get("gender", ""),
        first_name=user_info_data.get("firstName", ""),
        last_name=user_info_data.get("lastName", ""),
        address=user_info_data.get("address", ""),
        zip_city=user_info_data.get("zipCity", ""),
        status=user_info_data.get("status", ""),
        student_id=user_info_data.get("studentId", ""),
        email=user_info_data.get("email", ""),
        phone=user_info_data.get("phone", ""),
        accept_terms=user_info_data.get("acceptTerms", False),
        kursnr=user_info_data.get("kursnr", "")
    )
    
    return Config(
        target_url=data.get("TARGET_URL", ""),
        kurs_row=int(data.get("kursRow", 0)),
        user_headers=data.get("USER_HEADERS", {}),
        user_info=user_info
    )

if __name__ == "__main__":
    # Test loading
    try:
        cfg = load_config()
        print("Config loaded successfully:")
        print(f"Target URL: {cfg.target_url}")
        print(f"User Info: {cfg.user_info}")
    except Exception as e:
        print(f"Failed to load config: {e}")
