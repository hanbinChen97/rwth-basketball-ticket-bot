import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
from typing import Optional, Dict, Any, List
from .config import Config, UserInfo

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants for Form Fields and Button Texts
# TODO: Update these values once the actual HTML content is confirmed.
FIELD_MAPPING = {
    'sex': {'male': 'M', 'female': 'W'}, # Value mapping for gender
    'firstname': 'BS_F1100',
    'lastname': 'BS_F1200',
    'street': 'BS_F1300',
    'city': 'BS_F1400',
    'status': 'BS_F1600',
    'email': 'BS_F2000',
    'phone': 'BS_F2100',
    'matriculation': 'matr', # Substring match for name
    'terms': 'tnbed'
}

BUTTON_TEXTS = {
    'buchen': 'buchen',
    'book_button_class': 'bs_btn_buchen'
}

def create_client(config: Config) -> httpx.Client:
    """Create and return a configured httpx Client."""
    return httpx.Client(
        headers=config.user_headers,
        timeout=30.0,
        follow_redirects=True
    )

def fetch_url(client: httpx.Client, url: str, method: str = 'GET', data: dict = None, params: dict = None) -> Optional[httpx.Response]:
    """Helper to perform HTTP requests with error handling."""
    try:
        if method.upper() == 'POST':
            response = client.post(url, data=data)
        else:
            response = client.get(url, params=params)
        response.raise_for_status()
        return response
    except httpx.RequestError as e:
        logger.error(f"Request failed for {url}: {e}")
        return None

def get_course_rows(soup: BeautifulSoup) -> List[Any]:
    """Extract course rows from the main table."""
    courses_table = soup.find('table', class_='bs_kurse')
    if not courses_table:
        logger.error("Could not find course table (table.bs_kurse)")
        return []
    return courses_table.find_all('tr')

def find_row_by_kursnr(rows: List[Any], kursnr: str) -> Optional[Any]:
    """Find the specific row containing the Kursnr."""
    for row in rows:
        if kursnr in row.get_text():
            return row
    return None

def extract_booking_info_from_row(row: Any, base_url: str) -> Optional[Dict[str, Any]]:
    """Extract booking URL and method from the course row."""
    booking_cell = row.find(class_='bs_sbuch')
    if not booking_cell:
        logger.error("Found row but no booking cell (.bs_sbuch)")
        return None
        
    # Check for "buchen" button (Form)
    book_button = booking_cell.find('input', class_=BUTTON_TEXTS['book_button_class'])
    if book_button:
        form = book_button.find_parent('form')
        if form:
            action = form.get('action')
            method = form.get('method', 'get').lower()
            booking_url = urljoin(base_url, action) if not action.startswith('http') else action
            
            inputs = {
                input_tag.get('name'): input_tag.get('value') 
                for input_tag in form.find_all('input') 
                if input_tag.get('name')
            }
            logger.info(f"Found booking form. Action: {booking_url}")
            return {'type': 'form', 'url': booking_url, 'method': method, 'inputs': inputs}
    
    # Check for link
    link = booking_cell.find('a')
    if link:
        href = link.get('href')
        full_url = urljoin(base_url, href)
        logger.info(f"Found booking link: {full_url}")
        return {'type': 'link', 'url': full_url}

    logger.warning("Row found but no recognized booking button or link")
    return None

def find_course(client: httpx.Client, config: Config, kursnr: str) -> Optional[Dict[str, Any]]:
    """High-level function to find a course and return booking info."""
    logger.info(f"Navigating to target URL: {config.target_url}")
    response = fetch_url(client, config.target_url)
    if not response:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    rows = get_course_rows(soup)
    logger.info(f"Found {len(rows)} rows in course table")
    
    target_row = find_row_by_kursnr(rows, kursnr)
    if not target_row:
        logger.error(f"Course with Kursnr {kursnr} not found")
        return None

    logger.info(f"Found row for Kursnr {kursnr}")
    return extract_booking_info_from_row(target_row, str(response.url))

def find_form_by_button_text(soup: BeautifulSoup, text_hint: str) -> Optional[Any]:
    """Find a form that contains a submit button with specific text."""
    forms = soup.find_all('form')
    for form in forms:
        # Check input[type=submit]
        submit_btn = form.find('input', type='submit')
        if submit_btn:
            val = submit_btn.get('value', '').lower()
            name = submit_btn.get('name', '').lower()
            if text_hint in val or text_hint in name:
                return form
        
        # Check button tag
        btn = form.find('button')
        if btn and text_hint in btn.get_text().lower():
            return form
            
    return None

def extract_form_submission_data(form: Any, base_url: str) -> Dict[str, Any]:
    """Extract action URL, method, and input data from a form."""
    action = form.get('action')
    method = form.get('method', 'get').lower()
    url = urljoin(base_url, action)
    
    data = {
        input_tag.get('name'): input_tag.get('value', '')
        for input_tag in form.find_all('input')
        if input_tag.get('name')
    }
    return {'url': url, 'method': method, 'data': data}

