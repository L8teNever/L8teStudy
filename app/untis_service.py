
import webuntis
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)

# Cache structure: { (class_id, week_start_date): (timestamp, data) }
_UNTIS_CACHE = {}
_CACHE_TTL = 3600  # 1 hour default if background sync fails

def get_week_start(d):
    return d - timedelta(days=d.weekday())

def fetch_timetable_live(creds, target_date):
    """Internal helper to fetch data from Untis API"""
    try:
        # Safely extract server URL
        server_url = creds.server.strip().replace('https://', '').replace('http://', '')
        parts = server_url.split('/')
        server_url = parts[0] if parts else server_url
        school_name = creds.school.strip()
        
        s = webuntis.Session(
            server=server_url,
            username=creds.username,
            password=creds.get_password(),
            school=school_name,
            useragent='L8teStudy'
        )
        s.login()
        
        # Find class
        untis_class = None
        all_klassen = s.klassen()
        for c in all_klassen:
            if c.name.lower() == creds.untis_class_name.lower():
                untis_class = c
                break
        
        if not untis_class:
            s.logout()
            return None, f"Klasse {creds.untis_class_name} nicht gefunden"
            
        monday = get_week_start(target_date)
        # Use sunday to cover the whole week including weekend if any
        sunday = monday + timedelta(days=6)
        
        timetable_data = s.timetable(klasse=untis_class, start=monday, end=sunday)
        
        results = []
        for period in timetable_data:
            # Safely handle potentially empty lists
            subjects = getattr(period, 'subjects', [])
            teachers = getattr(period, 'teachers', [])
            rooms = getattr(period, 'rooms', [])
            
            results.append({
                'id': period.id,
                'start': period.start.isoformat(),
                'end': period.end.isoformat(),
                'subjects': [{'name': sub.name, 'long_name': getattr(sub, 'long_name', sub.name)} for sub in subjects] if subjects else [],
                'teachers': [{'name': t.name, 'long_name': getattr(t, 'long_name', t.name)} for t in teachers] if teachers else [],
                'rooms': [{'name': r.name, 'long_name': getattr(r, 'long_name', r.name)} for r in rooms] if rooms else [],
                'code': getattr(period, 'code', ''),
                'substText': getattr(period, 'substText', ''),
                'activityType': getattr(period, 'activityType', ''),
                'bkText': getattr(period, 'bkText', '')
            })
            
        s.logout()
        return results, None
    except Exception as e:
        logger.error(f"Untis fetch failed: {e}")
        return None, str(e)

def get_timetable(creds, target_date):
    """Main entry point for routes. Checks cache first."""
    class_id = creds.class_id
    week_start = get_week_start(target_date)
    cache_key = (class_id, week_start)
    
    # Check if in cache and not extremely old
    if cache_key in _UNTIS_CACHE:
        timestamp, data = _UNTIS_CACHE[cache_key]
        # Even if we have a background job, we check if it's too old just in case the job died
        if (datetime.now() - timestamp).total_seconds() < 7200: # 2 hours safety
            return data, None
            
    # If not in cache or too old, fetch live
    data, error = fetch_timetable_live(creds, target_date)
    if data is not None:
        _UNTIS_CACHE[cache_key] = (datetime.now(), data)
        return data, None
    
    return None, error

def update_untis_cache_job(app):
    """Background job to refresh cache for all active classes"""
    with app.app_context():
        from .models import UntisCredential
        logger.info("Starting background Untis cache update...")
        
        creds_list = UntisCredential.query.all()
        today = date.today()
        # Cache current week and next week
        target_dates = [today, today + timedelta(days=7)]
        
        for creds in creds_list:
            for d in target_dates:
                week_start = get_week_start(d)
                logger.debug(f"Refreshing Untis cache for class {creds.class_id} week {week_start}")
                data, error = fetch_timetable_live(creds, d)
                if data is not None:
                    _UNTIS_CACHE[(creds.class_id, week_start)] = (datetime.now(), data)
                else:
                    logger.warning(f"Background Untis sync failed for class {creds.class_id}: {error}")
        
        logger.info("Untis cache update finished.")
