from utils import make_request
from bs4 import BeautifulSoup
from datetime import datetime

def extract_page_html(url):
    return make_request(url)

def extract_all_features(html):
    features = {}
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        dt_dd = {'next_tag': 'dd'}
        dt_dd_price = {**dt_dd, 'target_tag': 'span', 'target_class': 'mr-2'}
        
        mappings = {
            'price': {'find_by': 'dt', 'find_value': 'Vraagprijs', **dt_dd_price},
            'price_per_m2': {'find_by': 'dt', 'find_value': 'Vraagprijs per m²', **dt_dd_price},
            'apartment_type': {'find_by': 'dt', 'find_value': 'Soort appartement', **dt_dd},
            'construction_type': {'find_by': 'dt', 'find_value': 'Soort bouw', **dt_dd},
            'build_year': {'find_by': 'dt', 'find_value': 'Bouwjaar', **dt_dd},
            'living_area': {'find_by': 'dt', 'find_value': 'Wonen', **dt_dd},
            'volume': {'find_by': 'dt', 'find_value': 'Inhoud', **dt_dd},
            'rooms': {'find_by': 'dt', 'find_value': 'Aantal kamers', **dt_dd},
            'energy_label': {'find_by': 'dt', 'find_value': 'Energielabel', **dt_dd},
            'vve_contribution': {'find_by': 'dt', 'find_value': 'Bijdrage VvE', **dt_dd},
            'heating_system': {'find_by': 'dt', 'find_value': 'Verwarming', **dt_dd},
            'address': {'find_by': 'span', 'find_value': 'block text-2xl font-bold md:text-3xl lg:text-4xl', 'by_class': True},
            'postal_city': {'find_by': 'span', 'find_value': 'text-neutral-40', 'by_class': True, 'parent_tag': 'h1', 'parent_class': 'object-header__container'}
        }
        
        for key, params in mappings.items():
            try:
                if params.get('parent_tag'):
                    parent = soup.find(params['parent_tag'], class_=params['parent_class'])
                    element = parent.find(params['find_by'], class_=params['find_value']) if parent else None
                else:
                    if params.get('by_class'):
                        element = soup.find(params['find_by'], class_=params['find_value'])
                    else:
                        element = soup.find(params['find_by'], string=params['find_value'])
                        if element and params.get('next_tag'):
                            element = element.find_next(params['next_tag'])
                            if params.get('target_tag'):
                                element = element.find(params['target_tag'], class_=params['target_class'])
                
                features[key] = element.text.strip() if element else None
            except:
                features[key] = None
        
        return features
    except:
        return {k: None for k in mappings.keys()}
    

    

def process_features(features):
    processed = features.copy()
    current_year = datetime.now().year
    
    # Process numerical values
    numerical_fields = {
        'price': {'replace': ['€', '.']},
        'price_per_m2': {'replace': ['€', '.']},
        'living_area': {'replace': ['m²', '²']},
        'volume': {'replace': ['m³', '³']}
    }
    
    for field, params in numerical_fields.items():
        if processed[field]:
            value = processed[field]
            for r in params['replace']:
                value = value.replace(r, '')
            value = ''.join(filter(str.isdigit, value.strip()))
            processed[field] = int(value) if value else None
    
    # Process VvE contribution
    if processed['vve_contribution']:
        value = processed['vve_contribution'].replace('€', '').replace(',', '.').strip()
        value = ''.join(c for c in value if c.isdigit() or c == '.')
        try:
            processed['vve_contribution'] = float(value) if value else None
        except ValueError:
            processed['vve_contribution'] = None
    
    # Process building year and age
    if processed['build_year']:
        year = ''.join(filter(str.isdigit, processed['build_year']))
        if year:
            processed['building_age'] = current_year - int(year)
            processed['build_year'] = int(year)
    
    # Process rooms
    if processed['rooms']:
        processed['rooms'] = next((int(c) for c in processed['rooms'] if c.isdigit()), None)
    
    # Process energy label
    if processed['energy_label']:
        processed['energy_label'] = processed['energy_label'].split('Wat')[0].strip()
    
    # Process postal code and city
    if processed['postal_city']:
        parts = processed['postal_city'].split()
        if len(parts) >= 2:
            processed['PC4'] = parts[0] if len(parts[0]) == 4 and parts[0].isdigit() else None
            processed['PC6'] = parts[1] if len(parts) > 1 else None
            processed['city'] = ' '.join(parts[2:]) if len(parts) > 2 else None
        else:
            processed['PC4'] = processed['PC6'] = processed['city'] = None
    else:
        processed['PC4'] = processed['PC6'] = processed['city'] = None
    
    # Process text fields to lowercase first word
    text_fields = ['apartment_type', 'construction_type', 'heating_system']
    for field in text_fields:
        if processed[field]:
            processed[field] = processed[field].split()[0].lower()
    
    # Remove processed original fields
    for field in ['postal_city', 'build_year']:
        processed.pop(field)
    
    return processed


def get_house_features(url):
    if html := extract_page_html(url):
        raw_features = extract_all_features(html)
        processed_features = process_features(raw_features)
        return {
            'features': processed_features
        }
    return None