def handle_buchen_step(client: httpx.Client, html_content: str, base_url: str) -> Optional[httpx.Response]:
    """Find and submit the 'Buchen' button on the popup page."""
    soup = BeautifulSoup(html_content, 'html.parser')
    buchen_form = find_form_by_button_text(soup, BUTTON_TEXTS['buchen'])
    
    if not buchen_form:
        # Fallback: if only one form exists, it might be the one
        forms = soup.find_all('form')
        if forms:
            logger.warning("Explicit 'Buchen' button not found, trying the first form.")
            buchen_form = forms[0]
        else:
            logger.error("No booking form found on the page")
            return None

    submission = extract_form_submission_data(buchen_form, base_url)
    logger.info(f"Submitting 'Buchen' form to {submission['url']}")
    
    return fetch_url(client, submission['url'], method=submission['method'], 
                     data=submission['data'] if submission['method'] == 'post' else None,
                     params=submission['data'] if submission['method'] == 'get' else None)

def map_user_to_form_fields(form: Any, user: UserInfo) -> Dict[str, str]:
    """Map UserInfo to the specific fields in the registration form."""
    data = {
        input_tag.get('name'): input_tag.get('value', '')
        for input_tag in form.find_all('input', type='hidden')
        if input_tag.get('name')
    }
    
    def get_name(element_id):
        el = form.find(id=element_id)
        return el.get('name') if el else None

    # Standard fields mapping
    fields = {
        'sex': FIELD_MAPPING['sex']['male'] if user.gender == 'männlich' else FIELD_MAPPING['sex']['female'],
        get_name(FIELD_MAPPING['firstname']): user.first_name,
        get_name(FIELD_MAPPING['lastname']): user.last_name,
        get_name(FIELD_MAPPING['street']): user.address,
        get_name(FIELD_MAPPING['city']): user.zip_city,
        get_name(FIELD_MAPPING['email']): user.email,
        get_name(FIELD_MAPPING['phone']): user.phone,
    }
    
    for name, value in fields.items():
        if name:
            data[name] = value

    # Status field (Select)
    status_el = form.find(id=FIELD_MAPPING['status'])
    if status_el:
        status_name = status_el.get('name')
        for option in status_el.find_all('option'):
            if user.status in option.get_text() or user.status == option.get('value'):
                data[status_name] = option.get('value')
                break

    # Student ID (Dynamic)
    if user.status == 'S-RWTH':
        matr_input = form.find('input', attrs={'name': lambda x: x and FIELD_MAPPING['matriculation'] in x.lower()})
        if matr_input:
            data[matr_input.get('name')] = user.student_id
            logger.info(f"Found matriculation field: {matr_input.get('name')}")
        else:
            logger.warning("Matriculation number field not found")

    # Terms
    if user.accept_terms:
        data[FIELD_MAPPING['terms']] = '1'
        
    return data

def handle_registration_step(client: httpx.Client, html_content: str, user: UserInfo, base_url: str) -> Optional[httpx.Response]:
    """Fill and submit the registration form."""
    soup = BeautifulSoup(html_content, 'html.parser')
    reg_form = soup.find('form')
    if not reg_form:
        logger.error("No registration form found")
        return None
        
    logger.info("Filling registration form")
    form_data = map_user_to_form_fields(reg_form, user)
    
    submission = extract_form_submission_data(reg_form, base_url)
    # Override data with our filled data
    submission['data'] = form_data
    
    logger.info(f"Submitting registration form to {submission['url']}")
    return fetch_url(client, submission['url'], method='POST', data=submission['data'])

def handle_confirmation_step(client: httpx.Client, html_content: str, base_url: str) -> bool:
    """Handle the final confirmation page."""
    soup = BeautifulSoup(html_content, 'html.parser')
    conf_form = soup.find('form')
    
    if not conf_form:
        logger.error("No confirmation form found")
        return False
        
    # Check if we need to click a button or if it's already done
    final_submit = conf_form.find('input', type='submit')
    if final_submit and BUTTON_TEXTS['buchen'] in final_submit.get('value', '').lower():
        logger.info("Found final confirmation button. Submitting...")
        submission = extract_form_submission_data(conf_form, base_url)
        
        # Add button value if needed
        if final_submit.get('name'):
            submission['data'][final_submit.get('name')] = final_submit.get('value')
            
        response = fetch_url(client, submission['url'], method='POST', data=submission['data'])
        if not response:
            return False
        text = response.text.lower()
    else:
        text = html_content.lower()

    if "erfolgreich" in text or "successful" in text:
        logger.info("Booking successful! 🎉")
        return True
    
    logger.warning("Booking finished but success message not found.")
    return True

def process_booking(client: httpx.Client, config: Config, booking_info: Dict[str, Any]) -> bool:
    """
    Execute the full booking flow.
    """
    # 1. Access Booking Page
    logger.info(f"Accessing booking page: {booking_info['url']}")
    response = fetch_url(client, booking_info['url'], 
                         method=booking_info.get('method', 'get'),
                         data=booking_info.get('inputs') if booking_info.get('method') == 'post' else None,
                         params=booking_info.get('inputs') if booking_info.get('method') == 'get' else None)
    if not response:
        return False

    # 2. Handle 'Buchen' Step (Popup)
    response = handle_buchen_step(client, response.text, str(response.url))
    if not response:
        return False

    # 3. Handle Registration Form
    response = handle_registration_step(client, response.text, config.user_info, str(response.url))
    if not response:
        return False

    # 4. Handle Final Confirmation
    return handle_confirmation_step(client, response.text, str(response.url))
