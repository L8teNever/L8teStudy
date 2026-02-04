
@api_bp.route('/decks/import', methods=['POST'])
@login_required
def import_deck():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = secure_filename(file.filename)
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    imported_cards = []
    deck_title = name.replace('_', ' ').replace('-', ' ').title()

    try:
        # CSV / TXT Import
        if ext in ['.csv', '.txt']:
            # Read into string
            try:
                content = file.stream.read().decode("utf-8")
            except UnicodeDecodeError:
                # Fallback to simple latin-1 if utf-8 fails
                file.stream.seek(0)
                content = file.stream.read().decode("latin-1")

            stream = StringIO(content, newline=None)
            
            # Detect delimiter
            sample = stream.getvalue()[:1024]
            delimiter = ';' if ';' in sample and sample.count(';') > sample.count(',') else ','
            if '\t' in sample: delimiter = '\t'
            
            csv_reader = csv.reader(stream, delimiter=delimiter)
            
            # Simple heuristic: look for 2+ columns
            for row in csv_reader:
                if len(row) >= 2:
                    front = row[0].strip()
                    back = row[1].strip()
                    if front and back:
                        imported_cards.append({'front': front, 'back': back})
        
        # Anki .apkg Import
        elif ext == '.apkg':
            # Need to save to temp file to use zipfile/sqlite3 easily on file paths or BytesIO
            temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"temp_anki_{current_user.id}_{int(datetime.utcnow().timestamp())}.apkg")
            file.save(temp_path)
            
            try:
                with zipfile.ZipFile(temp_path, 'r') as z:
                    # Extract collection.anki2 to a temp location
                    # Names inside zip might be arbitrary, but standard is 'collection.anki2'
                    # Or just look for any file that is an sqlite db? Standard is safe for now.
                    if 'collection.anki2' in z.namelist():
                        z.extract('collection.anki2', path=os.path.dirname(temp_path))
                        db_path = os.path.join(os.path.dirname(temp_path), 'collection.anki2')
                        
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        
                        # Fetch notes (cards content)
                        # fields are \x1f separated
                        cursor.execute("SELECT flds FROM notes")
                        rows = cursor.fetchall()
                        
                        for row in rows:
                            fields = row[0].split('\x1f')
                            if len(fields) >= 2:
                                imported_cards.append({
                                    'front': fields[0],
                                    'back': fields[1]
                                })
                        
                        conn.close()
                        
                        # Cleanup extracted DB
                        if os.path.exists(db_path):
                            os.remove(db_path)
            
            finally:
                # Cleanup zip
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        else:
             return jsonify({'error': 'Unsupported file type. Use .csv, .txt or .apkg'}), 400
             
        if not imported_cards:
            return jsonify({'error': 'No cards found in file'}), 400
            
        # Create Deck
        from .models import Deck, Flashcard
        new_deck = Deck(
            title=deck_title + " (Importiert)",
            user_id=current_user.id,
            description=f"Importiert am {date.today().strftime('%d.%m.%Y')}"
        )
        db.session.add(new_deck)
        db.session.flush()
        
        # Add Cards
        count = 0
        for card_data in imported_cards:
            # Optional: Clean HTML from Anki cards if desired, but retaining might be better
            # For now, raw import
            card = Flashcard(
                deck_id=new_deck.id,
                front=card_data['front'],
                back=card_data['back']
            )
            db.session.add(card)
            count += 1
            
        db.session.commit()
        
        return jsonify({'success': True, 'id': new_deck.id, 'count': count})

    except Exception as e:
        current_app.logger.error(f"Import error: {e}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'Import failed: {str(e)}'}), 500
