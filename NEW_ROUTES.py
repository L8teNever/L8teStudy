# Neue Routen für separate Seiten
# Diese Datei sollte in routes.py eingefügt werden

# Ersetze die class_view Funktion mit diesen spezifischen Routen:

@main_bp.route('/<class_name>/home')
def class_home(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied: You do not belong to this class.", 403
            
    return render_template('pages/home.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/tasks')
def class_tasks(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/tasks.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/calendar')
def class_calendar(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/calendar.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/stundenplan')
def class_stundenplan(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/stundenplan.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/grades')
def class_grades(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/grades.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/flashcards')
@main_bp.route('/<class_name>/flashcards/<path:subpath>')
def class_flashcards(class_name, subpath=None):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/flashcards.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/drive')
def class_drive(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/drive.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/mealplan')
def class_mealplan(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/mealplan.html', user=current_user, active_class=target_class, version=get_version())

@main_bp.route('/<class_name>/blackboard')
def class_blackboard(class_name):
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login_page'))
        
    from .models import SchoolClass
    target_class = SchoolClass.query.filter(SchoolClass.name.ilike(class_name)).first()
    
    if not target_class:
        return redirect('/')
        
    if not current_user.is_super_admin:
        if not current_user.school_class or current_user.school_class.id != target_class.id:
            return "Access Denied", 403
            
    return render_template('pages/blackboard.html', user=current_user, active_class=target_class, version=get_version())

# Helper function to get version
def get_version():
    try:
        with open('version.txt', 'r') as f:
            return f.read().strip()
    except:
        return '2.1.1'
